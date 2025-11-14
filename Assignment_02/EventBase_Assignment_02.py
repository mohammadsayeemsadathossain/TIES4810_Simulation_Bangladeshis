# Cell: imports & RNG
import simulus
import random
from collections import deque
from statistics import mean

# For reproducibility (set seed)
random.seed(12345)

# Create simulator
sim = simulus.simulator()

# --- PARAMETERS (changeable, don't hardcode deep inside functions) ---
MEAN_INTERARRIVAL = 25.0
P_PREP = 3          # number of prep rooms
R_RECOVERY = 3      # number of recovery beds
SIM_END = 10000.0   # simulation time to run (or use event-based stopping)

# Mean service times (example)
MEAN_PREP = 40.0
MEAN_OP = 20.0
MEAN_REC = 40.0

# --- STATE VARIABLES ---
EntryQueue = deque()   # waiting for prep
OpQueue = deque()      # waiting for OR
# Note: RecQueue is implicit via OR blocked flag + a slot holding blocked patient
num_free_prep = P_PREP
num_free_recovery = R_RECOVERY
op_busy = False
op_blocked = False
op_blocked_patient = None
op_block_start_time = None

# Per-patient records and global counters
next_patient_id = 0
patient_records = {}   # id -> dict with times and service times
completed_throughputs = []
n_block_events = 0
total_block_time = 0.0
total_arrivals = 0
n_unserved = 0  # if you later implement finite entry queue capacity

# Helper sampling functions (replace with numpy if you prefer)
def sample_interarrival():
    return random.expovariate(1.0/MEAN_INTERARRIVAL)

def sample_prep_time():
    return random.expovariate(1.0/MEAN_PREP)

def sample_op_time():
    return random.expovariate(1.0/MEAN_OP)

def sample_rec_time():
    return random.expovariate(1.0/MEAN_REC)


# --- EVENT HANDLERS ---
# 1) Arrival
def arrival():
    global next_patient_id, total_arrivals
    t = sim.now
    pid = next_patient_id
    next_patient_id += 1
    total_arrivals += 1

    # Create patient record
    patient_records[pid] = {
        'arrival_time': t,
        'status': 'Waiting',
        'prep_time': sample_prep_time(),
        'op_time': sample_op_time(),
        'rec_time': sample_rec_time()
    }

    # Enqueue to EntryQueue
    EntryQueue.append(pid)
    # print(f"[{sim.now:.1f}] ARRIVAL: Patient {pid} arrived "
      # f"(prep_time={patient_records[pid]['prep_time']:.1f}, "
      # f"op_time={patient_records[pid]['op_time']:.1f}, "
      # f"rec_time={patient_records[pid]['rec_time']:.1f}) | "
      # f"EntryQueue={len(EntryQueue)}")


    # Immediately try start prep (activity scanning)
    sim.sched(s_start_prep, offset=0)

    # Schedule next arrival
    sim.sched(arrival, offset=sample_interarrival())

# 2) S-Prep (Start Preparation)
def s_start_prep():
    global num_free_prep
    t = sim.now
    # Preconditions: EntryQueue not empty and free prep room
    if EntryQueue and num_free_prep > 0:
        pid = EntryQueue.popleft()
        num_free_prep -= 1
        patient_records[pid]['status'] = 'In_Prep'
        patient_records[pid]['prep_start'] = t
        
       #  print(f"[{sim.now:.1f}] S-Prep: Started prep for Patient {pid} | "
          # f"FreePrep={num_free_prep}, EntryQ={len(EntryQueue)}")

        # schedule end of prep
        sim.sched(e_end_prep, pid, offset=patient_records[pid]['prep_time'])
    # else: nothing to do; event is safe to try again later, only debugging info if needed
    # else:
        # print(f"[{sim.now:.1f}] S-Prep: Cannot start (FreePrep={num_free_prep}, "
          # f"EntryQ={len(EntryQueue)})")


# 3) E-Prep (End Preparation)
def e_end_prep(pid):
    t = sim.now
    # mark waiting for op and enqueue
    patient_records[pid]['prep_end'] = t
    patient_records[pid]['status'] = 'Waiting_Op'
    OpQueue.append(pid)
    # print(f"[{sim.now:.1f}] E-Prep: Patient {pid} finished prep → OpQueue "
      # f"(len={len(OpQueue)}) | FreePrep={num_free_prep}")

    # Try start operation and next prep
    sim.sched(s_start_op, offset=0)
    sim.sched(s_start_prep, offset=0)

# 4) S-Op (Start Operation)
def s_start_op():
    global op_busy, num_free_prep
    t = sim.now
    # Preconditions: OpQueue not empty and op not busy
    if (not op_busy) and OpQueue:
        pid = OpQueue.popleft()
        # release prep room (prep room freed when surgery STARTS)
        num_free_prep += 1
        op_busy = True
        # print(f"[{sim.now:.1f}] S-Op: Started surgery for Patient {pid} | "
          # f"OpBusy={op_busy}, OpQueue={len(OpQueue)}")

        patient_records[pid]['status'] = 'In_Op'
        patient_records[pid]['op_start'] = t
        # schedule end of surgery
        sim.sched(e_end_op, pid, offset=patient_records[pid]['op_time'])
   # else:
   #     print(f"[{t:.1f}] S-Op: Cannot start (op_busy={op_busy}, queue={len(OpQueue)})")

# 5) E-Op (End Operation)
def e_end_op(pid):
    global op_blocked, op_block_start_time, n_block_events, op_blocked_patient
    t = sim.now
    patient_records[pid]['op_end'] = t
    patient_records[pid]['status'] = 'Waiting_Rec'
    # print(f"[{sim.now:.1f}] E-Op: Patient {pid} finished operation | "
      # f"FreeRecovery={num_free_recovery}, OpBusy={op_busy}")

    # Try to start recovery immediately (S-Rec)
    # If no recovery bed -> OR becomes blocked and the patient stays in OR
    if num_free_recovery > 0:
        # schedule S-Rec immediately (as an event)
        sim.sched(s_start_rec, pid, offset=0)
    else:
        # OR blocked: set flag and keep track of blocked patient
        op_blocked = True
        op_block_start_time = t
        n_block_events += 1
        op_blocked_patient = pid
        # op_busy remains True while blocked (OR occupied by blocked patient)

# 6) S-Rec (Start Recovery)
def s_start_rec(pid):
    global num_free_recovery, op_busy, op_blocked, total_block_time, op_block_start_time, op_blocked_patient
    t = sim.now
    # Preconditions: recovery bed available and the patient must be waiting for rec
    if num_free_recovery > 0 and patient_records.get(pid, {}).get('status') == 'Waiting_Rec':
        # Reserve a recovery bed
        num_free_recovery -= 1
        # If this patient was blocking the OR, we must end the blocking
        if op_blocked and op_blocked_patient == pid:
            op_blocked = False
            # accumulate blocked time
            total_block_time += (t - op_block_start_time)
            op_block_start_time = None
            op_blocked_patient = None
            # releasing OR: op_busy becomes False after we start recovery
            op_busy = False
        else:
            # In normal case, the patient finished op and OR is freed here:
            op_busy = False

        patient_records[pid]['rec_start'] = t
        patient_records[pid]['status'] = 'Recovering'
        # print(f"[{sim.now:.1f}] S-Rec: Patient {pid} moved to Recovery | "
          # f"FreeRecovery={num_free_recovery}")

        # Schedule end of recovery
        sim.sched(e_end_rec, pid, offset=patient_records[pid]['rec_time'])

        # After freeing OR, try to start next Op if queued
        sim.sched(s_start_op, offset=0)
    # else: cannot start recovery now (shouldn't happen if caller checked), safe to ignore
    # else:
        # print(f"[{sim.now:.1f}] S-Rec: BLOCKED! No free recovery bed for Patient {pid} | "
          # f"FreeRecovery={num_free_recovery}")


# 7) E-Rec (End Recovery)
def e_end_rec(pid):
    global num_free_recovery
    t = sim.now
    # Release recovery bed
    num_free_recovery += 1
    patient_records[pid]['rec_end'] = t
    patient_records[pid]['status'] = 'Recovered'
    # print(f"[{sim.now:.1f}] E-Rec: Patient {pid} finished Recovery | "
      # f"FreeRecovery={num_free_recovery}")

    # Schedule final Release event
    sim.sched(release_patient, pid, offset=0)
    # After freeing a bed, maybe an OR-blocked patient can start recovery
    if op_blocked and op_blocked_patient is not None:
        # schedule starting recovery for blocked patient immediately
        sim.sched(s_start_rec, op_blocked_patient, offset=0)

# 8) Release (collect stats & cleanup)
def release_patient(pid):
    t = sim.now
    patient_records[pid]['release_time'] = t
    patient_records[pid]['status'] = 'Released'
    throughput = t - patient_records[pid]['arrival_time']
    completed_throughputs.append(throughput)
    # print(f"[{sim.now:.1f}] RELEASE: Patient {pid} leaves system | "
      # f"ThroughputTime={sim.now - patient_records[pid]['arrival_time']:.1f}")

    # Optionally remove record to save memory:
    # del patient_records[pid]


# --- Bootstrapping: schedule the first arrival and run ---
sim.sched(arrival, offset=0)

# Run simulation
sim.run(until=SIM_END)

# --- Simple post-run stats ---
print("Arrivals:", total_arrivals)
print("Completed:", len(completed_throughputs))
if completed_throughputs:
    print("Mean throughput:", mean(completed_throughputs))
print("Number of OR block events:", n_block_events)
print("Total OR blocked time:", total_block_time)
print("Final num_free_prep:", num_free_prep)
print("Final num_free_recovery:", num_free_recovery)

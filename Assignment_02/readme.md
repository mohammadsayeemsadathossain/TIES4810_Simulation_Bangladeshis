**Assignment 2**

**Event-Based Simulation Model**

**Scenario:** Hospital patient flow through Preparation, Operation, and
Recovery stages

**1. Background**

This simulation models the flow of patients through a small surgical
unit consisting of:

- *P* identical **preparation rooms**,

- *1* **operating theatre**, and

- *R* **recovery rooms**.

Patients arrive according to an interarrival time distribution (e.g.,
exponential) and move sequentially through the three phases:  
**Preparation → Operation → Recovery → Release.**

Each phase has a stochastic service time (e.g., exponential), and
resources have finite capacities.  
The simulation aims to measure:

- Average patient **throughput time**,

- **Operating theatre blocking time** (when it cannot release a patient
  because recovery is full), and

- Resource utilizations and queue lengths.

This model follows an **event-based paradigm**, where instantaneous
*events* change the system's state, and subsequent events are triggered
accordingly.

**2. Terminology and System Variables**

| **Category**            | **Symbol / Variable**                                             | **Description**                                          |
|-------------------------|-------------------------------------------------------------------|----------------------------------------------------------|
| **Resources**           | PrepRooms                                                         | Pool of P identical preparation facilities               |
|                         | OpRoom                                                            | Single operating theatre                                 |
|                         | RecoveryRooms                                                     | Pool of R identical recovery facilities                  |
| **Queues**              | EntryQueue                                                        | Queue of patients waiting for preparation                |
|                         | OpQueue                                                           | Queue of patients waiting for operation                  |
|                         | RecQueue                                                          | Queue of operated patients waiting for recovery          |
| **Patient Attributes**  | id                                                                | Unique identifier                                        |
|                         | arrival_time                                                      | Time of patient arrival                                  |
|                         | status                                                            | Current stage (Waiting, In_Prep, etc.)                   |
|                         | prep_time, op_time, rec_time                                      | Individual service times for each phase                  |
|                         | start_time, end_time                                              | For throughput measurement                               |
| **State Variables**     | num_free_prep, num_free_recovery                                  | Count of available facilities                            |
|                         | op_busy                                                           | Boolean (True if OR is in use)                           |
|                         | op_blocked                                                        | Boolean (True if OR cannot release due to recovery full) |
|                         | event_list                                                        | Chronological list of future events                      |
| **Performance Metrics** | avg_throughput_time, OR_blocking_time, queue_lengths, utilization | Collected during simulation                              |

**3. Events**

Eight distinct events govern the simulation.  
Each event has:

- **Preconditions** (checked before execution),

- **Actions** (state updates), and

- **Triggers** (subsequent events to schedule).

This is an **activity-scanning** type model --- *Start* events are "safe
to try" at any time, as they will only execute if their preconditions
are true.

**3.1. Event List**

| **Event**                      | **Preconditions**                                                              | **Actions (State Change)**                                                                                                                                         | **Triggers**                                                                     |
|--------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| **Arrival**                    | Always executable                                                              | \- Create new patient P.- Set P.status = \'Waiting\'.- Add P to EntryQueue.- Record arrival time.- Schedule next Arrival after interarrival_time.                  | \- Try S-Prep immediately.                                                       |
| **S-Prep (Start Preparation)** | EntryQueue not empty **and** num_free_prep \> 0                                | \- Dequeue one patient P from EntryQueue.- Reserve one preparation room (num_free_prep -= 1).- Set P.status = \'In_Prep\'.                                         | \- Schedule E-Prep after P.prep_time.                                            |
| **E-Prep (End Preparation)**   | Always after delay                                                             | \- Mark P.status = \'Waiting_Op\'.- Add P to OpQueue.                                                                                                              | \- Try S-Op (operation start).- Try S-Prep (for next patient).                   |
| **S-Op (Start Operation)**     | OpQueue not empty **and** OR free                                              | \- Dequeue one patient P.- Release one prep room (num_free_prep += 1).- Set OpRoom busy (op_busy = True).- Set P.status = \'In_Op\'.                               | \- Schedule E-Op after P.op_time.                                                |
| **E-Op (End Operation)**       | Always after delay                                                             | \- Mark P.status = \'Waiting_Rec\'.                                                                                                                                | \- Try S-Rec (to start recovery).                                                |
| **S-Rec (Start Recovery)**     | num_free_recovery \> 0 **and** OR has waiting patient (status=\'Waiting_Rec\') | \- Reserve one recovery bed (num_free_recovery -= 1).- Release OR (op_busy = False).- Record blocking duration if OR was waiting.- Mark P.status = \'Recovering\'. | \- Schedule E-Rec after P.rec_time.- Try S-Op (check if next patient can start). |
| **E-Rec (End Recovery)**       | Always after delay                                                             | \- Release one recovery bed (num_free_recovery += 1).- Mark P.status = \'Recovered\'.                                                                              | \- Schedule Release.- Try S-Rec (for any remaining patients).                    |
| **Release**                    | Always executable                                                              | \- Mark P.status = \'Released\'.- Record throughput time.- Update performance statistics.- Remove P from system.                                                   | None                                                                             |

**4. Synchronization and Logic Flow**

The event structure ensures proper synchronization between resources and
patients:

1.  **Arrival → S-Prep**: new patient enters queue and triggers
    preparation check.

2.  **S-Prep → E-Prep → S-Op**: after prep, patient moves to operation
    queue; next prep may begin.

3.  **S-Op → E-Op → S-Rec**: surgery completes; if recovery full, OR
    remains blocked.

4.  **S-Rec → E-Rec → Release**: recovery completes; resources released;
    statistics updated.

Whenever a **resource becomes free** or a **patient changes state**, the
corresponding *Start* event is automatically retried (activity
scanning).

**Resource Release Timing**

- **Prep room** released only when surgery starts (S-Op).

- **OR** released only when recovery starts (S-Rec).

- **Recovery bed** released at end of recovery (E-Rec).

**5. Flowchart Overview**

![A diagram of a flowchart AI-generated content may be
incorrect.](media/Event_Base_Flow_Chart.png){width="4.885416666666667in"
height="9.0in"}

**6. Data Collection and Outputs**

At simulation end, compute:

- **Average throughput time** = mean(release_time -- arrival_time)

- **OR blocking time / probability**

- **Utilization** of prep, OR, and recovery resources

- **Average queue lengths**

Optional monitoring process may record snapshots periodically to
approximate time-dependent averages.

**7. Possible Future Extensions**

a)  Multiple patient types with distinct service-time distributions.

b)  Priority handling (e.g., emergency vs. elective).

c)  Dynamic staff availability or resource breakdowns.

d)  Non-exponential service distributions.

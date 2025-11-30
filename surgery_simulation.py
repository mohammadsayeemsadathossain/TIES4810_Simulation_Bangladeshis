import simpy
import random
import statistics
from dataclasses import dataclass, field
from typing import List


@dataclass
class SimulationConfig:
    """Configuration parameters for surgery simulation"""

    # Resource capacities
    num_prep_rooms: int = 3
    num_operating_rooms: int = 1
    num_recovery_rooms: int = 2

    # Time distributions (in minutes)
    interarrival_mean: float = 25.0
    prep_time_mean: float = 40.0
    surgery_time_mean: float = 20.0
    recovery_time_mean: float = 40.0

    # Simulation parameters
    sim_duration: float = 1000.0  # Total simulation time
    warmup_period: float = 200.0  # Discard initial transient data
    random_seed: int = 42


@dataclass
class Patient:
    """Represents a patient with timestamps"""

    id: int
    arrival_time: float = 0.0
    prep_start: float = 0.0
    prep_end: float = 0.0
    surgery_start: float = 0.0
    surgery_end: float = 0.0
    recovery_start: float = 0.0
    recovery_end: float = 0.0

    def throughput_time(self) -> float:
        """Total time from arrival to departure"""
        return self.recovery_end - self.arrival_time


class SurgerySimulation:
    """Main simulation class using process-based approach"""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.env = simpy.Environment()

        # Resources (using simpy.Resource for capacity-limited facilities)
        self.prep_rooms = simpy.Resource(self.env, capacity=config.num_prep_rooms)
        self.operating_rooms = simpy.Resource(
            self.env, capacity=config.num_operating_rooms
        )
        self.recovery_rooms = simpy.Resource(
            self.env, capacity=config.num_recovery_rooms
        )

        # Statistics tracking
        self.patients: List[Patient] = []
        self.patient_counter = 0
        self.or_blocking_times: List[float] = []  # Times when OR was blocked
        self.or_blocking_start: float = None

        # Queue monitoring
        self.prep_queue_samples: List[int] = []
        self.prep_queue_times: List[float] = []
        self.sample_interval = 10.0  # Sample every 10 time units

    def patient_generator(self):
        """Generate patients with exponential inter-arrival times"""
        while True:
            yield self.env.timeout(
                random.expovariate(1.0 / self.config.interarrival_mean)
            )

            self.patient_counter += 1
            patient = Patient(id=self.patient_counter, arrival_time=self.env.now)
            self.patients.append(patient)

            # Start patient process
            self.env.process(self.patient_process(patient))

    def patient_process(self, patient: Patient):
        """
        Patient lifecycle - CRITICAL: Implements blocking mechanism correctly

        Key insight from feedback: Prep room should be released when surgery STARTS,
        not when prep ends, because patient waits in prep until OR is available.
        """

        # STAGE 1: PREPARATION
        prep_request = self.prep_rooms.request()
        yield prep_request  # Wait for prep room

        patient.prep_start = self.env.now
        prep_duration = random.expovariate(1.0 / self.config.prep_time_mean)
        yield self.env.timeout(prep_duration)
        patient.prep_end = self.env.now

        # STAGE 2: OPERATING ROOM (with blocking handling)
        or_request = self.operating_rooms.request()
        yield or_request  # Wait for OR availability

        # ⚠️ CRITICAL FIX: Release prep room ONLY when surgery starts
        # (Patient waited in prep room until OR became available)
        self.prep_rooms.release(prep_request)

        patient.surgery_start = self.env.now
        surgery_duration = random.expovariate(1.0 / self.config.surgery_time_mean)
        yield self.env.timeout(surgery_duration)
        patient.surgery_end = self.env.now

        # STAGE 3: RECOVERY (with blocking detection)
        # Check if recovery room available - if not, OR is BLOCKED
        recovery_request = self.recovery_rooms.request()

        if (
            len(self.recovery_rooms.queue) > 0
            or self.recovery_rooms.count >= self.config.num_recovery_rooms
        ):
            # OR is blocked! Record blocking start time
            if self.or_blocking_start is None:
                self.or_blocking_start = self.env.now

        yield recovery_request  # Wait for recovery room (OR stays occupied!)

        # Recovery room acquired - end blocking if it was occurring
        if self.or_blocking_start is not None:
            blocking_duration = self.env.now - self.or_blocking_start
            self.or_blocking_times.append(blocking_duration)
            self.or_blocking_start = None

        # ⚠️ CRITICAL: Release OR only AFTER recovery room is secured
        self.operating_rooms.release(or_request)

        patient.recovery_start = self.env.now
        recovery_duration = random.expovariate(1.0 / self.config.recovery_time_mean)
        yield self.env.timeout(recovery_duration)
        patient.recovery_end = self.env.now

        # Release recovery room
        self.recovery_rooms.release(recovery_request)

    def queue_monitor(self):
        """Monitor queue lengths at regular intervals"""
        while True:
            # Record current queue length before prep rooms
            queue_length = len(self.prep_rooms.queue)

            # Only record after warmup period
            if self.env.now >= self.config.warmup_period:
                self.prep_queue_samples.append(queue_length)
                self.prep_queue_times.append(self.env.now)

            yield self.env.timeout(self.sample_interval)

    def run(self):
        """Execute simulation"""
        random.seed(self.config.random_seed)
        self.env.process(self.patient_generator())
        self.env.process(self.queue_monitor())  # Start queue monitoring
        self.env.run(until=self.config.sim_duration)

    def get_statistics(self):
        """Calculate statistics excluding warmup period"""
        valid_patients = [
            p
            for p in self.patients
            if p.recovery_end > self.config.warmup_period and p.recovery_end > 0
        ]

        if not valid_patients:
            return None

        throughput_times = [p.throughput_time() for p in valid_patients]

        # OR blocking statistics
        total_blocking_time = sum(self.or_blocking_times)
        simulation_time = self.config.sim_duration - self.config.warmup_period
        blocking_probability = (
            total_blocking_time / simulation_time if simulation_time > 0 else 0
        )

        # Queue statistics
        avg_prep_queue = (
            statistics.mean(self.prep_queue_samples) if self.prep_queue_samples else 0
        )
        max_prep_queue = max(self.prep_queue_samples) if self.prep_queue_samples else 0

        return {
            "num_patients": len(valid_patients),
            "avg_throughput_time": statistics.mean(throughput_times),
            "std_throughput_time": (
                statistics.stdev(throughput_times) if len(throughput_times) > 1 else 0
            ),
            "min_throughput_time": min(throughput_times),
            "max_throughput_time": max(throughput_times),
            "total_or_blocking_time": total_blocking_time,
            "or_blocking_probability": blocking_probability,
            "num_blocking_events": len(self.or_blocking_times),
            "avg_prep_queue_length": avg_prep_queue,
            "max_prep_queue_length": max_prep_queue,
        }


# Quick test
if __name__ == "__main__":
    config = SimulationConfig()
    sim = SurgerySimulation(config)
    sim.run()
    stats = sim.get_statistics()

    print("=== Simulation Results ===")
    for key, value in stats.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")

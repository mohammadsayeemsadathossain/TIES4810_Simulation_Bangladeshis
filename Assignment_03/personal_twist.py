import simpy
import random
import statistics
import numpy as np
from dataclasses import dataclass
from typing import List, Dict
import json


@dataclass
class SimulationConfig:
    """Configuration parameters for surgery simulation"""

    num_prep_rooms: int = 3
    num_operating_rooms: int = 1
    num_recovery_rooms: int = 5

    interarrival_mean: float = 25.0
    prep_time_mean: float = 40.0
    surgery_time_mean: float = 20.0
    recovery_time_mean: float = 40.0

    sim_duration: float = 1000.0
    warmup_period: float = 200.0
    random_seed: int = 42

    # Personal twist: priority system
    emergency_probability: float = 0.2  # 20% of patients are emergency


@dataclass
class Patient:
    """Represents a patient with timestamps and priority"""

    id: int
    is_emergency: bool = False
    arrival_time: float = 0.0
    prep_start: float = 0.0
    prep_end: float = 0.0
    surgery_start: float = 0.0
    surgery_end: float = 0.0
    recovery_start: float = 0.0
    recovery_end: float = 0.0

    def throughput_time(self) -> float:
        return self.recovery_end - self.arrival_time


class PrioritySimulation:
    """Surgery simulation with priority-based scheduling"""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.env = simpy.Environment()

        # Use PriorityResource for prep and OR (lower priority number = higher priority)
        self.prep_rooms = simpy.PriorityResource(
            self.env, capacity=config.num_prep_rooms
        )
        self.operating_rooms = simpy.PriorityResource(
            self.env, capacity=config.num_operating_rooms
        )
        self.recovery_rooms = simpy.Resource(
            self.env, capacity=config.num_recovery_rooms
        )

        # Statistics tracking
        self.patients: List[Patient] = []
        self.patient_counter = 0
        self.or_blocking_times: List[float] = []
        self.or_blocking_start: float = None

        # Separate tracking for emergency vs elective
        self.emergency_patients: List[Patient] = []
        self.elective_patients: List[Patient] = []

        # Queue monitoring
        self.prep_queue_samples: List[int] = []
        self.sample_interval = 10.0

    def patient_generator(self):
        """Generate patients with priority classification"""
        while True:
            yield self.env.timeout(
                random.expovariate(1.0 / self.config.interarrival_mean)
            )

            self.patient_counter += 1
            is_emergency = random.random() < self.config.emergency_probability

            patient = Patient(
                id=self.patient_counter,
                arrival_time=self.env.now,
                is_emergency=is_emergency,
            )
            self.patients.append(patient)

            if is_emergency:
                self.emergency_patients.append(patient)
            else:
                self.elective_patients.append(patient)

            self.env.process(self.patient_process(patient))

    def patient_process(self, patient: Patient):
        """Patient lifecycle with priority"""
        # Priority: 0 for emergency, 1 for elective (lower = higher priority)
        priority = 0 if patient.is_emergency else 1

        # STAGE 1: PREPARATION (with priority)
        prep_request = self.prep_rooms.request(priority=priority)
        yield prep_request

        patient.prep_start = self.env.now
        prep_duration = random.expovariate(1.0 / self.config.prep_time_mean)
        yield self.env.timeout(prep_duration)
        patient.prep_end = self.env.now

        # STAGE 2: OPERATING ROOM (with priority)
        or_request = self.operating_rooms.request(priority=priority)
        yield or_request

        self.prep_rooms.release(prep_request)

        patient.surgery_start = self.env.now
        surgery_duration = random.expovariate(1.0 / self.config.surgery_time_mean)
        yield self.env.timeout(surgery_duration)
        patient.surgery_end = self.env.now

        # STAGE 3: RECOVERY (with blocking detection)
        recovery_request = self.recovery_rooms.request()

        if (
            len(self.recovery_rooms.queue) > 0
            or self.recovery_rooms.count >= self.config.num_recovery_rooms
        ):
            if self.or_blocking_start is None:
                self.or_blocking_start = self.env.now

        yield recovery_request

        if self.or_blocking_start is not None:
            blocking_duration = self.env.now - self.or_blocking_start
            self.or_blocking_times.append(blocking_duration)
            self.or_blocking_start = None

        self.operating_rooms.release(or_request)

        patient.recovery_start = self.env.now
        recovery_duration = random.expovariate(1.0 / self.config.recovery_time_mean)
        yield self.env.timeout(recovery_duration)
        patient.recovery_end = self.env.now

        self.recovery_rooms.release(recovery_request)

    def queue_monitor(self):
        """Monitor queue lengths"""
        while True:
            if self.env.now >= self.config.warmup_period:
                self.prep_queue_samples.append(len(self.prep_rooms.queue))
            yield self.env.timeout(self.sample_interval)

    def run(self):
        """Execute simulation"""
        random.seed(self.config.random_seed)
        self.env.process(self.patient_generator())
        self.env.process(self.queue_monitor())
        self.env.run(until=self.config.sim_duration)

    def get_statistics(self):
        """Calculate statistics for all patients and by priority"""
        valid_patients = [
            p
            for p in self.patients
            if p.recovery_end > self.config.warmup_period and p.recovery_end > 0
        ]

        valid_emergency = [p for p in valid_patients if p.is_emergency]
        valid_elective = [p for p in valid_patients if not p.is_emergency]

        if not valid_patients:
            return None

        # Overall statistics
        throughput_times = [p.throughput_time() for p in valid_patients]
        total_blocking_time = sum(self.or_blocking_times)
        simulation_time = self.config.sim_duration - self.config.warmup_period
        blocking_probability = (
            total_blocking_time / simulation_time if simulation_time > 0 else 0
        )
        avg_prep_queue = (
            statistics.mean(self.prep_queue_samples) if self.prep_queue_samples else 0
        )

        # Emergency statistics
        emergency_throughput = (
            [p.throughput_time() for p in valid_emergency] if valid_emergency else [0]
        )

        # Elective statistics
        elective_throughput = (
            [p.throughput_time() for p in valid_elective] if valid_elective else [0]
        )

        return {
            "num_patients": len(valid_patients),
            "num_emergency": len(valid_emergency),
            "num_elective": len(valid_elective),
            "avg_throughput_time": statistics.mean(throughput_times),
            "std_throughput_time": (
                statistics.stdev(throughput_times) if len(throughput_times) > 1 else 0
            ),
            "or_blocking_probability": blocking_probability,
            "avg_prep_queue_length": avg_prep_queue,
            # Priority-specific metrics
            "emergency_avg_throughput": statistics.mean(emergency_throughput),
            "emergency_std_throughput": (
                statistics.stdev(emergency_throughput)
                if len(emergency_throughput) > 1
                else 0
            ),
            "elective_avg_throughput": statistics.mean(elective_throughput),
            "elective_std_throughput": (
                statistics.stdev(elective_throughput)
                if len(elective_throughput) > 1
                else 0
            ),
        }


def run_priority_comparison():
    """Compare standard FIFO vs Priority-based system"""
    print("\n" + "=" * 70)
    print("🎯 PERSONAL TWIST: Priority-Based Scheduling")
    print("=" * 70)

    config = SimulationConfig(
        num_prep_rooms=3,
        num_operating_rooms=1,
        num_recovery_rooms=5,
        sim_duration=1000.0,
        warmup_period=200.0,
    )

    num_replications = 10
    results = []

    print("\nRunning 10 replications with PRIORITY SYSTEM...")
    print(f"  - 20% Emergency patients (higher priority)")
    print(f"  - 80% Elective patients (normal priority)\n")

    for i in range(num_replications):
        config.random_seed = 42 + i
        sim = PrioritySimulation(config)
        sim.run()
        stats = sim.get_statistics()

        if stats:
            results.append(stats)
            print(
                f"Rep {i+1:2d}: Emergency avg={stats['emergency_avg_throughput']:6.2f} min, "
                f"Elective avg={stats['elective_avg_throughput']:6.2f} min, "
                f"OR Blocking={stats['or_blocking_probability']:6.4f}"
            )

    # Compute confidence intervals
    emergency_times = [r["emergency_avg_throughput"] for r in results]
    elective_times = [r["elective_avg_throughput"] for r in results]
    blocking_probs = [r["or_blocking_probability"] for r in results]

    def ci(data):
        n = len(data)
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        margin = 2.262 * (std / np.sqrt(n))  # t-value for n=10
        return mean, margin

    emerg_mean, emerg_margin = ci(emergency_times)
    elect_mean, elect_margin = ci(elective_times)
    block_mean, block_margin = ci(blocking_probs)

    print("\n" + "=" * 70)
    print("📊 PRIORITY SYSTEM RESULTS")
    print("=" * 70)
    print(f"\n🚨 Emergency Patients:")
    print(f"   Average Throughput: {emerg_mean:.2f} ± {emerg_margin:.2f} min")
    print(f"\n📋 Elective Patients:")
    print(f"   Average Throughput: {elect_mean:.2f} ± {elect_margin:.2f} min")
    print(f"\n🔒 OR Blocking:")
    print(
        f"   Blocking Probability: {block_mean:.4f} ± {block_margin:.4f} ({block_mean*100:.2f}%)"
    )

    # Save results
    summary = {
        "emergency_throughput": {"mean": emerg_mean, "margin": emerg_margin},
        "elective_throughput": {"mean": elect_mean, "margin": elect_margin},
        "or_blocking": {"mean": block_mean, "margin": block_margin},
    }

    with open("results/priority_twist_results.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n✅ Results saved to: results/priority_twist_results.json")
    print("=" * 70)


if __name__ == "__main__":
    run_priority_comparison()

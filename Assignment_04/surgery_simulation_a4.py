"""
Assignment 4: Surgery Simulation with Design of Experiments
Main simulation model supporting all experimental factors
"""

import simpy
import random
import statistics
import numpy as np
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class DistributionType(Enum):
    """Types of probability distributions"""

    EXPONENTIAL = "exponential"
    UNIFORM = "uniform"


@dataclass
class SimulationConfig:
    """Configuration for surgery simulation - Assignment 4"""

    # Resource capacities
    num_prep_rooms: int = 4
    num_operating_rooms: int = 1
    num_recovery_rooms: int = 4

    # Interarrival time distribution
    interarrival_dist: DistributionType = DistributionType.EXPONENTIAL
    interarrival_param1: float = 25.0  # mean for exp, min for unif
    interarrival_param2: float = 25.0  # unused for exp, max for unif

    # Preparation time distribution
    prep_dist: DistributionType = DistributionType.EXPONENTIAL
    prep_param1: float = 40.0
    prep_param2: float = 40.0

    # Operation time (FIXED at exp(20))
    surgery_mean: float = 20.0

    # Recovery time distribution
    recovery_dist: DistributionType = DistributionType.EXPONENTIAL
    recovery_param1: float = 40.0
    recovery_param2: float = 40.0

    # Personal twist: priority system
    emergency_probability: float = 0.0  # 0.0=disabled, 0.2=enabled

    # Simulation parameters
    sim_duration: float = 5000.0
    warmup_period: float = 1000.0
    random_seed: int = 42


@dataclass
class Patient:
    """Patient with timestamps and priority"""

    id: int
    is_emergency: bool = False
    arrival_time: float = 0.0
    prep_queue_length_on_arrival: int = 0
    prep_start: float = 0.0
    prep_end: float = 0.0
    surgery_start: float = 0.0
    surgery_end: float = 0.0
    recovery_start: float = 0.0
    recovery_end: float = 0.0

    def throughput_time(self) -> float:
        return self.recovery_end - self.arrival_time


class SurgerySimulation:
    """Surgery simulation supporting all experimental factors"""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.env = simpy.Environment()

        # Resources
        if config.emergency_probability > 0:
            self.prep_rooms = simpy.PriorityResource(
                self.env, capacity=config.num_prep_rooms
            )
            self.operating_rooms = simpy.PriorityResource(
                self.env, capacity=config.num_operating_rooms
            )
        else:
            self.prep_rooms = simpy.Resource(self.env, capacity=config.num_prep_rooms)
            self.operating_rooms = simpy.Resource(
                self.env, capacity=config.num_operating_rooms
            )

        self.recovery_rooms = simpy.Resource(
            self.env, capacity=config.num_recovery_rooms
        )

        # Statistics
        self.patients: List[Patient] = []
        self.patient_counter = 0
        self.queue_length_on_arrivals: List[int] = []

    def sample_time(
        self, dist_type: DistributionType, param1: float, param2: float
    ) -> float:
        """Sample from specified distribution"""
        if dist_type == DistributionType.EXPONENTIAL:
            return random.expovariate(1.0 / param1)
        elif dist_type == DistributionType.UNIFORM:
            return random.uniform(param1, param2)
        else:
            raise ValueError(f"Unknown distribution: {dist_type}")

    def patient_generator(self):
        """Generate patients according to configured distribution"""
        while True:
            interarrival = self.sample_time(
                self.config.interarrival_dist,
                self.config.interarrival_param1,
                self.config.interarrival_param2,
            )
            yield self.env.timeout(interarrival)

            self.patient_counter += 1
            is_emergency = random.random() < self.config.emergency_probability

            patient = Patient(
                id=self.patient_counter,
                arrival_time=self.env.now,
                is_emergency=is_emergency,
            )

            # Record queue length at arrival
            patient.prep_queue_length_on_arrival = len(self.prep_rooms.queue)

            if self.env.now >= self.config.warmup_period:
                self.queue_length_on_arrivals.append(
                    patient.prep_queue_length_on_arrival
                )

            self.patients.append(patient)
            self.env.process(self.patient_process(patient))

    def patient_process(self, patient: Patient):
        """Patient lifecycle"""
        priority = 0 if patient.is_emergency else 1

        # STAGE 1: PREPARATION
        if self.config.emergency_probability > 0:
            prep_request = self.prep_rooms.request(priority=priority)
        else:
            prep_request = self.prep_rooms.request()

        yield prep_request

        patient.prep_start = self.env.now
        prep_duration = self.sample_time(
            self.config.prep_dist, self.config.prep_param1, self.config.prep_param2
        )
        yield self.env.timeout(prep_duration)
        patient.prep_end = self.env.now

        # STAGE 2: OPERATING ROOM
        if self.config.emergency_probability > 0:
            or_request = self.operating_rooms.request(priority=priority)
        else:
            or_request = self.operating_rooms.request()

        yield or_request
        self.prep_rooms.release(prep_request)

        patient.surgery_start = self.env.now
        surgery_duration = random.expovariate(1.0 / self.config.surgery_mean)
        yield self.env.timeout(surgery_duration)
        patient.surgery_end = self.env.now

        # STAGE 3: RECOVERY
        recovery_request = self.recovery_rooms.request()
        yield recovery_request

        self.operating_rooms.release(or_request)

        patient.recovery_start = self.env.now
        recovery_duration = self.sample_time(
            self.config.recovery_dist,
            self.config.recovery_param1,
            self.config.recovery_param2,
        )
        yield self.env.timeout(recovery_duration)
        patient.recovery_end = self.env.now

        self.recovery_rooms.release(recovery_request)

    def run(self):
        """Execute simulation"""
        random.seed(self.config.random_seed)
        self.env.process(self.patient_generator())
        self.env.run(until=self.config.sim_duration)

    def get_statistics(self) -> Dict:
        """Calculate statistics"""
        valid_patients = [
            p
            for p in self.patients
            if p.recovery_end > self.config.warmup_period and p.recovery_end > 0
        ]

        if not valid_patients:
            return {
                "num_patients": 0,
                "avg_queue_length": 0.0,
                "avg_throughput_time": 0.0,
            }

        avg_queue = (
            statistics.mean(self.queue_length_on_arrivals)
            if self.queue_length_on_arrivals
            else 0.0
        )
        throughput_times = [p.throughput_time() for p in valid_patients]
        avg_throughput = statistics.mean(throughput_times)

        return {
            "num_patients": len(valid_patients),
            "avg_queue_length": avg_queue,
            "max_queue_length": (
                max(self.queue_length_on_arrivals)
                if self.queue_length_on_arrivals
                else 0
            ),
            "avg_throughput_time": avg_throughput,
            "std_throughput_time": (
                statistics.stdev(throughput_times) if len(throughput_times) > 1 else 0.0
            ),
        }


def quick_test():
    """Quick test"""
    print("=== Testing Surgery Simulation ===\n")

    config = SimulationConfig(
        interarrival_dist=DistributionType.EXPONENTIAL,
        interarrival_param1=22.5,
        num_prep_rooms=4,
        num_recovery_rooms=4,
        prep_dist=DistributionType.UNIFORM,
        prep_param1=30.0,
        prep_param2=50.0,
        sim_duration=2000.0,
        warmup_period=500.0,
    )

    sim = SurgerySimulation(config)
    sim.run()
    stats = sim.get_statistics()

    print(f"Patients processed: {stats['num_patients']}")
    print(f"Average queue length: {stats['avg_queue_length']:.2f}")
    print(f"Max queue length: {stats['max_queue_length']}")
    print(f"Average throughput: {stats['avg_throughput_time']:.2f} min")


if __name__ == "__main__":
    quick_test()

import random
from enum import Enum

class FaultType(Enum):
    NONE = 0
    LOST_MESSAGE = 1
    SIGNAL_SPIKE = 2
    FAULT_CMD = 3

class FaultInjector:
    def __init__(self, fault_type=FaultType.NONE, probability=0.1):
        self.fault_type = fault_type
        self.probability = probability
        self.step_counter = 0
        self.fault_log = []

    def inject(self, current_cmd):
        self.step_counter += 1
        fault_triggered = False
        fault_desc = "正常"

        if self.fault_type == FaultType.NONE:
            return current_cmd, fault_triggered, fault_desc

        if random.random() >= self.probability:
            return current_cmd, fault_triggered, fault_desc

        fault_triggered = True

        if self.fault_type == FaultType.LOST_MESSAGE:
            fault_desc = f"CAN报文丢失 (步{self.step_counter})"
            self.fault_log.append(fault_desc)
            return None, fault_triggered, fault_desc

        if self.fault_type == FaultType.SIGNAL_SPIKE:
            spike_value = current_cmd * 10
            fault_desc = f"信号突变 {current_cmd}->{spike_value} (步{self.step_counter})"
            self.fault_log.append(fault_desc)
            return spike_value, fault_triggered, fault_desc

        if self.fault_type == FaultType.FAULT_CMD:
            fault_desc = f"错误诊断命令触发过流 (步{self.step_counter})"
            self.fault_log.append(fault_desc)
            return -999, fault_triggered, fault_desc

        return current_cmd, fault_triggered, fault_desc

    def get_fault_summary(self):
        return {
            'total_steps': self.step_counter,
            'fault_count': len(self.fault_log),
            'fault_details': self.fault_log
        }
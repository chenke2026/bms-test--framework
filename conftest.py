import pytest

class MockBattery:
    """模拟真实BMS（电池管理系统）的核心对象"""
    def __init__(self):
        self.voltage = 3.7          # 电压 (V)
        self.current = 0.0          # 电流 (A)，正为充电
        self.soc = 80.0             # 荷电状态 (%)
        self.temperature = 25.0     # 温度 (°C)
        self.is_safe = True         # 是否处于安全状态
        self.fault_injected = False # 是否被注入了故障

    def charge(self, voltage, current):
        """模拟充电过程中的状态更新"""
        self.voltage = voltage
        self.current = current
        
        # 简单模拟SOC上升
        if current > 0:
            self.soc += current * 0.1 
        if self.soc > 100: 
            self.soc = 100

        # 🛡️ 核心保护逻辑：过压或过温触发安全状态
        if self.voltage > 4.2 or self.temperature > 55:
            self.is_safe = False   # 进入安全状态（切断充电）
            self.current = 0
        else:
            self.is_safe = True

@pytest.fixture
def battery():
    """Pytest夹具：每个测试用例都会得到一个全新的电池对象"""
    return MockBattery()
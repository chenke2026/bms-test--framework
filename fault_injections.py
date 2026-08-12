import random

def inject_frame_loss(probability=0.3):
    """模拟CAN通讯丢帧：返回True表示丢包发生"""
    if random.random() < probability:
        return True
    return False

def inject_abnormal_voltage(battery, abnormal_value=5.0):
    battery.voltage = abnormal_value
    battery.fault_injected = True
    # 不再立即触发安全状态，交给下一轮的保护逻辑

def inject_diagnostic_error(battery):
    """模拟诊断仪发送非法数值（如负SOC）"""
    battery.soc = -10
    battery.fault_injected = True
    # 按照规范，非法值应触发安全默认值
    if battery.soc < 0:
        battery.soc = 0
        battery.is_safe = False  # 进入安全模式

def inject_abnormal_temp(battery, temp_value):
    """
    注入异常温度故障
    :param battery: 电池对象
    :param temp_value: 想要注入的目标温度（比如 80）
    """
    battery.temperature = temp_value
    battery.fault_injected = True
    # 注意：不直接触发安全状态，等下一轮保护逻辑去检测（这样响应时间才真实）
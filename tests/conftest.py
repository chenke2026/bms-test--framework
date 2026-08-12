# ============================================================================
# conftest.py - pytest 配置文件
# 作用：这个文件就像是"幕后工厂"，专门负责生产测试用的"虚拟电池"。
#        pytest 启动时会自动加载这个文件，不需要我们手动导入。
# ============================================================================

# 1. 导入必要的工具库
import pytest               # 导入pytest框架，才能使用 @pytest.fixture 等装饰器
import time                 # 导入时间库（虽然这里没用到，但保留用于扩展）
from dataclasses import dataclass  # 导入数据类装饰器，用来简单定义"数据容器"
from typing import Dict, Any      # 导入类型提示，告诉调用者传入的是什么类型的数据


# ============================================================================
# 2. 定义电池状态数据类（相当于一个"活页夹"，专门存放电池的各种参数）
# ============================================================================
@dataclass
class BatteryStatus:
    """
    这是一个"数据盒子"，用来存放电池当前的所有状态。
    你可以把它想象成一个仪表盘，显示电压、电流、温度、电量等信息。
    """
    voltage: float = 4.2        # 电池电压，默认4.2V（满电电压）
    current: float = 0.0        # 充电电流，默认0A（没充电）
    temperature: float = 25.0   # 电池温度，默认25°C（室温）
    ambient_temperature: float = 25.0  # ✅ 新增：环境温度（范围 -20°C ~ 50°C），默认25°C
    capacity: float = 50.0      # 电池剩余电量，默认50%（一半电）
    input_voltage: float = 5.0  # 外部充电器输入电压，默认5V（标准USB电压）
    fault_code: int = 0         # 故障代码，0表示"一切正常"，其他数字代表不同故障
    is_charging: bool = False   # 充电状态标志，True表示正在充电，False表示没充
    recharge_time: float = 0.0   # ✅ 加上这一行，默认充电时间为0小时



# ============================================================================
# 3. 核心：充电系统闭环控制类（这就是你的"Simulink电池模型"替代品）
# ============================================================================
class ChargingSystem:
    """
    这个类就是整个测试的"心脏"！它模拟了一个真实的电池管理系统（BMS）。
    测试用例（test_overcharge.py）就是通过调用这个类的方法，来施加电压/电流，
    并检查它的反应是否正常。
    """

    def __init__(self):
        """
        这是"构造函数"，每当测试用例要一个电池时，就会自动执行这里。
        作用：初始化一块全新的"虚拟电池"，并设置好故障词典和安全阈值。
        """
        # 创建一个电池状态对象（相当于给这块新电池配上一个仪表盘）
        self.battery = BatteryStatus()
        
        # 故障码翻译词典：把数字(1,2,3...)翻译成中文故障名
        # 这样测试报告里显示"过压保护"比显示"1"更直观
        self.fault_map = {
            1: "过压保护",   # 电压太高
            2: "欠压保护",   # 电压太低
            3: "过流保护",   # 电流太大
            4: "过温保护",   # 温度太高
            5: "低温保护",   # 温度太低
            6: "短路保护",   # 发生短路
            7: "反接保护" ,  # 电池正负极接反了
            8: "过充保护",   #充电时间过长  
            9: "环境温度过低", # 增加一条规则：如果环境温度低于 -10°C 或高于 45°C，触发 故障码 9（环境温度异常）。
            10:"环境温度过高"
             }
        
        # 安全阈值词典：设定各种"安全红线"，超过这些值就要触发保护
        self.safety_thresholds = {
            'max_voltage': 5.5,    # 输入电压最高不能超过 5.5V（超过即过压）
            'min_voltage': 3.0,    # 输入电压最低不能低于 3.0V（低于即欠压）
            'max_current': 2.5,    # 充电电流最大不能超过 2.5A（超过即过流）
            'max_temp': 60.0,      # 电池温度最高不能超过 60°C（超过即过温）
            'min_temp': 0.0,       # 电池温度最低不能低于 0°C（低于即低温）
            'short_current': 10.0 , # 短路电流阈值 10A（达到此值即判定为短路）
            'max_time':10,          #充电时间最高不能超过10小时（超过即过充)
            'max_ambient_temp': 45.0,    # ✅ 环境温度上限 50°C
            'min_ambient_temp': -10.0,   # ✅ 环境温度下限 -20°C
            }
    
          
        

    # ------------------------------------------------------------------------
    # 核心方法：施加激励（这是测试用例主要调用的"接口"）
    # ------------------------------------------------------------------------
    def apply_stimulus(self, stimulus: Dict[str, Any]) -> Dict[str, Any]:
        """
        这是整个脚本最核心的"闭环接口"！
        测试用例会调用这个方法，传入它想施加的电压/电流/温度等参数。
        
        参数 stimulus: 一个字典，例如 {'input_voltage': 6.5} 表示施加6.5V电压
        返回值: 一个字典，包含当前电池的所有状态（电压、电流、故障码等）
        """
        
        # ----- 第1步：根据传入的激励，更新电池的状态 -----
        # 如果传入了"输入电压"，就修改电池的输入电压
        if 'input_voltage' in stimulus:
            self.battery.input_voltage = stimulus['input_voltage']
        # 如果传入了"电流"，就修改电池的电流
        if 'current' in stimulus:
            self.battery.current = stimulus['current']
        # 如果传入了"温度"，就修改电池的温度
        if 'temperature' in stimulus:
            self.battery.temperature = stimulus['temperature']
        # 如果传入了"电量"，就修改电池的电量
        if 'capacity' in stimulus:
            self.battery.capacity = stimulus['capacity']
        # 如果传入了"反接标志"且为True，就把电池电压变为负数（模拟正负极接反）
        if 'reverse_polarity' in stimulus and stimulus['reverse_polarity']:
            self.battery.voltage = -abs(self.battery.voltage)
            #充电时间参数
        if  'recharge_time'in stimulus:
            self.battery.recharge_time = stimulus['recharge_time']
        # ✅ 新增：接收环境温度参数
        if  'ambient_temperature'in stimulus:
            self.battery.ambient_temperature = stimulus['ambient_temperature']
            


        # ----- 第2步：执行安全检查（调用内部的检测函数）-----
        # 根据当前的电压/电流/温度，判断有没有触发保护，返回故障码
        fault_code = self._safety_check()
        self.battery.fault_code = fault_code  # 把故障码记录到仪表盘上

        # ----- 第3步：根据故障码，决定是否允许充电 -----
        # 如果没有任何故障（fault_code == 0），并且电池没有反接，就允许充电
        if fault_code == 0 and not self._is_reverse_polarity():
            self.battery.is_charging = True   # 点亮"充电中"指示灯
            # 如果电量还没满（小于100%），就模拟充电过程
            if self.battery.capacity < 100:
                self.battery.current = 2.0    # 设置充电电流为2A
                self.battery.capacity += 0.5  # 电量缓慢增加（模拟充电）
        else:
            self.battery.is_charging = False
            if fault_code != 0:          # 只要故障码不是 0，电流归零
              self.battery.current = 0.0

        # ----- 第4步：特殊处理——如果电量达到了100%，强制停止充电（防过充）-----
        if self.battery.capacity >= 100:
            self.battery.is_charging = False
            self.battery.current = 0.0
            self.battery.capacity = 100.0  # 封顶100%，不能超过

        # ----- 第5步：把最终状态打包成字典，返回给测试用例 -----
        return self.get_status()

    # ------------------------------------------------------------------------
    # 内部私有方法：执行安全检查（带下划线_开头，表示是内部用的，不要直接调用）
    # ------------------------------------------------------------------------
    def _safety_check(self) -> int:
        """
        这个函数依次检查反接、过压、欠压、过流、过温、低温、短路。
        只要触发了其中一条，立刻返回对应的故障码。
        如果所有检查都通过，返回 0（表示正常）。
        """
        
        # 检查1：反接（电压为负数）
        if self._is_reverse_polarity():
            return 7  # 返回故障码7（反接保护）
            
        # 检查2：输入电压是否过高（超过5.5V）
        if self.battery.input_voltage > self.safety_thresholds['max_voltage']:
            return 1  # 返回故障码1（过压保护）
            
        # 检查3：输入电压是否过低（低于3.0V）
        if self.battery.input_voltage < self.safety_thresholds['min_voltage']:
            return 2  # 返回故障码2（欠压保护）

        # 检查4：是否短路（电流超过10A）
        if self.battery.current > self.safety_thresholds['short_current']:
            return 6  # 返回故障码6（短路保护）  
        # 检查5：充电电流是否过大（超过2.5A）
        if self.battery.current > self.safety_thresholds['max_current']:
            return 3  # 返回故障码3（过流保护）
            
        # 检查6：电池温度是否过高（超过60°C）
        if self.battery.temperature > self.safety_thresholds['max_temp']:
            return 4  # 返回故障码4（过温保护）
    
        # 检查7：电池温度是否过低（低于0°C）
        if self.battery.temperature < self.safety_thresholds['min_temp']:
            return 5  # 返回故障码5（低温保护）

         # 检查8：电池温度是否过充（高于10h）
        if self.battery.recharge_time > self.safety_thresholds['max_time']:  
            return 8  # 返回故障码8（过充保护）
        
         # 检查9：检查环境温度是否过低
        if self.battery.ambient_temperature < self.safety_thresholds['min_ambient_temp'] : 
           return 9 #环境温度过低保护
        if self.battery.ambient_temperature > self.safety_thresholds['max_ambient_temp'] :
           return 10 #环境温度过高保护
        # 所有检查都通过，返回0（一切正常）
        return 0

    # ------------------------------------------------------------------------
    # 内部私有方法：判断是否反接
    # ------------------------------------------------------------------------
    def _is_reverse_polarity(self) -> bool:
        """检查电池电压是否小于0，如果小于0说明正负极接反了"""
        return self.battery.voltage < 0

    # ------------------------------------------------------------------------
    # 公共方法：获取当前状态（把仪表盘上的数据全部打包成字典）
    # ------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """
        将电池的所有状态（电压、电流、温度、故障码、故障中文名等）打包成字典。
        这样测试用例就能清晰地读取当前系统状态了。
        """
        return {
            'voltage': self.battery.voltage,
            'current': self.battery.current,
            'temperature': self.battery.temperature,
            'capacity': self.battery.capacity,
            'input_voltage': self.battery.input_voltage,
            'fault_code': self.battery.fault_code,
            'recharge_time': self.battery.recharge_time,   # ✅ 必须加上这一行！
            'ambient_temperature':self.battery.ambient_temperature,
            # 根据故障码查词典，翻译成中文，如果没有对应码就显示"正常"
            'fault_msg': self.fault_map.get(self.battery.fault_code, '正常'),
            'is_charging': self.battery.is_charging
        }

    # ------------------------------------------------------------------------
    # 公共方法：人工清除故障（模拟维修人员修好了电池）
    # ------------------------------------------------------------------------
    def clear_faults(self):
        """清除所有故障，恢复正常充电状态，并把反接的电压正过来"""
        self.battery.fault_code = 0       # 故障码归零
        self.battery.is_charging = True   # 允许充电
        # 如果当前电压是负数（反接状态），把它乘以-1变成正数
        if self.battery.voltage < 0:
            self.battery.voltage = -self.battery.voltage


# ============================================================================
# 4. Pytest 夹具（Fixture）—— 相当于"自动售货机"
# ============================================================================
# 夹具的作用：测试用例（test_xxx函数）只要在参数里写上夹具的名字，
#            pytest就会自动调用这里的函数，把"虚拟电池"送到测试用例手里。

@pytest.fixture
def charging_system():
    """
    这是一个"基础夹具"。
    任何测试函数只要写上参数 charging_system，就会获得一个全新的 ChargingSystem 实例。
    相当于：每次测试都拿一块全新的、没动过的电池。
    """
    return ChargingSystem()  # 返回一块新电池


@pytest.fixture
def sample_system(charging_system):
    """
    这是一个"预置好状态的夹具"（继承自上面的基础夹具）。
    它先拿到一块新电池，然后提前设置好电压4.2V、电量50%、温度25°C、输入5V。
    这样测试用例就不用每次都重复设置这些初始条件了。
    """
    # 先拿到基础电池
    charging_system.battery.voltage = 4.2
    charging_system.battery.capacity = 50.0
    charging_system.battery.temperature = 25.0
    charging_system.battery.input_voltage = 5.0
    charging_system.battery.recharge_time = 0.0
    charging_system.battery.ambient_temperature  = 25.0                           #（环境温度）
    return charging_system  # 返回这块已经设置好的电池


# ============================================================================
# 5. Pytest 配置钩子（给测试用例打标签）
# ============================================================================
def pytest_configure(config):
    """
    这是一个pytest的"启动钩子"。
    作用：在pytest启动时，向系统中注册两个自定义标记（marker）。
    这样我们在 test_overcharge.py 中就可以用 @pytest.mark.smoke 来标记冒烟测试，
    用 @pytest.mark.regression 来标记回归测试。
    运行测试时，可以用 pytest -m smoke 只跑冒烟测试。
    """
    config.addinivalue_line("markers", "smoke: 冒烟测试标记")
    config.addinivalue_line("markers", "regression: 回归测试标记")
    # ============================================================================
# 6. 封装通用断言校验函数（核心进阶！
# ============================================================================
def check_charging_response(response, expected):
    """
    这是一个通用的响应校验器，用于验证充电系统的返回结果。
    使用 pytest.assume 进行软断言，一次报告所有失败。
    
    :param response: 系统返回的字典，如 {'is_charging': True, 'fault_code': 0, ...}
    :param expected: 期望值的字典，如 {'is_charging': False, 'fault_code': 5}
    """
    # 1. 校验充电状态
    pytest.assume(
        response['is_charging'] == expected['is_charging'],
        f"充电状态不符：期望 {expected['is_charging']}，实际 {response['is_charging']}"
    )
    
    # 2. 校验故障码
    pytest.assume(
        response['fault_code'] == expected['fault_code'],
        f"故障码不符：期望 {expected['fault_code']}，实际 {response['fault_code']}"
    )
    
    # 3. 如果有故障码，额外校验故障信息是否包含预期关键字
    if expected.get('fault_msg_keyword'):
        pytest.assume(
            expected['fault_msg_keyword'] in response['fault_msg'],
            f"故障信息不符：期望包含 '{expected['fault_msg_keyword']}'，实际为 '{response['fault_msg']}'"
        )
    
    # 4. 如果是正常充电场景，校验电流大于0
    if expected.get('check_current'):
        pytest.assume(
            response['current'] > 0,
            f"充电电流异常：期望 > 0，实际 {response['current']}"
        )
    
    # 5. 如果是充满场景，校验电量等于100%
    if expected.get('check_full_capacity'):
        pytest.assume(
            response['capacity'] == 100.0,
            f"电量未充满：期望 100.0%，实际 {response['capacity']}%"
        )
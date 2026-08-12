# ============================================================================
# test_overcharge.py - 充电保护系统的 "考场试卷"
# 作用：这个文件里写了 10 道考题（测试用例），每一道题都模拟一种真实场景
#       （比如过压、过流），然后检查虚拟电池的反应对不对。
# ============================================================================

# 1. 导入必要的工具
import pytest               # 导入 pytest 框架，这样才能使用 @pytest.mark 等装饰器
import time                 # 导入时间库（这里没用到，但保留备用）
from conftest import ChargingSystem  
# ↑ 注意：这行其实不是必须的（因为 pytest 会自动去 conftest.py 找 fixture）。
#   保留它只是为了让你在写代码时，IDE 能识别 ChargingSystem 类，方便查看定义。
from conftest import check_charging_response 
# <--- 【放这里】把你新加的那行 import 插在这一排

# ============================================================================
# 2. 定义一个测试类（把相关的测试用例打包在一起，方便管理）
# ============================================================================
class TestChargingSystem:
    """
    这个类就像一个"考试科目"，里面每个方法都是一道独立的考题。
    pytest 会自动找到这个类里面所有以 test_ 开头的方法，并逐一执行。
    """

    # ------------------------------------------------------------------------
    # TC-001：正常充电测试（冒烟测试 + 回归测试）
    # ------------------------------------------------------------------------
    @pytest.mark.smoke          # 标记为"冒烟测试"（最基本的核心功能，必须通过）
    @pytest.mark.regression     # 标记为"回归测试"（每次代码改动后都要跑）
    def test_normal_charging(self, sample_system):
        """
        【考题 TC-001】正常充电
        场景描述：就像你平时把手机插上充电器，电压正常（5V），没有故障。
        预期结果：充电指示灯亮（is_charging=True），电流 > 0，电量增加，故障码为0。
        """
        # 从夹具（fixture）中拿到一块"预置好的虚拟电池"
        # 这块电池初始是：电压4.2V，电量50%，温度25°C，输入电压5V
        system = sample_system
        initial_capacity = system.battery.capacity  # 记住充电前的电量，方便后面比较

        # ----- 第1步：施加激励（模拟插上充电器）-----
        # 调用 conftest.py 里的 apply_stimulus 方法，传入 5V 电压和 2A 电流
        response = system.apply_stimulus({
            'input_voltage': 5.0,
            'current': 2.0
        })

        # # ----- 第2步：断言（判卷）-----
        # # assert 是 Python 的断言关键字，条件为 False 时会抛异常，测试就算失败
        # assert response['is_charging'] == True, "系统应处于充电状态"
        # assert response['current'] > 0, "充电电流应大于0"
        # assert response['capacity'] > initial_capacity,
        # assert response['fault_code'] == 0, "无故障码"

        check_charging_response(response, {
                 'is_charging': True ,   # 期望：正在充电
                 'fault_code' :0 ,        # "无故障码" 
                 'check_current': True   # 期望：电流大于 0（自动执行 assert response['current'] > 0
        })
        #assert response['current'] > 0, "充电电流应大于0"
        assert response['capacity'] > initial_capacity , "电池电量应增加"
        # 如果所有断言都通过，打印一行成功信息（方便在终端查看）
        print(f"\n正常充电测试通过: 电量 {initial_capacity:.1f}% -> {response['capacity']:.1f}%")

    # ------------------------------------------------------------------------
    # TC-002：过压保护测试
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_overvoltage_protection(self, sample_system):
        """
        【考题 TC-002】过压保护
        场景描述：充电器坏了，输出了 6.5V 的高压（正常应该 5V）。
        预期结果：系统立刻停止充电，报出"过压保护"故障（故障码=1）。
        """
        system = sample_system

        # 施加 6.5V 过压激励（同时带着 2A 电流）
        response = system.apply_stimulus({
            'input_voltage': 6.5,   #"超过安全阈值 5.5V"
            'current': 2.0
        })
        time.sleep(0.1)   # 等待 100 毫秒，让系统完成关断动作

        # 断言：必须停止充电，必须报故障码1，故障信息里要有"过压"两个字
        assert response['is_charging'] == False, "过压时应停止充电"
        assert response['fault_code'] == 1, "故障码应为1(过压)"
        assert '过压' in response['fault_msg'], "故障信息应包含过压"
        assert response['current'] == 0, "充电电流应为0"

      
        print(f"\n过压保护测试通过: 故障码={response['fault_code']}, 信息={response['fault_msg']}")

    # ------------------------------------------------------------------------
    # TC-003：欠压保护测试
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_undervoltage_protection(self, sample_system):
        """
        【考题 TC-003】欠压保护
        场景描述：充电器输出只有 2.5V（太低了，带不动）。
        预期结果：停止充电，报"欠压保护"故障（故障码=2）。
        """
        system = sample_system

        response = system.apply_stimulus({
            'input_voltage': 2.5,  # 低于安全阈值 3.0V
            'current': 2.0
        })

        assert response['is_charging'] == False, "欠压时应停止充电"
        assert response['fault_code'] == 2, "故障码应为2(欠压)"
        assert '欠压' in response['fault_msg'], "故障信息应包含欠压"

        print(f"\n欠压保护测试通过: 故障码={response['fault_code']}")

    # ------------------------------------------------------------------------
    # TC-004：过流保护测试
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_overcurrent_protection(self, sample_system):
        """
        【考题 TC-004】过流保护
        场景描述：充电电流达到了 3.0A（正常最大 2.5A）。
        预期结果：停止充电，报"过流保护"故障（故障码=3）。
        """
        system = sample_system

        response = system.apply_stimulus({
            'input_voltage': 5.0,
            'current': 3.0  # 超过 2.5A 阈值
        })

        assert response['is_charging'] == False, "过流时应停止充电"
        assert response['fault_code'] == 3, "故障码应为3(过流)"
        assert '过流' in response['fault_msg'], "故障信息应包含过流"

        print(f"\n过流保护测试通过: 故障码={response['fault_code']}")

    # ------------------------------------------------------------------------
    # TC-005：过温保护测试
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_overtemperature_protection(self, sample_system):
        """
        【考题 TC-005】过温保护
        场景描述：电池温度飙升到 65°C（正常不超过 60°C）。
        预期结果：停止充电，报"过温保护"故障（故障码=4）。
        """
        system = sample_system

        response = system.apply_stimulus({
            'input_voltage': 5.0,
            'temperature': 65.0,  # 超过 60°C
            'current': 2.0
        })

        assert response['is_charging'] == False, "过温时应停止充电"
        assert response['fault_code'] == 4, "故障码应为4(过温)"
        assert '过温' in response['fault_msg'], "故障信息应包含过温"

        print(f"\n过温保护测试通过: 故障码={response['fault_code']}")

    # ------------------------------------------------------------------------
    # TC-006：低温保护测试
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_lowtemperature_protection(self, sample_system):
        """
        【考题 TC-006】低温保护
        场景描述：冬天电池太冷了，-5°C（正常不低于 0°C）。
        预期结果：停止充电，报"低温保护"故障（故障码=5）。
        """
        system = sample_system

        response = system.apply_stimulus({
            'input_voltage': 5.0,
            'temperature': -5.0,  # 低于 0°C
            'current': 2.0
        })

      # assert response['is_charging'] == False
      # assert response['fault_code'] == 5
      # assert '低温' in response['fault_msg']


        check_charging_response(response, {
         'is_charging': False,
    'fault_code': 5,
    'fault_msg_keyword': '低温'
})

        print(f"\n低温保护测试通过: 故障码={response['fault_code']}")

    # ------------------------------------------------------------------------
    # TC-007：充满截止测试（冒烟测试 + 回归测试）
    # ------------------------------------------------------------------------
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_full_capacity_cutoff(self, sample_system):
        """
        【考题 TC-007】充满自动截止
        场景描述：电池已经 100% 满了，但充电器还在插着。
        预期结果：系统自动停止充电，电流归零，电量不能超过 100%。
        """
        system = sample_system
        # 手动把电量设置为 100%（模拟已经充满的状态）
        system.battery.capacity = 100.0

        # 尝试继续充电（按理说应该充不进去了）
        response = system.apply_stimulus({
            'input_voltage': 5.0,
            'current': 2.0
        })

        # assert response['is_charging'] == False, "充满后应停止充电"
        # assert response['current'] == 0, "充电电流应为0"
        # assert response['capacity'] == 100.0, "电量不应超过100%"
        # assert response['fault_code'] == 0, "充满不是故障状态"  # 充满是正常现象，不是故障
        # 校验器：检查它能管的（状态、故障码、是否充满）
        check_charging_response(response, {
                 'is_charging': False,              # 期望停止充电
                 'fault_code': 0,                   # 期望无故障
                 'check_full_capacity': True        # 自动检查电量 == 100%
              })
# 普通 assert：额外检查电流是否为 0（校验器不支持精确等于 0）
        assert response['current'] == 0, "充满后电流应为0"
        print(f"\n充满截止测试通过: 电量={response['capacity']:.1f}%")

    # ------------------------------------------------------------------------
    # TC-008：短路保护测试
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_short_circuit_protection(self, sample_system):
        """
        【考题 TC-008】短路保护
        场景描述：输出端短路，电流瞬间飙升到 15A。
        预期结果：立刻切断输出，报"短路保护"故障（故障码=6）。
        """
        system = sample_system

        # 施加 15A 大电流（模拟短路）
        response = system.apply_stimulus({
            'input_voltage': 5.0,
            'current': 25.0  # 超过短路阈值 10A
        })

        assert response['is_charging'] == False, "短路时应断开输出"
        assert response['fault_code'] == 6, "故障码应为6(短路)"
        assert '短路' in response['fault_msg'], "故障信息应包含短路"
        assert response['current'] == 0, "短路后电流应为0"

        print(f"\n短路保护测试通过: 故障码={response['fault_code']}")

    # ------------------------------------------------------------------------
    # TC-009：反接保护测试
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_reverse_polarity_protection(self, sample_system):
        """
        【考题 TC-009】反接保护
        场景描述：电池正负极插反了（电压变成 -4.2V）。
        预期结果：不充电，报"反接保护"故障（故障码=7）。
        """
        system = sample_system

        # 手动把电池电压设为负数（模拟反接）
        system.battery.voltage = -4.2
        response = system.apply_stimulus({
            'input_voltage': 5.0,
            'reverse_polarity': True  # 给系统一个反接标志
        })

        assert response['is_charging'] == False, "反接时应不充电"
        assert response['fault_code'] == 7, "故障码应为7(反接)"
        assert '反接' in response['fault_msg'], "故障信息应包含反接"

        print(f"\n反接保护测试通过: 故障码={response['fault_code']}")

    # ------------------------------------------------------------------------
    # TC-010：故障恢复测试
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_fault_recovery(self, sample_system):
        """
        【考题 TC-010】故障恢复
        场景描述：之前发生了过压故障，现在维修人员把故障清除了，电压也正常了。
        预期结果：系统能自动恢复充电。
        """
        system = sample_system

        # 第1步：先故意触发一个过压故障（让系统进入故障状态）
        system.apply_stimulus({'input_voltage': 6.5})
        assert system.battery.fault_code == 1, "触发过压故障"  # 确认故障确实发生了

        # 第2步：模拟维修人员操作——清除故障，并恢复正常的电压和温度
        system.clear_faults()            # 调用 conftest.py 里的清故障方法
        system.battery.input_voltage = 5.0
        system.battery.temperature = 25.0

        # 第3步：再次尝试正常充电
        response = system.apply_stimulus({
            'input_voltage': 5.0,
            'current': 2.0
        })
     # 断言：故障清除了，应该能恢复充电
        assert response['fault_code'] == 0, "故障码应清除"
        assert response['is_charging'] == True, "应恢复充电状态"
        assert response['current'] > 0, "应有充电电流"

        print(f"\n故障恢复测试通过: 故障清除，恢复充电")
   
       # ------------------------------------------------------------------------
    # TC-011：充电时间测试（过充保护）
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    def test_recharge_time(self, sample_system):
        """
        【考题 TC-011】过充保护测试
        场景描述：连续充电超过 10 小时。
        预期结果：停止充电，报"过充保护"故障（故障码=8）。
        """
        system = sample_system

        # 第1步：施加激励（模拟连续充电 11 小时，超过 10 小时阈值）
        response = system.apply_stimulus({
            'recharge_time': 11   # 超过充电时间阈值 10 小时
        })

        # 第2步：断言验证（检查系统是否正确响应）
        assert response['is_charging'] == False, "过充时应停止充电"
        assert response['fault_code'] == 8, "故障码应为 8（过充保护）"
        assert '过充' in response['fault_msg'], "故障信息应包含'过充'"

        print(f"\n过充保护测试通过: 故障码={response['fault_code']}")
        # ------------------------------------------------------------------------
    # TC-012：环境温度测试（高温 / 低温）
    # ------------------------------------------------------------------------
    @pytest.mark.regression
    @pytest.mark.parametrize("ambient_temp, expected_fault_code, expected_keyword", [
        (-20, 9, "环境温度过低"),   # 低温场景：-20°C 触发故障码 9
        (55, 10, "环境温度过高"),   # 高温场景：55°C 触发故障码 10
    ])
    def test_ambient_temperature(self, sample_system, ambient_temp, expected_fault_code, expected_keyword):
        """
        【考题 TC-012】环境温度测试
        场景描述：环境温度超出 -10°C ~ 45°C 范围时，系统应停止充电并报故障。
        预期结果：
          - 温度 < -10°C → 故障码 9（环境温度过低）
          - 温度 > 45°C → 故障码 10（环境温度过高）
        """
        system = sample_system

        # 施加激励：设置环境温度
        response = system.apply_stimulus({
            'ambient_temperature': ambient_temp
        })

        # 断言验证
        assert response['is_charging'] == False, f"环境温度 {ambient_temp}°C 时应停止充电"
        assert response['fault_code'] == expected_fault_code, \
            f"环境温度 {ambient_temp}°C 时应触发故障码 {expected_fault_code}，实际 {response['fault_code']}"
        assert expected_keyword in response['fault_msg'], \
            f"故障信息应包含 '{expected_keyword}'，实际为 '{response['fault_msg']}'"

        print(f"\n环境温度测试通过: {ambient_temp}°C -> 故障码={response['fault_code']}, 信息={response['fault_msg']}")
    

# ============================================================================
# 3. 额外加分题：参数化测试（一条测试顶多条）
# ============================================================================
# 这个测试不在上面的类里面，但它依然会被 pytest 自动发现并执行。
# 它的特点是使用 @pytest.mark.parametrize，可以一次性测试多组数据。

@pytest.mark.regression
@pytest.mark.parametrize("input_voltage, expected_fault", [
    (3.5, 0),    # 测试组1：输入 3.5V，预期正常（故障码0）
    (4.5, 0),    # 测试组2：输入 4.5V，预期正常（故障码0）
    (5.8, 1),    # 测试组3：输入 5.8V，预期过压（故障码1）
    (2.8, 2),    # 测试组4：输入 2.8V，预期欠压（故障码2）
])
def test_voltage_thresholds(charging_system, input_voltage, expected_fault):
    """
    电压阈值批量测试
    这个函数会被 pytest 自动执行 4 次，每次带入不同的电压值和预期故障码。
    相当于用一条代码，覆盖了 4 种边界情况，非常高效！
    """
    # 施加激励（注意：这里用的是 charging_system，不是 sample_system，
    # 意味着每次都是全新的电池，互不干扰）
    response = charging_system.apply_stimulus({
        'input_voltage': input_voltage,
        'current': 2.0
    })

    # 断言：实际故障码必须等于预期故障码
    assert response['fault_code'] == expected_fault, \
        f"输入电压{input_voltage}V时，预期故障码{expected_fault}，实际{response['fault_code']}"

    # 辅助判断：如果没有故障（预期故障码=0），应该正在充电；否则应该停止充电
    if expected_fault == 0:
        assert response['is_charging'] == True, "电压正常时应充电"
    else:
        assert response['is_charging'] == False, "电压异常时应停止充电"

    # 打印当前测试的参数和结果
    print(f"电压阈值测试: {input_voltage}V -> 故障码={response['fault_code']}")


# ============================================================================
# 4. 主入口（让这个脚本也可以直接运行，而不是必须用 pytest 命令）
# ============================================================================
if __name__ == "__main__":
    """
    当你在终端直接执行 python test_overcharge.py 时，会进入这里。
    它会调用 pytest.main() 来运行当前文件的所有测试，并生成 HTML 报告。
    相当于一个"一键运行"的快捷方式。
    """
    pytest.main(["-v", "--html=test_report.html", "--self-contained-html", __file__])
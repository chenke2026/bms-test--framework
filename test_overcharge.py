import pytest
import csv
import time
from pathlib import Path
from fault_injections import inject_abnormal_voltage
from fault_injections import inject_abnormal_voltage, inject_abnormal_temp

def test_overcharge_with_fault_injection(battery, request):
    test_name = request.node.name
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"{test_name}.csv"

    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Test_Case", "Voltage", "Current",
                         "SOC", "Temp", "Is_Safe", "Fault_Flag"])

        for step in range(10):
            timestamp = time.time()

            # 1. 保护逻辑（基于当前电压）
            if battery. temperature > 55 :
                battery.is_safe = False
                battery.current = 0

            # 2. 注入故障（在第5步结束前修改电压）
            if step == 5:
                print(f"⚡ [注入故障] 在第 {step} 步注入 80℃ 异常温度...")
                inject_abnormal_temp(battery, 80) 

            # 3. 写入当前帧数据
            writer.writerow([
                timestamp,
                test_name,
                round(battery.voltage, 2),
                battery.current,
                round(battery.soc, 2),
                battery.temperature,
                battery.is_safe,
                battery.fault_injected
            ])

            time.sleep(0.1)

        # 断言：最终必须进入安全状态
        assert battery.is_safe == False, "❌ 故障注入后未进入安全状态！"
        print(f"✅ 测试通过，日志已保存至: {log_file}")
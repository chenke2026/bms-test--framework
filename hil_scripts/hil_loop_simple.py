import matlab.engine
import time
import pandas as pd
from datetime import datetime

model_path = r'D:\BMS_Study'
model_name = 'Battery_1RC_50Ah'
total_time = 12
dt = 0.01

print("正在连接 MATLAB...")
eng = matlab.engine.start_matlab()
eng.cd(model_path, nargout=0)
eng.load_system(model_name, nargout=0)
eng.set_param(model_name, 'Solver', 'ode1', nargout=0)
eng.set_param(model_name, 'FixedStep', str(dt), nargout=0)
print("✅ MATLAB 已连接，模型已加载。")

eng.set_param(model_name, 'SimulationCommand', 'stop', nargout=0)
eng.set_param(model_name, 'SimulationCommand', 'start', nargout=0)
eng.eval("clear", nargout=0)

print(f"🚀 开始仿真，总时长 {total_time}s，步长 {dt}s")
log = []
sim_time = 0.0

for step in range(int(total_time / dt)):
    start_t = sim_time
    stop_t = sim_time + dt
    eng.set_param(model_name, 'StartTime', str(start_t), nargout=0)
    eng.set_param(model_name, 'StopTime', str(stop_t), nargout=0)
    
    try:
        eng.eval(f"out = sim('{model_name}');", nargout=0)
        voltage = float(eng.eval("out.simout_voltage(end)", nargout=1))
        soc = float(eng.eval("out.simout_soc(end)", nargout=1))
    except Exception as e:
        print(f"⚠️ 读取数据异常: {e}")
        voltage = 0.0
        soc = 0.0

    log.append({'Time': sim_time + dt, 'Voltage': voltage, 'SOC': soc})
    sim_time = stop_t

    if (step + 1) % 100 == 0:
        print(f"  进度: {sim_time:.1f}s, 电压: {voltage:.2f}V, SOC: {soc:.2f}%")

print("✅ 仿真完成，正在保存数据...")
df = pd.DataFrame(log)
csv_name = f"hil_log_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(csv_name, index=False)
print(f"📁 日志已保存至 {csv_name}")

eng.close_system(model_name, nargout=0)
eng.quit()
print("🔌 MATLAB 引擎已关闭。")

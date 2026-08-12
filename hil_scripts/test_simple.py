import matlab.engine
import time
import pandas as pd
from datetime import datetime
import random
import os

MODEL_PATH = r'D:\BMS_Study'
MODEL_NAME = 'Battery_1RC_50Ah'
TOTAL_TIME = 30

print("正在连接 MATLAB...")
eng = matlab.engine.start_matlab()
eng.cd(MODEL_PATH, nargout=0)
eng.load_system(MODEL_NAME, nargout=0)
eng.set_param(MODEL_NAME, 'Solver', 'ode1', nargout=0)
eng.set_param(MODEL_NAME, 'FixedStep', '0.01', nargout=0)
print("✅ MATLAB 已连接。")

eng.set_param(MODEL_NAME, 'SimulationCommand', 'stop', nargout=0)
eng.set_param(MODEL_NAME, 'SimulationCommand', 'start', nargout=0)

print(f"🚀 开始一次性仿真，时长 {TOTAL_TIME}s...")
start = time.time()

eng.eval(f"out = sim('{MODEL_NAME}', 'StopTime', '{TOTAL_TIME}');", nargout=0)

print(f"✅ 仿真完成，耗时 {time.time()-start:.2f}s")

# --- 保存 CSV 到绝对路径 ---
csv_name = f"simulation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
csv_full_path = os.path.join(MODEL_PATH, csv_name)  # 绝对路径
eng.eval("T = table(out.tout, out.simout_voltage, out.simout_soc, 'VariableNames', {'Time','Voltage','SOC'});", nargout=0)
eng.eval(f"writetable(T, '{csv_full_path}');", nargout=0)
print(f"✅ CSV 已保存: {csv_full_path}")

eng.quit()
print("🔌 MATLAB 引擎已关闭。")

# --- 后处理：模拟故障注入 ---
print("\n📊 在后处理中模拟故障注入...")
df = pd.read_csv(csv_full_path)  # 使用绝对路径读取

fault_indices = random.sample(range(int(0.2*len(df)), int(0.9*len(df))), k=random.randint(3, 6))
df['Fault_Triggered'] = False
df['Fault_Desc'] = ''

for idx in fault_indices:
    df.loc[idx, 'Voltage'] = df.loc[idx, 'Voltage'] * 1.1
    df.loc[idx, 'Fault_Triggered'] = True
    df.loc[idx, 'Fault_Desc'] = f"信号突变 (时间 {df.loc[idx, 'Time']:.2f}s)"

fault_csv = csv_full_path.replace('.csv', '_with_faults.csv')
df.to_csv(fault_csv, index=False)
print(f"✅ 带故障标记的 CSV 已保存: {fault_csv}")

# --- 调用分析模块 ---
print("\n📊 开始分析...")
from fault_analyzer import FaultAnalyzer
analyzer = FaultAnalyzer(fault_csv)
analyzer.run_analysis()
import matlab.engine
import time
import pandas as pd
from datetime import datetime

# --- 配置区域 ---
model_path = r'D:\BMS_Study'
model_name = 'Battery_1RC_50Ah'
# --- 配置结束 ---

print("正在连接 MATLAB 引擎...")
eng = matlab.engine.start_matlab()
print("MATLAB 引擎已启动。")

eng.cd(model_path, nargout=0)

print(f"正在加载模型: {model_name}...")
eng.load_system(model_name, nargout=0)
print("模型加载完成。")

# 设置仿真参数
eng.set_param(model_name, 'StopTime', '3600', nargout=0)
eng.set_param(model_name, 'Solver', 'ode1', nargout=0)
eng.set_param(model_name, 'FixedStep', '0.01', nargout=0)

print("开始仿真...")
start_time = time.time()

eng.eval("out = sim('Battery_1RC_50Ah')", nargout=0)

elapsed = time.time() - start_time
print(f"仿真完成，耗时 {elapsed:.2f} 秒。")

time.sleep(1)

# --- 直接读取 out 中的字段 ---
try:
    # 直接获取数据
    voltage_data = eng.eval("out.simout_voltage", nargout=1)
    soc_data = eng.eval("out.simout_soc", nargout=1)
    time_data = eng.eval("out.tout", nargout=1)

    # 数据转换（列向量展平）
    voltage_flat = [v[0] for v in voltage_data]
    soc_flat = [s[0] for s in soc_data]
    time_flat = [t[0] for t in time_data]

    # 创建 DataFrame
    df = pd.DataFrame({
        'Time (s)': time_flat,
        'Voltage (V)': voltage_flat,
        'SOC (%)': soc_flat
    })

    csv_filename = f"simulation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"✅ 仿真数据已保存至: {csv_filename}")
    print(f"   数据点数量: {len(df)}")

except Exception as e:
    print(f"❌ 提取数据时出错: {e}")
    # 打印 out 的字段名，便于调试
    eng.eval("disp(fieldnames(out))", nargout=0)

# 关闭
eng.close_system(model_name, nargout=0)
eng.quit()
print("MATLAB 引擎已关闭。")
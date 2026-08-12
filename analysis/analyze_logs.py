import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def run_analysis():
    log_dir = Path("logs")
    if not log_dir.exists():
        print("❌ 没有找到 logs 文件夹，请先运行 pytest 生成日志。")
        return

    all_files = log_dir.glob("*.csv")
    df_list = []
    for f in all_files:
        df = pd.read_csv(f)
        df_list.append(df)
    
    if not df_list:
        print("❌ logs 文件夹下没有CSV文件。")
        return
    
    df_all = pd.concat(df_list, ignore_index=True)
    df_all['Timestamp'] = pd.to_datetime(df_all['Timestamp'], unit='s')
    
    print(f"📊 共加载 {len(df_all)} 条记录")

    plt.figure(figsize=(12, 8))
    
    # 上图：SOC 曲线（不变）
    plt.subplot(2, 1, 1)
    plt.plot(df_all['Timestamp'], df_all['SOC'], label='SOC', color='blue', marker='.')
    plt.title('Battery SOC Trend')
    plt.ylabel('SOC (%)')
    plt.grid(True)
    
    # 下图：🔥 改成画 温度（Temp）曲线
    plt.subplot(2, 1, 2)
    plt.plot(df_all['Timestamp'], df_all['Temp'], label='Temperature', color='orange', marker='.')
    
    # 标出超温点（超过 55℃）
    over_temp = df_all[df_all['Temp'] > 55]
    if not over_temp.empty:
        plt.scatter(over_temp['Timestamp'], over_temp['Temp'], 
                    color='red', s=150, marker='o', label='⚠️ Over Temp Fault')
    
    plt.axhline(y=55, color='r', linestyle='--', label='Safety Threshold 55℃')
    plt.title('Temperature with Anomalies Marked')
    plt.ylabel('Temperature (℃)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('analysis_report.png')
    print("📊 图表已保存为 analysis_report.png")

    # 计算响应时间（逻辑不变，依然是找故障标记到安全状态的时间差）
    fault_rows = df_all[df_all['Fault_Flag'] == True]
    safe_rows = df_all[df_all['Is_Safe'] == False]
    
    if not fault_rows.empty and not safe_rows.empty:
        first_fault_time = fault_rows.iloc[0]['Timestamp']
        first_safe_time = safe_rows.iloc[0]['Timestamp']
        response_time = (first_safe_time - first_fault_time).total_seconds()
        print(f"⏱️ 系统保护响应时间: {response_time:.3f} 秒")
    else:
        print("⏱️ 未能计算出响应时间（缺少故障或安全状态数据）")

    # 3-Sigma 统计也改成针对温度
    mean_temp = df_all['Temp'].mean()
    std_temp = df_all['Temp'].std()
    upper = mean_temp + 3 * std_temp
    lower = mean_temp - 3 * std_temp
    outliers = df_all[(df_all['Temp'] > upper) | (df_all['Temp'] < lower)]
    print(f"📐 温度均值: {mean_temp:.2f}℃, 标准差: {std_temp:.2f}℃")
    print(f"🔍 基于3-Sigma原则检出 {len(outliers)} 个温度异常点")

if __name__ == "__main__":
    run_analysis()
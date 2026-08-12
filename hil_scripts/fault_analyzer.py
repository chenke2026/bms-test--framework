import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class FaultAnalyzer:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.df.columns = self.df.columns.str.strip()

    def detect_anomalies_3sigma(self, column='Voltage'):
        mean = self.df[column].mean()
        std = self.df[column].std()
        lower = mean - 3 * std
        upper = mean + 3 * std
        anomalies = self.df[(self.df[column] < lower) | (self.df[column] > upper)]
        return anomalies, lower, upper

    def compute_response_time(self, target_soc=50.0):
        df_valid = self.df[self.df['SOC'] <= 100]
        if len(df_valid) == 0:
            return None
        start_time = df_valid.iloc[0]['Time']
        closest_idx = (df_valid['SOC'] - target_soc).abs().idxmin()
        end_time = df_valid.loc[closest_idx, 'Time']
        return end_time - start_time

    def plot_soc_curve(self, save_path='fault_analysis_report.png'):
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))

        axes[0].plot(self.df['Time'], self.df['SOC'], color='blue', linewidth=1.5)
        axes[0].set_ylabel('SOC (%)')
        axes[0].set_title('SOC 变化曲线')
        axes[0].grid(True, linestyle='--', alpha=0.6)

        axes[1].plot(self.df['Time'], self.df['Voltage'], color='red', linewidth=1.5)
        axes[1].set_ylabel('Voltage (V)')
        axes[1].set_xlabel('Time (s)')
        axes[1].set_title('端电压曲线')
        axes[1].grid(True, linestyle='--', alpha=0.6)

        anomalies, _, _ = self.detect_anomalies_3sigma('Voltage')
        if not anomalies.empty:
            axes[1].scatter(anomalies['Time'], anomalies['Voltage'],
                           color='orange', s=60, label='3-sigma 异常点')
            axes[1].legend()

        if 'Fault_Desc' in self.df.columns:
            fault_points = self.df[self.df['Fault_Triggered'] == True]
            if not fault_points.empty:
                axes[1].scatter(fault_points['Time'], fault_points['Voltage'],
                               color='red', s=80, marker='x', label='故障注入点')
                axes[1].legend()

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        print(f"✅ 图表已保存: {save_path}")
        plt.show()

    def run_analysis(self):
        print("\n" + "="*60)
        print("📊 故障日志分析报告")
        print("="*60)

        print(f"  数据点数量: {len(self.df)}")
        print(f"  电压范围: {self.df['Voltage'].min():.2f} ~ {self.df['Voltage'].max():.2f} V")
        print(f"  SOC 范围: {self.df['SOC'].min():.2f} ~ {self.df['SOC'].max():.2f} %")

        rt = self.compute_response_time(50.0)
        if rt:
            print(f"  响应时间 (SOC 100%→50%): {rt:.2f} 秒")

        anomalies, lower, upper = self.detect_anomalies_3sigma('Voltage')
        print(f"  3-sigma 异常点: {len(anomalies)} 个")
        if len(anomalies) > 0:
            print("  异常点详情 (前5个):")
            print(anomalies[['Time', 'Voltage', 'SOC']].head(5))

        if 'Fault_Triggered' in self.df.columns:
            fault_count = self.df['Fault_Triggered'].sum()
            print(f"  故障注入次数: {fault_count} 次")
            if fault_count > 0:
                print("  故障详情:")
                for desc in self.df[self.df['Fault_Triggered']]['Fault_Desc'].unique():
                    print(f"    - {desc}")

        print("="*60)
        self.plot_soc_curve()
        print("✅ 分析完成")
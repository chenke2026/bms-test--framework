import pandas as pd
from datetime import datetime

class DataCollector:
    def __init__(self, test_case_name="Default", fault_type="NONE"):
        self.test_case = test_case_name
        self.fault_type = fault_type
        self.start_time = datetime.now()
        self.log_data = []
        self.metadata = {
            'test_case': test_case_name,
            'fault_type': fault_type,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'solver': 'ode1',
            'step_size': '0.01'
        }

    def record(self, sim_time, current_cmd, voltage, soc, fault_triggered=False, fault_desc=""):
        self.log_data.append({
            'Time': sim_time,
            'Current_Cmd': current_cmd,
            'Voltage': voltage,
            'SOC': soc,
            'Fault_Triggered': fault_triggered,
            'Fault_Desc': fault_desc
        })

    def save(self):
        df = pd.DataFrame(self.log_data)
        timestamp = self.start_time.strftime('%Y%m%d_%H%M%S')
        filename = f"hil_log_{self.test_case}_{timestamp}.csv"
        df.to_csv(filename, index=False)

        meta_filename = filename.replace('.csv', '.meta')
        with open(meta_filename, 'w') as f:
            for k, v in self.metadata.items():
                f.write(f"{k}: {v}\n")
            f.write(f"data_points: {len(self.log_data)}\n")

        print(f"✅ 数据已保存: {filename}")
        print(f"✅ 元数据已保存: {meta_filename}")
        return filename
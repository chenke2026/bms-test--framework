&#x20;BMS 电池管理系统自动化测试框架



项目简介

本项目是一个基于 Pytest 的电池管理系统（BMS）自动化测试框架，通过软件模拟电池行为并注入故障（过温），验证 BMS 保护逻辑的响应时间。



技术栈

\-语言：Python 3.11+

\- 测试框架：Pytest

\- 数据分析：Pandas, Matplotlib

\- 环境管理：venv



&#x20;快速开始

bash

&#x20;1. 安装依赖

pip install -r requirements.txt



2\. 运行测试（注入80℃故障）

pytest -s



&#x20;3. 生成分析报告图表

python analysis/analyze\_logs.py

测试报告示例

https://analysis\_report.png



项目亮点

故障注入与响应时间量化：模拟真实检测延迟，精确计算出 0.1 秒级的保护响应时间。



数据驱动分析：测试自动生成结构化日志（CSV），利用 Pandas 和 Matplotlib 进行可视化分析。



模块化设计：模拟器、故障注入、测试用例和分析脚本分离，易于扩展新的测试场景。



项目结构

text

.

├── conftest.py              # Pytest 配置与电池模拟器

├── fault\_injections.py      # 故障注入函数库

├── test\_overcharge.py       # 核心测试用例

├── analysis/

│   └── analyze\_logs.py      # 日志分析与图表生成

├── logs/                    # 运行生成的 CSV 日志

├── requirements.txt         # 项目依赖

└── README.md                # 项目说明

&#x20;仓库地址

https://github.com/chenke2026/bms-test--framework


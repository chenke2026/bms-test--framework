BMS 电池管理系统自动化测试框架





项目简介



本项目是一个面向新能源汽车 BMS 电池管理系统的自动化测试验证平台，覆盖从模型到测试的全链路



\- Simulink 建模：基于一阶 RC 等效电路搭建电池模型，包含开路电压与 SOC 曲线、内阻、极化电容，输入电流，输出端电压和 SOC

\- Python 联合仿真：通过 MATLAB Engine API 实现 Python 与 Simulink 的实时数据交换

\- CAN 协议通讯：基于 DBC 文件定义报文，使用 python-can 和 cantools 实现虚拟总线通讯

\- 自动化测试：基于 Pytest 编写 18 条核心测试用例，自动生成 HTML 报告

\- 故障注入与分析：支持随机丢帧、异常值注入，并利用 Pandas 和 Matplotlib 进行日志分析与可视化





技术栈



建模与仿真      MATLAB R2023b / Simulink

联合仿真接口    MATLAB Engine API for Python

通讯协议        CAN（DBC 解析 + python-can + cantools）

测试框架        Pytest + pytest-html

数据分析        Pandas, Matplotlib

版本控制        Git / GitHub





项目结构



bms\_project\_v2/

├── README.md                      项目说明文档

├── requirements.txt               Python 依赖清单

├── pytest.ini                     Pytest 配置文件

├── .gitignore                     Git 忽略规则

│

├── models/                        Simulink 模型

│   └── Battery\_1RC\_50Ah.slx       一阶 RC 电池模型

│

├── hil\_scripts/                   HIL 仿真脚本

│   ├── hil\_loop\_simple.py         闭环仿真主脚本

│   ├── run\_fault\_test.py          故障注入测试

│   ├── fault\_injector.py          故障注入函数库

│   ├── hil\_interface.py           CAN 接口封装

│   ├── battery\_can.dbc            DBC 报文定义

│   └── fault\_analyzer.py          故障分析脚本

│

├── can/                           CAN 通讯模块

│   └── bms.dbc                    DBC 报文定义

│

├── tests/                         所有测试用例

│   ├── conftest.py                充电系统测试夹具

│   ├── test\_overcharge.py         模拟版过温故障注入测试

│   └── test\_charging\_system.py    充电系统 17 条功能测试

│

├── analysis/                      日志分析与可视化

│   ├── analyze\_logs.py            分析脚本

│   └── analysis\_report.png        生成的图表

│

├── logs/                          运行生成的 CSV 日志

├── test\_report.html               Pytest HTML 测试报告

├── test\_overcharge.py             模拟版测试入口

├── fault\_injections.py            故障注入函数库

├── conftest.py                    Pytest 夹具配置

├── analysis\_report.png            分析图表

└── bms\_venv\_win/                  Python 虚拟环境





快速开始



1\. 克隆项目



git clone https://github.com/chenke2026/bms-test--framework.git

cd bms-test--framework



2\. 创建并激活虚拟环境



python -m venv bms\_venv\_win



Windows:

bms\_venv\_win\\Scripts\\activate



Linux / Mac:

source bms\_venv\_win/bin/activate



3\. 安装依赖



pip install -r requirements.txt



4\. 运行所有测试（18 条用例）



pytest tests/ -s --html=test\_report.html --self-contained-html



5\. 生成分析报告图表



python analysis/analyze\_logs.py



6\. 查看 HTML 测试报告



双击打开 test\_report.html





测试用例列表



一、模拟版测试（1 条）



用例名称：test\_overcharge.py

说明：注入 80℃ 过温故障，验证系统保护响应时间

状态：通过



二、充电系统功能测试（17 条）



从 pytest\_demo 整合过来的完整测试套件



分类            测试项                          数量

电压保护        过压/欠压/电压阈值参数化         4

电流保护        过流保护                        1

温度保护        过温/低温/环境温度边界           3

充放电逻辑      充满断电/重新充电时间            2

故障处理        短路/反接/故障恢复               3

参数化测试      电压阈值边界测试                 4

总计                                           17



运行方式：



pytest tests/test\_charging\_system.py -s





测试报告示例



HTML 测试报告



运行 pytest tests/ -s --html=test\_report.html 后生成，包含所有用例的执行结果、耗时和错误信息



分析图表



运行 python analysis/analyze\_logs.py 后生成



图片：analysis\_report.png



上图展示

\- SOC 变化曲线（蓝色）

\- 温度变化曲线（橙色）

\- 异常点标注（红色圆圈，80℃ 过温故障点）

\- 安全阈值线（红色虚线，55℃）



HIL 故障分析报告



运行 python hil\_scripts/run\_fault\_test.py 后生成



指标                    数值

数据点数量              3001

电压范围                346.68 \~ 402.28 V

SOC 范围                99.99 \~ 100.00 %

响应时间                30.00 秒

3-sigma 异常点          4 个

故障注入次数            5 次





项目亮点



\- Simulink 电池模型：搭建了包含 OCV-SOC 曲线、内阻和极化效应的一阶 RC 等效电路模型，求解器采用固定步长，为实时仿真奠定基础



\- CAN 通讯闭环：通过 DBC 文件定义了电流指令和电压状态两条报文，实现了 Python 到 Simulink 的虚拟 CAN 数据交互，完全模拟 HIL 设备的数据流



\- 18 条自动化测试用例：覆盖过充保护、过放欠压保护、过温保护、短路保护等核心功能，每条用例均包含前置条件、测试步骤和断言验证



\- 故障注入与响应时间量化：支持随机丢帧、异常信号注入，并能精确计算出从故障发生到保护动作的响应时间



\- 数据驱动分析：测试自动生成结构化 CSV 日志，利用 Pandas 和 Matplotlib 进行可视化分析，异常点用红圈标注



\- 模块化设计：模拟器、故障注入、测试用例和分析脚本完全分离，便于扩展新的测试场景





环境要求



\- Python 3.11+

\- MATLAB R2023b（可选，用于 Simulink 联合仿真）

\- 虚拟环境（venv）





依赖清单



pytest >= 7.0.0

pytest-html >= 3.0.0

pandas >= 1.5.0

matplotlib >= 3.5.0

python-can >= 4.0.0（可选）

cantools >= 39.0.0（可选）





仓库地址



https://github.com/chenke2026/bms-test--framework




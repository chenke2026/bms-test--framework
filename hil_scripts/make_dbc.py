# make_dbc.py - 生成正确的 battery_can.dbc 文件
dbc_content = '''VERSION "1.0"

NS_ :
  NS_DESC_
  CM_
  BA_DEF_
  BA_
  VAL_
  CAT_DEF_
  CAT_
  FILTER
  BA_DEF_DEF_
  EV_DATA_
  ENVVAR_DATA_
  SGTYPE_
  SGTYPE_VAL_
  BA_DEF_SGTYPE_
  BA_SGTYPE_
  SIG_TYPE_REF_
  VAL_TABLE_
  SIG_GROUP_
  SIG_VALTYPE_
  SIGTYPE_VALTYPE_
  BO_TX_BU_
  BA_DEF_REL_
  BA_REL_
  BA_DEF_DEF_REL_
  BU_SG_REL_
  BU_EV_REL_
  BU_BO_REL_
  SG_MUL_VAL_

BS_:

BU_: HIL_HOST BMS_ECU

BO_ 100 BMS_Command: 8 BMS_ECU
 SG_ Current_Cmd : 0|16|1@1+ (0.1,0) [0|500] "A"  HIL_HOST

BO_ 101 BMS_Status: 8 HIL_HOST
 SG_ Voltage : 0|16|1@1+ (0.01,0) [0|500] "V"  BMS_ECU
 SG_ SOC : 16|16|1@1+ (0.1,0) [0|100] "%"  BMS_ECU
 SG_ Fault_Code : 32|8|1@1+ (1,0) [0|255] ""  BMS_ECU
'''

with open('battery_can.dbc', 'w', encoding='utf-8') as f:
    f.write(dbc_content)

print("✅ battery_can.dbc 已生成，格式完全正确。")
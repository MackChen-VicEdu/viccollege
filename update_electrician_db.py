import sqlite3
import json
import os
from server import get_default_electrician_detail_en, get_default_electrician_detail_zh, DB_PATH

def update_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    detail_en = json.dumps(get_default_electrician_detail_en(), ensure_ascii=False)
    detail_zh = json.dumps(get_default_electrician_detail_zh(), ensure_ascii=False)
    
    modules_en = json.dumps([
        "Canadian Electrical Code (CEC / OESC) Structure & Fast Navigation",
        "Electrical Safety, PPE, Lockout/Tagout (LOTO) & Arc Flash Protection",
        "DC/AC Electrical Theory, Magnetism & Power Calculations",
        "Residential Wiring Systems & 100A/200A Service Panels",
        "3-Phase Power Distribution & Commercial Wiring",
        "Transformers: Installation, Connections & Sizing Calculations",
        "Electric Motors, Magnetic Starters & Motor Control Circuits",
        "Conduit Bending, Raceways, Cable Trays & Installation Methods",
        "Electrical Blueprint Reading, Schematics & Specification Sizing",
        "Red Seal 309A / 442A C of Q Mock Exam Simulation & Question Bank"
    ], ensure_ascii=False)
    
    modules_zh = json.dumps([
        "加拿大电气规范 (CEC / OESC) 架构解析与极速查表秘籍",
        "电气安全施工规范、PPE、LOTO 挂牌上锁与电弧防范 (Arc Flash)",
        "直流/交流电理论、电磁学原理与三相电功率计算",
        "民用住宅电气布线系统与 100A/200A 主配电箱实战",
        "三相工业商业配电系统与配电柜接线 (Commercial 3-Phase)",
        "变压器原理、接线方式、过流保护与容量选型计算",
        "交流电动机、磁力启动器、控制继电器与电路原理图 (Motor Controls)",
        "管道弯管工艺 (Conduit Bending)、电缆桥架与穿线技巧",
        "电气施工图纸识图、图例符号、材料估算与负荷计算书编制",
        "安省 309A / 442A 执照考试全真模考冲刺与红宝书题库精讲"
    ], ensure_ascii=False)
    
    cursor.execute("""
    UPDATE programs SET
        detail_json_en = ?,
        detail_json_zh = ?,
        modules_en = ?,
        modules_zh = ?
    WHERE slug = 'electrician'
    """, (detail_en, detail_zh, modules_en, modules_zh))
    
    conn.commit()
    print("Electrician program updated in database successfully. Rows affected:", cursor.rowcount)
    conn.close()

if __name__ == '__main__':
    update_db()

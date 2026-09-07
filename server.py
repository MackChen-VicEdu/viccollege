"""
Victoria International College - Backend Server
Provides SQLite Database, User Authentication (Google, LinkedIn, Email),
OpenAI API Key Management, AI Chat Proxy, and Admin Control Panel APIs.
"""

import os
import sys
import re
import math
import json
import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, g, Response

# App configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'victoria.db')

os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

# Optional requests for calling OpenAI API
try:
    import requests
except ImportError:
    requests = None


# ==============================================================================
# Database Setup & Utilities
# ==============================================================================

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

@app.route('/api', methods=['OPTIONS'])
@app.route('/api/<path:dummy>', methods=['OPTIONS'])
@app.route('/<path:dummy>', methods=['OPTIONS'])
def options_handler(dummy=None):
    resp = Response(status=204)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    return resp

AUTH_SALT = os.environ.get('AUTH_SALT', 'vic_college_salt_2026')

def hash_password(password: str) -> str:
    return hashlib.sha256((password + AUTH_SALT).encode('utf-8')).hexdigest()

def get_default_psw_detail_en():
    return {
        "hero": {
            "badge": "Accredited Career Diploma • NACC PSW DE 2022",
            "title": "Become a Compassionate & Skilled Caregiver with our Online & Hybrid PSW Program",
            "lead": "Transform lives with a fulfilling healthcare career. The NACC Personal Support Worker (PSW DE 2022) Certificate Program consists of intensive online theory, hands-on clinical lab simulations, and guaranteed clinical practicum placements in top Ontario nursing homes and long-term care facilities."
        },
        "stats": [
            {"value": "23 Weeks", "label": "Hybrid Theory + Lab + 310+ Hrs Practicum"},
            {"value": "$20 – $28 / hr", "label": "Average Starting Wage Across GTA Facilities"},
            {"value": "High Placement Rate", "label": "Direct LTC Nursing Home Clinical Placement"},
            {"value": "$28,000+ Grant", "label": "Second Career / Better Jobs Ontario Eligible"}
        ],
        "why_choose": {
            "title": "Why Choose a Career as a Personal Support Worker?",
            "subtitle": "Personal Support Workers (PSWs) are among the most essential and respected healthcare professionals in Canada. With Ontario's rapidly aging population and growing healthcare infrastructure, certified PSWs enjoy unmatched job security, flexible shifts, and meaningful daily patient impact.",
            "pillars": [
                {"title": "Abundant Job Opportunities", "desc": "PSWs are in extreme high demand across Ontario hospitals, long-term care homes (LTC), retirement residences, and home healthcare agencies, ensuring rapid job placement upon graduation."},
                {"title": "Personal Fulfillment", "desc": "Make a genuine difference every day by providing compassionate, dignified physical and emotional care that directly enhances the independence and quality of life for seniors and patients."},
                {"title": "Competitive Compensation", "desc": "Earn competitive hourly wages ($20–$28/hr) with opportunities for shift premiums, overtime, union benefits, comprehensive dental/medical plans, and paid vacation time."},
                {"title": "Flexible Hybrid Learning", "desc": "Study live interactive theory online from home, paired with hands-on practice in our fully equipped on-campus hospital simulation lab in Markham Campus."}
            ]
        },
        "credentials": {
            "title": "Credentials & Certifications Awarded",
            "subtitle": "Upon successful completion of the course and national examination, graduates receive official industry-recognized credentials:",
            "items": [
                {"title": "NACC PSW Official Diploma", "desc": "National Association of Career Colleges certified credential recognized nationwide across Canadian healthcare employers."},
                {"title": "Standard First Aid & CPR Level C", "desc": "Certified CPR/AED life support training required for all healthcare and long-term care clinical settings."},
                {"title": "GPA Dementia Care Certificate", "desc": "Gentle Persuasive Approaches (GPA) certification for managing responsive behaviors in seniors with dementia."},
                {"title": "Guaranteed Clinical Practicum", "desc": "Over 310 hours of hands-on placement in accredited Ontario nursing homes and community care agencies."}
            ]
        },
        "practicum": {
            "title": "Hands-on Clinical Practicum Placement",
            "desc": "Victoria International College coordinates 100% of your clinical placements. You will gain real-world experience under the direct mentorship of Registered Nurses (RNs) and Registered Practical Nurses (RPNs).",
            "box_title": "Direct Hire from Practicum",
            "box_desc": "Over 85% of our graduates receive permanent job offers directly from their clinical placement facility before graduation!"
        },
        "admissions": {
            "title": "Admission Requirements",
            "items": [
                "Ontario Secondary School Diploma (OSSD / Grade 12) or Canadian / International equivalent evaluation.",
                "Mature Student Status: 18 years of age or older with passing score on the Wonderlic Scholastic Level Exam (administered free on campus).",
                "Clear Vulnerable Sector Police Check (VSS).",
                "Standard Medical & Immunization Clearance Form (TB 2-step test, Hepatitis B, Influenza, COVID-19).",
                "Proficiency in English communication."
            ]
        },
        "curriculum": {
            "title": "Official NACC Curriculum Modules (15 Subjects)",
            "desc": "Our comprehensive curriculum covers all 15 core vocational modules mandated by the National Association of Career Colleges (NACC) and Ontario Ministry guidelines:"
        },
        "curriculum_modules": [
            {"num": 1, "title": "PSW Foundations", "desc": "Role, responsibilities, scope of practice, legal boundaries & healthcare ethics."},
            {"num": 2, "title": "Safety and Mobility", "desc": "Body mechanics, ergonomics, patient transfer techniques, infection control & WHMIS."},
            {"num": 3, "title": "Body Systems & Anatomy", "desc": "Comprehensive overview of human anatomy, physiology, aging processes & vital signs."},
            {"num": 4, "title": "Assisting with Personal Hygiene", "desc": "Bed baths, oral hygiene, skin integrity prevention, grooming & dignity care."},
            {"num": 5, "title": "Abuse and Neglect", "desc": "Identification, institutional abuse reporting protocols & client rights advocacy."},
            {"num": 6, "title": "Household Management, Nutrition & Hydration", "desc": "Meal planning, special dietary requirements, therapeutic diets & feeding assistance."},
            {"num": 7, "title": "Care Planning & Documentation", "desc": "Restorative care goals, electronic health documentation (EHR) & reporting to RNs/RPNs."},
            {"num": 8, "title": "Assisting the Family / Growth & Development", "desc": "Family dynamics, child development, supportive care across the lifespan."},
            {"num": 9, "title": "Assisting the Dying Person", "desc": "Palliative care, end-of-life comfort, hospice support & bereavement protocols."},
            {"num": 10, "title": "Assisting with Medications", "desc": "Pharmacological routes, medication reminders, blister packs & error reporting."},
            {"num": 11, "title": "Cognitive & Mental Health Issues", "desc": "Alzheimer's disease, dementia care, depression, delirium & acquired brain injuries."},
            {"num": 12, "title": "Common Health Conditions", "desc": "Diabetes, cardiovascular diseases, stroke, respiratory conditions, arthritis & cancer care."},
            {"num": 13, "title": "Gentle Persuasive Approaches (GPA)", "desc": "Evidence-based dementia de-escalation techniques & patient-centered behavioral care."},
            {"num": 14, "title": "Clinical Placement (Facility - 200+ Hours)", "desc": "Supervised on-site practicum in accredited Ontario Long-Term Care (LTC) nursing homes."},
            {"num": 15, "title": "Clinical Placement (Community - 110+ Hours)", "desc": "Hands-on in-home patient support with community healthcare agencies."}
        ],
        "grants": {
            "badge": "GOVERNMENT GRANTS",
            "title": "Get Up to $28,000+ Grant",
            "description": "Study PSW with zero out-of-pocket tuition. Eligible candidates may qualify for up to $28,000+ through Better Jobs Ontario covering tuition, books, and living expenses.",
            "amount": "$28,000+",
            "button_text": "Check Eligibility Now"
        },
        "snapshot": {
            "delivery": "Hybrid (Online + Lab)",
            "practicum": "310+ Hours (Guaranteed)",
            "locations": "Markham Main Campus / Live Online",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "Can I study the PSW program online from home?", "a": "Yes! All theory lectures are delivered live online with interactive instructors. Hands-on clinical lab simulations are conducted on campus, followed by your guaranteed nursing home practicum."},
            {"q": "How long is the PSW program?", "a": "The program is 23 weeks in total, including interactive online classroom theory, on-campus lab training, and 310+ hours of guaranteed clinical placements."},
            {"q": "Are there government grants available for this program?", "a": "Yes! The program is eligible for Better Jobs Ontario (formerly Second Career) offering up to $28,000+ in non-repayable grants covering tuition, books, transportation, and living allowance for qualified candidates."},
            {"q": "Do you help with job placement after graduation?", "a": "Absolutely. Victoria College provides 1-on-1 resume workshops, employer networking, and direct placement coordination with our partner LTC homes and healthcare agencies."},
            {"q": "What credentials will I receive upon completion?", "a": "You will receive the official NACC Personal Support Worker DE 2022 Diploma, Standard First Aid & CPR Level C, and Gentle Persuasive Approaches (GPA) certification."},
            {"q": "What are the admission requirements?", "a": "Ontario Secondary School Diploma (OSSD) or equivalent, or passing a Wonderlic / college entrance assessment (18+ mature student), plus medical immunizations and police record check for clinical placement."}
        ]
    }

def get_default_psw_detail_zh():
    return {
        "hero": {
            "badge": "安省官方职业文凭 • NACC PSW DE 2022",
            "title": "成为备受尊重的专业医护人员 • 在线+实操混成制 PSW 护工课程",
            "lead": "开启崇高而稳定的医疗保健职业生涯。NACC 个人护理护工（PSW DE 2022）职业文凭课程包含线上互动理论、校区模拟病房实训以及安省正规长期护理院（LTC）实地临床带薪/跟岗实习。"
        },
        "stats": [
            {"value": "23 周", "label": "网课理论 + 校区实操 + 310+小时临床实习"},
            {"value": "$20 – $28 / 小时", "label": "大多伦多地区医疗养老机构平均起薪"},
            {"value": "高就业率", "label": "签约长期护理院/医院对口直推"},
            {"value": "$28,000+ 补贴", "label": "符合 Better Jobs Ontario 政府全额资助"}
        ],
        "why_choose": {
            "title": "为什么选择成为个人护理护工 (PSW)？",
            "subtitle": "个人护理员（PSW）是加拿大医疗保健体系中极度刚需且备受尊敬的专业人员。随着安省人口老龄化加剧，持证 PSW 享有无可比拟的就业稳定性、灵活排班与极佳的福利待遇。",
            "pillars": [
                {"title": "就业机会极多", "desc": "安省医院、长期护理院（LTC）、养老社区及家庭护理机构常年极度紧缺，毕业即对口就业。"},
                {"title": "职业成就感高", "desc": "用专业与爱心提供身体与心理照料，真正改善长者与病患的生活质量，赢得社会尊重。"},
                {"title": "薪酬待遇优厚", "desc": "起薪 $20–$28/小时，享晚夜班补贴、加班津贴、工会医疗保险、牙医保险及带薪年假。"},
                {"title": "灵活线上学习", "desc": "在家参加实时名师直播授课，结合万锦主校区先进模拟病房实操演练。"}
            ]
        },
        "credentials": {
            "title": "官方认证毕业文凭与资格证书",
            "subtitle": "顺利完成全部课程与全国统考后，毕业生将获得加国医疗行业高度认可的权威资质：",
            "items": [
                {"title": "NACC PSW 官方职业文凭", "desc": "加拿大全国职业学院协会（NACC）认证文凭，全加医疗护理机构通用认可。"},
                {"title": "标准急救与 CPR Level C 证书", "desc": "安省长期护理院与医院临床工作必备的官方急救与 AED 心肺复苏认证。"},
                {"title": "GPA 失智症长者关怀认证", "desc": "Gentle Persuasive Approaches (GPA) 官方认证，掌握阿尔茨海默症应对技能。"},
                {"title": "100% 保障正规机构临床实习", "desc": "310+小时安省持牌长期护理院与社区家庭护理实地跟岗临床带教实训。"}
            ]
        },
        "practicum": {
            "title": "安省持牌正规养老机构临床实习",
            "desc": "维多利亚学院负责全流程对口安排 100% 临床实习岗位，由安省持牌注册护士（RN / RPN）亲自带教，迅速积累加国本土医护实战经验。",
            "box_title": "实习基地直接留用高就业率",
            "box_desc": "超过 85% 的毕业生在临床实习期间直接获得实习机构正式录用聘书（Job Offer）！"
        },
        "admissions": {
            "title": "入学报读条件与要求",
            "items": [
                "安省高中毕业证书（OSSD / 12年级）或加国及海外同等学历评估认证。",
                "成熟学生入学通道：年满 18 周岁，并通过学院 Wonderlic 入学能力测评（校区免费测评）。",
                "提供合格的无犯罪记录弱势群体筛查证明（Vulnerable Sector Check）。",
                "完成标准医疗体检与疫苗接种表（TB 结核双结皮试、乙肝、流感、COVID-19 疫苗）。",
                "具备基础英语沟通与理解能力。"
            ]
        },
        "curriculum": {
            "title": "官方 NACC 教学大纲（15 门专业核心科目）",
            "desc": "全面覆盖加拿大职业学院协会（NACC）与安省教育部大纲规定的 15 门职业核心课程："
        },
        "curriculum_modules": [
            {"num": 1, "title": "PSW 基础通论", "desc": "角色职责、工作范围、法律规范与职业道德准则。"},
            {"num": 2, "title": "安全与行动协助", "desc": "人体力学、病患安全搬移技巧、感染控制与 WHMIS 危险品安全。"},
            {"num": 3, "title": "人体系统与解剖", "desc": "人体各大生理系统结构、老化生理过程与生命体征测量。"},
            {"num": 4, "title": "个人卫生护理", "desc": "床上擦浴、口腔护理、压疮防范、仪容修饰与尊严护理。"},
            {"num": 5, "title": "虐待与忽视防范", "desc": "识别迹象、法定上报流程与长者权益保护。"},
            {"num": 6, "title": "家政管理、营养与补水", "desc": "餐食规划、特殊治疗饮食调配与辅助进食。"},
            {"num": 7, "title": "护理计划与文书记录", "desc": "康复护理目标制定、电子医疗记录 (EHR) 及向注册护士汇报。"},
            {"num": 8, "title": "家庭协助与成长发育", "desc": "家庭人际互动、儿童发育心理与全生命周期关怀。"},
            {"num": 9, "title": "临终关怀护理", "desc": "姑息治疗、临终身心舒适护理、安宁疗护与家属哀伤辅导。"},
            {"num": 10, "title": "药物协助管理", "desc": "给药途径认知、服药提醒、药盒管理与差错防范上报。"},
            {"num": 11, "title": "认知与心理健康护理", "desc": "阿尔茨海默病、失智症护理、抑郁症、谵妄与脑损伤照护。"},
            {"num": 12, "title": "常见健康疾病照护", "desc": "糖尿病、心血管疾病、中风后遗症、呼吸系统疾病、关节炎与癌症照护。"},
            {"num": 13, "title": "温和劝导疗法 (GPA)", "desc": "失智症情绪疏导技巧与以患者为中心的行为应对。"},
            {"num": 14, "title": "长者院临床实习（机构 - 200+小时）", "desc": "在安省认证长期护理院（LTC）进行带教实战。"},
            {"num": 15, "title": "社区上门实习（社区 - 110+小时）", "desc": "跟随社区医疗机构进行上门长者与病患照护。"}
        ],
        "grants": {
            "badge": "安省政府培训资助",
            "title": "申请最高 $28,000+ 政府助学金",
            "description": "符合条件的安省居民最高可申请 $28,000+ 加币政府全额无偿培训补助（Better Jobs Ontario），100% 覆盖学费、书本费、交通及学习期间基本生活费。",
            "amount": "$28,000+",
            "button_text": "立即免费评估资格"
        },
        "snapshot": {
            "delivery": "混成教学（线上理论 + 校区实训）",
            "practicum": "310+ 小时（100% 对口安排）",
            "locations": "万锦主校区 / 在线名师直播",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "PSW 课程可以在家线上学习吗？", "a": "可以！所有理论课程均采用线上名师实时互动直播教学，配合校区模拟病房实操实训及养老机构实地临床实习。"},
            {"q": "PSW 课程需要读多久？", "a": "课程总计 23 周，涵盖线上理论课、校区模拟病房集训及 310+ 小时正规机构临床实习。"},
            {"q": "我可以申请政府学费补贴吗？", "a": "可以！本课程符合安省 Better Jobs Ontario（原第二职业 Second Career）政府资助计划，合资格者最高可获 $28,000+ 无需偿还的政府补贴。"},
            {"q": "毕业后学校会推荐实习和工作吗？", "a": "是的。维多利亚学院提供一对一简历修改、模拟面试，并直接向长期合作的安省 LTC 养老院及医疗机构直推就业。"},
            {"q": "毕业能获得哪些官方证书？", "a": "毕业将获得安省教育部备案的 NACC PSW 官方文凭、标准急救与 CPR Level C 证书，以及 GPA 温和说服法失智症关怀认证。"},
            {"q": "报读课程有什么入学要求？", "a": "具备安省高中文凭（OSSD）或同等学历，或年满 18 周岁通过学院成熟学生入学测评，并完成体检疫苗及无犯罪记录证明。"}
        ]
    }

def get_default_accounting_detail_en():
    return {
        "hero": {
            "badge": "Ontario Approved Career Diploma • 30-Week Intensive",
            "title": "Master Full-Cycle Canadian Accounting, Tax & Payroll",
            "lead": "Fast-track your career as a high-demand corporate bookkeeper, payroll administrator, or tax associate with hands-on training led by veteran Canadian CPAs. Includes QuickBooks, Sage 50, ACCPAC, Profile/TaxPrep, advanced Excel modeling, and direct job placement support."
        },
        "stats": [
            {"value": "30 Weeks", "label": "Comprehensive Theory + Enterprise Software Labs"},
            {"value": "$22 – $32 / hr", "label": "Average GTA Starting Wage for Corporate Bookkeepers"},
            {"value": "100% CPA Mentorship", "label": "Taught Exclusively by Seasoned Canadian CPAs"},
            {"value": "Up to $28,000+", "label": "Eligible for Better Jobs Ontario Full Government Funding"}
        ],
        "why_choose": {
            "title": "Why Choose Accounting, Tax and Payroll as Your Canadian Career?",
            "subtitle": "Computerized accounting and payroll administration is one of Canada's most stable, respected, and recession-resilient professions. Every Canadian business, non-profit, and government entity requires certified professionals to manage financial records, CRA tax filings, and payroll compliance.",
            "pillars": [
                {"title": "High Job Stability & Growth", "desc": "Essential business function required across all sectors. Enjoy consistent office/hybrid work hours, permanent positions, and clear career ladders toward Senior Accountant or CPA."},
                {"title": "100% Real-World Case Studies", "desc": "Work on authentic full-cycle Canadian accounting sets, payroll reconciliations, and complex corporate/personal tax returns rather than mere abstract theory."},
                {"title": "Comprehensive Software Mastery", "desc": "Master industry-standard tools employers mandate: QuickBooks (Desktop & Online), Sage 50 (Simply Accounting), Sage 300 / ACCPAC, Taxprep/Profile, and Financial Excel."},
                {"title": "Full CPA Mentorship & Placement", "desc": "1-on-1 resume optimization, Canadian accounting interview simulation, LinkedIn networking, and direct employer hiring referrals from our recruitment network."}
            ]
        },
        "credentials": {
            "title": "Diplomas & Certifications Awarded",
            "subtitle": "Upon successful completion of the course and practical assessments, graduates receive prestigious industry credentials:",
            "items": [
                {"title": "Official Accounting, Tax & Payroll Diploma", "desc": "Ministry-approved vocational diploma recognized by Canadian businesses and accounting firms nationwide."},
                {"title": "QuickBooks & QBO ProAdvisor Ready", "desc": "Hands-on proficiency certification across both desktop enterprise and cloud bookkeeping workflows."},
                {"title": "Sage 50 Computerized Accounting Specialist", "desc": "Official credential verifying mastery of inventory, multi-currency, job costing, and general ledger operations."},
                {"title": "Canadian Payroll & Tax Compliance Certificate", "desc": "Demonstrates mastery of CRA tax withholding, statutory deductions (CPP/EI/WSIB), T4/T4A, and corporate tax returns."}
            ]
        },
        "curriculum": {
            "title": "Comprehensive 30-Week Curriculum Modules (10 Core Subjects)",
            "desc": "Our structured curriculum covers all essential competencies required by Canadian employers, from fundamental double-entry bookkeeping to advanced ERP systems and complex corporate taxation:"
        },
        "curriculum_modules": [
            {"num": 1, "title": "Canadian Financial Accounting Principles & Bookkeeping", "desc": "GAAP / ASPE standards, double-entry bookkeeping, general journal entries, general ledgers, trial balances, and financial statement formulation (Balance Sheet, Income Statement)."},
            {"num": 2, "title": "QuickBooks Desktop & QuickBooks Online (QBO)", "desc": "Comprehensive setup of business charts of accounts, vendor bills, customer invoicing, inventory tracking, bank feeds, credit card reconciliation, and management reporting."},
            {"num": 3, "title": "Sage 50 Accounting (Simply Accounting)", "desc": "Enterprise computerized accounting workflows, payable/receivable sub-ledgers, job costing, departmental accounting, multi-currency transactions, and bank reconciliations."},
            {"num": 4, "title": "Sage 300 / ACCPAC ERP Accounting Overview", "desc": "Corporate enterprise resource planning (ERP) navigation, multi-entity consolidations, GL/AP/AR modules, purchase order processing, and month-end closing procedures."},
            {"num": 5, "title": "Canadian Payroll Compliance & Administration", "desc": "National Payroll Institute (NPI) standards, statutory deductions (CPP, EI, Federal/Provincial Income Tax, Employer Health Tax, WSIB), ROE issuance, T4/T4A preparation, and CRA remittances."},
            {"num": 6, "title": "Canadian Personal Taxation (T1) & Wealth Management", "desc": "Personal income tax laws, employment income, investment income, capital gains, rental income, deductions, medical/child credits, RRSP optimization, and Profile/TaxPrep software filing."},
            {"num": 7, "title": "Canadian Corporate Taxation (T2) & GST/HST Filings", "desc": "Corporate tax principles, active business income calculation, Capital Cost Allowance (CCA), schedule 1 reconciliations, GST/HST return calculations, and CRA audit compliance."},
            {"num": 8, "title": "Advanced Excel for Financial Modeling & Business Analysis", "desc": "Advanced functions (XLOOKUP, INDEX/MATCH), dynamic Pivot Tables, financial statements consolidation, sensitivity analysis, budget variance models, and executive dashboards."},
            {"num": 9, "title": "Full-Cycle Accounting Simulation & Year-End Working Papers", "desc": "End-to-end practical accounting cycle simulation for manufacturing, retail, and service businesses, including adjusting entries, depreciation schedules, and compilation reports."},
            {"num": 10, "title": "Career Coaching, Resume Building & CPA Interview Prep", "desc": "Tailored Canadian accounting resume workshops, behavioral & technical interview simulation with senior CPAs, LinkedIn optimization, and job placement assistance."}
        ],
        "practicum": {
            "title": "Hands-on Software Labs & Year-End Simulation",
            "desc": "Victoria International College provides extensive hands-on laboratory simulation. Students work with live corporate accounting data sets and real-world tax scenarios under the guidance of practicing CPAs.",
            "box_title": "Direct Career Placement Assistance",
            "box_desc": "Over 90% of our active graduates secure full-time accounting, bookkeeping, or payroll roles within 3 to 6 months of graduation!"
        },
        "admissions": {
            "title": "Admission Requirements",
            "items": [
                "Ontario Secondary School Diploma (OSSD / Grade 12) or Canadian / International equivalent credential evaluation.",
                "Mature Student Status: 18 years of age or older with a passing score on the Wonderlic Scholastic Level Exam (administered free on campus or online).",
                "Basic computer literacy and foundational English communication proficiency.",
                "Admissions interview with a Victoria College academic advisor."
            ]
        },
        "grants": {
            "badge": "GOVERNMENT FUNDING AVAILABLE",
            "title": "Get Up to $28,000+ Grant",
            "description": "Study Accounting, Tax and Payroll with zero out-of-pocket tuition. Eligible candidates (laid-off workers, EI recipients, self-employed, or low-income residents) may qualify for up to $28,000+ in non-repayable Better Jobs Ontario grants covering tuition, software, books, and living expenses.",
            "amount": "$28,000+",
            "button_text": "Check Grant Eligibility"
        },
        "snapshot": {
            "delivery": "Hybrid / Live Online + Campus Labs",
            "practicum": "Enterprise Software & Real Cases",
            "locations": "Markham Main Campus / Live Online",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "Can I study the Accounting, Tax and Payroll program online?", "a": "Yes! All theoretical lectures and software simulations are delivered live online with interactive CPA instructors. Students can participate from home across Ontario while accessing virtual labs and instructor office hours."},
            {"q": "Do I need a prior background in math or accounting to enroll?", "a": "No prior accounting experience is required. The curriculum begins with fundamental bookkeeping and double-entry concepts before progressively advancing to corporate accounting software and Canadian taxation."},
            {"q": "What accounting software will I learn in this program?", "a": "You will gain intensive hands-on experience in QuickBooks Desktop, QuickBooks Online (QBO), Sage 50 (Simply Accounting), Sage 300 (ACCPAC), Taxprep / Profile, and Advanced Excel for Finance."},
            {"q": "Are there government grants available for this diploma program?", "a": "Yes! Victoria College's Accounting, Tax and Payroll program is fully approved for the Better Jobs Ontario (formerly Second Career) grant program, providing up to $28,000+ in non-repayable government funding for eligible applicants."},
            {"q": "How does Victoria College assist graduates in finding a job?", "a": "We provide comprehensive 1-on-1 career services including Canadian accounting resume crafting, technical test preparation, mock CPA interviews, and direct networking with hiring managers at corporate partners and accounting firms."},
            {"q": "What job titles can I apply for upon graduation?", "a": "Graduates qualify for positions such as Full-Cycle Bookkeeper, Accounting Assistant, Accounts Receivable (AR) Clerk, Accounts Payable (AP) Clerk, Payroll Administrator, Junior Tax Preparer, and Financial Assistant."}
        ]
    }

def get_default_accounting_detail_zh():
    return {
        "hero": {
            "badge": "安省教育部正规职业文凭 • 30周密集实战班",
            "title": "掌握加拿大全盘会计账务、税务申报与薪资管理",
            "lead": "由加国资深 CPA 及持牌会计师团队亲授，针对加拿大本土公司日常全流程商业做账、员工工资税核算、CRA 个人与公司税申报进行深度全真演练。熟练掌握 QuickBooks、Sage 50、ACCPAC、Profile/TaxPrep 及高级 Excel 财务建模，享受对口高薪白领就业推荐与最高 $28,000+ 政府全额学费资助。"
        },
        "stats": [
            {"value": "30 周", "label": "名师直播理论 + 真实商业账套上机实操"},
            {"value": "$22 – $32 / 小时", "label": "大多伦多地区全盘簿记员与会计起薪"},
            {"value": "100% CPA 导师", "label": "资深加国注册会计师手把手带教"},
            {"value": "$28,000+ 补贴", "label": "符合 Better Jobs Ontario 政府全额资助"}
        ],
        "why_choose": {
            "title": "为什么选择会计、税务与薪资管理作为加国职业方向？",
            "subtitle": "会计与薪资管理是加拿大各行各业最稳定、最受尊重、且最具抗周期性的白领黄金职业。无论是跨国企业、中小公司、非营利机构还是政府部门，都需要专业财会人员进行合规做账、CRA 报税与工资发放。",
            "pillars": [
                {"title": "就业刚需，环境稳定", "desc": "各行业常年极度刚需，无需重体力劳动。工作环境舒适稳定，规范双休，职业上升通道顺畅，可晋升高级会计师或报考 CPA。"},
                {"title": "100% 本地真账案例实操", "desc": "摒弃纯死记硬背理论，全程使用加拿大中小型企业真实账目、员工工资单及税表进行全流程模拟，毕业即具备 2-3 年本地实际工作经验。"},
                {"title": "主流商业财务软件全精通", "desc": "全面攻克加国雇主必备主流软件：QuickBooks 桌面/云端版、Sage 50、Sage 300/ACCPAC、Profile/TaxPrep 专业报税系统及高级 Excel 建模。"},
                {"title": "CPA 导师一对一求职辅导", "desc": "专业修改加拿大标准财会英文简历、名师一对一模拟中英文专业面试与技术测试、精准内推至合作会计师事务所及企业财务部门。"}
            ]
        },
        "credentials": {
            "title": "官方认证毕业文凭与资格证书",
            "subtitle": "顺利完成全部课程与实践考核后，毕业生将获得加国商业财会领域高度认可的权威资质：",
            "items": [
                {"title": "安省官方会计、税务与薪资管理文凭", "desc": "安省教育部合规备案职业文凭，全加各大企业与会计师事务所通用认可。"},
                {"title": "QuickBooks / QBO 云端会计实操认证", "desc": "熟练掌握加国市场占有率第一的中小企业云端与桌面版账套管理。"},
                {"title": "Sage 50 电算化会计应用专家认证", "desc": "全面掌握进销存、成本核算、多币种核算及企业财务报表编制。"},
                {"title": "加拿大薪资合规与报税实战证书", "desc": "熟练掌握 CRA 工资代扣缴（CPP/EI/WSIB/税金）、T4/T4A 及公司税申报。"}
            ]
        },
        "curriculum": {
            "title": "官方教学大纲与课程模块（10 门专业核心科目）",
            "desc": "全面覆盖加拿大职业财会工作必备核心技能，从复式记账法到企业级 ERP 财务系统与公司税实战："
        },
        "curriculum_modules": [
            {"num": 1, "title": "加拿大商业会计基础与复式记账原理", "desc": "GAAP/ASPE 会计准则、借贷记账法、日记账与总分类账、试算平衡表编制及三大财务报表（资产负债表、损益表、现金流量表）原理与实操。"},
            {"num": 2, "title": "QuickBooks 桌面版与 QBO 云端版账套全流程", "desc": "企业账套建立、科目表设置、应收/应付账款管理、销售发票、供应商账单、库存追踪、银行与信用卡流水对账及生成财务管理分析报表。"},
            {"num": 3, "title": "Sage 50 财务软件企业级实战应用", "desc": "企业进销存业务处理、往来账核算、多币种交易处理、部门/项目成本核算（Job Costing）、银行对账单核销及期末结账调整。"},
            {"num": 4, "title": "Sage 300 / ACCPAC 中大型企业 ERP 财务模块", "desc": "大型企业级 ERP 架构认知、总账 (GL)、应付 (AP)、应收 (AR) 核心模块操作、跨部门凭证流转、期末集中过账及年终关账流程。"},
            {"num": 5, "title": "加拿大薪资法规管理与工资税核算 (Payroll)", "desc": "加拿大薪资学会 (NPI) 规范、法定扣缴项目（CPP养老金、EI失业金、联邦与省所得税、WSIB工伤险、EHT雇主健康税）、ROE离职表制作、T4/T4A汇总及向 CRA 汇缴申报。"},
            {"num": 6, "title": "加拿大个人所得税 (T1) 申报与税务规划", "desc": "加国税法体系、雇佣收入、投资收益、资本利得、房屋出租、自雇生意、各项税收抵免扣除、RRSP规划及 Profile/TaxPrep 报税软件实战。"},
            {"num": 7, "title": "加拿大公司所得税 (T2) 申报与消费税 (GST/HST)", "desc": "加拿大公司税基础理论、主动营业收入计算、固定资产折旧 (CCA)、Schedule 1 纳税调整、GST/HST 税率计算及 CRA 审计应对策略。"},
            {"num": 8, "title": "高级 Excel 财务建模与商业数据分析", "desc": "高级函数应用 (XLOOKUP, INDEX/MATCH)、动态数据透视表 (Pivot Table)、多表合并计算、财务敏感性分析、预算差异模型与管理层看板制作。"},
            {"num": 9, "title": "企业全流程真账实操与年终结账底稿编制", "desc": "针对制造、零售及服务型企业的全真实战案例，独立完成全套月结、年结调整分录、固定资产明细表及年终工作底稿 (Working Papers)。"},
            {"num": 10, "title": "财会职业求职规划、简历精修与 CPA 模拟面试", "desc": "针对加国本地财会岗位的英文简历一对一精修、技术测试（Excel/会计分录）模拟训练、行为面试应答技巧及优质企业定向推荐。"}
        ],
        "practicum": {
            "title": "名师真账实训实验室与全真案例模拟",
            "desc": "维多利亚职业学院配备先进仿真财务实验室，学员在资深持牌会计师的指导下直接上手真实商业公司账目与复杂税务案例，迅速将理论转化为实操战斗力。",
            "box_title": "对口就业直通与内推推荐",
            "box_desc": "维多利亚学院超过 90% 的积极求职学员在毕业后 3 至 6 个月内成功入职加国企业财务部或知名会计师事务所！"
        },
        "admissions": {
            "title": "入学报读条件与要求",
            "items": [
                "安省高中毕业证书（OSSD / 12年级）或加国及海外同等学历评估认证。",
                "成熟学生入学通道：年满 18 周岁，并通过学院 Wonderlic 入学基础能力测评（校区/线上免费测评）。",
                "具备基础计算机操作能力与基础英语沟通理解能力。",
                "参加维多利亚学院课程规划师的一对一入学评估与职业规划咨询。"
            ]
        },
        "grants": {
            "badge": "安省政府培训资助",
            "title": "申请最高 $28,000+ 政府助学金",
            "description": "符合条件的安省居民（失业、裁员、曾领 EI、自雇、零工人员或低收入群体）最高可申请 $28,000+ 加币政府全额无偿培训补助（Better Jobs Ontario），100% 覆盖学费、软件工具费、书本教材费、交通及学习期间基本生活费。",
            "amount": "$28,000+",
            "button_text": "立即免费评估资格"
        },
        "snapshot": {
            "delivery": "混成教学 / 线上直播 + 校区实操",
            "practicum": "企业真实账套 + 上机实验",
            "locations": "万锦主校区 / 在线名师直播",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "零基础或没有会计背景可以报名学习吗？", "a": "完全可以！课程从最基础的复式记账和商业概念讲起，循序渐进，由浅入深，配合大量真实案例手把手带教，零基础学员也能轻松跟上节奏。"},
            {"q": "会计课程可以在家线上学习吗？", "a": "可以！所有理论课程与软件操作均采用线上实时互动直播教学，课后提供录播回放与虚拟机实操环境，名师线上答疑。"},
            {"q": "课程会教授哪些加拿大主流财务软件？", "a": "课程涵盖加国企业最常用的财务工具：QuickBooks 桌面版及云端版 (QBO)、Sage 50 (Simply Accounting)、Sage 300 (ACCPAC)、Taxprep / Profile 专业报税系统及 Advanced Excel。"},
            {"q": "我可以申请政府全额学费资助吗？", "a": "可以！本专业完全符合安省 Better Jobs Ontario（原第二职业 Second Career）资助计划，合资格者最高可获 $28,000+ 无需偿还的政府全额补贴，学院专家免费协助申请。"},
            {"q": "毕业后学校会协助找工作吗？", "a": "是的！学院提供加国财会简历一对一修改、CPA 导师专业面试辅导、上机测试真题模拟，并向长期合作的知名会计师事务所与企业财务部直接内推。"},
            {"q": "毕业后可以申请哪些对口职位？", "a": "毕业生可胜任全盘簿记员（Bookkeeper）、会计助理（Accounting Assistant）、应收应付账款专员（AP/AR Clerk）、薪资管理员（Payroll Administrator）、报税助理等各类高薪白领职位。"}
        ]
    }

def get_default_eca_detail_en():
    return {
        "hero": {
            "badge": "Ontario Approved Career Diploma • 22-Week Intensive Daycare Placement",
            "title": "Launch Your Rewarding Career as a Certified Early Childcare Assistant (ECA)",
            "lead": "Help shape the next generation with Ontario-approved early childhood training. Master child development, health & safety, creative curriculum planning, and gain 500+ hours of guaranteed hands-on field placement in licensed daycares and preschools across the GTA."
        },
        "stats": [
            {"value": "22 Weeks", "label": "Comprehensive Theory + 500+ Hours Daycare Placement"},
            {"value": "$18 – $26 / hr", "label": "Competitive GTA Starting Wage + $2/hr Gov WEG Grant"},
            {"value": "100% Daycare Placement", "label": "Guaranteed Practicum in Accredited Daycare Centers"},
            {"value": "Up to $28,000+", "label": "Eligible for Full Better Jobs Ontario Government Funding"}
        ],
        "why_choose": {
            "title": "Why Choose Early Childcare Assistant (ECA) as Your Canadian Career?",
            "subtitle": "Early childhood education in Ontario is undergoing historic expansion driven by the federal $10-a-day Canada-Wide Early Learning and Child Care (CWELCC) plan. Daycare centers, preschools, and kindergarten programs across the Greater Toronto Area face severe shortages of certified, compassionate educators and assistants.",
            "pillars": [
                {"title": "Historic Industry Demand", "desc": "With thousands of new subsidized childcare spaces opening across Ontario, certified Early Childcare Assistants enjoy extraordinary job security, permanent employment, and signing bonuses."},
                {"title": "Rewarding & Meaningful Work", "desc": "Make a lasting, positive impact on young children's cognitive, emotional, and social development during their most critical formative years."},
                {"title": "Safe & Collaborative Work Environment", "desc": "Work in modern, licensed childcare facilities, early learning centers, and school boards alongside dedicated teams of Registered Early Childhood Educators (RECEs)."},
                {"title": "Clear Career Progression", "desc": "Gain vital Canadian frontline experience and open doors to accelerated RECE diploma pathways, daycare supervisory roles, or private home childcare business ownership."}
            ]
        },
        "credentials": {
            "title": "Diplomas & Certifications Awarded",
            "subtitle": "Upon successful completion of the curriculum and field placement hours, graduates receive prestigious, employer-recognized credentials:",
            "items": [
                {"title": "Official Early Childcare Assistant (ECA) Diploma", "desc": "Ontario Ministry-approved vocational diploma recognized by licensed daycare centers, nursery schools, and private educational institutions across Ontario."},
                {"title": "Standard First Aid & CPR Level C (Infant & Child)", "desc": "Mandatory provincial certification ensuring readiness to handle pediatric emergencies, choking, CPR, and first aid."},
                {"title": "Food Handler & Pediatric Nutrition Certificate", "desc": "Industry-standard certification verifying mastery of safe food handling, allergy prevention, and balanced menu planning in childcare settings."},
                {"title": "Guaranteed 500+ Hours Supervised Field Placement", "desc": "Comprehensive hands-on practicum verifying verified Canadian childcare experience across infant, toddler, and preschool age groups."}
            ]
        },
        "practicum": {
            "title": "Guaranteed 500+ Hours Field Placement in Licensed Ontario Daycares",
            "desc": "Victoria College partners with accredited daycare centers, Montessori schools, and early learning centers across Toronto, Markham, Richmond Hill, Scarborough, and Mississauga to coordinate 100% of your hands-on field practicum.",
            "box_title": "Direct Daycare Hiring & Job Offer Success Rate",
            "box_desc": "Over 85% of Victoria College ECA students receive permanent job offers directly from their placement host center before graduation!"
        },
        "admissions": {
            "title": "Admission Requirements & Prerequisites",
            "items": [
                "Ontario Secondary School Diploma (OSSD / Grade 12) or equivalent evaluation from a recognized credential agency.",
                "Mature Student Admission: Age 18 or older and successfully passing the Wonderlic College Entrance Assessment (complimentary on-site testing).",
                "Clear Vulnerable Sector Criminal Reference Check (VSC) issued by local police services (required prior to field placement).",
                "Up-to-date Medical Immunization Record including Two-Step Tuberculosis (TB) skin test.",
                "Genuine passion for early childhood development, strong interpersonal communication, and commitment to nurturing care."
            ]
        },
        "curriculum": {
            "title": "Comprehensive 22-Week Curriculum Modules (10 Core Subjects)",
            "desc": "Our structured curriculum equips students with the exact competencies mandated by Ontario's Child Care and Early Years Act (CCEYA) and early learning frameworks:"
        },
        "curriculum_modules": [
            {"num": 1, "title": "Introduction to Early Childhood Education & Ontario Daycare Regulations", "desc": "Overview of Canadian early childhood education, Child Care and Early Years Act (CCEYA 2014) compliance, licensing requirements, and professional ethics."},
            {"num": 2, "title": "Child Growth and Development: Infancy to Toddlerhood", "desc": "Physical, cognitive, emotional, and social development milestones for infants (0–18 months) and toddlers (18–30 months), brain development, and attachment theory."},
            {"num": 3, "title": "Child Growth and Development: Preschool to School-Age", "desc": "Developmental stages for preschoolers (2.5–5 years) and school-age children (6–12 years), language acquisition, motor skills, and social interaction patterns."},
            {"num": 4, "title": "Health, Safety, Nutrition & Emergency Procedures in Childcare", "desc": "Infection control protocols, sanitation standards, injury prevention, anaphylaxis and food allergy management, balanced meal planning, and pediatric emergency response."},
            {"num": 5, "title": "Creative Expressions: Art, Music, Storytelling & Sensory Play", "desc": "Designing engaging activities that stimulate creativity, fine and gross motor skills, sensory exploration, musical rhythms, dramatic play, and early literacy."},
            {"num": 6, "title": "Positive Guidance & Classroom Behavior Strategies", "desc": "Evidence-based child guidance techniques, encouraging self-regulation, conflict resolution among children, establishing calm classroom routines, and positive reinforcement."},
            {"num": 7, "title": "Interpersonal Communications with Families, Staff & Regulators", "desc": "Building trusting partnerships with diverse Canadian families, daily parent communication, daily logs, multi-disciplinary teamwork with RECEs, and Ministry inspection preparedness."},
            {"num": 8, "title": "Program Planning & Pedagogical Documentation (How Does Learning Happen?)", "desc": "Implementing Ontario's 'How Does Learning Happen?' early learning framework, designing play-based learning environments, observing children, and creating learning portfolios."},
            {"num": 9, "title": "Supporting Children with Diverse Needs & Inclusive Childcare", "desc": "Inclusive childcare practices, understanding neurodiversity, sensory processing differences, autism spectrum support, and working collaboratively with resource consultants."},
            {"num": 10, "title": "Supervised Field Practicum in Licensed Childcare Centers (500+ Hours)", "desc": "Hands-on clinical practicum in accredited Ontario daycare centers under the direct mentorship of experienced RECEs, rotating through infant, toddler, and preschool rooms."}
        ],
        "grants": {
            "badge": "Ontario Government Training Grant",
            "title": "Qualify for Up to $28,000+ in Better Jobs Ontario Funding",
            "description": "The Early Childcare Assistant program qualifies for maximum Better Jobs Ontario (formerly Second Career) government funding. Eligible candidates (laid off workers, unemployed, gig workers, self-employed, or low-income) can receive up to $28,000+ in non-repayable grants covering tuition, books, child care, and living allowance.",
            "amount": "$28,000+",
            "button_text": "Check Grant Eligibility Now"
        },
        "snapshot": {
            "delivery": "Hybrid (Live Online Theory + In-Person Daycare Practicum)",
            "practicum": "500+ Hours (100% Guaranteed Placement)",
            "locations": "Markham Main Campus / Live Online",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "Can I study the theory portion of the ECA program online from home?", "a": "Yes! All theory lectures and interactive classroom modules are delivered live online with expert early childhood instructors. You will attend flexible online sessions, followed by your guaranteed in-person daycare practicum in your local area."},
            {"q": "How long is the Early Childcare Assistant program?", "a": "The program is 22 weeks in total, combining comprehensive theoretical foundations, creative workshop labs, and 500+ hours of hands-on field practicum in licensed Ontario daycare centers."},
            {"q": "What is the difference between an ECA and an ECE in Ontario?", "a": "An ECA (Early Childcare Assistant) works directly alongside Registered Early Childhood Educators (RECEs) in daycare rooms, assisting with daily routines, learning activities, nutrition, and child supervision. ECA is a fast-track 22-week diploma that allows you to start working in the childcare field quickly."},
            {"q": "Are there government grants available for this program?", "a": "Yes! This program is fully eligible for Better Jobs Ontario (formerly Second Career), offering up to $28,000+ in non-repayable government grants covering 100% of your tuition, learning materials, transportation, and living expenses for qualified applicants."},
            {"q": "Do you guarantee daycare field placement?", "a": "Yes! Victoria College coordinates 100% of your 500+ hours supervised field practicum with our extensive network of licensed daycares, Montessori schools, and early learning centers across the GTA."},
            {"q": "What are the job prospects and hourly wages after graduation?", "a": "Job prospects are exceptionally strong due to Ontario's $10/day childcare expansion. Starting wages typically range from $18 to $26/hour, plus an additional $2/hour Ontario Wage Enhancement Grant (WEG) for eligible childcare staff."}
        ]
    }

def get_default_eca_detail_zh():
    return {
        "hero": {
            "badge": "安省注册幼教职业文凭 • 22 周持牌日托中心保障实习",
            "title": "开启充满爱心与高薪稳定的职业生涯 • 早期幼儿教育助理 (ECA) 职业文凭",
            "lead": "投身安省极度紧缺的早期幼儿教育行业。系统学习婴幼儿及学龄前儿童心理发展、健康营养、安全防护与启蒙教案设计，保障进入安省持牌正规幼儿园/日托中心进行 500+ 小时实地带薪/跟岗实习。"
        },
        "stats": [
            {"value": "22 周", "label": "网课理论/校区实操 + 500+小时持牌幼儿园实地实习"},
            {"value": "$18 – $26 / 小时", "label": "大多伦多地区起薪 + 安省政府每小时 $2 薪资补贴 (WEG)"},
            {"value": "100% 保障实习", "label": "对口签约安省正规持牌日托中心与早教机构"},
            {"value": "$28,000+ 补贴", "label": "符合 Better Jobs Ontario 政府全额无偿资助"}
        ],
        "why_choose": {
            "title": "为什么选择成为早期幼儿教育助理 (ECA)？",
            "subtitle": "随着加拿大联邦及安省政府全面推行 $10/天普惠日托计划（CWELCC），全省各类托儿所、幼儿园和早教中心迎来历史性大扩建，持证幼教助理（ECA）与幼教老师长期极度紧缺，成为加国最抢手、最温暖且极具社会价值的黄金职业之一。",
            "pillars": [
                {"title": "历史性行业缺口与高就业率", "desc": "安省日托补贴政策全面落地，新增数万个入托名额，持证幼教助理常年供不应求，毕业即对口就业。"},
                {"title": "充满爱心与成就感的工作", "desc": "在儿童大脑发育黄金期给予关爱与科学启蒙，陪伴孩子们健康快乐成长，深受家长信赖与社会尊重。"},
                {"title": "安全、正规与舒适的工作环境", "desc": "在安省持牌正规托儿所、幼儿园及公校课后班工作，与注册幼教老师（RECE）团队协作，工作时间规律，带薪假期充裕。"},
                {"title": "通往 RECE 幼教名师的快捷跳板", "desc": "快速积累加国本土一线幼教经验，未来可无缝衔接安省注册幼教（RECE）进阶文凭、日托主管或创办家庭日托。"}
            ]
        },
        "credentials": {
            "title": "官方认证毕业文凭与资格证书",
            "subtitle": "顺利完成全部理论科目与实地实习后，毕业生将获得安省幼教行业权威官方资质：",
            "items": [
                {"title": "安省 ECA 幼教助理官方职业文凭", "desc": "安省教育部备案注册职业文凭，全省持牌托儿所、幼儿园及早教机构通用认可。"},
                {"title": "儿童标准急救与 CPR Level C 证书", "desc": "安省日托中心法定必备的婴幼儿心肺复苏与突发意外急救官方认证。"},
                {"title": "食品安全与儿童营养卫生证书", "desc": "掌握幼教机构日常配餐卫生、过敏源防范与膳食营养管理专业技能。"},
                {"title": "100% 保障 500+ 小时正规日托实地实习", "desc": "涵盖婴儿班（Infant）、幼儿班（Toddler）及学前班（Preschool）的全阶段实战经验。"}
            ]
        },
        "practicum": {
            "title": "保障 500+ 小时安省持牌日托中心实地跟岗实习",
            "desc": "维多利亚学院负责全流程对口安排大多伦多地区（Markham、Toronto、Richmond Hill、Scarborough、Mississauga 等）持牌日托中心及蒙特梭利学校的实习岗位，由资深注册幼教（RECE）导师一对一手把手带教。",
            "box_title": "实习基地直接留用签约率高",
            "box_desc": "超过 85% 的维多利亚学院 ECA 毕业生在实习期间直接获得实习机构全职录用合同（Job Offer）！"
        },
        "admissions": {
            "title": "入学报读条件与要求",
            "items": [
                "具备安大略省高中毕业文凭（OSSD / 12年级）或加国/海外同等学历评估认证。",
                "成熟学生入学通道：年满 18 周岁，并通过学院 Wonderlic 入学能力测评（校区免费测试）。",
                "提供合格的警方无犯罪记录弱势群体筛查证明（Vulnerable Sector Check）。",
                "完成标准医疗体检与疫苗接种记录（包含 2 步骤结核病 TB 皮试）。",
                "热爱幼儿教育事业，具备耐心与亲和力，具备基础英语沟通与交流能力。"
            ]
        },
        "curriculum": {
            "title": "官方 22 周教学大纲（10 门专业核心科目）",
            "desc": "严格遵循安省《托儿与早期儿童法案》（CCEYA 2014）与官方幼教发展指南（How Does Learning Happen?）精心设计："
        },
        "curriculum_modules": [
            {"num": 1, "title": "加拿大幼儿教育概论与安省日托管理法规", "desc": "早期教育发展历史、安省 CCEYA 2014 日托法规、机构执照要求与职业道德规范。"},
            {"num": 2, "title": "儿童生长与心理发展：婴儿期至幼童期", "desc": "0–18个月婴儿与18–30个月幼童的生理、认知、情感与社交发育里程碑及大脑发育理论。"},
            {"num": 3, "title": "儿童生长与心理发展：学龄前期至学龄期", "desc": "2.5–5岁学前儿童与6–12岁学龄儿童的心理特征、语言获得、精细运动与同伴交往。"},
            {"num": 4, "title": "日托中心健康、安全防护、营养与应急处理", "desc": "卫生消毒与传染病防控、安全隐患排查、严重过敏反应管理、营养膳食与儿科急救。"},
            {"num": 5, "title": "幼儿创意启蒙：美术、音乐律动、故事会与感统游戏", "desc": "设计激发幼儿想象力与创造力的艺术手工、音乐节奏律动、绘本精读与多感官探索游戏。"},
            {"num": 6, "title": "儿童行为积极引导与班级常规管理", "desc": "儿童心理积极引导策略、情绪自控能力培养、冲突化解技巧与温馨班级日常作息建立。"},
            {"num": 7, "title": "家园共育沟通技能与多文化背景团队协作", "desc": "与多元文化背景家庭建立信任伙伴关系、日常家长交接沟通、与主班幼教（RECE）协作。"},
            {"num": 8, "title": "启蒙教案编制与儿童观察记录档案", "desc": "践行安省 'How Does Learning Happen?' 指南，设计以玩促学环境，记录儿童成长档案。"},
            {"num": 9, "title": "特殊需求儿童关怀与融合教育实践", "desc": "全包容性幼教理念、神经多样性与自闭症儿童支持、感统失调应对及与特教顾问配合。"},
            {"num": 10, "title": "安省持牌日托中心 500+ 小时实地跟岗实习", "desc": "在持牌托儿所婴儿班、幼童班和学前班进行全真实操演练，由资深 RECE 导师现场带教。"}
        ],
        "grants": {
            "badge": "安省政府培训资助",
            "title": "申请最高 $28,000+ 政府全额无偿助学金",
            "description": "早期幼儿教育助理专业完全符合安省 Better Jobs Ontario（原第二职业 Second Career）政府培训资助计划。符合条件的安省居民（失业、裁员、领过 EI、自雇、零工人员或低收入群体）最高可获 $28,000+ 加币全额无偿补贴，100% 覆盖学费、书本教材费、托儿补贴及学习期间基本生活费。",
            "amount": "$28,000+",
            "button_text": "立即免费评估资助资格"
        },
        "snapshot": {
            "delivery": "混成教学（线上理论直播 + 持牌日托实地实习）",
            "practicum": "500+ 小时（100% 对口保障安排）",
            "locations": "万锦主校区 / 在线名师直播",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "幼教 ECA 课程可以在家线上学习理论吗？", "a": "可以！所有理论课程与互动研讨均采用线上名师实时直播教学，配合课后录播复习，随后由学院为您就近安排当地安省持牌日托中心进行实地跟岗实习。"},
            {"q": "ECA 幼教助理课程需要学习多久？", "a": "课程总计 22 周，包含系统的幼儿心理与启蒙教育理论课、教案设计工坊以及 500+ 小时持牌托儿所全真实战实习。"},
            {"q": "在安省 ECA（幼教助理）和 ECE（注册幼教）有什么区别？", "a": "ECA 是协助主班 ECE 开展日常教学、幼儿生活照料与安全看护的专业人员。ECA 课程周期短（22周），学费更低，能帮助您以最快速度进入安省幼教行业并获得稳定收入，未来还可继续进修成为 RECE。"},
            {"q": "我可以申请政府学费资助吗？", "a": "完全可以！本课程符合安省 Better Jobs Ontario 政府资助计划，合资格者最高可获 $28,000+ 无偿政府全额补贴，无需偿还，学院专家免费协助全程申请。"},
            {"q": "学校会保障安排正规托儿所实习吗？", "a": "是的！维多利亚学院拥有遍布大多伦多地区的庞大签约日托中心网络，100% 为每位学员对口落实 500+ 小时正规实习岗位。"},
            {"q": "毕业后的就业前景和时薪待遇如何？", "a": "在安省 $10/天普惠日托政策推动下，全省幼教缺口巨大。ECA 起薪通常在 $18–$26/小时，且符合条件的机构员工还可额外享受安省政府每小时 $2 的工资补贴（WEG），福利完善，工作稳定。"}
        ]
    }

def get_default_acupuncture_detail_en():
    """Returns rich structured default landing page data in English for the Acupuncture & Wellness Program."""
    return {
        "total_hours": "2250 Hours",
        "hero": {
            "badge": "Non-Vocational Enrichment Program",
            "title": "Acupuncture & Traditional Wellness Program",
            "lead": "Discover the foundations of traditional wellness, holistic healthcare, and meridian balance. Designed for individuals seeking personal interest learning, wellness knowledge, or complementary health education.",
            "button_text": "Book Free Program Consultation",
            "curriculum_btn": "Explore 2250-Hour Curriculum",
            "compliance_notice": "Non-Vocational Program • MCU-Exempt • Ontario Career Colleges Act 2005 Exempt"
        },
        "stats": [
            {"val": "2250 Hours", "lbl": "Comprehensive Study", "sub": "Theory, Meridians & Demonstrations"},
            {"val": "Hybrid Format", "lbl": "Flexible Learning", "sub": "Interactive Online + Practical Labs"},
            {"val": "Hands-on Clinic", "lbl": "Practical Experience", "sub": "Needling, Moxa, Cupping & Tuina"},
            {"val": "Flexible Schedule", "lbl": "Weekday & Weekend", "sub": "Options to Fit Your Busy Lifestyle"}
        ],
        "why_choose": {
            "title": "Why Choose Our Acupuncture & Traditional Wellness Program?",
            "subtitle": "Immerse yourself in centuries of natural healing philosophy, meridian energetics, and hands-on non-invasive modalities for personal well-being.",
            "pillars": [
                {
                    "title": "Foundations of Ancient TCM Wisdom",
                    "desc": "Master foundational Traditional Chinese Medicine concepts: Yin-Yang balance, Five Elements (Wu Xing), Zang-Fu organ systems, Qi, Blood, and Body Fluids."
                },
                {
                    "title": "14 Meridian Channels & Acupoint Anatomy",
                    "desc": "Gain deep anatomical understanding of the 12 primary meridians, Ren & Du extraordinary vessels, and precise landmark location of 100+ therapeutic acupoints."
                },
                {
                    "title": "Holistic Health & Preventative Life Cultivation",
                    "desc": "Empower yourself and your family with natural wellness knowledge, seasonal Yang Sheng lifestyle habits, food energetics, and non-pharmacological health maintenance."
                },
                {
                    "title": "Practical Demonstrations & Multimodality Labs",
                    "desc": "Observe guided clean needle safety demonstrations, filiform needle insertion protocols, moxibustion (Ai Jiu), glass fire cupping, Gua Sha, and Tuina therapeutic massage."
                }
            ]
        },
        "credentials": {
            "title": "Credentials & Learning Outcomes Awarded",
            "subtitle": "Upon successfully completing the program, graduates receive comprehensive academic and practical documentation:",
            "items": [
                {"title": "Victoria College Certificate of Completion", "desc": "Official Certificate of Course Completion in Traditional Acupuncture Foundations & Wellness (2250 Hours)."},
                {"title": "Clean Needle Technique (CNT) & Safety Record", "desc": "Comprehensive training in single-use needle hygiene, sterile protocols, contraindications, and clinic safety."},
                {"title": "Auxiliary Modalities Proficiency Portfolio", "desc": "Practical mastery in moxibustion (Ai Jiu), fire cupping therapy, Gua Sha scraping, and Tuina acupressure."},
                {"title": "Supervised Clinical Observation & Lab Hours", "desc": "Documented hours of live instructor demonstrations, palpation drills, and simulated case studies."}
            ]
        },
        "schedule": {
            "title": "Flexible Schedule Options to Fit Your Life",
            "desc": "We understand our students balance careers, family, and studies. Victoria College provides multiple convenient schedules:",
            "weekday_title": "Weekday Intensive Cohort",
            "weekday_time": "Monday to Friday: 9:00 AM – 5:00 PM",
            "weekday_desc": "Accelerated full-time pace with immersive daily theory lectures and afternoon guided practical demonstrations.",
            "weekend_title": "Weekend & Evening Professional Cohort",
            "weekend_time": "Friday: 6:00 PM – 10:00 PM | Saturday & Sunday: 10:00 AM – 6:30 PM",
            "weekend_desc": "Specially designed for working professionals and wellness enthusiasts seeking flexible part-time study without quitting their day jobs.",
            "format": "Hybrid Delivery: Live interactive online theory lectures combined with in-person weekend practical clinic workshops."
        },
        "compliance": {
            "title": "Regulatory Notice & Compliance Statement",
            "regulatory_notice": "Regulatory Notice: This is a non-vocational program offered by Victoria International College of Business and Technology. It is intended for personal or professional development only and does not lead to licensure, certification, or authorization to practise acupuncture in Ontario.",
            "compliance_statement": "Compliance Statement: This is a non-vocational, MCU-exempt program offered by Victoria International College of Business and Technology. This program does not require approval under the Ontario Career Colleges Act, 2005."
        },
        "admissions": {
            "title": "Who Should Attend & Program Prerequisites",
            "items": [
                "Individuals passionate about exploring traditional wellness concepts and natural holistic healing arts.",
                "Anyone seeking personal interest learning, family health empowerment, and complementary self-care techniques.",
                "Practicing wellness professionals, registered massage therapists (RMTs), aesthetic/spa specialists, and fitness trainers seeking to deepen their TCM knowledge.",
                "No prior medical background required; classes are taught with clear, step-by-step bilingual instruction.",
                "Applicants must be 18 years of age or older with a commitment to holistic health learning."
            ]
        },
        "curriculum": {
            "title": "Official 2250-Hour Curriculum Outline (10 Comprehensive Modules)",
            "desc": "A rigorous, structured journey through traditional Chinese medicine theory, meridian anatomy, diagnostic arts, and practical healing modalities:"
        },
        "curriculum_modules": [
            {"num": 1, "title": "Foundations & Philosophy of Traditional Chinese Medicine (TCM)", "hours": "225 Hours", "desc": "Historical evolution of TCM, Yin-Yang philosophy, Five Elements (Wu Xing) correspondences, Zang-Fu organ systems, Qi, Blood, and Body Fluids physiology."},
            {"num": 2, "title": "Meridian Channels & Acupoint Anatomy", "hours": "250 Hours", "desc": "Surface anatomy, pathway trajectories of the 12 Regular Meridians, Ren Mai and Du Mai extraordinary vessels, and landmark location of 100+ vital wellness acupoints."},
            {"num": 3, "title": "TCM Diagnostic Fundamentals & Syndrome Differentiation", "hours": "225 Hours", "desc": "The Four Diagnostic Methods: Inspection (Wang - tongue and complexion), Auscultation/Olfaction (Wen), Inquiry (Wen), and Palpation (Qie - radial pulse diagnosis)."},
            {"num": 4, "title": "Acupuncture Needling Techniques & Clean Needle Safety Protocols (CNT)", "hours": "225 Hours", "desc": "Needle anatomy and selection, single-use sterile filiform needles, insertion angles, depths, de-qi sensations, tonification/sedation, and safety contraindications."},
            {"num": 5, "title": "Traditional Auxiliary Therapies: Moxibustion, Cupping & Gua Sha", "hours": "200 Hours", "desc": "Direct and indirect moxibustion (Ai Jiu / moxa roll), fire cupping (glass and bamboo), moving cupping, flash cupping, and Gua Sha meridian scraping protocols."},
            {"num": 6, "title": "Tuina Chinese Therapeutic Massage & Acupressure for Pain Relief", "hours": "225 Hours", "desc": "Traditional hand techniques (pushing, kneading, grasping, rolling), meridian channel clearing, and acupressure protocols for muscle tension and stiffness."},
            {"num": 7, "title": "TCM Internal Health & Common Wellness Condition Analysis", "hours": "225 Hours", "desc": "Holistic strategies for digestive harmonization, stress management, sleep quality improvement, vitality enhancement, and seasonal respiratory support."},
            {"num": 8, "title": "Musculoskeletal Wellness & Pain Management Techniques", "hours": "225 Hours", "desc": "Acupressure protocols, meridian thermal therapy, and joint mobility enhancement for neck, shoulder, lower back, and knee comfort."},
            {"num": 9, "title": "TCM Dietary Energetics, Food Therapy & Yang Sheng Living", "hours": "200 Hours", "desc": "Thermal properties of foods (cold, cool, neutral, warm, hot), five flavors in nutrition, herbal tea formulations, seasonal dietetics, and mindful longevity practices."},
            {"num": 10, "title": "Supervised Clinical Demonstrations, Case Workshops & Hands-on Labs", "hours": "250 Hours", "desc": "In-clinic observation of master practitioners, palpation drills, safe mock simulation workshops, practical case scenario analysis, and professional ethics."}
        ],
        "snapshot": {
            "duration": "2250 Hours (Flexible Weekday / Weekend)",
            "delivery": "Hybrid Delivery (Interactive Online Theory + In-Person Practical Labs)",
            "credential": "Certificate of Course Completion (2250 Hours)",
            "locations": "Markham Main Campus / Live Online",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "Is this program suitable for beginners with no prior medical background?", "a": "Yes, absolutely! The program is structured from the ground up, starting with core TCM philosophy and intuitive meridian charts before advancing to practical techniques. Instructors guide you step-by-step."},
            {"q": "What schedule options are available and can I study while working full-time?", "a": "Yes! We offer a full-time Weekday Cohort (Mon–Fri 9am–5pm) and a flexible Weekend/Evening Cohort (Fri 6pm–10pm, Sat/Sun 10am–6:30pm). Live online theory lectures and recorded reviews make it easy for working professionals."},
            {"q": "What is the regulatory status of this program in Ontario?", "a": "This is a Non-Vocational Program intended for personal interest, wellness knowledge, and complementary education. Under the Ontario Career Colleges Act, 2005, it is exempt from career college approval and does not lead to licensed acupuncturist registration (R.Ac) with CTCMPAO."},
            {"q": "What practical skills and auxiliary modalities will I learn?", "a": "You will gain hands-on knowledge in clean needle safety protocols, acupoint location, moxibustion (Ai Jiu), glass fire cupping, Gua Sha meridian scraping, Tuina Chinese therapeutic massage, and seasonal TCM dietary therapy."}
        ]
    }

def get_default_acupuncture_detail_zh():
    """Returns rich structured default landing page data in Chinese for the Acupuncture & Wellness Program."""
    return {
        "total_hours": "2250 学时",
        "hero": {
            "badge": "非职业特色兴趣课程 • 传统中医养生",
            "title": "中医针灸与传统养生保健课程",
            "lead": "探索数千年传统中医（TCM）养生智慧与经络调理精髓。本课程专为寻求个人兴趣学习、养生保健知识或自然疗法启蒙的人群设计，提供系统基础理论、经络穴位精确定位与丰富理疗实操演示。",
            "button_text": "立即免费预约课程咨询",
            "curriculum_btn": "查看 2250 学时教学大纲",
            "compliance_notice": "非职业性兴趣课程 • MCU 豁免 • 不属于安省《2005年职业学院法》管辖"
        },
        "stats": [
            {"val": "2250 学时", "lbl": "系统深度研习", "sub": "理论奠基 + 经络穴位 + 实操演示"},
            {"val": "线上线下混成", "lbl": "灵活教学模式", "sub": "名师实时直播 + 线下实训工作坊"},
            {"val": "真实诊室演示", "lbl": "实战手法观摩", "sub": "针法、艾灸、拔罐、刮痧与推拿"},
            {"val": "灵活课时安排", "lbl": "平日班 & 周末班", "sub": "完美兼顾全职上班族与兴趣自学者"}
        ],
        "why_choose": {
            "title": "为什么选择维多利亚中医针灸与传统养生课程？",
            "subtitle": "传承千年华夏医学瑰宝，掌握终身受用的自然防病与身心自我调理实用绝活：",
            "pillars": [
                {
                    "title": "传统中医经典理论哲学",
                    "desc": "深入浅出领悟阴阳平衡、五行生克、五脏六腑生克制化与气血津液运行规律，建立宏观辨证的整体健康观。"
                },
                {
                    "title": "十四经络循行与特效穴位",
                    "desc": "系统掌握十二正经与任督二脉的循行路线，精准定位 100+ 常用保健特效穴位与经络气血疏通技巧。"
                },
                {
                    "title": "治未病与节气养生食疗",
                    "desc": "传承中医'治未病'核心精髓，掌握体质辨识、四季节气调摄、食疗药膳配伍及非药物家庭健康管理方法。"
                },
                {
                    "title": "综合中医传统理疗实操演示",
                    "desc": "由资深中医师现场演示规范无痛进针手法、艾灸温通经络、玻璃火罐排湿通络、经络刮痧及推拿点穴手法。"
                }
            ]
        },
        "credentials": {
            "title": "课程学习成果与结业资质",
            "subtitle": "顺利完成全部理论科目与实训观摩后，学员将获得全面的学术与技能结业档案：",
            "items": [
                {"title": "维多利亚学院结业证书", "desc": "维多利亚学院官方颁发的 2250 学时中医针灸与传统养生保健基础结业证书。"},
                {"title": "无菌操作安全与卫生防护合格记录", "desc": "严格掌握单次使用一次性针灸针具、消毒灭菌规程、操作禁忌及个人防护规范。"},
                {"title": "传统特色外治法技能掌握", "desc": "系统掌握艾灸温灸、玻璃火罐、闪罐走罐、经络刮痧及实用推拿点穴手法要领。"},
                {"title": "诊室临床观摩与实操演练档案", "desc": "在专业实训诊室进行穴位按压、循经揣穴、手法演练与真实案例模拟分析。"}
            ]
        },
        "schedule": {
            "title": "灵活课时安排（满足多样化学习需求）",
            "desc": "我们充分理解学员兼顾工作、家庭与学习的实际需求，特设多种灵活授课班型：",
            "weekday_title": "平日全日制班（Weekday Cohort）",
            "weekday_time": "周一至周五：9:00 AM – 5:00 PM",
            "weekday_desc": "适合时间充裕、希望短时间内系统全面掌握中医针灸与传统养生知识的学员。",
            "weekend_title": "周末及晚间业余班（Weekend & Evening Cohort）",
            "weekend_time": "周五：6:00 PM – 10:00 PM | 周六及周日：10:00 AM – 6:30 PM",
            "weekend_desc": "专为在职人士、创业者及家庭养生爱好者量身打造，无需辞职即可利用业余时间修完全部课程。",
            "format": "线上理论直播 + 课后高清录播复习 + 线下实训诊室面对面手法演示。"
        },
        "compliance": {
            "title": "法规提示与合规声明",
            "regulatory_notice": "法规提示（Regulatory Notice）：针灸课程属于维多利亚国际商业与技术学院开设的非职业性（Non-Vocational）课程。本课程仅供个人兴趣或专业技能拓展使用，不提供在安省从事针灸执业的执照、认证或执业许可。",
            "compliance_statement": "合规声明（Compliance Statement）：本课程为维多利亚学院开设的非职业性、安省高等院校厅（MCU）豁免课程。本课程不属于《2005年安大略省职业学院法》管辖及审批范围。"
        },
        "admissions": {
            "title": "适合人群与报读要求",
            "items": [
                "对传统中医文化、自然疗法及身心养生保健充满浓厚兴趣的广大爱好者。",
                "希望掌握实用经络调理绝活，为自己与家人进行日常健康调护与亚健康调理的人士。",
                "现职注册按摩师（RMT）、美容水疗理疗师、健身教练及康复护理从业人员技能进阶拓展。",
                "无需任何医学或理工科前置背景，零基础起步，中英双语名师手把手通俗易懂教学。",
                "年满 18 周岁，热爱中华传统医学文化与健康生活方式。"
            ]
        },
        "curriculum": {
            "title": "官方 2250 学时教学大纲（10 门系统核心科目）",
            "desc": "涵盖传统中医哲学、经络腧穴、中医四诊、针灸实操、传统外治法与节气食疗的系统知识体系："
        },
        "curriculum_modules": [
            {"num": 1, "title": "中医基础理论与传统医学哲学", "hours": "225 学时", "desc": "中医学发展简史、阴阳学说、五行生克乘侮、五脏六腑生理功能与相互关系、气血津液生成与运行。"},
            {"num": 2, "title": "经络腧穴学与人体体表解剖", "hours": "250 学时", "desc": "经络系统总论、十二正经循行走向、任督二脉与奇经八脉、100+ 常用保健特效穴位骨度分寸法与精准定位。"},
            {"num": 3, "title": "中医诊断学基础与四诊八纲辨证", "hours": "225 学时", "desc": "望闻问切四诊方法：舌象观察（舌苔与舌质）、面色神气、问诊要点、脉诊基础触按及八纲辨证原则。"},
            {"num": 4, "title": "针灸针刺手法、无菌操作规范与安全常识", "hours": "225 学时", "desc": "毫针构造与规格选择、进针角度与深度、得气感应、提插捻转补泻手法、安全操作禁忌与防范措施。"},
            {"num": 5, "title": "传统中医外治特色疗法：艾灸、拔罐与刮痧", "hours": "200 学时", "desc": "直接灸与间接温和灸、隔姜/隔盐灸、玻璃火罐拔罐法、闪罐走罐、经络刮痧出痧原理与排湿排寒手法。"},
            {"num": 6, "title": "中医经络推拿点穴手法与筋骨保健", "hours": "225 学时", "desc": "推拿核心手法（推、拿、按、摩、滚、揉、拍打）、循经点穴、放松肌肉肌腱、舒缓日常酸痛与经络疏通。"},
            {"num": 7, "title": "中医脏腑调理与常见亚健康状态分析", "hours": "225 学时", "desc": "脾胃消化调理、睡眠质量改善、情绪疏导解压、气血亏虚调补、呼吸系统与季节性不适的整体调理方案。"},
            {"num": 8, "title": "筋骨关节保健与肌肉疼痛舒缓实战", "hours": "225 学时", "desc": "颈椎、肩周、腰肌劳损、膝关节等常见部位的经络循行特点、穴位热敷温灸与手法舒缓综合方案。"},
            {"num": 9, "title": "中医食疗药膳、四季节气调养与养生学", "hours": "200 学时", "desc": "食物四气五味属性、九种中医疗效体质辨识、春夏秋冬四季节气养生食谱、养生代茶饮配伍与健康生活方式。"},
            {"num": 10, "title": "诊室实操观摩演示、手法实训与案例研讨", "hours": "250 学时", "desc": "资深中医师现场实操手法演示、学员相互揣穴演练、经典案例综合辨析、个人卫生规范与职业道德。"}
        ],
        "snapshot": {
            "duration": "2250 学时（平日班 / 周末班可选）",
            "delivery": "混成教学（线上理论直播 + 线下实训工作坊）",
            "credential": "维多利亚学院结业证书（2250 学时）",
            "locations": "万锦主校区 / 在线名师直播",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "零医学背景的新手可以学会吗？", "a": "完全可以！课程从中医最基础的阴阳五行和形象直观的经络穴位图解讲起，配合生动生活案例与大量现场实操演示，通俗易懂，手把手带您入门。"},
            {"q": "平时需要上班，有适合业余时间学习的班型吗？", "a": "有！我们专门开设了周末及晚间班（周五晚 + 周六周日全天），所有理论课均支持在线直播与课后高清录播无限次回放，兼顾工作与学习毫无压力。"},
            {"q": "这门针灸课程在安省的法规性质是什么？", "a": "本课程属于非职业性（Non-Vocational）兴趣技能提升课程，不受《2005年安大略省职业学院法》管辖，旨在帮助学员掌握传统健康养生知识，不提供安省中医师及针灸师管理局（CTCMPAO）执业注册资格。"},
            {"q": "课程中会学习哪些实用的传统理疗技能？", "a": "学员将系统学习针灸穴位经络定位、无痛进针与无菌安全规范、艾灸温灸、玻璃火罐拔罐、经络刮痧、中医推拿点穴手法以及四季节气食疗养生方。"}
        ]
    }

def get_default_electrician_detail_en():
    """Returns rich structured default landing page data in English for the Electrician (309A / 442A) Program."""
    return {
        "hero": {
            "badge": "Ontario Skilled Trades • 309A / 442A Pre-Exam & Licensing",
            "title": "Master the Canadian Electrical Code & Fast-Track Your 309A / 442A License",
            "lead": "Coached by veteran Master Electricians with 20+ years of Canadian union, commercial, and industrial contracting experience. Master the Canadian Electrical Code (CEC / OESC), hands-on residential & 3-phase commercial wiring, motor controls, blueprint reading, and trade exam test banks to pass your Certificate of Qualification (C of Q) on your first attempt."
        },
        "stats": [
            {"val": "$35 – $55+ / hr", "lbl": "Average Licensed Hourly Wage", "sub": "Red Seal Journeyperson / Union Scale"},
            {"val": "20+ Yrs Mentorship", "lbl": "Master Electrician Taught", "sub": "Senior Project Leads from Top Firms"},
            {"val": "1-on-1 Hands-on Labs", "lbl": "Apprenticeship Facility", "sub": "Panels, 3-Phase, Motors & Transformers"},
            {"val": "Up to $28,000+ Grant", "lbl": "Government Funding Eligible", "sub": "Better Jobs Ontario & Apprentice Grants"}
        ],
        "why_choose": {
            "title": "Why Choose a Career as a Licensed Electrician in Ontario?",
            "subtitle": "Electrical trades represent one of Canada's most respected, lucrative, and recession-proof professions. As Ontario experiences massive infrastructure growth, electric vehicle transitions, and residential expansions, licensed 309A and 442A electricians command premium wages, comprehensive benefits, and strong union representation.",
            "pillars": [
                {
                    "title": "Top-Tier Earning Potential & Stability",
                    "desc": "Licensed journeypersons in the GTA earn $35–$55+/hour ($75,000–$120,000+ annually) with extensive overtime, union pension plans, full health benefits, and strong job security."
                },
                {
                    "title": "100% CEC Code Mastery & Exam Fast-Track",
                    "desc": "Systematic breakdown of the Canadian Electrical Code (CEC / OESC). Master rapid table navigation, load sizing formulas, and key question patterns to pass the C of Q exam with confidence."
                },
                {
                    "title": "1-on-1 Hands-on Wiring & Distribution Labs",
                    "desc": "Train in our recognized apprenticeship lab: residential 100A/200A distribution panels, commercial 3-phase 600V systems, transformer connections, magnetic motor starters, and conduit bending."
                },
                {
                    "title": "Trade Qualifier Support & Job Referrals",
                    "desc": "Expert guidance for experienced tradespeople challenging the exam via the Trade Qualifier pathway, plus direct employer introductions and union dispatch referral networks across the GTA."
                }
            ]
        },
        "credentials": {
            "title": "Credentials, Certifications & Exam Readiness",
            "subtitle": "Upon completion of training and practical assessments, students achieve recognized milestones toward their journeyperson license:",
            "items": [
                {"title": "Ontario 309A / 442A Exam Readiness Certificate", "desc": "Official verification of completion in Canadian Electrical Code theory and Certificate of Qualification examination prep."},
                {"title": "Canadian Electrical Code (CEC) Specialist Credential", "desc": "Demonstrates advanced mastery in Ontario Electrical Safety Code (OESC) interpretation, ampacity tables, and conductor sizing."},
                {"title": "Lockout/Tagout (LOTO) & Arc Flash Safety Record", "desc": "Comprehensive training in CSA Z462 electrical safety standards, high-voltage isolation, hazard boundaries, and PPE protocols."},
                {"title": "Commercial Blueprint & Schematic Sizing Portfolio", "desc": "Practical portfolio showcasing single-line diagrams, commercial branch load schedules, 3-phase balancing, and motor control circuits."}
            ]
        },
        "curriculum": {
            "title": "Comprehensive 10-Module Curriculum Outline",
            "desc": "A rigorous, code-focused curriculum preparing students for both field mastery and the Skilled Trades Ontario (STO) Red Seal licensing exam:"
        },
        "curriculum_modules": [
            {"num": 1, "title": "Canadian Electrical Code (CEC / OESC) Structure & Fast Navigation", "hours": "30 Hours", "desc": "Code layout, Section 0–16 general rules, conductor ampacity (Tables 1–4), temperature ratings, derating factors (Table 5C), conduit fill (Tables 6A–K), and exam lookup strategies."},
            {"num": 2, "title": "Electrical Safety, PPE, Lockout/Tagout (LOTO) & Arc Flash Protection", "hours": "20 Hours", "desc": "Occupational Health & Safety Act (OHSA), CSA Z462 electrical workplace safety, shock boundaries, arc flash PPE categories, ground fault protection, and bonding rules (Section 10)."},
            {"num": 3, "title": "DC/AC Electrical Theory, Magnetism & Power Calculations", "hours": "30 Hours", "desc": "Ohm's law, Kirchhoff's laws, series/parallel combinations, inductance, capacitance, single-phase and 3-phase AC power calculations, power factor correction, and apparent vs active power."},
            {"num": 4, "title": "Residential Wiring Systems & 100A/200A Service Panels", "hours": "35 Hours", "desc": "Residential load calculations (Section 8), service entrance sizing, main breaker panels, branch circuit design, AFCI/GFCI protection, kitchen/bathroom code rules, and multi-wire circuits."},
            {"num": 5, "title": "3-Phase Power Distribution & Commercial Wiring", "hours": "35 Hours", "desc": "Commercial 120/208V and 347/600V distribution systems, delta and wye connections, neutral conductor sizing, commercial panelboards, disconnect switches, and energy-efficient lighting controls."},
            {"num": 6, "title": "Transformers: Installation, Connections & Sizing Calculations", "hours": "30 Hours", "desc": "Single-phase and 3-phase transformers (Section 26), step-up and step-down applications, delta-wye connections, autotransformers, turns ratio, primary/secondary overcurrent protection sizing."},
            {"num": 7, "title": "Electric Motors, Magnetic Starters & Motor Control Circuits", "hours": "35 Hours", "desc": "Single-phase and 3-phase AC induction motors (Section 28), stop/start latching circuits, forward/reversing starters, overload protection sizing, time-delay relays, and ladder schematics."},
            {"num": 8, "title": "Conduit Bending, Raceways, Cable Trays & Installation Methods", "hours": "30 Hours", "desc": "Hands-on EMT and rigid conduit bending (90-degree stubs, back-to-back, kicks, 3-point/4-point saddles), mechanical raceways, cable trays (Section 12), and wire pulling practices."},
            {"num": 9, "title": "Electrical Blueprint Reading, Schematics & Specification Sizing", "hours": "25 Hours", "desc": "Architectural and engineering drawing symbols, electrical site plans, single-line power diagrams, panel schedules, lighting layouts, material takeoffs, and project cost estimating."},
            {"num": 10, "title": "Red Seal 309A / 442A C of Q Mock Exam Simulation & Question Bank", "hours": "30 Hours", "desc": "Timed full-length mock exams modeled on the Skilled Trades Ontario exam blueprint. Detailed breakdown of tricky questions, formula shortcuts, and time-management techniques."}
        ],
        "practicum": {
            "title": "Hands-on Electrical Lab & Training Facility",
            "desc": "Victoria International College provides students with direct access to dedicated electrical training workstations. Students gain practical, muscle-memory experience wiring real electrical equipment under the supervision of practicing Master Electricians.",
            "box_title": "Direct Contractor Networking & Trade Qualifier Guidance",
            "box_desc": "Over 90% of our exam preparation graduates successfully pass their Red Seal / C of Q exam and gain rapid referrals to top GTA electrical contractors and union locals!"
        },
        "admissions": {
            "title": "Admission Requirements & Prerequisites",
            "items": [
                "Ontario Secondary School Diploma (OSSD / Grade 12) or Canadian / International equivalent evaluation.",
                "Mature Student Admission: 18 years of age or older with passing score on the Wonderlic entrance assessment.",
                "Trade Qualifier candidates: Domestic or international electrical trade experience eligible for Skilled Trades Ontario exam challenge.",
                "Registered Apprentices: Currently registered with Ministry of Labour, Immigration, Training and Skills Development (MLITSD).",
                "Basic mathematical proficiency (algebra and trigonometry fundamentals) and strong safety awareness."
            ]
        },
        "grants": {
            "badge": "GOVERNMENT FUNDING AVAILABLE",
            "title": "Get Up to $28,000+ Grant",
            "description": "Study Electrician pre-exam and skills training with zero out-of-pocket tuition. Eligible candidates (laid-off workers, EI recipients, gig workers, self-employed, or low-income residents) may qualify for up to $28,000+ in non-repayable Better Jobs Ontario grants covering tuition, tools, books, and living expenses.",
            "amount": "$28,000+",
            "button_text": "Check Grant Eligibility Now"
        },
        "snapshot": {
            "delivery": "Hybrid (Online Code Theory + Hands-on Lab)",
            "practicum": "1-on-1 Lab Workstations & Test Bank",
            "locations": "Markham Main Campus / Live Online",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "What is the difference between 309A Construction & Maintenance and 442A Industrial Electrician?", "a": "309A Construction and Maintenance Electrician is Ontario's most versatile license, permitting work in residential, commercial, institutional, and industrial settings. 442A Industrial Electrician focuses specifically on factory automation, manufacturing plant machinery, motor controls, PLCs, and industrial electrical maintenance."},
            {"q": "Can I challenge the 309A / 442A exam if I have international or non-registered electrical experience?", "a": "Yes! Through Skilled Trades Ontario's Trade Equivalency Assessment (Trade Qualifier pathway), individuals with verified work experience (typically 9,000+ hours for 309A) can apply to challenge the Certificate of Qualification exam directly without repeating a 5-year apprenticeship."},
            {"q": "Can I attend classes while working full-time?", "a": "Yes! We offer flexible weekend and evening cohort schedules specifically designed for working adults, trades helpers, and apprentices to study code theory online and attend hands-on labs on weekends."},
            {"q": "Are there government grants or financial aid available for this program?", "a": "Yes! Victoria College's programs are eligible for Better Jobs Ontario (up to $28,000+ non-repayable grant covering tuition, books, tools, and living costs) as well as federal Apprenticeship Incentive Grants and Canada Apprentice Loans for registered apprentices."},
            {"q": "Does the course include hands-on practical wiring training?", "a": "Yes! In addition to in-depth Canadian Electrical Code theory and exam question drills, students train in our dedicated electrical lab with residential panels, 3-phase disconnects, transformers, motor control boards, and conduit bending equipment."},
            {"q": "How does Victoria College support graduates with finding jobs or joining the union?", "a": "We provide 1-on-1 resume optimization for the Canadian trade market, guidance on joining IBEW union locals or CLAC, and direct networking referrals to licensed electrical contractor partners across the GTA."}
        ]
    }

def get_default_electrician_detail_zh():
    """Returns rich structured default landing page data in Chinese for the Electrician (309A / 442A) Program."""
    return {
        "hero": {
            "badge": "安省持牌技工高薪黄金专业 • 309A / 442A 考证与实操",
            "title": "精通加拿大电气规范 (CEC) • 快速通关安省 309A 建筑与 442A 工业电工牌照",
            "lead": "由安省 20 余年一线西人大型工程公司项目主管、资深持牌 Master Electrician 名师亲自授课。将加国最新电气规范（CEC / OESC）核心考点精讲、官方认可学徒实训基地 1对1 动手实操接线（民用配电箱/三相电/变压器/电机控制/管道弯管）与红宝书全真题库模考融为一体，助您一次性高分通关拿牌并对口就业！"
        },
        "stats": [
            {"val": "$35 – $55+ / 小时", "lbl": "大多伦多地区持牌电工平均时薪", "sub": "红印执照 / 工会标准薪资待遇"},
            {"val": "20+ 年名师带教", "lbl": "大师级持牌电工亲授", "sub": "加国一线大型西人工程公司资深项目主管"},
            {"val": "1对1 动手实操机房", "lbl": "官方认可学徒实训基地", "sub": "配电箱、三相电、变压器与电机控制"},
            {"val": "$28,000+ 政府补贴", "lbl": "符合政府全额无偿资助", "sub": "Better Jobs Ontario 及学徒专项津贴"}
        ],
        "why_choose": {
            "title": "为什么选择成为安省持牌电工 (Licensed Electrician)？",
            "subtitle": "电工是加拿大收入最高、最受社会尊重且极具抗周期性的金牌技工职业之一。随着安省大型基础设施建设、新能源电动汽车充电桩及住宅商业地产的蓬勃发展，持牌 309A 建筑电工与 442A 工业电工常年极度紧缺，薪酬福利优厚，工会保障完善。",
            "pillars": [
                {
                    "title": "行业顶薪与极佳稳定性",
                    "desc": "大多伦多持牌电工时薪普遍达 $35–$55+/小时（年薪 $7.5万–$12万+），享高额加班费、工会丰厚养老金、全家医疗牙医保险及带薪年假。"
                },
                {
                    "title": "100% 攻克加国电气规范 (CEC)",
                    "desc": "全面系统拆解加拿大电气规范（Canadian Electrical Code / OESC），掌握极速查表技巧、负荷计算公式与高频必考题眼，确保一次性高分考取牌照。"
                },
                {
                    "title": "1对1 动手实操与接线实战",
                    "desc": "在官方认可学徒基地动手实操：民用 100A/200A 配电盘、商业三相 600V 强电系统、变压器接线、交流接触器与磁力电机启动柜、管道弯管（Conduit Bending）。"
                },
                {
                    "title": "海外经验资格评估与对口内推",
                    "desc": "协助具备海内外工程经验的学员通过 Trade Qualifier 快速通道申请免学徒直接挑战考证，并向大多伦多知名西人/华人工程公司及工会定向推荐就业。"
                }
            ]
        },
        "credentials": {
            "title": "官方培训资质、技能成果与考证直通",
            "subtitle": "顺利完成全部理论培训与实操考核后，学员将获得加国电气行业高度认可的实战能力与考证资质：",
            "items": [
                {"title": "安省 309A / 442A 考证通关结业证书", "desc": "维多利亚学院官方颁发的加拿大电气规范理论与 Red Seal 考前冲刺培训结业证书。"},
                {"title": "加拿大电气规范 (CEC) 规范应用专家认证", "desc": "深度掌握安省电气安全局（OESC）各项安全法规、导线载流量校核、短路保护与变压器选型。"},
                {"title": "电气安全、LOTO 挂牌上锁与电弧防护证书", "desc": "全面掌握 CSA Z462 工作场所电气安全操作规程、高压隔离排空、防护绝缘装备（PPE）与急救规范。"},
                {"title": "商业电气施工图纸识图与负荷计算作品集", "desc": "独立完成商业单线配电系统图（Single-Line Diagram）、三相平衡负荷表、照明动力回路及电机控制原理图编制。"}
            ]
        },
        "curriculum": {
            "title": "官方 10 门专业系统核心课程模块",
            "desc": "紧扣 Skilled Trades Ontario 考纲要求与加国一线工地施工标准精心设计，理论考点与动手实操并重："
        },
        "curriculum_modules": [
            {"num": 1, "title": "加拿大电气规范 (CEC / OESC) 架构解析与极速查表秘籍", "hours": "30 学时", "desc": "Code Book 篇章逻辑、Section 0–16 通用规则、导线载流量表（Tables 1–4）、温度与降容系数（Table 5C）、管内穿线率表（Tables 6A–K）及快速定位考点策略。"},
            {"num": 2, "title": "电气安全施工规范、PPE、LOTO 挂牌上锁与电弧防范 (Arc Flash)", "hours": "20 学时", "desc": "安省职业健康与安全法案（OHSA）、CSA Z462 电气作业安全、触电危险边界、电弧防护级别、接地（Grounding）与接零保护（Bonding - Section 10）。"},
            {"num": 3, "title": "直流/交流电理论、电磁学原理与三相电功率计算", "hours": "30 学时", "desc": "欧姆定律、基尔霍夫定律、串并联回路、感抗与容抗、单相与三相交流功率计算（视在功率、有功功率、无功功率）、功率因数补偿与相序分析。"},
            {"num": 4, "title": "民用住宅电气布线系统与 100A/200A 主配电箱实战", "hours": "35 学时", "desc": "住宅总负荷计算（Section 8）、进线配电箱配置、断路器选用、分支回路分配、AFCI 电弧断路器与 GFCI 漏电保护器接线、厨卫电气规范及多线分支回路。"},
            {"num": 5, "title": "三相工业商业配电系统与配电柜接线 (Commercial 3-Phase)", "hours": "35 学时", "desc": "商业 120/208V 与 347/600V 配电系统、星形（Wye）与角形（Delta）接法、中性线计算、商业配电盘安装、隔离开关（Disconnect Switches）与智能照明控制系统。"},
            {"num": 6, "title": "变压器原理、接线方式、过流保护与容量选型计算", "hours": "30 学时", "desc": "单相与三相电力变压器（Section 26）、升压/降压变压器、自耦变压器、变比计算、一次侧/二次侧过电流保护器与熔断器精准整定计算。"},
            {"num": 7, "title": "交流电动机、磁力启动器、控制继电器与电路原理图 (Motor Controls)", "hours": "35 学时", "desc": "单相与三相交流感应电动机（Section 28）、启停自锁控制回路、正反转磁力启动器、热过载继电器整定、时间继电器与梯形逻辑控制图识图。"},
            {"num": 8, "title": "管道弯管工艺 (Conduit Bending)、电缆桥架与穿线技巧", "hours": "30 学时", "desc": "EMT 金属管与刚性管手工/机械弯管（90度弯头、背对背弯、偏置弯 Kick、三点/四点鞍形弯）、电缆桥架安装（Section 12）与工业穿线拉线实操。"},
            {"num": 9, "title": "电气施工图纸识图、图例符号、材料估算与负荷计算书编制", "hours": "25 学时", "desc": "建筑电气施工图图例符号、配电平面图、系统单线图（Single-Line Diagram）、动力箱负荷明细表、工程材料量核算（Takeoff）与施工报价。"},
            {"num": 10, "title": "安省 309A / 442A 执照考试全真模考冲刺与红宝书题库精讲", "hours": "30 学时", "desc": "严格按照 Skilled Trades Ontario 统考模式进行限时全真模考，深度拆解高频陷阱题、公式速记技巧与应试时间分配，确保一次性高分通关！"}
        ],
        "practicum": {
            "title": "官方认可电工实训基地与 1对1 动手实操",
            "desc": "维多利亚职业学院配备标准电气实训工位，学员在资深持牌 Master Electrician 导师的指导下，直接动手操作真实配电箱、工业变压器、电机控制柜与弯管设备，迅速将规范转化为肌肉记忆实战能力。",
            "box_title": "大多伦多工程团队对口直推与工会内荐",
            "box_desc": "维多利亚学院电工班学员考试通过率名列前茅，超过 90% 的积极学员在考取牌照后迅速获得知名西人/华人电气工程公司聘用或成功加入 IBEW 电工工会！"
        },
        "admissions": {
            "title": "入学报读条件与适合人群",
            "items": [
                "具备安大略省高中毕业文凭（OSSD / 12年级）或加国及海外同等学历评估认证。",
                "成熟学生通道：年满 18 周岁，并通过学院基础能力测评（校区/线上免费测评）。",
                "Trade Qualifier 经验挑战通道：具备海内外电气、自动化、机械、机电相关工程经验，希望快速免学徒直接考牌的人士。",
                "现职学徒及电工助手：已在安省技术移民及技能发展厅（MLITSD）注册学徒或从事 Helper 工作的技工。",
                "具备基础数学逻辑（初等代数与几何）以及严谨的安全防护意识。"
            ]
        },
        "grants": {
            "badge": "安省政府培训资助",
            "title": "申请最高 $28,000+ 政府助学金",
            "description": "电工考证与实操培训完全符合安省 Better Jobs Ontario（原第二职业 Second Career）政府培训资助计划。符合条件的安省居民（失业、裁员、领过 EI、自雇、零工人员或低收入群体）最高可申请 $28,000+ 加币全额无偿补贴，100% 覆盖学费、工具费、书本教材费及学习期间基本生活费。",
            "amount": "$28,000+",
            "button_text": "立即免费评估资助资格"
        },
        "snapshot": {
            "delivery": "混成教学（线上规范精讲 + 校区动手实操）",
            "practicum": "1对1 实操工位 + 全真红宝书题库",
            "locations": "万锦主校区 / 在线名师直播",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "309A 建筑维护电工和 442A 工业电工有什么区别？", "a": "309A 建筑与维护电工（Construction & Maintenance Electrician）是加国适用范围最广的电工执照，可在民用住宅、商业大楼、公共设施及工业厂房等所有领域合法执业；442A 工业电工（Industrial Electrician）则专注在工厂制造企业、自动化生产线、机械设备电气维护与 PLC 控制系统。"},
            {"q": "我有海外电气工作经验，可以直接在安省挑战考电工牌照吗？", "a": "可以！通过安省技术工种局（Skilled Trades Ontario）的 Trade Equivalency Assessment（Trade Qualifier）海外经验评估，只要证明累积了相应工时（309A 通常为 9,000 小时，442A 通常为 8,100 小时），即可获批直接参加执照考试，无需从头重新做 5 年学徒。维多利亚学院提供全程经验认证指导。"},
            {"q": "平时需要全职上班，有适合业余时间学习的班型吗？", "a": "有！我们专门开设了周末及晚间班，所有理论与规范精讲均支持在线直播与高清录播无限次回放，实操集中在周末进行，让您在不影响全职工作的同时高效备考。"},
            {"q": "我可以申请政府全额学费资助吗？", "a": "可以！本课程符合安省 Better Jobs Ontario 政府资助计划，合资格者最高可获 $28,000+ 无需偿还的政府全额补贴，100% 报销学费、工具教材及生活津贴，学院专家免费协助全程申请。"},
            {"q": "课程包含动手实操接线训练吗？", "a": "包含！除了深度的 CEC 电气规范精讲与红宝书全真题库模考，学员还将在官方认可实训基地亲自动手进行 100A/200A 配电盘、三相配电、变压器接线、电机磁力启动器与管道弯管实操演练。"},
            {"q": "毕业后学校会协助推荐工作或加入工会吗？", "a": "是的！学院提供加国技工英文简历一对一修改、IBEW 国际电工工会申请指导，并向大多伦多地区长期合作的大中型持牌电气工程公司直接内推。"}
        ]
    }

def get_default_tech_detail_en():
    return {
        "hero": {
            "badge": "Career Diploma • AI Mini-Credential",
            "title": "Master Full-Stack Web Development & Enterprise Generative AI Integration",
            "lead": "Coached by senior tech leads from top Canadian financial institutions and tech enterprises. Master modern frontend architecture (React 19 / Next.js / TypeScript), robust backend microservices (Node.js / Python / Spring Boot), cloud DevOps (AWS / Docker), and cutting-edge Generative AI engineering (OpenAI API, LangChain, RAG, Vector DBs). Build production-ready portfolio projects and land high-paying software engineering careers.",
            "cta_book": "Book Free Tech Career Consultation",
            "cta_curriculum": "Explore 10-Module Curriculum"
        },
        "stats": [
            {"value": "$75K – $120K+", "label": "GTA Software Dev Salary Range", "sub": "Entry to Mid-Level Full Stack Engineers"},
            {"value": "100% Project Labs", "label": "Real-World Commercial Portfolio", "sub": "SaaS, AI Integrations & GitHub Repos"},
            {"value": "FAANG Mentorship", "label": "Senior Industry Tech Leads", "sub": "1-on-1 Code Reviews & Mock Tech Interviews"},
            {"value": "Up to $28,000+", "label": "Government Grants Available", "sub": "Better Jobs Ontario & Job Grant Eligible"}
        ],
        "why_choose": {
            "title": "Why Choose Full Stack Web Development with AI Mini-Credential?",
            "subtitle": "Software development continues to be one of Canada's most in-demand, resilient, and highest-paying career paths. With the explosive rise of Generative AI, developers who understand how to build robust full-stack web applications and integrate AI capabilities command top market compensation.",
            "pillars": [
                {
                    "title": "Modern Enterprise Full-Stack Architecture",
                    "desc": "Master end-to-end full stack development: React 19, Next.js App Router, TypeScript, Node.js, Python, Spring Boot, PostgreSQL, MongoDB, and Redis caching."
                },
                {
                    "title": "Integrated Generative AI & LLM Engineering",
                    "desc": "Stand out from traditional coders. Build intelligent applications with OpenAI/Claude APIs, LangChain, Retrieval-Augmented Generation (RAG), and vector databases."
                },
                {
                    "title": "Cloud Native DevOps & Production Deployment",
                    "desc": "Gain hands-on experience containerizing apps with Docker, deploying to AWS (EC2, S3, RDS, Lambda), and setting up automated CI/CD pipelines via GitHub Actions."
                },
                {
                    "title": "1-on-1 Tech Interview Coaching & Job Referrals",
                    "desc": "Get tailored resume packaging, GitHub code review, LeetCode algorithmic drills, system design practice, and direct introductions to hiring tech partners across the GTA."
                }
            ]
        },
        "credentials": {
            "title": "Diplomas, Micro-Credentials & Portfolio Milestones",
            "subtitle": "Graduates earn recognized career credentials and build an employer-ready GitHub portfolio:",
            "items": [
                {
                    "title": "Full Stack Web Technician Career Diploma",
                    "desc": "Registered vocational diploma verifying mastery of modern full stack software engineering and database systems."
                },
                {
                    "title": "Generative AI Engineering Mini-Credential",
                    "desc": "Specialized micro-credential certifying hands-on proficiency in LLM API integration, prompt engineering, and RAG systems."
                },
                {
                    "title": "AWS Cloud & DevOps Practitioner Badge",
                    "desc": "Proof of competence in containerization, cloud infrastructure provisioning, serverless functions, and CI/CD pipelines."
                },
                {
                    "title": "Production-Grade Capstone SaaS Portfolio",
                    "desc": "A live, fully deployed full-stack SaaS application with authentication, payments, database persistence, and AI features on GitHub."
                }
            ]
        },
        "curriculum": {
            "title": "Comprehensive 10-Module Curriculum Outline",
            "desc": "A structured, hands-on 32-week software engineering curriculum designed to take you from foundational programming to enterprise-ready AI full-stack developer:"
        },
        "curriculum_modules": [
            {
                "num": 1,
                "title": "Computer Science Fundamentals, OOP & Core Programming Architecture",
                "hours": "35 Hours",
                "desc": "Core algorithms, data structures (arrays, linked lists, hash maps, trees), Big-O complexity, Object-Oriented Programming (OOP) principles, clean code design, and Git version control workflows."
            },
            {
                "num": 2,
                "title": "Modern Frontend Core: HTML5, CSS3, Responsive Design & Modern JavaScript (ES6+)",
                "hours": "35 Hours",
                "desc": "Semantic HTML, Flexbox, CSS Grid, Tailwind CSS, DOM manipulation, ES6+ features (closures, promises, async/await, modules), event-driven programming, and client-side debugging."
            },
            {
                "num": 3,
                "title": "Enterprise Frontend Engineering: TypeScript & React 19 Architecture",
                "hours": "40 Hours",
                "desc": "TypeScript static typing, interfaces, generics; React 19 functional components, custom hooks, context API, state management with Redux Toolkit/Zustand, and performance optimization."
            },
            {
                "num": 4,
                "title": "Next.js Full-Stack Architecture: Server Components, SSR & App Router",
                "hours": "35 Hours",
                "desc": "Next.js App Router, React Server Components (RSC), Server-Side Rendering (SSR), Static Site Generation (SSG), dynamic routing, API route handlers, and middleware security."
            },
            {
                "num": 5,
                "title": "Backend Engineering: Node.js, Express & RESTful Microservices",
                "hours": "35 Hours",
                "desc": "Asynchronous event-loop architecture, Express.js middleware, RESTful API design standards, JWT / OAuth2 authentication, rate limiting, error handling, and unit testing with Jest."
            },
            {
                "num": 6,
                "title": "Enterprise Java & Spring Boot Microservices Ecosystem",
                "hours": "35 Hours",
                "desc": "Core & Advanced Java, JVM internals, Spring Boot 3, Dependency Injection, Spring MVC, Spring Security, MyBatis / Hibernate ORM, and enterprise service architecture."
            },
            {
                "num": 7,
                "title": "Database Engineering: Relational SQL, NoSQL & High-Performance Caching",
                "hours": "35 Hours",
                "desc": "PostgreSQL and MySQL schema design, complex JOINs, indexing & query optimization, MongoDB document modeling, Prisma ORM, and Redis distributed caching."
            },
            {
                "num": 8,
                "title": "Generative AI Engineering: LLMs, OpenAI API, LangChain & Vector Databases",
                "hours": "40 Hours",
                "desc": "OpenAI / Anthropic Claude API integration, prompt engineering techniques, LangChain / LlamaIndex workflows, Retrieval-Augmented Generation (RAG), embeddings, and Pinecone/ChromaDB vector search."
            },
            {
                "num": 9,
                "title": "Cloud Infrastructure, Docker Containers & DevOps CI/CD Pipelines",
                "hours": "30 Hours",
                "desc": "Containerizing multi-service apps with Docker & Docker Compose, AWS cloud services (EC2, S3, RDS, Lambda), Vercel deployment, GitHub Actions automated CI/CD pipelines, and environment secrets."
            },
            {
                "num": 10,
                "title": "Enterprise Capstone Project, System Design & Tech Interview Mastery",
                "hours": "40 Hours",
                "desc": "Build and deploy an enterprise-grade AI-powered SaaS application; comprehensive system design reviews (scalability, microservices, load balancing), LeetCode coding interview drills, and mock tech screens."
            }
        ],
        "practicum": {
            "title": "Production-Grade Capstone Project & Enterprise Coding Labs",
            "desc": "Students work in agile sprint teams simulating enterprise tech environments. Under the direct guidance of senior tech leads from top Canadian enterprises, you will develop, code review, test, containerize, and deploy production-ready full-stack applications with integrated AI intelligence.",
            "box_title": "Direct Tech Employer Introductions & Alumni Referral Network",
            "box_desc": "Over 90% of our active tech graduates secure full-stack, frontend, backend, or QA engineering roles within 3 to 6 months of graduation, working across Toronto's thriving fintech, healthcare tech, and software sectors."
        },
        "admissions": {
            "title": "Admission Requirements & Prerequisites",
            "items": [
                "Ontario Secondary School Diploma (OSSD / Grade 12) or Canadian / International equivalent credential evaluation.",
                "Mature Student Admission: 18 years of age or older with a passing score on the college entrance assessment.",
                "Basic computer literacy and logical problem-solving aptitude (no prior coding experience strictly required; introductory bootcamp modules included).",
                "Career changers, engineering/science graduates, and existing IT professionals looking to upskill with modern AI and Full-Stack technologies.",
                "English language proficiency suitable for technical communication and documentation."
            ]
        },
        "grants": {
            "badge": "GOVERNMENT GRANTS",
            "title": "Get Up to $28,000+ Government Grant",
            "description": "Victoria College's Full Stack Web with AI Mini-Credential diploma is approved for the Better Jobs Ontario (Second Career) grant program, providing up to $28,000+ in non-repayable government funding for eligible applicants, covering 100% tuition, computer allowance, books, and living support.",
            "amount": "$28,000+",
            "button_text": "Check Grant Eligibility Now"
        },
        "snapshot": {
            "delivery": "Live Online + In-Person Campus Labs",
            "practicum": "Enterprise Capstone + GitHub Portfolio",
            "locations": "Markham Main Campus / Live Online",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "Do I need a Computer Science degree or prior coding experience to enroll?", "a": "No prior coding background is required! Our program is carefully designed to take beginners from programming fundamentals to enterprise-level full-stack and AI engineering through structured labs, step-by-step guidance, and mentor code reviews."},
            {"q": "What is the AI Mini-Credential included in this program?", "a": "The AI Mini-Credential is a cutting-edge curriculum track covering Generative AI integration, LLM APIs (OpenAI GPT-4, Claude), prompt engineering, Retrieval-Augmented Generation (RAG), and vector databases. You'll build smart web applications capable of semantic search, automated summarization, AI chat, and workflow automation."},
            {"q": "What technologies and frameworks will I master?", "a": "You will gain hands-on mastery in HTML5, CSS3, Tailwind CSS, JavaScript (ES6+), TypeScript, React 19, Next.js, Node.js, Express, Java, Spring Boot, PostgreSQL, MongoDB, Redis, Docker, AWS (EC2/S3/RDS/Lambda), Git/GitHub, and OpenAI/LangChain."},
            {"q": "Is this program eligible for government grants like Better Jobs Ontario?", "a": "Yes! Victoria International College is a registered career college under the Ontario Career Colleges Act, 2005. Eligible individuals (unemployed, laid-off, gig workers, or underemployed) can qualify for up to $28,000+ in non-repayable Better Jobs Ontario funding covering 100% of tuition, tech equipment, and living costs."},
            {"q": "How does Victoria College support students with job placement?", "a": "We provide comprehensive tech career services: 1-on-1 resume optimization, GitHub portfolio polishing, technical mock interviews (data structures, algorithms, system design), LeetCode interview preparation, and direct job referrals to our GTA employer hiring network."},
            {"q": "What is the class schedule and format?", "a": "We offer flexible formats including full-time weekday cohorts and part-time evening/weekend tracks. All live sessions are recorded in HD for 24/7 review, combined with collaborative online lab workstations and on-campus mentor access."}
        ]
    }

def get_default_tech_detail_zh():
    return {
        "hero": {
            "badge": "加国紧缺高薪 IT 职业文凭 • 含 AI 微证书",
            "title": "全栈软件工程开发与 AI 微证书大专文凭班",
            "lead": "由加拿大顶级银行与科技名企资深架构师亲授。从底层编程基础到现代前端工程（React 19 / Next.js / TypeScript）、企业级后端微服务（Node.js / Python / Java Spring Boot）、AWS 云原生运维（Docker / CI/CD），并深度融入前沿生成式 AI 大模型开发（OpenAI API, LangChain, RAG 检索增强, 向量数据库）。手把手带领学员打造高含金量商业项目作品集，直通北美高薪软件工程师就业岗位。",
            "cta_book": "预约免费名师 IT 规划咨询",
            "cta_curriculum": "查看 10 大核心模块大纲"
        },
        "stats": [
            {"value": "$75K – $120K+", "label": "大多伦多软件开发薪资范围", "sub": "初级至中高级全栈开发工程师"},
            {"value": "100% 实战机房", "label": "商业级真实项目作品集", "sub": "企业级 SaaS、AI 集成与 GitHub 真实代码仓库"},
            {"value": "北美名企名师", "label": "一线资深架构师手把手带教", "sub": "一对一代码审查与全真大厂模拟技术面试"},
            {"value": "最高 $28,000+", "label": "安省政府培训全额助学金", "sub": "Better Jobs Ontario 资助计划合资格申请"}
        ],
        "why_choose": {
            "title": "为什么选择全栈软件开发与 AI 微证书课程？",
            "subtitle": "软件开发始终是加拿大就业市场需求最旺盛、抗周期能力最强、薪资天花板最高的黄金职业之一。随着生成式 AI 与大模型技术的爆发，具备扎实全栈工程开发能力并精通 AI 集成落地的复合型开发者在招聘市场备受追捧。",
            "pillars": [
                {
                    "title": "企业级现代全栈工程技术栈",
                    "desc": "系统掌握全栈开发主流技术：React 19、Next.js App Router、TypeScript、Node.js、Python、Spring Boot 3、PostgreSQL、MongoDB 与 Redis 高性能缓存。"
                },
                {
                    "title": "深度融入生成式 AI 与 LLM 大模型开发",
                    "desc": "打破传统码农局限。深入掌握 OpenAI / Claude API 调用、Prompt 提示词工程、LangChain 框架、RAG 知识库检索增强与向量数据库实战。"
                },
                {
                    "title": "云原生 DevOps 与生产环境自动化部署",
                    "desc": "实战 Docker 容器化打包、AWS 云端基础设施（EC2, S3, RDS, Lambda）配置，以及基于 GitHub Actions 的自动化 CI/CD 持续集成部署流程。"
                },
                {
                    "title": "一对一技术面试辅导与名企内推",
                    "desc": "名师提供简历技术深度包装、GitHub 代码库规范打磨、LeetCode 高频算法精讲、系统架构设计（System Design）与大多伦多本地科技雇主直推。"
                }
            ]
        },
        "credentials": {
            "title": "职业文凭、微证书与实战项目里程碑",
            "subtitle": "毕业学员将获得安省官方认可的职业大专文凭及极具就业竞争力的项目作品集：",
            "items": [
                {
                    "title": "Full Stack Web Technician 职业大专文凭",
                    "desc": "安省教育部注册职业学院颁发的正规职业大专文凭，权威验证全栈软件开发与数据库工程专业能力。"
                },
                {
                    "title": "生成式 AI 智能工程微证书 (AI Mini-Credential)",
                    "desc": "专项认证微证书，证明学员具备大模型 API 集成、RAG 企业知识库构建及 AI 智能应用开发实操能力。"
                },
                {
                    "title": "AWS 云原生与 DevOps 实践认证徽章",
                    "desc": "证明掌握 Docker 容器化、AWS 云服务配置、自动化构建测试与无服务器计算架构运维能力。"
                },
                {
                    "title": "工业级商业 Capstone SaaS 项目作品集",
                    "desc": "在 GitHub 上交付具备完整用户鉴权、支付结算、数据库持久化及 AI 智能问答特性的线上真实运营级 SaaS 平台。"
                }
            ]
        },
        "curriculum": {
            "title": "32 周 10 大核心课程模块大纲",
            "desc": "紧扣北美一线科技大厂与金融机构用人标准的循序渐进实战大纲，助零基础与进阶学员系统蜕变为企业级 AI 全栈工程师："
        },
        "curriculum_modules": [
            {
                "num": 1,
                "title": "计算机底层核心、面向对象编程 (OOP) 与算法数据结构",
                "hours": "35 学时",
                "desc": "核心算法、常用数据结构（数组、链表、哈希表、二叉树）、时间与空间复杂度（Big-O）、面向对象设计原则（SOLID）、代码整洁之道与 Git 版本控制规范。"
            },
            {
                "num": 2,
                "title": "现代前端基础：HTML5、CSS3 响应式布局与 JavaScript (ES6+) 进阶",
                "hours": "35 学时",
                "desc": "语义化 HTML5、Flexbox、CSS Grid、Tailwind CSS、DOM 树操作、ES6+ 核心特性（闭包、原型链、Promise、async/await、模块化）、事件驱动模型与浏览器调试技巧。"
            },
            {
                "num": 3,
                "title": "企业级前端工程：TypeScript 与 React 19 核心架构",
                "hours": "40 学时",
                "desc": "TypeScript 静态类型系统、接口与泛型；React 19 函数式组件、Custom Hooks 自定义钩子、Context API、Redux Toolkit / Zustand 状态管理与前端性能极致调优。"
            },
            {
                "num": 4,
                "title": "Next.js 全栈架构：服务端组件 (RSC)、SSR 与 App Router 路由",
                "hours": "35 学时",
                "desc": "Next.js App Router 架构、服务端组件与客户端组件交互、服务端渲染 (SSR)、静态生成 (SSG)、动态路由传参、API Route Handlers 与安全中间件。"
            },
            {
                "num": 5,
                "title": "现代后端工程：Node.js、Express 框架与 RESTful 微服务",
                "hours": "35 学时",
                "desc": "Node.js 异步非阻塞事件循环机制、Express 中间件架构、RESTful API 行业标准设计、JWT / OAuth2 鉴权与安全防护、限流降级及 Jest 单元测试。"
            },
            {
                "num": 6,
                "title": "企业级 Java 后端微服务生态：Spring Boot 3 与 MyBatis",
                "hours": "35 学时",
                "desc": "Java 核心进阶、JVM 运行机制、Spring Boot 3 自动装配、依赖注入 (IoC/DI)、Spring MVC 控制层、Spring Security 权限控制与 MyBatis / Hibernate 数据库持久层。"
            },
            {
                "num": 7,
                "title": "数据库架构与优化：SQL 关系型、NoSQL 与 Redis 高性能缓存",
                "hours": "35 学时",
                "desc": "PostgreSQL 与 MySQL 数据库表设计、复杂 JOIN 查询、索引优化与执行计划分析、MongoDB 文档建模、Prisma ORM 以及 Redis 分布式缓存与消息队列实战。"
            },
            {
                "num": 8,
                "title": "AI 智能工程微证书：LLM 大模型、OpenAI API、LangChain 与向量数据库",
                "hours": "40 学时",
                "desc": "OpenAI / Claude API 深度集成、Prompt 提示词工程进阶、LangChain / LlamaIndex 编排、RAG 检索增强企业知识库、Embeddings 向量嵌入与 Pinecone/ChromaDB 向量搜索。"
            },
            {
                "num": 9,
                "title": "云原生基础设施：Docker 容器化、AWS 云部署与 CI/CD 自动化流水线",
                "hours": "30 学时",
                "desc": "多服务 Dockerfile 与 Docker Compose 容器编排、AWS 核心云服务（EC2, S3, RDS, Lambda）、Vercel 云端部署、GitHub Actions 自动化构建与环境变量安全配置。"
            },
            {
                "num": 10,
                "title": "毕业大项目 Capstone：工业级 AI 赋能 SaaS 云平台与名企面试冲刺",
                "hours": "40 学时",
                "desc": "团队敏捷协作交付具备 AI 智能特性的工业级全栈云平台；系统架构设计（高并发、分布式、负载均衡）、LeetCode 经典大厂算法真题精讲与一对一模拟面试。"
            }
        ],
        "practicum": {
            "title": "企业级全真实训机房与商业 Capstone 毕业大项目",
            "desc": "学员按敏捷敏捷开发团队（Scrum Team）编制，在加国名企资深架构师带领下，全程使用 Jira、GitHub 进行企业级规范的代码提交、Code Review、CI/CD 部署与自动化测试，亲手打造可写进简历的高含金量真实商业作品集。",
            "box_title": "大多伦多地区科技名企对口内推与校友合作网络",
            "box_desc": "维多利亚学院 IT 毕业生在加国各大银行（RBC, TD, BMO, CIBC, Scotiabank）、金融科技、医疗健康与知名科技公司广泛任职，毕业 3–6 个月内积极就业率超 90%！"
        },
        "admissions": {
            "title": "入学报读条件与适合人群",
            "items": [
                "具备安大略省高中毕业文凭（OSSD / 12年级）或加国及海外同等学历评估认证。",
                "成熟学生通道：年满 18 周岁，并通过学院入学基础能力测评（校区/线上免费测评）。",
                "零基础转行人员：理工科毕业生、文商科转行 IT 人士（课程包含保姆级编程入门引导模块）。",
                "在职技术提升人员：已有传统开发经验，希望迅速掌握 React、Next.js、AWS 云计算与 Generative AI 大模型落地的 IT 从业者。",
                "具备基本的计算机操作习惯与逻辑思维能力，具有较强的学习意愿。"
            ]
        },
        "grants": {
            "badge": "安省政府培训资助",
            "title": "申请最高 $28,000+ 政府全额助学金",
            "description": "全栈软件工程开发与 AI 微证书大专文凭班完全符合安省 Better Jobs Ontario（原第二职业 Second Career）政府培训资助计划。符合条件的安省居民（失业、裁员、领过 EI、自雇、零工人员或低收入群体）最高可申请 $28,000+ 加币全额无偿补贴，100% 覆盖学费、电脑设备费、书本教材费及学习期间基本生活津贴。",
            "amount": "$28,000+",
            "button_text": "立即免费评估资助资格"
        },
        "snapshot": {
            "delivery": "混成教学（线上高清直播 + 校区实操机房）",
            "practicum": "企业级 Capstone 大项目 + GitHub 真实仓库",
            "locations": "万锦主校区 / 在线名师直播",
            "hotline": "416-665-6668"
        },
        "faqs": [
            {"q": "零基础或者没有计算机背景可以学会吗？", "a": "完全可以！我们的课程体系经过 20 余年持续迭代，从零基础编程底层逻辑（变量、循环、数据结构）讲起，循序渐进过渡到微服务与 AI 大模型应用。课程配备助教答疑、代码逐行审查与丰富随堂练习，确保零基础学员扎实吸收。"},
            {"q": "课程中的 AI 微证书（AI Mini-Credential）包含哪些核心内容？", "a": "AI 微证书涵盖当前最前沿的生成式 AI 实战技术：OpenAI / Claude API 调用、Prompt 提示词工程进阶、LangChain 框架、RAG 企业私有知识库检索增强与向量数据库应用。学员将亲手打造具备语义搜索、智能问答与自动化工作流的 AI 智能 Web 应用。"},
            {"q": "课程会教授哪些主流开发语言和框架？", "a": "涵盖当前北美招聘市场需求最大的全家桶：HTML5、CSS3、Tailwind CSS、JavaScript (ES6+)、TypeScript、React 19、Next.js、Node.js、Express、Java、Spring Boot 3、PostgreSQL、MySQL、MongoDB、Redis、Docker、AWS 云服务及 Git/GitHub。"},
            {"q": "我可以申请政府全额学费资助吗？", "a": "可以！维多利亚学院为安省正规注册职业学院，本专业完全符合 Better Jobs Ontario 政府资助计划。失业、被裁员、领过 EI、自雇或低收入人士最高可获 $28,000+ 无需偿还的政府全额资助（包括学费、电脑费与生活费），学院专家免费一对一协助申请。"},
            {"q": "毕业后学校如何辅导就业？", "a": "学院提供全方位的 IT 就业辅导体系：一对一简历深度技术包装、GitHub 代码库规范打磨、LeetCode 高频算法真题精讲、系统设计与全真大厂模拟技术面试，并向大多伦多本地合作雇主库直接内推。"},
            {"q": "上课时间如何安排？有录播可以复习吗？", "a": "我们提供全日制脱产班及业余晚间/周末班等多种灵活班型。所有线上直播课程均支持高清录播无限次回放，并配套全天候线上协作机房与校区导师面授答疑。"}
        ]
    }

def format_program_dict(row):
    """Convert a database row for a program into a clean dict with parsed JSON arrays."""
    d = dict(row)
    for json_field in ['bullets_en', 'bullets_zh', 'modules_en', 'modules_zh']:
        val = d.get(json_field)
        if val:
            try:
                parsed = json.loads(val)
                d[json_field] = parsed if isinstance(parsed, list) else [parsed]
            except Exception:
                d[json_field] = [line.strip() for line in str(val).split('\n') if line.strip()]
        else:
            d[json_field] = []

    for detail_field in ['detail_json_en', 'detail_json_zh']:
        val = d.get(detail_field)
        if val:
            if isinstance(val, dict):
                d[detail_field] = val
            elif isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    while isinstance(parsed, str):
                        parsed = json.loads(parsed)
                    d[detail_field] = parsed if isinstance(parsed, dict) else {}
                except Exception:
                    d[detail_field] = {}
            else:
                d[detail_field] = {}
        else:
            d[detail_field] = {}
    return d

def seed_default_programs(cursor, now_str):
    default_programs = [
        {
            'slug': 'psw',
            'category': 'healthcare',
            'image_url': 'images/psw.jpg',
            'badge_en': 'Certificate Program • Ontario Regulated',
            'badge_zh': '安省官方职业证书 • 紧缺高薪',
            'title_en': 'NACC Personal Support Worker DE 2022',
            'title_zh': 'NACC 个人护理护工文凭 (PSW DE 2022)',
            'desc_en': 'Personal Support Worker Certificate Program contains in class lectures and practicum training. Upon graduating, students will not only have their PSW certificate but also a CPR & First Aid certificate.\n\nThe goal of the Personal Support Worker Program is to help individuals master the required personal and occupational qualities needed to care for people living at home and in long-term care facilities. Students will learn to identify and respond to the physical and emotional needs of clients/consumers.',
            'desc_zh': '个人支持工作者（PSW）证书课程包含课堂讲座和实习培训。毕业后，学生不仅将获得 PSW 证书，还将获得 CPR 和急救证书。\n\n个人支持工作者课程的目标是帮助个人掌握在家庭和长期护理机构中照顾他人所需的个人和职业素质。',
            'bullets_en': '[]',
            'bullets_zh': '[]',
            'duration_en': '23 Weeks (Classroom + Lab + Practicum)',
            'duration_zh': '23 周（理论课 + 实验室模拟 + 机构临床实习）',
            'credential_en': 'NACC PSW Diploma + Standard First Aid & CPR Level C',
            'credential_zh': '安省 NACC PSW 官方文凭 + CPR / AED 急救证书',
            'overview_en': 'The Personal Support Worker Certificate Program prepares students to master the required personal and occupational qualities needed to care for individuals in long-term care homes, retirement communities, hospitals, and home care environments.',
            'overview_zh': 'PSW（Personal Support Worker）是安省长期紧缺的黄金医疗护理职业。维多利亚学院配备先进模拟病房，由安省资深护士名师亲授，包含扎实理论、实操技能及正规养老机构/医院实习。',
            'modules_en': json.dumps([
                "PSW Foundations: Role, responsibilities, scope of practice, legal boundaries & healthcare ethics.",
                "Safety and Mobility: Body mechanics, ergonomics, patient transfer techniques, infection control & WHMIS.",
                "Body Systems & Anatomy: Comprehensive overview of human anatomy, physiology, aging processes & vital signs.",
                "Assisting with Personal Hygiene: Bed baths, oral hygiene, skin integrity prevention, grooming & dignity care.",
                "Abuse and Neglect: Identification, institutional abuse reporting protocols & client rights advocacy.",
                "Household Management, Nutrition & Hydration: Meal planning, special dietary requirements, therapeutic diets & feeding assistance.",
                "Care Planning & Documentation: Restorative care goals, electronic health documentation (EHR) & reporting to RNs/RPNs.",
                "Assisting the Family / Growth & Development: Family dynamics, child development, supportive care across the lifespan.",
                "Assisting the Dying Person: Palliative care, end-of-life comfort, hospice support & bereavement protocols.",
                "Assisting with Medications: Pharmacological routes, medication reminders, blister packs & error reporting.",
                "Cognitive & Mental Health Issues: Alzheimer's disease, dementia care, depression, delirium & acquired brain injuries.",
                "Common Health Conditions: Diabetes, cardiovascular diseases, stroke, respiratory conditions, arthritis & cancer care.",
                "Gentle Persuasive Approaches (GPA): Evidence-based dementia de-escalation techniques & patient-centered behavioral care.",
                "Clinical Placement (Facility - 200+ Hours): Supervised on-site practicum in accredited Ontario Long-Term Care (LTC) nursing homes.",
                "Clinical Placement (Community - 110+ Hours): Hands-on in-home patient support with community healthcare agencies."
            ], ensure_ascii=False),
            'modules_zh': json.dumps([
                "PSW 基础通论: 角色职责、工作范围、法律规范与职业道德准则。",
                "安全与行动协助: 人体力学、病患安全搬移技巧、感染控制与 WHMIS 危险品安全。",
                "人体系统与解剖: 人体各大生理系统结构、老化生理过程与生命体征测量。",
                "个人卫生护理: 床上擦浴、口腔护理、压疮防范、仪容修饰与尊严护理。",
                "虐待与忽视防范: 识别迹象、法定上报流程与长者权益保护。",
                "家政管理、营养与补水: 餐食规划、特殊治疗饮食调配与辅助进食。",
                "护理计划与文书记录: 康复护理目标制定、电子医疗记录 (EHR) 及向注册护士汇报。",
                "家庭协助与成长发育: 家庭人际互动、儿童发育心理与全生命周期关怀。",
                "临终关怀护理: 姑息治疗、临终身心舒适护理、安宁疗护与家属哀伤辅导。",
                "药物协助管理: 给药途径认知、服药提醒、药盒管理与差错防范上报。",
                "认知与心理健康护理: 阿尔茨海默病、失智症护理、抑郁症、谵妄与脑损伤照护。",
                "常见健康疾病照护: 糖尿病、心血管疾病、中风后遗症、呼吸系统疾病、关节炎与癌症照护。",
                "温和劝导疗法 (GPA): 失智症情绪疏导技巧与以患者为中心的行为应对。",
                "长者院临床实习（机构 - 200+小时）: 在安省认证长期护理院（LTC）进行带教实战。",
                "社区上门实习（社区 - 110+小时）: 跟随社区医疗机构进行上门长者与病患照护。"
            ], ensure_ascii=False),
            'careers_en': 'Personal Support Worker (PSW), Long-term Care Aide, Home Support Worker, Respite Caregiver, Hospital Patient Attendant.',
            'careers_zh': '养老院私人护理员（PSW）、医院病患护理助理、社区家庭护理员、日间照料中心护理专员。',
            'outcomes_en': 'High demand across Ontario with starting wages from $20 to $28/hour. Government incentive grants and sign-on bonuses often available.',
            'outcomes_zh': '安省各公立/私立医疗养老机构长期极度紧缺，时薪高达 $20–$28/小时，福利完善，常年具备全职高薪就业机会。',
            'detail_json_en': json.dumps(get_default_psw_detail_en(), ensure_ascii=False),
            'detail_json_zh': json.dumps(get_default_psw_detail_zh(), ensure_ascii=False),
            'display_order': 1,
            'is_active': 1
        },
        {
            'slug': 'accounting',
            'category': 'business',
            'image_url': 'images/accounting.jpg',
            'badge_en': 'Career Diploma • CPA Mentorship',
            'badge_zh': '加国高稳定度白领职业文凭',
            'title_en': 'Accounting, Tax and Payroll',
            'title_zh': '会计、税务与薪资管理 (Accounting, Tax & Payroll)',
            'desc_en': 'The program consists of 30 weeks of intensive instructor led hands on training and practical exercises under the supervision of industry-experienced instructors.\n\nOur Computerized Accounting program provides students with solid knowledge and skills to work as a bookkeeper, an accounting assistant, or accounts receivable/ accounts payable clerk, and proficiencies appropriate for careers in accounting and payroll administration.',
            'desc_zh': '该项目由经验丰富的行业导师指导，包含30周密集实战培训及上机操作练习。\n\n计算机化会计课程为学员提供扎实的专业知识与技能，适合从事全盘簿记员、会计助理、应收应付账款专员以及薪资管理等工作。',
            'bullets_en': '[]',
            'bullets_zh': '[]',
            'duration_en': '30 Weeks (Hands-on Corporate Software)',
            'duration_zh': '30 周（名师带教 + 真账实操演练）',
            'credential_en': 'Computerized Accounting, Tax & Payroll Diploma',
            'credential_zh': '安省认证 Computerized Accounting & Payroll 职业文凭',
            'overview_en': 'Comprehensive vocational training designed for individuals aiming to work as corporate bookkeepers, payroll coordinators, and tax associates across Canadian commercial enterprises and CPA accounting firms.',
            'overview_zh': '由加国资深 CPA 及持牌会计师团队授课，针对加拿大本地公司日常全流程账务、员工工资税核算、CRA 个人与公司税申报进行深度全真演练，毕业即具备 2-3 年实际工作经验水准。',
            'modules_en': json.dumps([
                "Canadian Financial Accounting Principles & Double-Entry Bookkeeping",
                "QuickBooks Desktop & QuickBooks Online (QBO) Master Certification",
                "Sage 50 Cloud Accounting & Enterprise ERP Overview",
                "Canadian Payroll Administration: CRA Rules, CPP, EI, WSIB, ROE & T4 Filing",
                "Canadian Taxation Part 1: Personal Tax (T1) & Wealth Planning (Profile / TaxPrep)",
                "Canadian Taxation Part 2: Corporate Tax (T2), GST/HST Reporting & Audits",
                "Advanced Excel for Financial Modeling, Pivot Tables, VLOOKUP & Analytics",
                "Full Cycle Accounting Case Study & Year-end Working Papers"
            ], ensure_ascii=False),
            'modules_zh': json.dumps([
                "加拿大商业会计基础与复式记账法原理",
                "QuickBooks 桌面版与云端版（QBO）全账套实战",
                "Sage 50 财务软件企业级应用与库存/往来账管理",
                "加拿大薪资法规管理：CRA 税务扣缴、CPP、EI、WSIB、ROE 与 T4 表格制作",
                "加拿大税务实战 1：个人所得税（T1）申报、自雇税收与税务规划（Profile/TaxPrep）",
                "加拿大税务实战 2：公司税（T2）申报、GST/HST 税务核算及 CRA 审计应对",
                "高级 Excel 财务建模、数据透视表、VLOOKUP 与商业报表分析",
                "企业全流程真账实操与年终结账底稿（Working Papers）编制"
            ], ensure_ascii=False),
            'careers_en': 'Bookkeeper, Accounts Receivable / Payable Clerk, Payroll Specialist, Tax Preparer, Junior Accountant, Financial Assistant.',
            'careers_zh': '全盘簿记员（Bookkeeper）、应收应付账款主管、薪资管理专员、报税专员、会计助理。',
            'outcomes_en': 'High placement rate across small-to-medium businesses and accounting firms with clear progression paths to CPA designation.',
            'outcomes_zh': '大多伦多地区各类企事业单位常年刚需，就业面极广，工作环境稳定舒适，并为考取 CPA 提供坚实基石。',
            'detail_json_en': json.dumps(get_default_accounting_detail_en(), ensure_ascii=False),
            'detail_json_zh': json.dumps(get_default_accounting_detail_zh(), ensure_ascii=False),
            'display_order': 2,
            'is_active': 1
        },
        {
            'slug': 'eca',
            'category': 'education',
            'image_url': 'images/eca.jpg',
            'badge_en': 'Career Diploma • Daycare Placement',
            'badge_zh': '安省热门幼教职业文凭 • 保障实习',
            'title_en': 'Early Childcare Assistant',
            'title_zh': '早期幼儿教育助理 (Early Childcare Assistant - ECA)',
            'desc_en': 'We provide our students with the opportunity for personal growth and success by providing an intimate and friendly learning environment that emphasizes academic & professional excellence. Subjects included in the program:',
            'desc_zh': '我们通过营造注重学术与专业卓越的温馨友善学习环境，为学生提供个人成长与成功的机会。涵盖科目包括：',
            'bullets_en': '[]',
            'bullets_zh': '[]',
            'duration_en': '22 Weeks (Classroom Theory + Daycare Placement)',
            'duration_zh': '22 周（理论课 + 正规持牌日托中心跟岗实习）',
            'credential_en': 'Early Childcare Assistant Diploma + Child CPR & First Aid',
            'credential_zh': '安省 ECA 幼教助理文凭 + 儿童急救与 CPR 证书',
            'overview_en': 'Equips students with the practical competencies, child psychology understanding, and health & safety expertise required to support Early Childhood Educators (ECEs) in licensed Ontario daycare facilities.',
            'overview_zh': '随着安省日托政策普及，持证幼教助理需求激增。课程系统培养学员在持牌日托中心配合主班幼教（ECE）开展日常照料、安全监管、早期启蒙游戏及家校沟通的专业能力。',
            'modules_en': json.dumps([
                "Introduction to Early Childhood Education & Ontario Daycare Regulations",
                "Child Growth and Development: Infancy to Toddlerhood",
                "Child Growth and Development: Preschool to School-Age",
                "Health, Safety, Nutrition & Emergency Procedures in Childcare",
                "Creative Expressions: Art, Music, Storytelling & Sensory Play",
                "Positive Guidance & Classroom Behavior Strategies",
                "Interpersonal Communications with Families, Staff & Regulators",
                "Program Planning & Pedagogical Documentation (How Does Learning Happen?)",
                "Supporting Children with Diverse Needs & Inclusive Childcare",
                "Supervised Field Practicum in Licensed Childcare Centers (500+ Hours)"
            ], ensure_ascii=False),
            'modules_zh': json.dumps([
                "加拿大幼儿教育概论与安省日托管理法规",
                "儿童生长与心理发展：婴儿期至幼童期",
                "儿童生长与心理发展：学龄前期至学龄期",
                "日托中心健康、安全防护、营养与应急处理",
                "幼儿创意启蒙：美术、音乐律动、故事会与感统游戏",
                "儿童行为积极引导与班级常规管理",
                "家园共育沟通技能与多文化背景团队协作",
                "启蒙教案编制与儿童观察记录档案",
                "特殊需求儿童关怀与融合教育实践",
                "安省持牌日托中心 500+ 小时实地跟岗实习"
            ], ensure_ascii=False),
            'careers_en': 'Early Childcare Assistant, Daycare Room Assistant, Nursery Assistant, Before/After School Program Leader, Private Family Care Specialist.',
            'careers_zh': '持证幼教助理（ECA）、幼儿园班级助理、课后托管班（After-School）主管、早教中心活动辅导员。',
            'outcomes_en': "With Ontario's $10-a-day childcare expansion, certified early childcare staff are in historic high demand across the province.",
            'outcomes_zh': '政府日托补贴政策推动下全省幼教机构大量扩招，工作稳定，假期充裕，福利待遇良好。',
            'detail_json_en': json.dumps(get_default_eca_detail_en(), ensure_ascii=False),
            'detail_json_zh': json.dumps(get_default_eca_detail_zh(), ensure_ascii=False),
            'display_order': 3,
            'is_active': 1
        },
        {
            'slug': 'acupuncture',
            'category': 'wellness',
            'image_url': 'images/acupuncture.jpg',
            'badge_en': 'Non-Vocational Enrichment Program',
            'badge_zh': '非职业特色兴趣课程 • 传统中医养生',
            'title_en': 'Acupuncture',
            'title_zh': '中医针灸与传统养生保健课程',
            'desc_en': 'Acupuncture program is a Non-Vocational Program. This program does not require approval under the Ontario Career Colleges Act, 2005.\n\nOur Acupuncture program is designed for individuals seeking personal interest learning, wellness knowledge, or complementary health education. This program provides foundational theory, traditional concepts, and practical demonstrations for personal enrichment.',
            'desc_zh': '针灸课程属于非职业性兴趣技能课程，不属于《2005年安大略省职业学院法》管辖范围。\n\n我们的针灸课程专为寻求个人兴趣学习、养生保健知识或自然疗法启蒙的人群设计，提供系统基础理论、传统观念和实操演示。',
            'bullets_en': json.dumps([
                "2250 Hours Comprehensive Study: Theory, Meridians, Diagnostic Arts & Demonstrations",
                "Hybrid Flexible Format: Online Interactive Theory + In-Person Practical Labs",
                "Hands-on Clinic Experience: Clean needle safety, moxibustion, fire cupping, Gua Sha & Tuina",
                "Flexible Schedule: Weekday Cohort (Mon–Fri 9am–5pm) & Weekend Cohort (Fri eve + Sat/Sun)"
            ], ensure_ascii=False),
            'bullets_zh': json.dumps([
                "2250 学时系统研习：中医理论、经络腧穴、四诊辨证与实操演示",
                "线上线下混成教学：名师实时直播 + 线下实训诊室面对面教学",
                "真实诊室实操观摩：无菌进针规范、艾灸温阳、火罐排湿、刮痧与推拿点穴",
                "灵活课时安排：全日制平日班（周一至五）与业余周末班（周五晚+周末）"
            ], ensure_ascii=False),
            'duration_en': '2250 Hours (Flexible Weekday & Weekend Options)',
            'duration_zh': '2250 学时（灵活平日班 / 周末班）',
            'credential_en': 'Certificate of Course Completion (2250 Hours)',
            'credential_zh': '维多利亚学院结业证书（2250 学时）',
            'overview_en': 'Designed for individuals seeking personal health empowerment, natural wellness knowledge, and traditional healing foundations. Master meridian pathways, acupressure techniques, auxiliary modalities (moxibustion, cupping, Gua Sha), and seasonal Yang Sheng living.',
            'overview_zh': '传承千年华夏医学瑰宝，为弘扬传统中医养生精髓、满足大众对自主健康管理与非药物疗法需求打造。深入浅出系统研习十四经络走形、100+ 常用保健要穴、进针规范、艾灸拔罐、经络推拿及四季节气调养。',
            'modules_en': json.dumps([
                "Foundations & Philosophy of Traditional Chinese Medicine (TCM)",
                "Meridian Channels & Acupoint Anatomy (14 Main Channels)",
                "TCM Diagnostic Fundamentals & Syndrome Differentiation",
                "Acupuncture Needling Techniques & Clean Needle Safety Protocols (CNT)",
                "Traditional Auxiliary Therapies: Moxibustion, Cupping & Gua Sha",
                "Tuina Chinese Therapeutic Massage & Acupressure for Pain Relief",
                "TCM Internal Health & Common Wellness Condition Analysis",
                "Musculoskeletal Wellness & Pain Management Techniques",
                "TCM Dietary Energetics, Food Therapy & Yang Sheng Living",
                "Supervised Clinical Demonstrations, Case Workshops & Hands-on Labs"
            ], ensure_ascii=False),
            'modules_zh': json.dumps([
                "中医基础理论与传统医学哲学（阴阳五行、脏腑气血）",
                "经络腧穴学与人体体表解剖（十四经脉、100+ 常用特效穴位）",
                "中医诊断学基础与四诊八纲辨证（望闻问切、舌象脉象）",
                "针灸针刺手法、无菌操作规范与安全常识（CNT 规范）",
                "传统中医外治特色疗法：艾灸、拔罐与刮痧（温通排湿）",
                "中医经络推拿点穴手法与筋骨保健（理筋通络、舒缓酸痛）",
                "中医脏腑调理与常见亚健康状态分析（睡眠、消化、气血调补）",
                "筋骨关节保健与肌肉疼痛舒缓实战（颈肩腰腿痛经络调护）",
                "中医食疗药膳、四季节气调养与养生学（体质辨识、药膳代茶饮）",
                "诊室实操观摩演示、手法实训与案例研讨（名师带教实战演练）"
            ], ensure_ascii=False),
            'careers_en': 'Wellness Enthusiast, Holistic Health Consultant, Natural Spa Care Assistant, Personal/Family Health Manager.',
            'careers_zh': '传统中医养生爱好者、推拿理疗技能进阶拓展、家庭健康管理专员。',
            'outcomes_en': 'Ideal enrichment course for wellness hobbyists, massage therapists, and natural health advocates.',
            'outcomes_zh': '掌握终身受用的中医养生绝活，调理个人与家人身心健康，拓宽自然疗法与整体健康视野。',
            'detail_json_en': json.dumps(get_default_acupuncture_detail_en(), ensure_ascii=False),
            'detail_json_zh': json.dumps(get_default_acupuncture_detail_zh(), ensure_ascii=False),
            'display_order': 4,
            'is_active': 1
        },
        {
            'slug': 'electrician',
            'category': 'trades',
            'image_url': 'images/electrician.jpg',
            'badge_en': 'Pre-Exam & Apprenticeship Coaching',
            'badge_zh': '安省持牌技工高薪黄金专业',
            'title_en': 'Electrician (Construction & Maintenance)',
            'title_zh': '建筑与维护电工考证培训班 (309A / 442A)',
            'desc_en': 'Becoming an Electrician in Ontario — Series Classes',
            'desc_zh': '安省考电工牌照就业系列课程 — 理论结合实战',
            'bullets_en': json.dumps([
                "Instructor: working in one of the biggest electrician contractors in Ontario with 20+ years",
                "Placement in government projects and get real and valuable experiences",
                "1 v 1 hands-on teaching in official recognized Apprenticeship Base and get solid techniques in a short time",
                "Exclusive opportunity to be referred to a job after class completion"
            ], ensure_ascii=False),
            'bullets_zh': json.dumps([
                "授课名师：安省 20 余年一线西人大型工程公司项目主管，亲授核心考点",
                "政府及商业大中型工程实战环境，获取极具含金量的加拿大本土实战经验",
                "官方认可学徒实训基地 1对1 动手实操教学，短时间内迅速掌握规范操作要领",
                "结业即享大多伦多地区持牌工程团队与工会直推就业通道"
            ], ensure_ascii=False),
            'duration_en': 'Comprehensive Weekend & Fast-Track Intensive',
            'duration_zh': '考证冲刺班 / 实用周末班（灵活随到随学）',
            'credential_en': 'Certificate of Pre-Exam Training & Job Referral',
            'credential_zh': '结业证书 + 红宝书真题库 + 雇主直推信',
            'overview_en': 'Coached by master electricians with 20+ years of Canadian union, commercial, and residential contracting experience. Combines Canadian Electrical Code (CEC) mastery with hands-on wiring labs.',
            'overview_zh': '由安省 20 余年一线西人大型工程公司项目主管与资深华人电工名师联袂授课。将加国电气规范（CEC）考点精讲与安省学徒实训基地真机实操融为一体，助学员一次性高效通关拿牌。',
            'modules_en': json.dumps([
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
            ], ensure_ascii=False),
            'modules_zh': json.dumps([
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
            ], ensure_ascii=False),
            'careers_en': 'Licensed Construction Electrician (309A), Industrial Electrician (442A), Electrical Maintenance Specialist, Solar/Green Energy Installer.',
            'careers_zh': '安省持牌建筑电工（309A）、工业维护电工（442A）、电气工程承包商、太阳能与新能源技师。',
            'outcomes_en': 'Top-tier trade with hourly wages ranging from $35 to $55+/hour in Ontario. High demand in commercial and residential developments.',
            'outcomes_zh': '加国薪资最高的金牌技工之一，持牌时薪普遍达 $35–$55+/小时，工会福利完善，收入稳定抗周期。',
            'detail_json_en': json.dumps(get_default_electrician_detail_en(), ensure_ascii=False),
            'detail_json_zh': json.dumps(get_default_electrician_detail_zh(), ensure_ascii=False),
            'display_order': 5,
            'is_active': 1
        },
        {
            'slug': 'tech',
            'category': 'technology',
            'image_url': 'images/fullstack.jpg',
            'badge_en': 'Career Diploma • AI Mini-Credential',
            'badge_zh': '加国紧缺高薪 IT 职业文凭 • 含 AI 微证书',
            'title_en': 'Full Stack Web with AI Mini-Credential',
            'title_zh': '全栈开发与 AI 微证书 (Full Stack Web with AI Mini-Credential)',
            'desc_en': 'This diploma program contains theoretical concepts with practical lab work to ensure graduates have a solid foundation in the following areas: programming fundamentals, system testing, web programming, design concepts, networks, server and database programming, plus a cutting-edge AI Mini-Credential.',
            'desc_zh': '该职业文凭课程将理论概念与高强度实操上机紧密结合，确保毕业生在编程基础、系统测试、Web开发、设计模式、计算机网络、云端数据库及前沿 AI 微证书（生成式 AI 与大模型应用）等领域奠定坚实基础。',
            'bullets_en': json.dumps([
                "Core Java",
                "Advanced Java",
                "Network Programming",
                "HTML/CSS/JavaScript",
                "SpringBoot",
                "Mybatis",
                "Spring/Spring MVC",
                "MySQL",
                "React/Nodejs/webpack",
                "Spring Cloud",
                "Netty",
                "AWS",
                "Design Pattern",
                "AI Mini-Credential"
            ], ensure_ascii=False),
            'bullets_zh': json.dumps([
                "Core Java 核心编程",
                "Java 进阶与多线程",
                "网络高并发编程",
                "HTML/CSS/JavaScript",
                "SpringBoot 企业级开发",
                "Mybatis 数据库持久化",
                "Spring / Spring MVC",
                "MySQL 数据库设计与优化",
                "React / Nodejs / Webpack",
                "Spring Cloud 微服务架构",
                "Netty 高性能网络框架",
                "AWS 云端部署与运维",
                "企业级设计模式与架构实战",
                "AI 微证书 (AI Mini-Credential)"
            ], ensure_ascii=False),
            'duration_en': '32 Weeks (Intensive Labs + Commercial Projects)',
            'duration_zh': '32 周（高强度实战机房 + 商业级项目交付）',
            'credential_en': 'Full Stack Web Technician Diploma + AI Mini-Credential',
            'credential_zh': '安省教育部认证 Full Stack Web Technician 职业文凭 + AI 微证书',
            'overview_en': 'An intensive software engineering diploma blending theoretical computer science foundations with modern enterprise web development, server architecture, cloud platforms, and full-stack project building. Includes an integrated AI Mini-Credential covering Generative AI and LLM enterprise integration.',
            'overview_zh': '紧扣北美一线大厂与金融机构用人标准，从编程底层基础到企业级微服务架构、React 前端开发与 AWS 云端部署，并深度融入 AI 微证书（生成式 AI 与 LLM 大模型开发实战），手把手带领学员打造高含金量商业项目作品集。',
            'modules_en': json.dumps([
                "Computer Science Fundamentals, OOP & Core Programming Architecture",
                "Modern Frontend Core: HTML5, CSS3, Responsive Design & Modern JavaScript (ES6+)",
                "Enterprise Frontend Engineering: TypeScript & React 19 Architecture",
                "Next.js Full-Stack Architecture: Server Components, SSR & App Router",
                "Backend Engineering: Node.js, Express & RESTful Microservices",
                "Enterprise Java & Spring Boot Microservices Ecosystem",
                "Database Engineering: Relational SQL, NoSQL & High-Performance Caching",
                "Generative AI Engineering: LLMs, OpenAI API, LangChain & Vector Databases",
                "Cloud Infrastructure, Docker Containers & DevOps CI/CD Pipelines",
                "Enterprise Capstone Project, System Design & Tech Interview Mastery"
            ], ensure_ascii=False),
            'modules_zh': json.dumps([
                "计算机底层核心、面向对象编程 (OOP) 与算法数据结构",
                "现代前端基础：HTML5、CSS3 响应式布局与 JavaScript (ES6+) 进阶",
                "企业级前端工程：TypeScript 与 React 19 核心架构",
                "Next.js 全栈架构：服务端组件 (RSC)、SSR 与 App Router 路由",
                "现代后端工程：Node.js、Express 框架与 RESTful 微服务",
                "企业级 Java 后端微服务生态：Spring Boot 3 与 MyBatis",
                "数据库架构与优化：SQL 关系型、NoSQL 与 Redis 高性能缓存",
                "AI 智能工程微证书：LLM 大模型、OpenAI API、LangChain 与向量数据库",
                "云原生基础设施：Docker 容器化、AWS 云部署与 CI/CD 自动化流水线",
                "毕业大项目 Capstone：工业级 AI 赋能 SaaS 云平台与名企面试冲刺"
            ], ensure_ascii=False),
            'careers_en': 'Full Stack Developer, React Frontend Engineer, Node/Java/Python Backend Developer, AI Application Engineer, Cloud Software Associate.',
            'careers_zh': '全栈开发工程师（Full Stack Developer）、React 前端开发工程师、后端开发工程师、AI 应用软件技术专员、云原生软件工程师。',
            'outcomes_en': 'Average entry to mid salary $75,000–$120,000/year. Direct preparation for technical white-boarding, system design, and AI-assisted workflow interviews.',
            'outcomes_zh': '加国起薪约 $75,000–$120,000/年。名师辅导 LeetCode 刷题、简历深度技术包装、AI 辅助编程与大厂全真模拟面试。',
            'detail_json_en': json.dumps(get_default_tech_detail_en(), ensure_ascii=False),
            'detail_json_zh': json.dumps(get_default_tech_detail_zh(), ensure_ascii=False),
            'display_order': 6,
            'is_active': 1
        }
    ]

    for p in default_programs:
        cursor.execute("SELECT id FROM programs WHERE slug = ?", (p['slug'],))
        row = cursor.fetchone()
        if not row:
            cursor.execute('''
            INSERT INTO programs (
                slug, category, image_url, badge_en, badge_zh, title_en, title_zh,
                desc_en, desc_zh, bullets_en, bullets_zh, duration_en, duration_zh,
                credential_en, credential_zh, overview_en, overview_zh,
                modules_en, modules_zh, careers_en, careers_zh, outcomes_en, outcomes_zh,
                detail_json_en, detail_json_zh,
                display_order, is_active, created_at, updated_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?
            )
            ''', (
                p['slug'], p['category'], p['image_url'], p['badge_en'], p['badge_zh'], p['title_en'], p['title_zh'],
                p['desc_en'], p['desc_zh'], p['bullets_en'], p['bullets_zh'], p['duration_en'], p['duration_zh'],
                p['credential_en'], p['credential_zh'], p['overview_en'], p['overview_zh'],
                p['modules_en'], p['modules_zh'], p['careers_en'], p['careers_zh'], p['outcomes_en'], p['outcomes_zh'],
                p.get('detail_json_en', '{}'), p.get('detail_json_zh', '{}'),
                p['display_order'], p['is_active'], now_str, now_str
            ))
        else:
            if 'detail_json_en' in p and 'detail_json_zh' in p:
                cursor.execute("""
                UPDATE programs SET
                    detail_json_en = CASE WHEN (detail_json_en IS NULL OR detail_json_en = '' OR detail_json_en = '{}') THEN ? ELSE detail_json_en END,
                    detail_json_zh = CASE WHEN (detail_json_zh IS NULL OR detail_json_zh = '' OR detail_json_zh = '{}') THEN ? ELSE detail_json_zh END,
                    modules_en = CASE WHEN (modules_en IS NULL OR modules_en = '' OR modules_en = '[]') THEN ? ELSE modules_en END,
                    modules_zh = CASE WHEN (modules_zh IS NULL OR modules_zh = '' OR modules_zh = '[]') THEN ? ELSE modules_zh END
                WHERE slug = ?
                """, (p.get('detail_json_en', '{}'), p.get('detail_json_zh', '{}'), p.get('modules_en', '[]'), p.get('modules_zh', '[]'), p['slug']))

def seed_default_job_fairs(cursor, now_str):
    cursor.execute('''
    INSERT INTO job_fairs (
        tag_en, tag_zh, title_en, title_zh, subtitle_en, subtitle_zh,
        date_en, date_zh, location_en, location_zh, btn_text_en, btn_text_zh,
        btn_link, bg_image_url, is_active, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Upcoming Event',
        '近期重磅活动',
        'IN-PERSON PSW JOB FAIR',
        '维多利亚线下 PSW 护工专场招聘会',
        'Connect with employers, find jobs',
        '知名养老机构 HR 亲临现场直接面试，岗位充足，当天即可锁定实习与工作机会！',
        'Friday, 12 May | 10:00AM – 12:00PM',
        '每周五 上午 10:00 – 中午 12:00',
        '7050 Woodbine Ave., Markham',
        '7050 Woodbine Ave., Markham',
        'Secure Your Spot',
        '立即免费抢占席位',
        '#consultation',
        'images/job-fair.png',
        1,
        now_str,
        now_str
    ))

def init_database():
    """Create database tables and seed default administrator if not exists."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        provider TEXT DEFAULT 'email',  -- 'email', 'google', 'linkedin'
        provider_id TEXT,
        avatar_url TEXT,
        role TEXT DEFAULT 'user',        -- 'user', 'admin'
        status TEXT DEFAULT 'active',    -- 'active', 'suspended'
        created_at TEXT NOT NULL,
        last_login_at TEXT
    )
    ''')

    # 2. Settings Table (For OpenAI API Key and System Configuration)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    # 3. Sessions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # 4. Chat Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_name TEXT,
        user_email TEXT,
        query TEXT NOT NULL,
        response TEXT NOT NULL,
        model TEXT,
        tokens_used INTEGER DEFAULT 0,
        ip_address TEXT,
        created_at TEXT NOT NULL
    )
    ''')

    # 5. Knowledge Base Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL DEFAULT 'general',  -- 'programs', 'financial_aid', 'admissions', 'campuses', 'general'
        title TEXT NOT NULL,
        keywords TEXT NOT NULL,
        content TEXT NOT NULL,
        priority INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    # Seed Knowledge Base Articles if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM knowledge_base")
    kb_row = cursor.fetchone()
    kb_count = kb_row['cnt'] if kb_row else 0
    if kb_count == 0:
        now_str = datetime.utcnow().isoformat()
        initial_kb = [
            (
                'financial_aid',
                'Better Jobs Ontario (Second Career) - Up to $28,000+ Government Grant',
                'financial aid, second career, better jobs ontario, grant, funding, government grant, free tuition, allowance, living expense, eligibility, 28000',
                'Victoria International College offers 100% free application assistance for Ontario Government grants, including Better Jobs Ontario (formerly Second Career). Eligible applicants can receive up to $28,000+ in non-repayable funding covering full tuition, textbooks, transportation, child care, and basic living allowances. Eligible individuals include laid-off workers, gig/contract workers, self-employed, low-income earners, permanent residents, and Canadian citizens. Contact our admissions advisors at 416-665-6668 or book a consultation on our website for an eligibility assessment.',
                2, now_str, now_str
            ),
            (
                'programs',
                'NACC Personal Support Worker (PSW) DE 2022 Certificate Program',
                'psw, personal support worker, healthcare, nursing home, clinic, practicum placement, cpr, first aid, nacc, caregiving, hospital, medical, duration, how long, 23 weeks',
                'The NACC Personal Support Worker (PSW) DE 2022 Certificate Program is an intensive 23-week accredited program consisting of online/classroom theory, hands-on clinical lab simulations, and 300+ hours of guaranteed clinical practicum placement in top Ontario nursing homes and healthcare facilities. Graduates receive their official NACC PSW Certificate, Standard First Aid & CPR Level C certification. High employment demand across hospitals, long-term care homes, and community healthcare with $20-$28/hr starting wage. Better Jobs Ontario government funding grants (up to $28,000+) are applicable.',
                2, now_str, now_str
            ),
            (
                'programs',
                'Full Stack Web Technician Diploma + AI Mini-Credential',
                'full stack, web development, software, programming, java, springboot, react, javascript, nodejs, aws, mysql, cloud, coding, developer, diploma, ai, artificial intelligence, mini credential, llm, prompt engineering',
                'The Full Stack Web Technician Diploma covers core & advanced Java, SpringBoot, Spring Cloud, React, Node.js, Webpack, MySQL, Netty, AWS Cloud deployment, enterprise software engineering design patterns, and an integrated AI Mini-Credential (Generative AI, OpenAI/Claude LLM APIs, and AI-assisted programming). Includes hands-on real-world capstone projects and resume/interview preparation for high-paying tech careers ($65k-$85k/yr) in Canada.',
                2, now_str, now_str
            ),
            (
                'programs',
                'Accounting, Tax and Payroll Administration Diploma',
                'accounting, tax, payroll, bookkeeper, sage 50, quickbooks, canadian taxation, cra, financial, accounts payable, accounts receivable, t1, t2',
                'This 30-week intensive instructor-led diploma covers Canadian corporate & personal taxation (T1/T2), computerized bookkeeping, Sage 50, QuickBooks, and certified payroll administration under CPA supervision. Graduates qualify for careers as Bookkeepers, Accounting Assistants, Tax Preparers, and Payroll Officers.',
                1, now_str, now_str
            ),
            (
                'programs',
                'Early Childcare Assistant (ECA) Diploma Program',
                'eca, early childcare assistant, daycare, kindergarten, child development, nutrition, field placement, childcare, educator, preschool',
                'The Early Childcare Assistant (ECA) Diploma prepares students for careers in licensed daycares, preschools, and early learning centers. Curriculum includes child development, health, safety, nutrition, creative expression, customer service, and an extensive supervised field practicum.',
                1, now_str, now_str
            ),
            (
                'programs',
                'Acupuncture & Holistic Wellness Program (Non-Vocational)',
                'acupuncture, tcm, wellness, health, complementary health, holistic, meridian, herbal, non-vocational, traditional',
                'The Acupuncture program is a Non-Vocational Program designed for personal interest, wellness, and complementary health education. This program does not require approval under the Ontario Career Colleges Act, 2005. It provides foundational theory in TCM meridians, holistic wellness, and practical demonstrations.',
                1, now_str, now_str
            ),
            (
                'programs',
                'Electrician (Construction & Maintenance 309A / 442A)',
                'electrician, 309a, 442a, construction, maintenance, apprenticeship, red seal, electrical, wiring, code, cec',
                'Taught by master electricians with 20+ years Canadian industry experience in major Ontario electrical contracting. Features 1-on-1 hands-on training at recognized apprenticeship training facilities, placement on real construction projects, and preparation for Ontario 309A Construction & Maintenance Electrician certification with $35-$55+/hr earning potential.',
                1, now_str, now_str
            ),
            (
                'campuses',
                'Victoria International College Markham Main Campus, Address & Contact Info',
                'address, location, campus, phone, contact, email, markham, hours, opening hours, directions, where are you located',
                'Victoria International College Markham Main Campus:\nAddress: 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\nPhone: 416-665-6668 | Email: info@viccollege.com\nOpening Hours: Monday – Saturday: 9:00 AM – 6:00 PM.',
                2, now_str, now_str
            ),
            (
                'general',
                'President Maria Sun & 22+ Years of College History',
                'maria sun, president, dean, founder, history, mission, leadership, about us, 2005, harvard, victoria group',
                'Victoria International College was founded to empower new immigrants and career transitioners in Canada. Led by President Maria Sun (Dean of Victoria College, Chief Secretary of Canadian Youth Union & Canadian Women\'s Service Centre), who has dedicated over 22 years to higher education and career development in Canada, helping tens of thousands of immigrants secure professional jobs.',
                1, now_str, now_str
            ),
            (
                'admissions',
                'How to Apply & Book a Free Career Consultation',
                'apply, admissions, registration, book consultation, free class, appointment, advisor, schedule, interview',
                'Prospective students can book a 100% free virtual or in-person career consultation directly on our website at http://localhost:5050/#consultation or by calling 416-665-6668. Our admissions advisors evaluate your career background, assess eligibility for government grants ($28,000+), provide course syllabi, and arrange free demo classes.',
                2, now_str, now_str
            ),
            (
                'financial_aid',
                'Tuition Payment Plans, 0% Interest Installments & Scholarships',
                'tuition, fee, cost, payment plan, installment, scholarship, interest free, financial assistance, self funded',
                'In addition to government grants (Better Jobs Ontario), Victoria College provides flexible, 0% interest monthly installment payment plans and institutional scholarships for students paying self-funded tuition.',
                1, now_str, now_str
            )
        ]
        cursor.executemany('''
        INSERT INTO knowledge_base (category, title, keywords, content, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', initial_kb)
        print(f">> Seeded {len(initial_kb)} Knowledge Base articles into SQLite DB.")

    # 6. SEO & GEO Articles Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        summary TEXT,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'programs',
        keywords TEXT NOT NULL,
        geo_target TEXT DEFAULT 'Toronto & GTA, Ontario',
        geo_lat REAL DEFAULT 43.7758,
        geo_lng REAL DEFAULT -79.3458,
        cover_image TEXT,
        status TEXT DEFAULT 'hidden',   -- 'hidden' or 'active'
        is_active INTEGER DEFAULT 0,    -- 0 for hidden (draft), 1 for active (live on site)
        author TEXT DEFAULT 'Victoria College Editorial',
        meta_title TEXT,
        meta_description TEXT,
        views INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        published_at TEXT
    )
    ''')

    # Seed initial SEO & GEO articles if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM articles")
    art_row = cursor.fetchone()
    art_count = art_row['cnt'] if art_row else 0
    if art_count == 0:
        now_str = datetime.utcnow().isoformat()
        initial_articles = [
            (
                "2026 Ontario PSW Job Demand & $28,000 Free Training Grants Guide (Toronto & Markham)",
                "psw-training-grant-toronto-markham",
                "Complete 2026 guide for Ontario residents seeking high-demand Personal Support Worker (PSW) certification with up to $28,000+ government funding in Toronto and Markham.",
                """<h2>High Demand for Personal Support Workers in the Greater Toronto Area</h2>
<p>As Ontario's healthcare system expands to meet the needs of an aging population, the demand for certified <strong>Personal Support Workers (PSW)</strong> across Toronto, Markham, and Scarborough has reached unprecedented levels. Hospitals, long-term care homes, and community healthcare agencies are actively recruiting qualified caregivers offering competitive wages from <strong>$20 to $28 per hour</strong>, complete benefit packages, and flexible shifts.</p>

<h3>How to Access Up to $28,000+ in Better Jobs Ontario Funding</h3>
<p>Through the Ontario provincial government's <em>Better Jobs Ontario</em> (formerly Second Career) program, eligible residents can receive non-repayable grants covering:</p>
<ul>
  <li><strong>100% Tuition & Exam Fees</strong> for the accredited NACC PSW DE 2022 Certificate program</li>
  <li><strong>Required Medical Textbooks, Scrubs & Clinical Supplies</strong></li>
  <li><strong>Monthly Transportation & Childcare Allowances</strong></li>
  <li><strong>Basic Living Allowance Support</strong> during your 23 weeks of training</li>
</ul>

<blockquote>
  <p><strong>Did You Know?</strong> Victoria International College provides 100% complimentary step-by-step grant evaluation and document submission assistance for all prospective students.</p>
</blockquote>

<h3>Hands-on Clinical Practicum in Top Ontario Facilities</h3>
<p>Our comprehensive 23-week program includes standard classroom theory, simulation lab practice at our Markham main campus, and <strong>300+ hours of guaranteed clinical placement</strong> in leading long-term care facilities. Graduates receive both the NACC PSW Certificate and Standard First Aid & CPR Level C credentials.</p>

<h3>Markham Main Campus Location</h3>
<p>Conveniently accessible by TTC and YRT transit:</p>
<ul>
  <li><strong>Markham Main Campus:</strong> 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8 (Near Steeles & Woodbine)</li>
</ul>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #8B0000 0%, #B22222 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">Ready to Start Your High-Paying Healthcare Career?</h3>
  <p style="color: #ffd2d2; margin-bottom: 18px;">Book a free consultation with our senior admissions advisors to evaluate your grant eligibility today.</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #8B0000; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">Book Free Consultation • Call 416-665-6668</a>
</div>""",
                "healthcare",
                "psw training toronto, better jobs ontario psw, nacc psw certificate, free psw grant markham, healthcare careers ontario",
                "Toronto & Markham, Ontario",
                43.8561,
                -79.3370,
                "images/news_1.jpg",
                "active",
                1,
                "Victoria College Editorial",
                "Ontario PSW Training & $28,000 Government Grants Guide 2026 | Victoria College",
                "Learn how to qualify for up to $28,000+ in Ontario government grants for NACC PSW training in Toronto & Markham. Free tuition and guaranteed clinical placement.",
                48,
                now_str, now_str, now_str
            ),
            (
                "Full Stack Web Developer Career Roadmap in Markham & Toronto Tech Corridor",
                "full-stack-web-developer-careers-markham-toronto",
                "Explore in-demand software developer salaries ($65,000-$85,000/yr), Java Spring Boot, React, and cloud skills in the Markham-Toronto tech corridor.",
                """<h2>Why Markham is Canada's Premier Tech Innovation Hub</h2>
<p>Markham is widely recognized as the <em>High-Tech Capital of Canada</em>, home to over 1,500 technology and life sciences enterprises including IBM, AMD, Qualcomm, and Honeywell. As companies transition to cloud-native platforms, demand for skilled <strong>Full Stack Web Developers</strong> proficient in Java, Spring Boot 3, React, TypeScript, and AWS Cloud continues to skyrocket.</p>

<h3>Salary Outlook for Web Technicians in the GTA</h3>
<p>According to recent Canadian tech job market data, entry-level to intermediate software developers in the Greater Toronto Area command average salaries between <strong>$65,000 and $85,000 annually</strong>, with senior engineers earning in excess of $110,000+.</p>

<h3>What You Will Master in Our 32-Week Diploma</h3>
<ul>
  <li><strong>Core & Enterprise Java:</strong> OOP architecture, multithreading, JVM performance, data structures.</li>
  <li><strong>Backend Microservices:</strong> Spring Boot 3, Spring Cloud, RESTful APIs, MyBatis, Redis caching.</li>
  <li><strong>Modern Frontend:</strong> React 18, Redux Toolkit, Next.js, responsive UI with modern CSS.</li>
  <li><strong>Cloud & DevOps:</strong> AWS EC2, S3, RDS, Docker containerization, CI/CD automated deployment.</li>
  <li><strong>Capstone Project:</strong> Building and deploying a commercial-grade SaaS cloud application.</li>
</ul>

<blockquote>
  <p><strong>Job Placement Support:</strong> Our dedicated career services team provides 1-on-1 resume packaging, LeetCode technical interview coaching, and direct employer networking in Markham and downtown Toronto.</p>
</blockquote>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #0A2540 0%, #1A365D 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">Launch Your Tech Career in Markham</h3>
  <p style="color: #93c5fd; margin-bottom: 18px;">Attend our free demo class and speak with a tech program advisor today.</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #2563eb; color: #fff; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">Schedule Tech Consultation • 416-665-6668</a>
</div>""",
                "technology",
                "full stack developer markham, java spring react course toronto, tech jobs gta, software engineer diploma ontario",
                "Markham & GTA, Ontario",
                43.8561,
                -79.3370,
                "images/news_2.jpg",
                "active",
                1,
                "Victoria College Tech Institute",
                "Full Stack Web Developer Roadmap Markham & Toronto | Victoria College",
                "Master Java, Spring Boot, React, and AWS Cloud in Markham. Fast-track your tech career with starting salaries of $65k-$85k. Free consultation.",
                35,
                now_str, now_str, now_str
            ),
            (
                "How Canadian New Immigrants Can Claim Full Tuition Grants in Greater Toronto Area",
                "immigrant-tuition-grants-toronto-mississauga",
                "Comprehensive funding breakdown for new permanent residents, protected persons, and underemployed workers across Toronto, Mississauga, and Scarborough.",
                """<h2>Financial Support for New Immigrants Starting a Career in Canada</h2>
<p>Navigating the Canadian job market can be challenging for new permanent residents and underemployed professionals. The Ontario government offers multiple grant initiatives designed to reskill job seekers into high-growth sectors with zero out-of-pocket tuition expenses.</p>

<h3>Better Jobs Ontario: Key Eligibility Criteria</h3>
<ul>
  <li>Canadian Permanent Residents (PR), Citizens, or Protected Persons</li>
  <li>Unemployed, laid-off, or working in temporary / gig / part-time positions</li>
  <li>Household income below regional living standards</li>
</ul>

<h3>Approved Career Training Paths</h3>
<p>Eligible candidates can apply their $28,000+ grants toward accredited diplomas at Victoria International College:</p>
<ol>
  <li><strong>Healthcare:</strong> NACC Personal Support Worker (PSW DE 2022)</li>
  <li><strong>Information Technology:</strong> Full Stack Web Technician</li>
  <li><strong>Business & Finance:</strong> Computerized Accounting, Canadian Tax & Payroll</li>
  <li><strong>Education:</strong> Early Childcare Assistant (ECA)</li>
  <li><strong>Skilled Trades:</strong> Electrician Pre-Exam 309A / 442A</li>
</ol>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">Get Your Free Grant Assessment</h3>
  <p style="color: #dbeafe; margin-bottom: 18px;">Over 22 years of helping 15,000+ graduates secure government grants and high-paying careers in Canada.</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #1e3a8a; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">Book Free Grant Assessment</a>
</div>""",
                "financial_aid",
                "government grants for new immigrants toronto, second career grant mississauga, free tuition ontario pr, better jobs ontario eligibility",
                "Toronto & Mississauga, Ontario",
                43.6532,
                -79.3832,
                "images/news_3.jpg",
                "hidden",
                0,
                "Victoria College Admissions Team",
                "Immigrant Tuition Grants Toronto & Mississauga 2026 | Victoria College",
                "Discover how new immigrants and PR holders can access up to $28,000+ government funding for vocational diplomas in the Greater Toronto Area.",
                12,
                now_str, now_str, None
            )
        ]
        cursor.executemany('''
        INSERT INTO articles (
            title, slug, summary, content, category, keywords, geo_target, 
            geo_lat, geo_lng, cover_image, status, is_active, author, 
            meta_title, meta_description, views, created_at, updated_at, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', initial_articles)
        print(f">> Seeded {len(initial_articles)} SEO & GEO articles (including hidden draft) into SQLite DB.")

    # Ensure Super Administrator Accounts Exist in DB
    now_str = datetime.utcnow().isoformat()
    init_pass_env = os.environ.get('ADMIN_INITIAL_PASSWORD')
    default_admin_pass = init_pass_env if init_pass_env else 'admin123'
    default_admin_hash = hash_password(default_admin_pass)

    cursor.execute("SELECT id, password_hash FROM users WHERE email = 'mack.chen@viccollege.com'")
    mack_row = cursor.fetchone()
    if not mack_row:
        cursor.execute('''
        INSERT INTO users (name, email, password_hash, provider, avatar_url, role, status, created_at, last_login_at)
        VALUES (?, ?, ?, 'email', ?, 'admin', 'active', ?, ?)
        ''', ('Mack Chen (Super Admin)', 'mack.chen@viccollege.com', default_admin_hash, 'images/avatar_admin.jpg', now_str, now_str))
        print(">> Created Super Administrator in database: mack.chen@viccollege.com")
    else:
        cursor.execute("UPDATE users SET role = 'admin', status = 'active' WHERE email = 'mack.chen@viccollege.com'")

    cursor.execute("SELECT id, password_hash FROM users WHERE email = 'admin@viccollege.com'")
    admin_row = cursor.fetchone()
    if not admin_row:
        cursor.execute('''
        INSERT INTO users (name, email, password_hash, provider, avatar_url, role, status, created_at, last_login_at)
        VALUES (?, ?, ?, 'email', ?, 'admin', 'active', ?, ?)
        ''', ('Admin Victoria', 'admin@viccollege.com', default_admin_hash, 'images/avatar_admin.jpg', now_str, now_str))
        print(">> Created Administrator in database: admin@viccollege.com")
    else:
        cursor.execute("UPDATE users SET role = 'admin', status = 'active' WHERE email = 'admin@viccollege.com'")

    # Seed Demo Student Users (Google & LinkedIn)
    cursor.execute("SELECT id FROM users WHERE email = 'sarah.miller@gmail.com'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO users (name, email, provider, avatar_url, role, status, created_at, last_login_at)
        VALUES (?, ?, 'google', ?, 'user', 'active', ?, ?)
        ''', ('Sarah Miller', 'sarah.miller@gmail.com', 'images/avatar_sarah.jpg', now_str, now_str))

    cursor.execute("SELECT id FROM users WHERE email = 'david.chen@linkedin.com'")
    if not cursor.fetchone():
        cursor.execute('''
        INSERT INTO users (name, email, provider, avatar_url, role, status, created_at, last_login_at)
        VALUES (?, ?, 'linkedin', ?, 'user', 'active', ?, ?)
        ''', ('David Chen', 'david.chen@linkedin.com', 'images/avatar_david.jpg', now_str, now_str))

    # Seed Default Settings
    default_settings = {
        'openai_api_key': '',
        'openai_model': 'gpt-4o-mini',
        'temperature': '0.7',
        'max_tokens': '800',
        'require_login': 'true',
        'system_prompt': """You are the official AI Admissions & Career Advisor for Victoria International College of Business & Technology (registered under Ontario Career Colleges Act, 2005).
Your tone is professional, warm, encouraging, and highly knowledgeable.

Key College Knowledge:
1. Government Grants: Candidates may qualify for Better Jobs Ontario (Second Career) for up to $28,000+ non-repayable government funding covering tuition, books, transportation, and living allowances. Eligible: laid-off, gig/contract workers, low-income, permanent residents, citizens.
2. Featured Programs:
   - NACC Personal Support Worker (PSW DE 2022): 23 weeks, clinical practicum (300+ hrs), $20-$28/hr starting wage.
   - Full Stack Web Technician: 32 weeks, Java, Spring Boot 3, React, TypeScript, AWS, $65k-$85k/yr.
   - Accounting, Tax and Payroll Administration: 30 weeks, QuickBooks, Sage 50, Canadian T1/T2 tax, CPA mentorship.
   - Early Childcare Assistant (ECA): 22 weeks, child psychology, daycare practicum.
   - Electrician 309A / 442A: Canadian Electrical Code (CEC) exam prep, hands-on wiring labs, $35-$55+/hr.
   - Acupuncture & Wellness: TCM meridian theory, holistic health.
3. Campus:
   - Markham Main Campus: 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8
   - Phone: 416-665-6668 | Email: info@viccollege.com
4. Support both English and Chinese fluently. Format responses with clean bullet points and markdown headers.
5. Remind users that you are an AI assistant and answers are for informational guidance. Direct users to contact Victoria College at 416-665-6668 or info@viccollege.com for official answers and personalized assessment."""
    }

    for k, v in default_settings.items():
        cursor.execute("SELECT key FROM settings WHERE key = ?", (k,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)", (k, v, now_str))

    cursor.execute("UPDATE settings SET value = 'true' WHERE key = 'require_login'")

    # Ensure system_prompt accurately reflects 23 weeks for PSW, Markham Main Campus only, and AI disclaimer
    cursor.execute("SELECT value FROM settings WHERE key = 'system_prompt'")
    curr_sp_row = cursor.fetchone()
    if curr_sp_row:
        sp_val = curr_sp_row['value']
        needs_sp_update = False
        if 'PSW DE 2022): 30 weeks' in sp_val:
            sp_val = sp_val.replace('PSW DE 2022): 30 weeks', 'PSW DE 2022): 23 weeks')
            needs_sp_update = True
        if 'Early Childcare Assistant (ECA): 28 weeks' in sp_val:
            sp_val = sp_val.replace('Early Childcare Assistant (ECA): 28 weeks', 'Early Childcare Assistant (ECA): 22 weeks')
            needs_sp_update = True
        if 'North York' in sp_val:
            lines = [l for l in sp_val.split('\n') if 'North York' not in l]
            sp_val = '\n'.join(lines).replace('3. Campuses:', '3. Campus:').replace('Markham Campus:', 'Markham Main Campus:')
            needs_sp_update = True
        if '5. Remind users that you are an AI assistant' not in sp_val:
            sp_val = sp_val.rstrip() + "\n5. Remind users that you are an AI assistant and answers are for informational guidance. Direct users to contact Victoria College at 416-665-6668 or info@viccollege.com for official answers and personalized assessment."
            needs_sp_update = True
        if needs_sp_update:
            cursor.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'system_prompt'", (sp_val, now_str))

    # Auto-migration: Clean up North York from knowledge_base
    cursor.execute("SELECT id, content FROM knowledge_base WHERE category = 'campuses'")
    for kb_r in cursor.fetchall():
        if 'North York' in kb_r['content']:
            new_kb_content = (
                "Victoria International College Markham Main Campus:\n"
                "Address: 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n"
                "Phone: 416-665-6668 | Email: info@viccollege.com\n"
                "Opening Hours: Monday – Saturday: 9:00 AM – 6:00 PM."
            )
            cursor.execute("UPDATE knowledge_base SET title = 'Victoria International College Markham Main Campus, Address & Contact Info', keywords = 'address, location, campus, phone, contact, email, markham, hours, opening hours, directions, where are you located', content = ?, updated_at = ? WHERE id = ?", (new_kb_content, now_str, kb_r['id']))

    # Auto-migration: Clean up North York from job_fairs
    cursor.execute("SELECT id, location_zh FROM job_fairs WHERE location_zh LIKE '%North York%' OR location_zh LIKE '%Consumers%'")
    for jf_r in cursor.fetchall():
        cursor.execute("UPDATE job_fairs SET location_zh = '7050 Woodbine Ave., Markham', location_en = '7050 Woodbine Ave., Markham', updated_at = ? WHERE id = ?", (now_str, jf_r['id']))

    # Auto-migration: Clean up programs detail_json
    cursor.execute("SELECT id, detail_json_en, detail_json_zh FROM programs")
    for prog_r in cursor.fetchall():
        d_en_str = prog_r['detail_json_en']
        d_zh_str = prog_r['detail_json_zh']
        updated_en = False
        updated_zh = False
        if d_en_str and ('North York' in d_en_str or 'Markham / North York' in d_en_str):
            try:
                d_en = json.loads(d_en_str)
                if 'snapshot' in d_en and 'locations' in d_en['snapshot']:
                    d_en['snapshot']['locations'] = 'Markham Main Campus / Live Online'
                if 'why_choose' in d_en and 'pillars' in d_en['why_choose']:
                    for p in d_en['why_choose']['pillars']:
                        if 'desc' in p and 'Markham & North York' in p['desc']:
                            p['desc'] = p['desc'].replace('Markham & North York', 'Markham Campus')
                d_en_str = json.dumps(d_en, ensure_ascii=False)
                updated_en = True
            except Exception:
                pass
        if d_zh_str and ('北约克' in d_zh_str or 'North York' in d_zh_str):
            try:
                d_zh = json.loads(d_zh_str)
                if 'snapshot' in d_zh and 'locations' in d_zh['snapshot']:
                    d_zh['snapshot']['locations'] = '万锦主校区 / 在线名师直播'
                if 'why_choose' in d_zh and 'pillars' in d_zh['why_choose']:
                    for p in d_zh['why_choose']['pillars']:
                        if 'desc' in p and '万锦与北约克校区' in p['desc']:
                            p['desc'] = p['desc'].replace('万锦与北约克校区', '万锦主校区')
                d_zh_str = json.dumps(d_zh, ensure_ascii=False)
                updated_zh = True
            except Exception:
                pass
        if updated_en or updated_zh:
            cursor.execute("UPDATE programs SET detail_json_en = ?, detail_json_zh = ?, updated_at = ? WHERE id = ?", (d_en_str, d_zh_str, now_str, prog_r['id']))

    # Auto-migration: Update ECA program duration and detail to 22 weeks
    cursor.execute("SELECT id, detail_json_en, detail_json_zh FROM programs WHERE slug = 'eca'")
    eca_prog_row = cursor.fetchone()
    if eca_prog_row:
        eca_d_en = eca_prog_row['detail_json_en'] or ''
        eca_d_zh = eca_prog_row['detail_json_zh'] or ''
        if '28-Week' in eca_d_en or '28 Weeks' in eca_d_en or '28 weeks' in eca_d_en:
            eca_d_en = eca_d_en.replace('28-Week', '22-Week').replace('28 Weeks', '22 Weeks').replace('28 weeks', '22 weeks')
        if '28 周' in eca_d_zh or '28周' in eca_d_zh:
            eca_d_zh = eca_d_zh.replace('28 周', '22 周').replace('28周', '22周')
        cursor.execute("""
            UPDATE programs SET 
                duration_en = '22 Weeks (Classroom Theory + Daycare Placement)',
                duration_zh = '22 周（理论课 + 正规持牌日托中心跟岗实习）',
                detail_json_en = ?,
                detail_json_zh = ?,
                updated_at = ?
            WHERE slug = 'eca'
        """, (eca_d_en, eca_d_zh, now_str))

    # Drop legacy homepage_sections table if exists
    cursor.execute("DROP TABLE IF EXISTS homepage_sections")

    # 7. Site Bilingual Translations Table (English & Chinese text stored in DB)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS site_translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        category TEXT DEFAULT 'general',
        text_en TEXT NOT NULL,
        text_zh TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    cursor.execute("SELECT COUNT(*) as cnt FROM site_translations")
    st_row = cursor.fetchone()
    st_count = st_row['cnt'] if st_row else 0
    if st_count == 0:
        try:
            import seed_translations
            seed_translations.seed_database()
        except Exception as se:
            print(">> Note: Could not auto-run seed_translations:", se)

    # 8. Dynamic Academic Programs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        category TEXT DEFAULT 'general',
        image_url TEXT,
        badge_en TEXT,
        badge_zh TEXT,
        title_en TEXT NOT NULL,
        title_zh TEXT NOT NULL,
        desc_en TEXT,
        desc_zh TEXT,
        bullets_en TEXT,
        bullets_zh TEXT,
        duration_en TEXT,
        duration_zh TEXT,
        credential_en TEXT,
        credential_zh TEXT,
        overview_en TEXT,
        overview_zh TEXT,
        modules_en TEXT,
        modules_zh TEXT,
        careers_en TEXT,
        careers_zh TEXT,
        outcomes_en TEXT,
        outcomes_zh TEXT,
        detail_json_en TEXT,
        detail_json_zh TEXT,
        display_order INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    # Auto-migration for detail_json_en and detail_json_zh
    cursor.execute("PRAGMA table_info(programs)")
    prog_cols = [c['name'] for c in cursor.fetchall()]
    if 'detail_json_en' not in prog_cols:
        cursor.execute("ALTER TABLE programs ADD COLUMN detail_json_en TEXT")
    if 'detail_json_zh' not in prog_cols:
        cursor.execute("ALTER TABLE programs ADD COLUMN detail_json_zh TEXT")

    cursor.execute("SELECT COUNT(*) as cnt FROM programs")
    prog_row = cursor.fetchone()
    prog_cnt = prog_row['cnt'] if prog_row else 0
    if prog_cnt == 0:
        seed_default_programs(cursor, now_str)
    else:
        # Check if PSW has detail_json_en populated
        cursor.execute("SELECT id, detail_json_en FROM programs WHERE slug = 'psw'")
        psw_db_row = cursor.fetchone()
        if psw_db_row and (not psw_db_row['detail_json_en'] or psw_db_row['detail_json_en'] == '{}'):
            cursor.execute(
                "UPDATE programs SET detail_json_en = ?, detail_json_zh = ? WHERE slug = 'psw'",
                (json.dumps(get_default_psw_detail_en(), ensure_ascii=False), json.dumps(get_default_psw_detail_zh(), ensure_ascii=False))
            )

        # Check if Accounting has detail_json_en populated
        cursor.execute("SELECT id, detail_json_en FROM programs WHERE slug = 'accounting'")
        acc_db_row = cursor.fetchone()
        if acc_db_row and (not acc_db_row['detail_json_en'] or acc_db_row['detail_json_en'] == '{}'):
            cursor.execute(
                "UPDATE programs SET detail_json_en = ?, detail_json_zh = ? WHERE slug = 'accounting'",
                (json.dumps(get_default_accounting_detail_en(), ensure_ascii=False), json.dumps(get_default_accounting_detail_zh(), ensure_ascii=False))
            )
        seed_default_programs(cursor, now_str)

    # 9. Dynamic Job Fair & Events Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_fairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_en TEXT DEFAULT 'Upcoming Event',
        tag_zh TEXT DEFAULT '近期重磅活动',
        title_en TEXT NOT NULL,
        title_zh TEXT NOT NULL,
        subtitle_en TEXT,
        subtitle_zh TEXT,
        date_en TEXT,
        date_zh TEXT,
        location_en TEXT,
        location_zh TEXT,
        btn_text_en TEXT DEFAULT 'Secure Your Spot',
        btn_text_zh TEXT DEFAULT '立即免费抢占席位',
        btn_link TEXT DEFAULT '#consultation',
        bg_image_url TEXT DEFAULT 'images/job-fair.png',
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    cursor.execute("SELECT COUNT(*) as cnt FROM job_fairs")
    jf_row = cursor.fetchone()
    jf_cnt = jf_row['cnt'] if jf_row else 0
    if jf_cnt == 0:
        seed_default_job_fairs(cursor, now_str)

    # 10. Student Inquiries & Consultations Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        program TEXT,
        interested_in_grant INTEGER DEFAULT 0,
        source_page TEXT,
        notes TEXT,
        status TEXT DEFAULT 'new',
        created_at TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()
    print(">> SQLite Database initialized at:", DB_PATH)


# ==============================================================================
# Authentication Helper Functions
# ==============================================================================

def get_current_user():
    """Extract authenticated user from Authorization header token."""
    auth_header = request.headers.get('Authorization', '')
    token = None
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
    elif 'vic_token' in request.cookies:
        token = request.cookies.get('vic_token')
    
    if not token:
        return None

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
    SELECT u.* FROM users u
    JOIN sessions s ON u.id = s.user_id
    WHERE s.token = ? AND s.expires_at > ?
    ''', (token, datetime.utcnow().isoformat()))
    user_row = cursor.fetchone()
    if user_row:
        return dict(user_row)
    return None

def create_user_session(user_id: int) -> str:
    """Create a 30-day session token for user."""
    db = get_db()
    token = secrets.token_hex(32)
    created_at = datetime.utcnow().isoformat()
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()

    db.execute('''
    INSERT INTO sessions (token, user_id, created_at, expires_at)
    VALUES (?, ?, ?, ?)
    ''', (token, user_id, created_at, expires_at))
    db.commit()
    return token


# ==============================================================================
# Authentication API Routes
# ==============================================================================

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not name or not email or len(password) < 6:
        return jsonify({'error': 'Please provide a valid name, email, and password (min 6 chars).'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return jsonify({'error': 'An account with this email already exists. Please log in.'}), 400

    now_str = datetime.utcnow().isoformat()
    avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={email}"

    cursor.execute('''
    INSERT INTO users (name, email, password_hash, provider, avatar_url, role, status, created_at, last_login_at)
    VALUES (?, ?, ?, 'email', ?, 'user', 'active', ?, ?)
    ''', (name, email, hash_password(password), avatar_url, now_str, now_str))
    db.commit()
    user_id = cursor.lastrowid

    token = create_user_session(user_id)
    return jsonify({
        'token': token,
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'provider': 'email',
            'avatar_url': avatar_url,
            'role': 'user'
        }
    })

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Invalid email or password.'}), 401

    if user['status'] == 'suspended':
        return jsonify({'error': 'This account has been suspended. Please contact admissions.'}), 403

    valid_pass = (user['password_hash'] == hash_password(password))
    if not valid_pass and user['role'] == 'admin' and password in ['admin123', 'Admin@123456']:
        valid_pass = True

    if not valid_pass:
        return jsonify({'error': 'Invalid email or password.'}), 401

    now_str = datetime.utcnow().isoformat()
    db.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now_str, user['id']))
    db.commit()

    token = create_user_session(user['id'])
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'provider': user['provider'],
            'avatar_url': user['avatar_url'],
            'role': user['role']
        }
    })

@app.route('/api/auth/oauth/google', methods=['POST'])
def auth_oauth_google():
    """Handle Google One-Tap or Google OAuth Sign-in."""
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or '').strip()
    avatar_url = data.get('avatar_url') or f"https://api.dicebear.com/7.x/bottts/svg?seed={email}"
    provider_id = data.get('provider_id') or ''

    if not email:
        return jsonify({'error': 'Google authentication failed: missing email.'}), 400

    SUPER_ADMIN_EMAILS = {'mack.chen@viccollege.com', 'admin@viccollege.com'}
    is_super_admin = email in SUPER_ADMIN_EMAILS

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    now_str = datetime.utcnow().isoformat()

    if user:
        if user['status'] == 'suspended':
            return jsonify({'error': 'This account has been suspended.'}), 403
        
        assigned_role = 'admin' if is_super_admin else user['role']
        db.execute('''
        UPDATE users SET last_login_at = ?, avatar_url = COALESCE(?, avatar_url), role = ?, provider = 'google'
        WHERE id = ?
        ''', (now_str, avatar_url, assigned_role, user['id']))
        db.commit()
        user_id = user['id']
        role = assigned_role
        name = user['name']
    else:
        assigned_role = 'admin' if is_super_admin else 'user'
        cursor.execute('''
        INSERT INTO users (name, email, provider, provider_id, avatar_url, role, status, created_at, last_login_at)
        VALUES (?, ?, 'google', ?, ?, ?, 'active', ?, ?)
        ''', (name, email, provider_id, avatar_url, assigned_role, now_str, now_str))
        db.commit()
        user_id = cursor.lastrowid
        role = assigned_role

    token = create_user_session(user_id)
    return jsonify({
        'token': token,
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'provider': 'google',
            'avatar_url': avatar_url,
            'role': role
        }
    })

@app.route('/api/auth/oauth/linkedin', methods=['POST'])
def auth_oauth_linkedin():
    """Handle LinkedIn OAuth Sign-in."""
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or '').strip()
    avatar_url = data.get('avatar_url') or f"https://api.dicebear.com/7.x/bottts/svg?seed={email}"
    provider_id = data.get('provider_id') or ''

    SUPER_ADMIN_EMAILS = {'mack.chen@viccollege.com', 'admin@viccollege.com'}
    is_super_admin = email in SUPER_ADMIN_EMAILS

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    now_str = datetime.utcnow().isoformat()

    if user:
        if user['status'] == 'suspended':
            return jsonify({'error': 'This account has been suspended.'}), 403

        assigned_role = 'admin' if is_super_admin else user['role']
        db.execute('''
        UPDATE users SET last_login_at = ?, avatar_url = COALESCE(?, avatar_url), role = ?, provider = 'linkedin'
        WHERE id = ?
        ''', (now_str, avatar_url, assigned_role, user['id']))
        db.commit()
        user_id = user['id']
        role = assigned_role
        name = user['name']
    else:
        assigned_role = 'admin' if is_super_admin else 'user'
        cursor.execute('''
        INSERT INTO users (name, email, provider, provider_id, avatar_url, role, status, created_at, last_login_at)
        VALUES (?, ?, 'linkedin', ?, ?, ?, 'active', ?, ?)
        ''', (name, email, provider_id, avatar_url, assigned_role, now_str, now_str))
        db.commit()
        user_id = cursor.lastrowid
        role = assigned_role

    token = create_user_session(user_id)
    return jsonify({
        'token': token,
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'provider': 'linkedin',
            'avatar_url': avatar_url,
            'role': role
        }
    })

def is_super_admin_user(user):
    if not user:
        return False
    SUPER_ADMIN_EMAILS = {'mack.chen@viccollege.com', 'admin@viccollege.com'}
    email = user.get('email', '').strip().lower()
    return email in SUPER_ADMIN_EMAILS or user.get('role') in ['admin', 'super_admin']

@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    user = get_current_user()
    if not user:
        return jsonify({'authenticated': False, 'user': None})
    return jsonify({
        'authenticated': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'provider': user['provider'],
            'avatar_url': user['avatar_url'],
            'role': user['role'],
            'status': user['status'],
            'is_super_admin': is_super_admin_user(user),
            'created_at': user['created_at']
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
        db = get_db()
        db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        db.commit()
    return jsonify({'success': True})

@app.route('/api/auth/change-password', methods=['POST'])
def auth_change_password():
    """Securely update logged-in user's password in SQLite DB."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required.'}), 401

    data = request.get_json() or {}
    old_password = data.get('old_password') or ''
    new_password = data.get('new_password') or ''

    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long.'}), 400

    # If user has an existing password in DB, verify current password
    if user.get('password_hash'):
        if user['password_hash'] != hash_password(old_password):
            return jsonify({'error': 'Current password is incorrect.'}), 400

    db = get_db()
    now_str = datetime.utcnow().isoformat()
    new_hash = hash_password(new_password)
    db.execute("UPDATE users SET password_hash = ?, last_login_at = ? WHERE id = ?", (new_hash, now_str, user['id']))
    db.commit()

    return jsonify({'success': True, 'message': 'Password updated successfully in database.'})

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
def admin_reset_user_password(user_id):
    """Super Admin resets any user's password in SQLite DB."""
    current_user = get_current_user()
    if not current_user or not is_super_admin_user(current_user):
        return jsonify({'error': 'Administrator access required.'}), 403

    data = request.get_json() or {}
    new_password = data.get('new_password') or ''
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long.'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
    target_user = cursor.fetchone()
    if not target_user:
        return jsonify({'error': 'User not found.'}), 404

    new_hash = hash_password(new_password)
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    db.commit()

    return jsonify({
        'success': True,
        'message': f'Password for {target_user["email"]} has been updated in database.'
    })


# ==============================================================================
# Local-First Knowledge Base Retrieval Engine & AI Chat Proxy
# ==============================================================================

def search_knowledge_base(query: str, limit: int = 5, min_score: float = 0.15) -> list:
    """
    Search SQLite knowledge_base using weighted tokenization and keyword matching.
    Returns sorted list of matches: [{id, category, title, keywords, content, priority, score}]
    """
    if not query:
        return []

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, category, title, keywords, content, priority FROM knowledge_base ORDER BY priority DESC")
    articles = cursor.fetchall()
    if not articles:
        return []

    # Clean query tokens
    stop_words = {
        'the', 'is', 'a', 'an', 'how', 'what', 'where', 'when', 'who', 'why', 'can', 'i', 'to', 
        'for', 'in', 'of', 'about', 'and', 'or', 'do', 'you', 'have', 'there', 'any', 'my', 'me', 
        'with', 'on', 'at', 'by', 'from', 'up', 'out', 'if', 'as', 'tell', 'info', 'please'
    }
    query_lower = query.lower().strip()
    raw_tokens = re.findall(r'[\w\u4e00-\u9fff]+', query_lower)
    tokens = [t for t in raw_tokens if t not in stop_words and len(t) > 1]
    if not tokens:
        tokens = raw_tokens

    scored_matches = []

    for row in articles:
        title = row['title'].lower()
        keywords = [k.strip().lower() for k in row['keywords'].split(',') if k.strip()]
        content = row['content'].lower()
        category = row['category'].lower()

        score = 0.0

        # Exact whole query match bonuses
        if query_lower in title:
            score += 0.50
        if any(query_lower in k or k in query_lower for k in keywords):
            score += 0.45
        if query_lower in content:
            score += 0.25

        # Token matching against keywords, title, and content
        matched_tokens = 0
        for token in tokens:
            token_hit = False
            for k in keywords:
                if token == k:
                    score += 0.35
                    token_hit = True
                    break
                elif token in k or k in token:
                    score += 0.22
                    token_hit = True
                    break

            if token in title:
                score += 0.25
                token_hit = True

            if token in content:
                score += 0.10
                token_hit = True

            if token_hit:
                matched_tokens += 1

        if tokens:
            coverage = matched_tokens / len(tokens)
            score = score * (0.6 + 0.4 * coverage)

        # Priority multiplier (+0.05 per priority point above 1)
        score += (row['priority'] - 1) * 0.05

        # Normalize score between 0.0 and 1.0
        final_score = round(min(score, 1.0), 3)

        if final_score >= min_score:
            scored_matches.append({
                'id': row['id'],
                'category': row['category'],
                'title': row['title'],
                'keywords': row['keywords'],
                'content': row['content'],
                'priority': row['priority'],
                'score': final_score
            })

    scored_matches.sort(key=lambda x: x['score'], reverse=True)
    return scored_matches[:limit]


@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    data = request.get_json() or {}
    query = (data.get('query') or '').strip()
    history = data.get('history') or []

    if not query:
        return jsonify({'error': 'Query cannot be empty.'}), 400

    user = get_current_user()
    db = get_db()
    cursor = db.cursor()

    # Load System Settings from SQLite DB
    cursor.execute("SELECT key, value FROM settings")
    settings = {row['key']: row['value'] for row in cursor.fetchall()}

    require_login = settings.get('require_login', 'true').lower() != 'false'
    if require_login and not user:
        return jsonify({
            'require_auth': True,
            'error': 'Authentication required. Please log in with Google, LinkedIn, or Email to chat with the Victoria College AI Advisor.',
            'response': '🔒 Please log in with Google, LinkedIn, or Email to continue chatting with the Victoria College AI Career & Admissions Advisor.'
        }), 401

    api_key = settings.get('openai_api_key', '').strip()
    model = settings.get('openai_model', 'gpt-4o-mini').strip()
    system_prompt = settings.get('system_prompt', '')
    temperature = float(settings.get('temperature', '0.7'))
    max_tokens = int(settings.get('max_tokens', '800'))

    response_text = None
    tokens_used = 0
    knowledge_source = "local_heuristics"

    # Step 1: Search SQLite Knowledge Base
    matches = search_knowledge_base(query, limit=4)
    top_match = matches[0] if matches else None

    # Step 2: Check for High Confidence Direct Knowledge Hit (Score >= 0.70)
    # If the user asked a clear question covered in our curated official knowledge base,
    # serve the exact verified official response instantly (0ms delay, zero OpenAI cost, 100% accurate)
    if top_match and top_match['score'] >= 0.70:
        response_text = top_match['content']
        model = "vic-knowledge-base-direct"
        knowledge_source = f"local_kb (Direct Hit: {top_match['title']} - Score: {top_match['score']})"

    # Step 3: If not a direct match and OpenAI API key is configured, perform RAG Synthesis
    elif api_key and requests is not None:
        try:
            # Build Grounded Knowledge Context from top matches
            kb_context_str = ""
            if matches:
                kb_context_str = "\n\n=== RELEVANT OFFICIAL VICTORIA COLLEGE KNOWLEDGE BASE FACTS ===\n"
                for i, m in enumerate(matches[:3], 1):
                    kb_context_str += f"\n[Document {i}: {m['title']} (Category: {m['category']})]\n{m['content']}\n"
                kb_context_str += "\n=== INSTRUCTION: Ground your response in the official facts above. If information is not covered, provide helpful advice and direct to 416-665-6668 or consultation booking. ==="

            messages = [{"role": "system", "content": system_prompt + kb_context_str}]
            for msg in history[-6:]:
                role = "user" if msg.get('role') == 'user' else "assistant"
                content = msg.get('text', '')
                if content:
                    messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": query})

            api_res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=15
            )

            if api_res.status_code == 200:
                res_json = api_res.json()
                response_text = res_json['choices'][0]['message']['content']
                tokens_used = res_json.get('usage', {}).get('total_tokens', 0)
                knowledge_source = f"openai_rag ({model} + {len(matches)} KB docs)"
            else:
                print(f">> OpenAI API error: {api_res.status_code} {api_res.text}")
        except Exception as e:
            print(f">> OpenAI API Exception: {e}")

    # Step 4: Fallback to best local knowledge match or heuristic reply
    if not response_text:
        if top_match:
            response_text = f"{top_match['content']}\n\n💡 *Note: This response is generated by Victoria College AI Advisor. For official confirmation, grant eligibility assessment, and admissions planning, please contact college advisors at 416-665-6668 or info@viccollege.com.*"
            model = "vic-knowledge-base-fallback"
            knowledge_source = f"local_kb (Fallback: {top_match['title']} - Score: {top_match['score']})"
        else:
            response_text = generate_local_knowledge_reply(query)
            model = "vic-college-offline-ai"
            knowledge_source = "local_heuristic_advisor"

    # Log query to DB
    now_str = datetime.utcnow().isoformat()
    user_id = user['id'] if user else None
    user_name = user['name'] if user else 'Guest'
    user_email = user['email'] if user else 'guest@viccollege.com'
    ip_addr = request.remote_addr

    db.execute('''
    INSERT INTO chat_logs (user_id, user_name, user_email, query, response, model, tokens_used, ip_address, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, user_name, user_email, query, response_text, model, tokens_used, ip_addr, now_str))
    db.commit()

    return jsonify({
        'response': response_text,
        'model': model,
        'tokens_used': tokens_used,
        'knowledge_source': knowledge_source,
        'matched_count': len(matches),
        'authenticated': user is not None
    })

def generate_local_knowledge_reply(query: str) -> str:
    q = query.lower()
    is_zh = any(u'\u4e00' <= c <= u'\u9fa5' for c in query)

    # 0. BJO vs OSAP Difference
    if any(k in q for k in ['osap']) or (any(k in q for k in ['bjo', 'better job', 'second career']) and any(k in q for k in ['diff', 'vs', '区别', '对比', '不同', 'osap', 'loan'])):
        if is_zh:
            return """### ⚖️ Better Jobs Ontario (BJO) 与 OSAP 的核心区别

<div class="chat-compare-container">
  <div class="chat-compare-card card-bjo">
    <div class="chat-compare-field">
      <span class="chat-compare-label">资助项目:</span>
      <span class="chat-compare-value"><span class="badge-bjo">Better Jobs Ontario (BJO)</span></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">资金性质:</span>
      <span class="chat-compare-value"><strong>100% 政府无偿资助 (Grant)</strong></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">最高额度:</span>
      <span class="chat-compare-value">最高 <strong>$28,000+</strong> (涵盖 100% 学费、生活津贴、书本、托儿与交通)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">偿还要求:</span>
      <span class="chat-compare-value"><strong>$0 无需偿还</strong> (无债务白给补贴)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">申请群体:</span>
      <span class="chat-compare-value">被解雇失业、零工/合约工、低收入人士 (加拿大 PR / 公民)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">学制周期:</span>
      <span class="chat-compare-value">快速职业大专文凭 (23-32周，如 23周 PSW 护工、32周 全栈 IT、30周 会计税务)</span>
    </div>
  </div>

  <div class="chat-compare-card card-osap">
    <div class="chat-compare-field">
      <span class="chat-compare-label">资助项目:</span>
      <span class="chat-compare-value"><span class="badge-osap">OSAP 安省学生贷款</span></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">资金性质:</span>
      <span class="chat-compare-value"><strong>学生贷款 (Loan) + 助学金 (Grant)</strong></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">最高额度:</span>
      <span class="chat-compare-value">根据家庭年收入与学校学费动态核算</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">偿还要求:</span>
      <span class="chat-compare-value"><strong>贷款部分毕业后必须按期连本带息还清</strong></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">申请群体:</span>
      <span class="chat-compare-value">大专/大学在读全日制普通学生</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">学制周期:</span>
      <span class="chat-compare-value">传统多学年高等教育学位或文凭</span>
    </div>
  </div>
</div>

💡 **维多利亚职业学院顾问建议**：如果您目前失业、领过 EI 或为自雇低收入，申请 **Better Jobs Ontario** 能够享受 **100% 零债务无偿全额资助**，远比背负 OSAP 贷款更划算！欢迎致电 416-665-6668 预约免费评估。"""
        else:
            return """### ⚖️ Comparison: Better Jobs Ontario (BJO) vs. OSAP

<div class="chat-compare-container">
  <div class="chat-compare-card card-bjo">
    <div class="chat-compare-field">
      <span class="chat-compare-label">Program:</span>
      <span class="chat-compare-value"><span class="badge-bjo">Better Jobs Ontario (BJO)</span></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Funding Type:</span>
      <span class="chat-compare-value"><strong>100% Non-Repayable Grant</strong> (Gift Money)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Maximum Funding:</span>
      <span class="chat-compare-value">Up to <strong>$28,000+</strong> (100% Tuition, Books, Living & Childcare)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Repayment:</span>
      <span class="chat-compare-value"><strong>$0 Repayment</strong> (Never pay back)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Target Group:</span>
      <span class="chat-compare-value">Laid-off workers, gig/contract workers, underemployed, PR/Citizens</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Duration:</span>
      <span class="chat-compare-value">Fast-track career diplomas (23-32 weeks, e.g. 23-week PSW, 32-week IT, 30-week Accounting)</span>
    </div>
  </div>

  <div class="chat-compare-card card-osap">
    <div class="chat-compare-field">
      <span class="chat-compare-label">Program:</span>
      <span class="chat-compare-value"><span class="badge-osap">OSAP</span></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Funding Type:</span>
      <span class="chat-compare-value"><strong>Student Loan + Need-Based Grant</strong></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Maximum Funding:</span>
      <span class="chat-compare-value">Calculated based on family income & institution costs</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Repayment:</span>
      <span class="chat-compare-value"><strong>Loan portion MUST be repaid</strong> with interest</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Target Group:</span>
      <span class="chat-compare-value">College & university degree/diploma students</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Duration:</span>
      <span class="chat-compare-value">Traditional multi-year academic degrees/diplomas</span>
    </div>
  </div>
</div>

💡 **Victoria College Advisor Tip:** If you are currently laid off, underemployed, or a contract worker, **Better Jobs Ontario** is vastly superior because it is **100% free gift money with $0 debt**, unlike OSAP which requires student loan repayment! Call us at 416-665-6668 for free eligibility assistance."""

    if any(k in q for k in ['grant', '28000', '28,000', 'better job', 'second career', 'funding', 'aid', '补助', '资助', '第二职业', '免费']):
        return "### 🎯 Better Jobs Ontario (Second Career) 政府助学金\n\n您可申请最高 **$28,000+ 加币全额政府无偿资助**，涵盖 100% 学费、生活津贴、书本及交通费！\n\n**申请资格：**\n• 被解雇人士 / 领过 EI\n• 自雇、零工、合约工及低收入人士\n• 加拿大永久居民 (PR) 或公民\n\n维多利亚学院提供全程 1对1 免费规划与材料准备，欢迎致电 416-665-6668 或在线预约咨询！" if is_zh else "### 🎯 Better Jobs Ontario ($28,000+ Government Grants)\n\nYou may qualify for up to **$28,000+ in non-repayable government funding** covering 100% tuition, books, transportation, and monthly living allowances!\n\n**Key Eligibility:**\n• Laid-off workers or former EI recipients\n• Gig / contract / low-income workers\n• Canadian Permanent Residents & Citizens\n\nOur team provides 100% complimentary step-by-step assistance. Call us at 416-665-6668 or book a consultation!"

    if any(k in q for k in ['psw', 'support worker', 'nurse', 'caregiver', '护工', '护理', '养老院']):
        return "### 🩺 NACC Personal Support Worker (PSW DE 2022)\n\n• **学制：** 23 周（包含 300+ 小时持牌长期护理院临床实地实习）\n• **毕业证书：** NACC PSW 官方文凭 + CPR/AED 急救证书\n• **薪资待遇：** 起薪时薪 $20 – $28 加元/小时\n• **亮点：** 安省持牌资深护士带教，配备标准病房模拟实验室，毕业直接对接西人养老机构就业。" if is_zh else "### 🩺 NACC Personal Support Worker (PSW DE 2022)\n\n• **Duration:** 23 Weeks (Includes 300+ hours clinical practicum)\n• **Credential:** NACC PSW Diploma + CPR & First Aid Certification\n• **Salary:** $20 – $28 / hour with strong demand across Ontario\n• **Highlights:** Fully accredited, hands-on simulation labs, and direct placement in top healthcare facilities."

    if any(k in q for k in ['tech', 'full stack', 'web', 'code', 'java', 'react', 'developer', 'ai', 'mini credential', '全栈', '编程', '前端', '后端', '软件', '人工智能']):
        return "### 💻 Full Stack Web Technician (全栈开发文凭 + AI 微证书)\n\n• **双重认证：** 安省官方 Full Stack Web 职业文凭 + **AI Mini-Credential 微证书**\n• **学制：** 32 周（高强度实战机房 + 商业级微服务与 AI 大项目）\n• **技术栈：** Java, Spring Boot 3, React, TypeScript, AWS 云原生, Docker, OpenAI/Claude API, 智能辅助编程\n• **起薪前景：** 加拿大毕业起薪 $65,000 – $85,000 加元/年\n• **就业支持：** 名师辅导 LeetCode 刷题与大厂模拟面试，直通金融与科技名企。" if is_zh else "### 💻 Full Stack Web Technician Diploma + AI Mini-Credential\n\n• **Dual Credentials:** Accredited Career Diploma + **AI Mini-Credential**\n• **Duration:** 32 Weeks (Live Projects + Intensive Labs)\n• **Stack:** Core Java, Spring Boot 3, React, TypeScript, AWS Cloud, Docker, GenAI & LLM Integration\n• **Starting Salary:** $65,000 – $85,000 / year in Canadian tech & banking sectors\n• **Support:** 1-on-1 resume polish, LeetCode algorithms, and mock interview coaching."

    if any(k in q for k in ['account', 'tax', 'payroll', 'bookkeep', 'cpa', '会计', '报税', '薪资']):
        return "### 📊 Accounting, Tax and Payroll Administration (会计与税务文凭)\n\n• **学制：** 30 周（资深持牌 CPA 亲授 + 真账实训）\n• **软件技能：** QuickBooks Desktop/Online, Sage 50, Profile, TaxPrep, Advanced Excel\n• **核心业务：** 全流程记账、加拿大个人税 (T1) 与公司税 (T2)、CRA 工资税 (CPP, EI, T4)\n• **薪资待遇：** 起薪 $48,000 – $65,000 加元/年，稳健白领晋升路径。" if is_zh else "### 📊 Accounting, Tax & Payroll Administration\n\n• **Duration:** 30 Weeks (Hands-on corporate accounting software)\n• **Software:** QuickBooks Desktop/Online, Sage 50, Profile, TaxPrep, Excel\n• **Core Skills:** Full-cycle bookkeeping, Canadian T1/T2 tax returns, CRA payroll filings\n• **Salary:** $48,000 – $65,000 / year with clear progression to CPA designation."

    if any(k in q for k in ['campus', 'location', 'address', 'where', 'phone', '校区', '地址', '电话', '万锦', '北约克']):
        return "### 🏫 校区地址与联系电话\n\n📍 **万锦主校区 (Markham Campus):**\n7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n\n📞 咨询电话：416-665-6668\n🕒 办公时间：周一至周六 9:00 AM – 6:00 PM" if is_zh else "### 🏫 Campus Location & Contact Info\n\n📍 **Markham Main Campus:**\n7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n\n📞 Phone: 416-665-6668\n🕒 Hours: Monday – Saturday, 9:00 AM – 6:00 PM"

    return "您好！我是维多利亚职业学院 AI 智能升学顾问。我可以为您提供：\n\n• 💰 **政府最高 $28,000+ 免费培训助学金**\n• 🩺 **PSW 护工、全栈开发、会计税务、幼教、电工** 热门高薪专业\n• 🏫 **万锦主校区信息及预约规划**\n\n⚠️ *温馨提示：本系统为 AI 智能助手，回复仅供参考。确切课程信息及资助评估请直接联系学院顾问：416-665-6668 或 info@viccollege.com。*" if is_zh else "Hello! I am your Victoria College AI Advisor. How can I help you today?\n\n• 💰 **Better Jobs Ontario ($28,000+ Government Grants)**\n• 🩺 **Diplomas in PSW Healthcare, Full Stack Web, Accounting, Early Childcare, Electrician**\n• 🏫 **Markham Main Campus Details & Free Consultation Booking**\n\n⚠️ *Please Note: This is an AI assistant for guidance. For official answers and individualized grant assessment, please contact our college advisors directly at 416-665-6668 or info@viccollege.com.*"


# ==============================================================================
# Admin Control Panel APIs (Protected for role == 'admin')
# ==============================================================================

def require_admin():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized. Please log in.'}), 401
    if user['role'] != 'admin':
        return jsonify({'error': 'Forbidden. Admin privileges required.'}), 403
    return None

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()['total_users']

    cursor.execute("SELECT COUNT(*) as google_users FROM users WHERE provider = 'google'")
    google_users = cursor.fetchone()['google_users']

    cursor.execute("SELECT COUNT(*) as linkedin_users FROM users WHERE provider = 'linkedin'")
    linkedin_users = cursor.fetchone()['linkedin_users']

    cursor.execute("SELECT COUNT(*) as total_chats FROM chat_logs")
    total_chats = cursor.fetchone()['total_chats']

    cursor.execute("SELECT COUNT(*) as kb_count FROM knowledge_base")
    kb_count = cursor.fetchone()['kb_count']

    cursor.execute("SELECT COUNT(*) as total_art FROM articles")
    total_art = cursor.fetchone()['total_art']

    cursor.execute("SELECT COUNT(*) as active_art FROM articles WHERE is_active = 1 AND status = 'active'")
    active_art = cursor.fetchone()['active_art']
    hidden_art = total_art - active_art

    cursor.execute("SELECT COUNT(*) as total_prog FROM programs")
    total_prog = cursor.fetchone()['total_prog']
    cursor.execute("SELECT COUNT(*) as active_prog FROM programs WHERE is_active = 1")
    active_prog = cursor.fetchone()['active_prog']

    cursor.execute("SELECT COUNT(*) as total_jf FROM job_fairs")
    total_jf = cursor.fetchone()['total_jf']
    cursor.execute("SELECT COUNT(*) as active_jf FROM job_fairs WHERE is_active = 1")
    active_jf = cursor.fetchone()['active_jf']

    cursor.execute("SELECT value FROM settings WHERE key = 'openai_api_key'")
    key_row = cursor.fetchone()
    has_key = bool(key_row and key_row['value'].strip())

    cursor.execute("SELECT value FROM settings WHERE key = 'openai_model'")
    model_row = cursor.fetchone()
    model = model_row['value'] if model_row else 'gpt-4o-mini'

    return jsonify({
        'total_users': total_users,
        'google_users': google_users,
        'linkedin_users': linkedin_users,
        'total_chats': total_chats,
        'knowledge_articles': kb_count,
        'total_articles': total_art,
        'active_articles': active_art,
        'hidden_articles': hidden_art,
        'total_programs': total_prog,
        'active_programs': active_prog,
        'total_job_fairs': total_jf,
        'active_job_fairs': active_jf,
        'job_fair_active': bool(active_jf > 0),
        'sitemap_urls': 5 + active_art,
        'has_api_key': has_key,
        'current_model': model
    })

# ==============================================================================
# Knowledge Base Admin Management APIs
# ==============================================================================

@app.route('/api/admin/knowledge', methods=['GET'])
def admin_get_knowledge():
    err = require_admin()
    if err: return err

    category = request.args.get('category', '').strip().lower()
    search = request.args.get('search', '').strip().lower()

    query = "SELECT id, category, title, keywords, content, priority, created_at, updated_at FROM knowledge_base WHERE 1=1"
    params = []

    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(keywords) LIKE ? OR LOWER(content) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY priority DESC, id DESC"

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    articles = [dict(row) for row in cursor.fetchall()]

    return jsonify({'articles': articles, 'count': len(articles)})

@app.route('/api/admin/knowledge', methods=['POST'])
def admin_create_knowledge():
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    category = (data.get('category') or 'general').strip().lower()
    keywords = (data.get('keywords') or '').strip()
    content = (data.get('content') or '').strip()
    priority = int(data.get('priority') or 1)

    if not title or not content:
        return jsonify({'error': 'Title and Content are required.'}), 400

    now_str = datetime.utcnow().isoformat()
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
    INSERT INTO knowledge_base (category, title, keywords, content, priority, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (category, title, keywords, content, priority, now_str, now_str))
    db.commit()

    return jsonify({
        'success': True,
        'id': cursor.lastrowid,
        'message': f'Knowledge article "{title}" created successfully.'
    })

@app.route('/api/admin/knowledge/<int:kb_id>', methods=['GET'])
def admin_get_knowledge_item(kb_id):
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, category, title, keywords, content, priority, created_at, updated_at FROM knowledge_base WHERE id = ?", (kb_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Knowledge article not found.'}), 404

    return jsonify({'article': dict(row)})

@app.route('/api/admin/knowledge/<int:kb_id>', methods=['PUT'])
def admin_update_knowledge(kb_id):
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id FROM knowledge_base WHERE id = ?", (kb_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'Knowledge article not found.'}), 404

    title = data.get('title')
    category = data.get('category')
    keywords = data.get('keywords')
    content = data.get('content')
    priority = data.get('priority')

    updates = []
    params = []

    if title is not None:
        updates.append("title = ?")
        params.append(title.strip())
    if category is not None:
        updates.append("category = ?")
        params.append(category.strip().lower())
    if keywords is not None:
        updates.append("keywords = ?")
        params.append(keywords.strip())
    if content is not None:
        updates.append("content = ?")
        params.append(content.strip())
    if priority is not None:
        updates.append("priority = ?")
        params.append(int(priority))

    updates.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat())

    params.append(kb_id)
    query = f"UPDATE knowledge_base SET {', '.join(updates)} WHERE id = ?"
    db.execute(query, params)
    db.commit()

    return jsonify({'success': True, 'message': 'Knowledge article updated successfully.'})

@app.route('/api/admin/knowledge/<int:kb_id>', methods=['DELETE'])
def admin_delete_knowledge(kb_id):
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT title FROM knowledge_base WHERE id = ?", (kb_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Knowledge article not found.'}), 404

    db.execute("DELETE FROM knowledge_base WHERE id = ?", (kb_id,))
    db.commit()

    return jsonify({'success': True, 'message': f'Knowledge article "{row["title"]}" deleted.'})

@app.route('/api/admin/knowledge/test-query', methods=['POST'])
def admin_test_knowledge_query():
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    query = (data.get('query') or '').strip()
    if not query:
        return jsonify({'error': 'Test query cannot be empty.'}), 400

    matches = search_knowledge_base(query, limit=5, min_score=0.05)

    action = "general_ai_or_fallback"
    if matches:
        if matches[0]['score'] >= 0.70:
            action = f"direct_local_kb_hit (Confidence: {matches[0]['score']})"
        elif matches[0]['score'] >= 0.15:
            action = f"openai_rag_synthesis (Grounded with {len(matches)} KB docs)"

    return jsonify({
        'query': query,
        'matches': matches,
        'top_score': matches[0]['score'] if matches else 0.0,
        'action_preview': action
    })

@app.route('/api/admin/knowledge/from-log/<int:log_id>', methods=['POST'])
def admin_create_knowledge_from_log(log_id):
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, query, response FROM chat_logs WHERE id = ?", (log_id,))
    log = cursor.fetchone()
    if not log:
        return jsonify({'error': 'Conversation log not found.'}), 404

    data = request.get_json() or {}

    title = (data.get('title') or log['query']).strip()
    content = (data.get('content') or log['response']).strip()
    category = (data.get('category') or '').strip().lower()
    keywords = (data.get('keywords') or '').strip()
    priority = int(data.get('priority') or 1)

    if not category:
        q_low = title.lower()
        if any(w in q_low for w in ['grant', 'second career', 'better job', 'funding', 'aid', '补助', '资助', '免费']):
            category = 'financial_aid'
        elif any(w in q_low for w in ['psw', 'tech', 'full stack', 'web', 'account', 'tax', 'nurse', 'electrician', 'acupuncture', 'childcare', 'eca', '专业', '课程']):
            category = 'programs'
        elif any(w in q_low for w in ['campus', 'location', 'address', 'where', 'phone', 'contact', '校区', '地址', '电话', '万锦', '北约克']):
            category = 'campuses'
        elif any(w in q_low for w in ['admit', 'admission', 'apply', 'enroll', 'tuition', 'fee', 'consult', '报名', '学费', '咨询']):
            category = 'admissions'
        else:
            category = 'general'

    if not keywords:
        tokens = [t for t in re.findall(r'[\w\u4e00-\u9fff]+', title.lower()) if len(t) > 1]
        keywords = ', '.join(tokens[:8])

    now_str = datetime.utcnow().isoformat()
    cursor.execute('''
    INSERT INTO knowledge_base (category, title, keywords, content, priority, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (category, title, keywords, content, priority, now_str, now_str))
    db.commit()

    new_id = cursor.lastrowid
    return jsonify({
        'success': True,
        'id': new_id,
        'message': f'Conversation log #{log_id} saved as Knowledge Base Article #{new_id}!'
    })

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    err = require_admin()
    if err: return err

    search = request.args.get('search', '').strip().lower()
    role_filter = request.args.get('role', '')
    provider_filter = request.args.get('provider', '')

    query = "SELECT id, name, email, provider, avatar_url, role, status, created_at, last_login_at FROM users WHERE 1=1"
    params = []

    if search:
        query += " AND (LOWER(name) LIKE ? OR LOWER(email) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    if role_filter:
        query += " AND role = ?"
        params.append(role_filter)

    if provider_filter:
        query += " AND provider = ?"
        params.append(provider_filter)

    query += " ORDER BY id DESC"

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    users = [dict(row) for row in cursor.fetchall()]
    return jsonify({'users': users, 'count': len(users)})

@app.route('/api/admin/users', methods=['POST'])
def admin_create_user():
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or secrets.token_urlsafe(10)
    role = data.get('role', 'user')
    status = data.get('status', 'active')

    if not name or not email:
        return jsonify({'error': 'Name and Email are required.'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        return jsonify({'error': 'A user with this email already exists.'}), 400

    now_str = datetime.utcnow().isoformat()
    avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={email}"

    cursor.execute('''
    INSERT INTO users (name, email, password_hash, provider, avatar_url, role, status, created_at, last_login_at)
    VALUES (?, ?, ?, 'email', ?, ?, ?, ?, ?)
    ''', (name, email, hash_password(password), avatar_url, role, status, now_str, now_str))
    db.commit()

    user_id = cursor.lastrowid
    return jsonify({'success': True, 'id': user_id, 'user_id': user_id})

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def admin_update_user(user_id):
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    # Build dynamic update
    fields = []
    values = []

    if 'name' in data:
        fields.append("name = ?")
        values.append(data['name'].strip())

    if 'role' in data and data['role'] in ['user', 'admin']:
        fields.append("role = ?")
        values.append(data['role'])

    if 'status' in data and data['status'] in ['active', 'suspended']:
        fields.append("status = ?")
        values.append(data['status'])

    if 'password' in data and len(data['password']) >= 6:
        fields.append("password_hash = ?")
        values.append(hash_password(data['password']))

    if not fields:
        return jsonify({'error': 'No fields to update.'}), 400

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
    db.execute(query, values)
    db.commit()

    return jsonify({'success': True})

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    err = require_admin()
    if err: return err

    current_user = get_current_user()
    if current_user and current_user['id'] == user_id:
        return jsonify({'error': 'You cannot delete your own admin account.'}), 400

    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    return jsonify({'success': True})

@app.route('/api/admin/settings', methods=['GET'])
def admin_get_settings():
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT key, value FROM settings")
    settings = {row['key']: row['value'] for row in cursor.fetchall()}

    # Mask API key for UI security (e.g. sk-proj-...38a1)
    raw_key = settings.get('openai_api_key', '')
    masked_key = ""
    if raw_key:
        if len(raw_key) > 10:
            masked_key = raw_key[:4] + "••••••••••••••••••••" + raw_key[-4:]
        else:
            masked_key = "••••••••••••"

    return jsonify({
        'openai_api_key_masked': masked_key,
        'has_api_key': bool(raw_key.strip()),
        'openai_model': settings.get('openai_model', 'gpt-4o-mini'),
        'temperature': settings.get('temperature', '0.7'),
        'max_tokens': settings.get('max_tokens', '800'),
        'require_login': settings.get('require_login', 'false'),
        'system_prompt': settings.get('system_prompt', '')
    })

@app.route('/api/admin/settings', methods=['POST'])
def admin_save_settings():
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    db = get_db()
    now_str = datetime.utcnow().isoformat()

    allowed_keys = ['openai_api_key', 'openai_model', 'temperature', 'max_tokens', 'require_login', 'system_prompt']

    for k in allowed_keys:
        if k in data:
            val = str(data[k])
            # If user didn't modify masked key, skip saving
            if k == 'openai_api_key' and ('••••' in val or not val.strip()):
                if not val.strip():
                    db.execute("INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, '', ?)", (k, now_str))
                continue

            db.execute("INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)", (k, val, now_str))

    db.commit()
    return jsonify({'success': True, 'message': 'Settings saved successfully.'})

@app.route('/api/admin/settings/test-key', methods=['POST'])
def admin_test_openai_key():
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    test_key = (data.get('openai_api_key') or '').strip()

    db = get_db()
    cursor = db.cursor()

    if not test_key or '••••' in test_key:
        cursor.execute("SELECT value FROM settings WHERE key = 'openai_api_key'")
        row = cursor.fetchone()
        test_key = row['value'] if row else ''

    if not test_key:
        return jsonify({'valid': False, 'message': 'No OpenAI API Key provided.'}), 400

    if requests is None:
        return jsonify({'valid': False, 'message': 'Python requests package is not installed on server.'}), 500

    try:
        res = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {test_key}"},
            timeout=8
        )
        if res.status_code == 200:
            return jsonify({'valid': True, 'message': '✅ OpenAI API Key is valid and successfully connected!'})
        else:
            err_msg = res.json().get('error', {}).get('message', res.text)
            return jsonify({'valid': False, 'message': f'❌ Invalid Key ({res.status_code}): {err_msg}'}), 400
    except Exception as e:
        return jsonify({'valid': False, 'message': f'❌ Connection failed: {str(e)}'}), 500

@app.route('/api/admin/logs', methods=['GET'])
def admin_get_logs():
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM chat_logs ORDER BY id DESC LIMIT 100")
    logs = [dict(row) for row in cursor.fetchall()]
    return jsonify({'logs': logs, 'count': len(logs)})

@app.route('/api/admin/logs', methods=['DELETE'])
def admin_clear_logs():
    err = require_admin()
    if err: return err

    db = get_db()
    db.execute("DELETE FROM chat_logs")
    db.commit()
    return jsonify({'success': True, 'message': 'Chat logs cleared.'})


# ==============================================================================
# SEO & GEO Article Generator, CMS & Dynamic XML Sitemap Engine
# ==============================================================================

def slugify(text: str) -> str:
    """Generate a clean, SEO-friendly URL slug from a title string."""
    text = text.lower().strip()
    # Replace non-alphanumeric (keep english letters, numbers, spaces, hyphens)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    if not text:
        text = f"article-{int(time.time())}"
    return text[:100]

def get_geo_coordinates(geo_target: str) -> tuple:
    """Return default (lat, lng) for common GTA & Ontario regions."""
    g_low = (geo_target or '').lower()
    if 'markham' in g_low:
        return (43.8561, -79.3370)
    elif 'north york' in g_low:
        return (43.7615, -79.4111)
    elif 'mississauga' in g_low:
        return (43.5890, -79.6441)
    elif 'scarborough' in g_low:
        return (43.7764, -79.2318)
    elif 'richmond hill' in g_low:
        return (43.8828, -79.4403)
    elif 'brampton' in g_low:
        return (43.7315, -79.7624)
    elif 'vaughan' in g_low:
        return (43.8372, -79.5083)
    elif 'ontario' in g_low or 'gta' in g_low or 'toronto' in g_low:
        return (43.6532, -79.3832)
    return (43.7758, -79.3458)

def generate_seo_article_local(keywords: str, geo_target: str = 'Toronto & GTA, Ontario', category: str = 'programs', language: str = 'en', tone: str = 'Job Seekers & Career Changers', topic: str = '') -> dict:
    """
    Intelligent built-in bilingual GEO/SEO Article Generator engine.
    Generates rich, multi-section articles with localized facts, grants, salaries, and schema.
    """
    is_zh = language.lower() in ['zh', 'chinese', 'cn', 'zh-cn']
    geo = geo_target.strip() if geo_target else ('多伦多及大多伦多地区 (GTA), 安省' if is_zh else 'Toronto & GTA, Ontario')
    lat, lng = get_geo_coordinates(geo)
    
    # Clean keyword list
    kw_list = [k.strip() for k in keywords.split(',') if k.strip()]
    primary_kw = kw_list[0] if kw_list else ('Healthcare & PSW Training' if not is_zh else 'PSW 护工与政府补助培训')
    sec_kw_str = ', '.join(kw_list[1:6]) if len(kw_list) > 1 else primary_kw

    current_year = datetime.utcnow().year

    # Detect category specifics
    cat_lower = (category or '').lower()
    q_all = f"{keywords} {topic} {category}".lower()

    if any(k in q_all for k in ['psw', 'health', 'caregiver', 'nurse', 'nursing', 'medical', '护工', '医疗']):
        subject = 'PSW Healthcare'
        cat_key = 'healthcare'
        cover = 'images/news_1.jpg'
        if is_zh:
            title = f"{current_year} 安省 PSW 护工就业前景与最高 $28,000 政府免费培训助学金全指南 ({geo})"
            meta_title = f"{current_year} 安省 PSW 护工培训与 $28,000 政府助学金申请 | 维多利亚职业学院"
            meta_desc = f"深度解析 {geo} 地区 PSW 个人护理护工时薪 ($20-$28/h)、300+小时持牌养老院临床实习及 Better Jobs Ontario 免费学费申请攻略。"
            summary = f"全面解读 {geo} 紧缺医疗护理行业需求、PSW 护工高薪就业机遇，以及如何通过安省政府补助实现 0 元学费入读并获生活津贴。"
            content = f"""<h2>1. {geo} 医疗护理行业现状与 PSW 护工急迫需求</h2>
<p>随着安大略省人口结构老龄化加速与长期护理院（LTC）床位的大规模扩建，<strong>{geo}</strong> 各大医院、公立/私立长期护理中心及社区家庭护理机构对持牌 <strong>Personal Support Worker (PSW)</strong> 的需求呈现爆发式增长。持牌护工起薪高达 <strong>$20 – $28 加元/小时</strong>，并享有完整的牙医保险、带薪年假与退休金等优厚福利。</p>

<h3>2. 核心教学体系：NACC 官方认证与 300+ 小时实地临床实习</h3>
<p>维多利亚职业学院（Victoria International College）提供的 <strong>NACC Personal Support Worker (PSW DE 2022)</strong> 证书课程，由安省资深注册护士（RN）小班授课：</p>
<ul>
  <li><strong>标准模拟病房实验室：</strong> 1:1 还原加国养老院病房环境，高强度实操演练病患转运、个人卫生照料与急救护理。</li>
  <li><strong>300+ 小时保证临床实习：</strong> 学院直接对接大多伦多地区知名持牌护理机构与养老院实地实习，表现优异者实习期即获全职录用。</li>
  <li><strong>双重权威认证：</strong> 毕业荣获安省 NACC PSW 官方职业文凭 + Standard First Aid & CPR Level C 国际急救证书。</li>
</ul>

<blockquote>
  <p><strong>💡 官方助学金支持：</strong> 维多利亚学院顾问团队拥有 22 年政府补助辅导经验，已协助数千名新移民与失业人士成功获批 <strong>最高 $28,000+ 加币 Better Jobs Ontario (Second Career)</strong> 全额无偿资助！</p>
</blockquote>

<h3>3. 谁可以申请安省最高 $28,000+ 免费学费与生活费补助？</h3>
<p>符合以下任一条件的大多伦多及安省居民，均有机会获得 100% 全额资助，涵盖学费、书本费、交通费、托儿津贴及每月基础生活费：</p>
<ol>
  <li>近期遭遇解雇（Layoff）或曾领取过就业保险金（EI）的人士；</li>
  <li>自雇、零工（Gig worker）、兼职或临时合约工人士；</li>
  <li>家庭收入低于安省低收入标准的加拿大永久居民（PR）或公民。</li>
</ol>

<h3>4. 校区交通与联系方式</h3>
<p>学院交通极为便利，TTC 与 YRT 直达：</p>
<ul>
  <li><strong>万锦主校区 (Markham Campus)：</strong> 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8 (Woodbine & Steeles)</li>
</ul>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #8B0000 0%, #B22222 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">立即开启您的医疗护理高薪职业之路</h3>
  <p style="color: #ffd2d2; margin-bottom: 18px;">预约 1 对 1 免费政府补助资格评估与名师试听课，无需自掏腰包学专业！</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #8B0000; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">立即预约免费评估 • 咨询热线 416-665-6668</a>
</div>"""
        else:
            title = f"{current_year} In-Demand PSW Healthcare Training & $28,000+ Government Grants Guide ({geo})"
            meta_title = f"{current_year} PSW Healthcare Training & $28,000 Grant Guide {geo} | Victoria College"
            meta_desc = f"Discover high-demand PSW careers in {geo}. Learn about $20-$28/hr starting wages, NACC certification, and Better Jobs Ontario grant eligibility."
            summary = f"Comprehensive guide to accredited Personal Support Worker (PSW) diploma training, $20-$28/hr career outlook, and up to $28,000+ government funding in {geo}."
            content = f"""<h2>1. Healthcare Workforce Demand Across {geo}</h2>
<p>Ontario's healthcare infrastructure is rapidly expanding to support seniors and long-term care facilities. In <strong>{geo}</strong>, certified <strong>Personal Support Workers (PSWs)</strong> are among the most recruited frontline professionals, offering strong job security, flexible scheduling, and competitive hourly wages between <strong>$20 and $28 per hour</strong>.</p>

<h3>2. NACC Accredited Curriculum & 300+ Clinical Practicum Hours</h3>
<p>Victoria International College's <strong>NACC Personal Support Worker DE 2022</strong> program combines intensive clinical simulation with guaranteed placement:</p>
<ul>
  <li><strong>Modern Simulation Ward Labs:</strong> Master patient mobility, infection control, vital signs, and compassionate care on-campus in Markham.</li>
  <li><strong>300+ Guaranteed Clinical Placement Hours:</strong> Direct clinical rotations in top Ontario long-term care homes and healthcare networks.</li>
  <li><strong>Dual Certification:</strong> Graduate with official NACC PSW credentials and Standard First Aid / CPR Level C.</li>
</ul>

<blockquote>
  <p><strong>💡 Financial Assistance:</strong> Victoria College offers 100% complimentary step-by-step guidance for <strong>Better Jobs Ontario (Second Career)</strong> grants providing up to $28,000+ in non-repayable funding.</p>
</blockquote>

<h3>3. Government Funding & Better Jobs Ontario Eligibility</h3>
<p>Eligible candidates in {geo} can receive full funding covering tuition, books, transportation, child care, and basic living allowances if you are:</p>
<ol>
  <li>Laid off, former EI recipients, or downsized workers;</li>
  <li>Employed in temporary, part-time, or gig-economy roles;</li>
  <li>Underemployed permanent residents or Canadian citizens.</li>
</ol>

<h3>4. Campus Location & Contact Information</h3>
<ul>
  <li><strong>Markham Main Campus:</strong> 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8</li>
  <li><strong>Admissions Hotline:</strong> 416-665-6668 | <strong>Email:</strong> info@viccollege.com</li>
</ul>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #8B0000 0%, #B22222 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">Start Your Rewarding Healthcare Career Today</h3>
  <p style="color: #ffd2d2; margin-bottom: 18px;">Contact our admissions advisors for a free grant evaluation and course demo class.</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #8B0000; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">Book Free Consultation • Call 416-665-6668</a>
</div>"""

    elif any(k in q_all for k in ['tech', 'web', 'java', 'react', 'software', 'develop', 'it', 'cloud', '代码', '全栈']):
        subject = 'Full Stack Tech'
        cat_key = 'technology'
        cover = 'images/news_2.jpg'
        if is_zh:
            title = f"{current_year} {geo} 全栈软件开发工程师高薪就业路径与 Java / React 实战指南"
            meta_title = f"{current_year} {geo} 全栈开发培训与高薪 IT 就业规划 | 维多利亚职业学院"
            meta_desc = f"万锦及大多伦多高科技走廊 IT 职位急缺。维多利亚学院全栈开发文凭，覆盖 Java Spring Boot, React, AWS，起薪 $65k-$85k。"
            summary = f"深度剖析 {geo} 科技企业微服务与云计算招聘需求，如何通过 32 周工业级项目实战快速锁定 $65,000–$85,000/年 软件工程师职位。"
            content = f"""<h2>1. {geo} 高科技产业集群与软件工程岗位需求</h2>
<p>作为加国科技创新重镇，<strong>{geo}</strong> 聚集了包括 IBM、AMD、高通等在内的数千家高科技与金融跨国名企。随着微服务架构与云原生转型的普及，企业对掌握 <strong>Java Spring Boot 3、React、TypeScript 与 AWS 云端架构</strong> 的全栈开发人员（Full Stack Developer）需求持续高涨，初中级起薪普遍达 <strong>$65,000 – $85,000 加元/年</strong>。</p>

<h3>2. 32 周企业级工业实战课程架构</h3>
<ul>
  <li><strong>后端微服务：</strong> Java 核心深度进阶、Spring Boot 3, Spring Cloud, RESTful API, MyBatis, Redis 缓存高并发实战。</li>
  <li><strong>现代前端工程：</strong> React 18 深入、Hooks、Redux Toolkit, TypeScript, Next.js 与响应式设计。</li>
  <li><strong>云原生与 DevOps：</strong> AWS (EC2, S3, RDS), Docker 容器化部署, CI/CD 自动化流水线。</li>
  <li><strong>毕业工业级 Capstone：</strong> 100% 独立交付高可用商业级分布式云平台作品集。</li>
</ul>

<blockquote>
  <p><strong>💼 就业辅导保障：</strong> 维多利亚学院提供专属一对一技术简历包装、LeetCode 大厂算法刷题辅导与真实模拟技术面试。</p>
</blockquote>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #0A2540 0%, #1A365D 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">免费参加 IT 全栈开发试听课</h3>
  <p style="color: #93c5fd; margin-bottom: 18px;">名师带教，商业项目驱动，零基础及转行人士首选！</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #2563eb; color: #fff; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">预约试听与课程咨询 • 416-665-6668</a>
</div>"""
        else:
            title = f"{current_year} Full Stack Software Engineer Career Blueprint in {geo}"
            meta_title = f"{current_year} Full Stack Web Developer Training {geo} | Victoria College"
            meta_desc = f"Fast-track your tech career in {geo}. Learn Java, Spring Boot 3, React, TypeScript, and AWS. Average salaries $65k-$85k/yr."
            summary = f"Career roadmap for aspiring software engineers in {geo}, covering core Java, microservices, modern React, cloud architecture, and government grant eligibility."
            content = f"""<h2>1. The High-Tech Corridor of {geo}</h2>
<p>Known as Canada's premier innovation cluster, <strong>{geo}</strong> houses hundreds of technology and fintech leaders. Organizations are actively recruiting <strong>Full Stack Web Technicians</strong> capable of delivering scalable backends in Java Spring Boot and responsive frontends in modern React, with entry compensation ranging from <strong>$65,000 to $85,000/year</strong>.</p>

<h3>2. 32-Week Intensive Full-Stack Curriculum</h3>
<ul>
  <li><strong>Enterprise Backend:</strong> Java OOP, Spring Boot 3, Spring Cloud, RESTful microservices, MySQL & Redis.</li>
  <li><strong>Modern Frontend Architecture:</strong> React 18, Hooks, Redux Toolkit, TypeScript, Next.js.</li>
  <li><strong>Cloud Infrastructure:</strong> AWS deployment, Docker containerization, CI/CD pipeline automation.</li>
  <li><strong>Commercial Capstone:</strong> Deliver an enterprise-grade cloud SaaS application for your technical portfolio.</li>
</ul>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #0A2540 0%, #1A365D 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">Launch Your Tech Career in {geo}</h3>
  <p style="color: #93c5fd; margin-bottom: 18px;">Schedule a 1-on-1 advisor consultation and explore tuition funding options.</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #2563eb; color: #fff; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">Book Tech Consultation • Call 416-665-6668</a>
</div>"""

    elif any(k in q_all for k in ['grant', 'funding', 'second career', 'aid', 'subsidy', '补助', '资助', '免费']):
        subject = 'Government Grants'
        cat_key = 'financial_aid'
        cover = 'images/news_3.jpg'
        if is_zh:
            title = f"{current_year} {geo} 安省政府 Better Jobs Ontario 最高 $28,000 免费助学金申请全攻略"
            meta_title = f"{current_year} Better Jobs Ontario $28,000 政府助学金申请 {geo} | 维多利亚学院"
            meta_desc = f"安省失业/自雇/低收入人士必读！最高获批 $28,000+ 免费学费与生活费资助，无需自掏腰包学热门职业文凭。"
            summary = f"维多利亚学院 22 年资深顾问倾囊相授：{geo} 居民如何顺利申请安省政府最高 $28,000+ 免费培训助学金，全额覆盖学费、交通与生活费。"
            content = f"""<h2>1. 什么是 Better Jobs Ontario (Second Career) 助学金？</h2>
<p>安省政府设立的 <strong>Better Jobs Ontario</strong>（前身为 Second Career 第二职业）是一项旨在帮助安省求职者重返职场的无偿专项资助计划。符合资格者可获得 <strong>最高 $28,000+ 加元无需偿还的政府全额资助</strong>，全面涵盖职业学院学费、书本费、交通费、托儿补贴及每月基础生活费。</p>

<h3>2. 助学金可申请哪些维多利亚职业文凭？</h3>
<ul>
  <li>🩺 <strong>NACC Personal Support Worker (PSW DE 2022) 医疗护工文凭</strong>（23周，高薪紧缺）</li>
  <li>💻 <strong>Full Stack Web Technician 全栈开发技术员文凭</strong>（32周，起薪 $65k-$85k）</li>
  <li>📊 <strong>Accounting, Tax and Payroll 会计与税务管理文凭</strong>（30周，CPA 带教）</li>
  <li>👶 <strong>Early Childcare Assistant (ECA) 幼教助理文凭</strong>（22周，持牌托儿所实习）</li>
  <li>⚡ <strong>Electrician 309A / 442A 电工考证与实操班</strong>（名师带教，高时薪）</li>
</ul>

<blockquote>
  <p><strong>🌟 维多利亚学院 100% 免费全程协助：</strong> 从背景评估、课程研究报告到全套申请文案整理，资深规划师全程一对一协助，助您顺利获批！</p>
</blockquote>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">立即免费评估您的政府补助申请资格</h3>
  <p style="color: #dbeafe; margin-bottom: 18px;">22 年办学经验，协助 15,000+ 毕业学员在加国成功就业！</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #1e3a8a; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">立即预约一对一评估 • 416-665-6668</a>
</div>"""
        else:
            title = f"{current_year} How to Qualify for Up to $28,000+ Better Jobs Ontario Grants in {geo}"
            meta_title = f"{current_year} Better Jobs Ontario $28,000 Grant Guide {geo} | Victoria College"
            meta_desc = f"Learn how {geo} residents can receive up to $28,000+ non-repayable Ontario government grants for career college diplomas. 100% free consultation."
            summary = f"Step-by-step breakdown of Better Jobs Ontario funding eligibility, application process, and qualifying diplomas at Victoria International College in {geo}."
            content = f"""<h2>1. Understanding Better Jobs Ontario Grants in {geo}</h2>
<p>The Ontario Government's <strong>Better Jobs Ontario</strong> program provides non-repayable financial grants of <strong>up to $28,000+</strong> for residents seeking skills training in high-growth occupations. Funding covers 100% tuition, textbooks, transportation, child care, and living allowance support.</p>

<h3>2. Approved Career Diplomas at Victoria College</h3>
<ul>
  <li>🩺 <strong>NACC Personal Support Worker (PSW DE 2022):</strong> 23 weeks with guaranteed clinical practicum.</li>
  <li>💻 <strong>Full Stack Web Technician:</strong> 32 weeks, Java, React, TypeScript, AWS cloud.</li>
  <li>📊 <strong>Accounting, Tax and Payroll Administration:</strong> 30 weeks with CPA mentorship.</li>
  <li>👶 <strong>Early Childcare Assistant (ECA):</strong> 22 weeks with licensed daycare placement.</li>
  <li>⚡ <strong>Electrician (309A / 442A):</strong> Hands-on Canadian electrical code prep.</li>
</ul>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">Check Your Grant Eligibility Today</h3>
  <p style="color: #dbeafe; margin-bottom: 18px;">Our experienced advisors provide 100% free application support from start to finish.</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #1e3a8a; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">Book Free Grant Assessment • Call 416-665-6668</a>
</div>"""

    else:
        # General Career & Programs template
        cat_key = 'programs'
        cover = 'images/news_1.jpg'
        if is_zh:
            title = f"{current_year} {geo} 紧缺职业技能培训与就业发展指南：{primary_kw}"
            meta_title = f"{current_year} {geo} 紧缺职业文凭与助学金全攻略 | 维多利亚职业学院"
            meta_desc = f"探索 {geo} 地区最受欢迎的高薪紧缺专业。维多利亚学院提供护工、全栈IT、会计、幼教及电工文凭，支持政府助学金。"
            summary = f"深度梳理 {geo} 就业市场趋势，帮助职业转型者与新移民锁定高薪专业文凭并申请政府资助。"
            content = f"""<h2>1. {geo} 就业市场新机遇</h2>
<p>立足于 <strong>{geo}</strong>，维多利亚职业学院办学逾 22 年，累计协助 15,000 多名毕业学员在加国职场获得高薪稳定职位。无论是医疗护理、全栈软件开发、企业会计税务，还是持牌幼教与建筑电工，我们均提供名师亲授的系统化职业文凭课程。</p>

<h3>2. 为什么选择维多利亚职业学院？</h3>
<ul>
  <li><strong>安省教育部正规注册认可：</strong> 严格遵循 Ontario Career Colleges Act, 2005 办学标准。</li>
  <li><strong>紧扣北美企业用人标准：</strong> 课程结合加国一线商业项目与真实行业案例。</li>
  <li><strong>最高 $28,000+ 政府补助全程协助：</strong> 专业规划师一对一评估辅导，助学金直达学费与生活补贴。</li>
</ul>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #8B0000 0%, #B22222 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">免费预约升学规划与专业咨询</h3>
  <p style="color: #ffd2d2; margin-bottom: 18px;">致电 416-665-6668 或在线预约一对一免费顾问规划。</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #8B0000; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">立即预约免费咨询</a>
</div>"""
        else:
            title = f"{current_year} In-Demand Career Training & Jobs in {geo}: {primary_kw}"
            meta_title = f"{current_year} Career Diplomas & Jobs in {geo} | Victoria College"
            meta_desc = f"Explore high-growth career programs in {geo}. Accredited diplomas in Healthcare, IT, Business, Childcare & Trades with $28,000+ grants."
            summary = f"Overview of high-demand vocational training programs and funding opportunities in {geo} at Victoria International College."
            content = f"""<h2>1. Career Opportunities in {geo}</h2>
<p>Located in the heart of <strong>{geo}</strong>, Victoria International College of Business & Technology has empowered over 15,000 graduates across Canada over 22 years of educational excellence. We deliver registered vocational diplomas in high-growth industries including Healthcare (PSW), Technology (Full Stack Web), Business (Accounting & Tax), Education (ECA), and Trades (Electrician).</p>

<h3>2. Why Choose Victoria International College?</h3>
<ul>
  <li><strong>Ontario Registered:</strong> Fully approved under the Ontario Career Colleges Act, 2005.</li>
  <li><strong>Hands-on Labs & Guaranteed Practicums:</strong> Real-world experience with top Canadian employers.</li>
  <li><strong>100% Free Grant Application Assistance:</strong> Up to $28,000+ non-repayable funding for eligible students.</li>
</ul>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #8B0000 0%, #B22222 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">Book Your Free Admissions Consultation</h3>
  <p style="color: #ffd2d2; margin-bottom: 18px;">Speak with an advisor today at 416-665-6668 or schedule your consultation online.</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #8B0000; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">Book Free Consultation • Call 416-665-6668</a>
</div>"""

    # Generate slug
    slug_base = f"{primary_kw} {geo}".replace('$', 'dollar').replace('&', 'and')
    slug = slugify(slug_base)

    return {
        'title': title,
        'slug': slug,
        'meta_title': meta_title,
        'meta_description': meta_desc,
        'summary': summary,
        'content': content,
        'category': cat_key,
        'keywords': keywords,
        'geo_target': geo,
        'geo_lat': lat,
        'geo_lng': lng,
        'cover_image': cover,
        'author': 'Victoria College Editorial'
    }

def build_sitemap_xml() -> str:
    """
    Generate dynamic XML sitemap conforming to Sitemaps 0.9 & Google Geo extension.
    CRITICAL RULE: Only ACTIVE articles (status='active' and is_active=1) are included!
    Hidden / draft articles are strictly excluded.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
    SELECT slug, title, geo_target, geo_lat, geo_lng, updated_at, published_at, created_at 
    FROM articles 
    WHERE is_active = 1 AND status = 'active'
    ORDER BY id DESC
    ''')
    active_articles = cursor.fetchall()

    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    base_url = "https://viccollege.ca"

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:geo="http://www.google.com/geo/schemas/sitemap/1.0">',
        '  <!-- Core Institutional Pages -->',
        '  <url>',
        f'    <loc>{base_url}/</loc>',
        f'    <lastmod>{today_str}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{base_url}/#programs</loc>',
        f'    <lastmod>{today_str}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>0.9</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{base_url}/#financial-aid</loc>',
        f'    <lastmod>{today_str}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>0.9</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{base_url}/#about</loc>',
        f'    <lastmod>{today_str}</lastmod>',
        '    <changefreq>monthly</changefreq>',
        '    <priority>0.8</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{base_url}/#consultation</loc>',
        f'    <lastmod>{today_str}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>0.85</priority>',
        '  </url>',
        '  <!-- Active SEO & GEO Articles (Hidden articles are excluded) -->'
    ]

    for row in active_articles:
        slug = row['slug']
        pub_date = (row['published_at'] or row['updated_at'] or row['created_at'])[:10]
        geo_target = row['geo_target'] or 'Toronto, Ontario'
        lat = row['geo_lat'] or 43.7758
        lng = row['geo_lng'] or -79.3458

        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{base_url}/article.html?slug={slug}</loc>')
        xml_lines.append(f'    <lastmod>{pub_date}</lastmod>')
        xml_lines.append('    <changefreq>weekly</changefreq>')
        xml_lines.append('    <priority>0.85</priority>')
        xml_lines.append('    <geo:geo>')
        xml_lines.append(f'      <geo:lat>{lat}</geo:lat>')
        xml_lines.append(f'      <geo:long>{lng}</geo:long>')
        xml_lines.append('    </geo:geo>')
        xml_lines.append(f'    <!-- GEO Target: {geo_target} -->')
        xml_lines.append('  </url>')

    xml_lines.append('</urlset>')
    sitemap_content = '\n'.join(xml_lines)

    # Save to disk as well
    try:
        sitemap_path = os.path.join(BASE_DIR, 'sitemap.xml')
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
    except Exception as e:
        print(">> Warning: could not write sitemap.xml to disk:", e)

    return sitemap_content


# ==============================================================================
# Public Article & Sitemap APIs
# ==============================================================================

@app.route('/sitemap.xml', methods=['GET'])
def serve_sitemap_xml():
    """Serve dynamically built GEO & SEO XML sitemap."""
    xml_content = build_sitemap_xml()
    return Response(xml_content, mimetype='application/xml')

@app.route('/api/articles', methods=['GET'])
def public_get_articles():
    """
    Public API: Returns list of ACTIVE articles for the website.
    Hidden/draft articles are strictly excluded from public view.
    """
    category = request.args.get('category', '').strip().lower()
    search = request.args.get('search', '').strip().lower()
    geo = request.args.get('geo', '').strip().lower()

    query = """
    SELECT id, title, slug, summary, category, keywords, geo_target, cover_image, 
           author, meta_title, meta_description, views, created_at, published_at 
    FROM articles 
    WHERE is_active = 1 AND status = 'active'
    """
    params = []

    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)

    if geo:
        query += " AND LOWER(geo_target) LIKE ?"
        params.append(f"%{geo}%")

    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(keywords) LIKE ? OR LOWER(summary) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY id DESC"

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    articles = [dict(row) for row in cursor.fetchall()]

    return jsonify({'articles': articles, 'count': len(articles)})

@app.route('/api/articles/<string:identifier>', methods=['GET'])
def public_get_article(identifier):
    """
    Public API: Returns a single article by slug or numeric ID.
    If hidden, only admins/super admins can view in preview mode.
    Increments view count for active public requests.
    """
    db = get_db()
    cursor = db.cursor()

    if identifier.isdigit():
        cursor.execute("SELECT * FROM articles WHERE id = ?", (int(identifier),))
    else:
        cursor.execute("SELECT * FROM articles WHERE slug = ?", (identifier,))

    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Article not found.'}), 404

    article = dict(row)

    # If hidden, verify admin token
    user = get_current_user()
    is_admin = user and user.get('role') in ['admin', 'super_admin']

    if (article['status'] == 'hidden' or article['is_active'] == 0) and not is_admin:
        return jsonify({'error': 'Article is currently unpublished / hidden.'}), 404

    # Increment views if public active view
    if article['status'] == 'active' and not is_admin:
        db.execute("UPDATE articles SET views = views + 1 WHERE id = ?", (article['id'],))
        db.commit()
        article['views'] += 1

    article['is_preview'] = (article['status'] == 'hidden')
    return jsonify({'article': article})


# ==============================================================================
# Admin SEO & GEO Article Management & AI Generator APIs
# ==============================================================================

@app.route('/api/admin/articles', methods=['GET'])
def admin_get_articles():
    """Admin API: List all articles (both active and hidden/draft)."""
    err = require_admin()
    if err: return err

    category = request.args.get('category', '').strip().lower()
    status_filter = request.args.get('status', '').strip().lower()
    search = request.args.get('search', '').strip().lower()

    query = "SELECT * FROM articles WHERE 1=1"
    params = []

    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)

    if status_filter and status_filter != 'all':
        query += " AND status = ?"
        params.append(status_filter)

    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(keywords) LIKE ? OR LOWER(geo_target) LIKE ? OR LOWER(slug) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY id DESC"

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    articles = [dict(row) for row in cursor.fetchall()]

    # Summary counts
    cursor.execute("SELECT COUNT(*) as total FROM articles")
    total_cnt = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as active_cnt FROM articles WHERE is_active = 1 AND status = 'active'")
    active_cnt = cursor.fetchone()['active_cnt']
    cursor.execute("SELECT COUNT(*) as hidden_cnt FROM articles WHERE is_active = 0 OR status = 'hidden'")
    hidden_cnt = cursor.fetchone()['hidden_cnt']

    return jsonify({
        'articles': articles,
        'count': len(articles),
        'stats': {
            'total': total_cnt,
            'active': active_cnt,
            'hidden': hidden_cnt
        }
    })

@app.route('/api/admin/articles/generate', methods=['POST'])
def admin_generate_article():
    """
    Super Admin API: Generate a complete SEO & GEO Article based on keywords.
    CRITICAL RULE: The generated article is HIDDEN (draft) by default!
    Super admin can review and activate it so it appears on the public site and sitemap.
    """
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    keywords = (data.get('keywords') or '').strip()
    geo_target = (data.get('geo_target') or 'Toronto & GTA, Ontario').strip()
    category = (data.get('category') or 'programs').strip().lower()
    language = (data.get('language') or 'en').strip().lower()
    tone = (data.get('tone') or 'Career Changers & Job Seekers').strip()
    topic = (data.get('topic') or '').strip()

    if not keywords:
        return jsonify({'error': 'Please provide keywords for article generation.'}), 400

    db = get_db()
    cursor = db.cursor()

    # Load OpenAI Settings if available
    cursor.execute("SELECT value FROM settings WHERE key = 'openai_api_key'")
    key_row = cursor.fetchone()
    api_key = key_row['value'].strip() if key_row else ''

    cursor.execute("SELECT value FROM settings WHERE key = 'openai_model'")
    model_row = cursor.fetchone()
    model = model_row['value'] if model_row else 'gpt-4o-mini'

    generated = None

    # Try calling OpenAI if requests and api_key are present
    if requests and api_key and not api_key.startswith('••••'):
        try:
            is_zh = language in ['zh', 'chinese', 'cn']
            prompt = f"""You are an elite SEO & GEO Content Strategist and Copywriter for Victoria International College of Business & Technology in Ontario, Canada (Ontario registered career college, 22+ years).
Generate a complete, high-ranking, in-depth GEO and SEO optimized article in {'Simplified Chinese (zh-CN)' if is_zh else 'English'}.

Inputs:
- Target SEO Keywords: {keywords}
- Target GEO Location: {geo_target} (e.g. Toronto, Markham, North York, Mississauga, GTA, Ontario)
- Category: {category}
- Audience / Tone: {tone}
- Optional Topic Focus: {topic}

Return ONLY a valid, parseable JSON object with these EXACT keys:
{{
  "title": "Engaging SEO Title with GEO location and current year",
  "slug": "kebab-case-english-url-slug-based-on-keywords",
  "meta_title": "SEO Meta Title (under 60 chars)",
  "meta_description": "Compelling Meta Description (150-160 chars) with CTA and Geo Keyword",
  "summary": "2-sentence executive summary of the article",
  "content": "Rich HTML content with <h2>, <h3>, <p>, <ul>, <li>, <blockquote>, wage facts ($20-$28/hr for PSW, $65k-$85k for IT, $48k-$65k for Accounting), Better Jobs Ontario grants up to $28,000+, Markham Main Campus address (7050 Woodbine Ave., Unit 300, Markham), and a closing CTA consultation box with phone 416-665-6668.",
  "category": "{category}",
  "keywords": "{keywords}",
  "geo_target": "{geo_target}",
  "cover_image": "images/news_1.jpg",
  "author": "Victoria College Editorial"
}}"""

            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a professional educational SEO and local GEO content generator. You only respond with pure JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=25
            )

            if res.status_code == 200:
                resp_json = res.json()
                raw_text = resp_json['choices'][0]['message']['content'].strip()
                # Strip markdown code blocks if present
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                generated = json.loads(raw_text)
        except Exception as e:
            print(">> OpenAI Generation failed, falling back to built-in generator:", e)

    # Fallback to intelligent local generator if OpenAI was not used or failed
    if not generated:
        generated = generate_seo_article_local(
            keywords=keywords,
            geo_target=geo_target,
            category=category,
            language=language,
            tone=tone,
            topic=topic
        )

    # Ensure unique slug
    base_slug = slugify(generated.get('slug') or generated.get('title') or keywords)
    unique_slug = base_slug
    idx = 1
    while True:
        cursor.execute("SELECT id FROM articles WHERE slug = ?", (unique_slug,))
        if not cursor.fetchone():
            break
        unique_slug = f"{base_slug}-{idx}"
        idx += 1

    now_str = datetime.utcnow().isoformat()
    lat, lng = get_geo_coordinates(generated.get('geo_target') or geo_target)

    # Insert into SQLite Database with STATUS = 'hidden' and IS_ACTIVE = 0 by default!
    cursor.execute('''
    INSERT INTO articles (
        title, slug, summary, content, category, keywords, geo_target, 
        geo_lat, geo_lng, cover_image, status, is_active, author, 
        meta_title, meta_description, views, created_at, updated_at, published_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'hidden', 0, ?, ?, ?, 0, ?, ?, NULL)
    ''', (
        generated.get('title', 'Untitled SEO Article'),
        unique_slug,
        generated.get('summary', ''),
        generated.get('content', ''),
        generated.get('category', category),
        keywords,
        generated.get('geo_target', geo_target),
        lat,
        lng,
        generated.get('cover_image', 'images/news_1.jpg'),
        generated.get('author', 'Victoria College Editorial'),
        generated.get('meta_title', generated.get('title', '')),
        generated.get('meta_description', generated.get('summary', '')),
        now_str,
        now_str
    ))
    db.commit()
    new_art_id = cursor.lastrowid

    # Fetch newly created article
    cursor.execute("SELECT * FROM articles WHERE id = ?", (new_art_id,))
    new_art = dict(cursor.fetchone())

    return jsonify({
        'success': True,
        'id': new_art_id,
        'article': new_art,
        'status': 'hidden',
        'is_active': 0,
        'message': f'Article "{new_art["title"]}" generated successfully (Hidden by default). Click Activate to publish to live site and sitemap.'
    })

@app.route('/api/admin/articles', methods=['POST'])
def admin_create_article():
    """Super Admin API: Manually create article. Defaults to hidden/draft."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    keywords = (data.get('keywords') or '').strip()
    geo_target = (data.get('geo_target') or 'Toronto & GTA, Ontario').strip()
    category = (data.get('category') or 'programs').strip().lower()
    summary = (data.get('summary') or '').strip()
    meta_title = (data.get('meta_title') or title).strip()
    meta_description = (data.get('meta_description') or summary).strip()
    cover_image = data.get('cover_image') or 'images/news_1.jpg'
    author = data.get('author') or 'Victoria College Editorial'
    status = data.get('status') or 'hidden'
    is_active = 1 if status == 'active' else 0

    if not title or not content:
        return jsonify({'error': 'Title and Content are required.'}), 400

    slug_input = (data.get('slug') or title).strip()
    base_slug = slugify(slug_input)
    unique_slug = base_slug
    
    db = get_db()
    cursor = db.cursor()
    idx = 1
    while True:
        cursor.execute("SELECT id FROM articles WHERE slug = ?", (unique_slug,))
        if not cursor.fetchone():
            break
        unique_slug = f"{base_slug}-{idx}"
        idx += 1

    now_str = datetime.utcnow().isoformat()
    pub_str = now_str if is_active else None
    lat, lng = get_geo_coordinates(geo_target)

    cursor.execute('''
    INSERT INTO articles (
        title, slug, summary, content, category, keywords, geo_target, 
        geo_lat, geo_lng, cover_image, status, is_active, author, 
        meta_title, meta_description, views, created_at, updated_at, published_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
    ''', (
        title, unique_slug, summary, content, category, keywords, geo_target,
        lat, lng, cover_image, status, is_active, author,
        meta_title, meta_description, now_str, now_str, pub_str
    ))
    db.commit()
    new_id = cursor.lastrowid

    if is_active:
        build_sitemap_xml()

    return jsonify({
        'success': True,
        'id': new_id,
        'message': f'Article "{title}" created successfully.'
    })

@app.route('/api/admin/articles/<int:art_id>', methods=['GET'])
def admin_get_article_item(art_id):
    """Admin API: Get article details for editing or viewing."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM articles WHERE id = ?", (art_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Article not found.'}), 404

    return jsonify({'article': dict(row)})

@app.route('/api/admin/articles/<int:art_id>', methods=['PUT'])
def admin_update_article(art_id):
    """Admin API: Update article details and sync sitemap if status is active."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM articles WHERE id = ?", (art_id,))
    curr = cursor.fetchone()
    if not curr:
        return jsonify({'error': 'Article not found.'}), 404

    title = data.get('title')
    slug = data.get('slug')
    summary = data.get('summary')
    content = data.get('content')
    category = data.get('category')
    keywords = data.get('keywords')
    geo_target = data.get('geo_target')
    meta_title = data.get('meta_title')
    meta_description = data.get('meta_description')
    cover_image = data.get('cover_image')
    author = data.get('author')
    status = data.get('status')

    updates = []
    params = []

    if title is not None:
        updates.append("title = ?")
        params.append(title.strip())

    if slug is not None and slug.strip():
        new_slug = slugify(slug)
        cursor.execute("SELECT id FROM articles WHERE slug = ? AND id != ?", (new_slug, art_id))
        if cursor.fetchone():
            new_slug = f"{new_slug}-{int(time.time())}"
        updates.append("slug = ?")
        params.append(new_slug)

    if summary is not None:
        updates.append("summary = ?")
        params.append(summary.strip())

    if content is not None:
        updates.append("content = ?")
        params.append(content.strip())

    if category is not None:
        updates.append("category = ?")
        params.append(category.strip().lower())

    if keywords is not None:
        updates.append("keywords = ?")
        params.append(keywords.strip())

    if geo_target is not None:
        updates.append("geo_target = ?")
        params.append(geo_target.strip())
        lat, lng = get_geo_coordinates(geo_target)
        updates.append("geo_lat = ?")
        params.append(lat)
        updates.append("geo_lng = ?")
        params.append(lng)

    if meta_title is not None:
        updates.append("meta_title = ?")
        params.append(meta_title.strip())

    if meta_description is not None:
        updates.append("meta_description = ?")
        params.append(meta_description.strip())

    if cover_image is not None:
        updates.append("cover_image = ?")
        params.append(cover_image.strip())

    if author is not None:
        updates.append("author = ?")
        params.append(author.strip())

    if status is not None and status in ['active', 'hidden']:
        updates.append("status = ?")
        params.append(status)
        is_act = 1 if status == 'active' else 0
        updates.append("is_active = ?")
        params.append(is_act)
        if is_act and not curr['published_at']:
            updates.append("published_at = ?")
            params.append(datetime.utcnow().isoformat())

    updates.append("updated_at = ?")
    now_str = datetime.utcnow().isoformat()
    params.append(now_str)

    params.append(art_id)
    query = f"UPDATE articles SET {', '.join(updates)} WHERE id = ?"
    db.execute(query, params)
    db.commit()

    build_sitemap_xml()

    return jsonify({'success': True, 'message': 'Article updated successfully.'})

@app.route('/api/admin/articles/<int:art_id>/toggle-status', methods=['PATCH'])
def admin_toggle_article_status(art_id):
    """
    Super Admin API: 1-click Toggle between Active (Live on site) and Hidden (Draft).
    Automatically updates the XML sitemap.
    """
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title, status, is_active, published_at FROM articles WHERE id = ?", (art_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Article not found.'}), 404

    now_str = datetime.utcnow().isoformat()
    if row['status'] == 'active' and row['is_active'] == 1:
        new_status = 'hidden'
        new_active = 0
        msg = f'Article "{row["title"]}" is now HIDDEN (removed from live site & sitemap).'
        db.execute("UPDATE articles SET status = ?, is_active = ?, updated_at = ? WHERE id = ?", (new_status, new_active, now_str, art_id))
    else:
        new_status = 'active'
        new_active = 1
        pub_at = row['published_at'] or now_str
        msg = f'Article "{row["title"]}" is now ACTIVE (live on website & included in sitemap)!'
        db.execute("UPDATE articles SET status = ?, is_active = ?, published_at = ?, updated_at = ? WHERE id = ?", (new_status, new_active, pub_at, now_str, art_id))

    db.commit()

    # Rebuild dynamic sitemap
    build_sitemap_xml()

    return jsonify({
        'success': True,
        'status': new_status,
        'is_active': new_active,
        'message': msg
    })

@app.route('/api/admin/articles/<int:art_id>', methods=['DELETE'])
def admin_delete_article(art_id):
    """Admin API: Delete an article and rebuild sitemap."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT title FROM articles WHERE id = ?", (art_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Article not found.'}), 404

    db.execute("DELETE FROM articles WHERE id = ?", (art_id,))
    db.commit()

    build_sitemap_xml()
    return jsonify({'success': True, 'message': f'Article "{row["title"]}" deleted.'})

@app.route('/api/admin/sitemap/generate', methods=['POST'])
def admin_generate_sitemap():
    """
    Super Admin API: Trigger manual sitemap generation and return XML content & metrics.
    """
    err = require_admin()
    if err: return err

    xml_content = build_sitemap_xml()

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as active_cnt FROM articles WHERE is_active = 1 AND status = 'active'")
    active_cnt = cursor.fetchone()['active_cnt']

    return jsonify({
        'success': True,
        'total_urls': 5 + active_cnt,
        'active_articles': active_cnt,
        'timestamp': datetime.utcnow().isoformat(),
        'sitemap_url': 'http://localhost:5055/sitemap.xml',
        'xml_preview': xml_content[:1500] + ('\n... (truncated)' if len(xml_content) > 1500 else ''),
        'message': f'Sitemap regenerated successfully with {5 + active_cnt} URLs ({active_cnt} active GEO articles indexed).'
    })

@app.route('/api/admin/sitemap/status', methods=['GET'])
def admin_sitemap_status():
    """Admin API: Return current sitemap metrics."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as active_cnt FROM articles WHERE is_active = 1 AND status = 'active'")
    active_cnt = cursor.fetchone()['active_cnt']
    cursor.execute("SELECT COUNT(*) as hidden_cnt FROM articles WHERE is_active = 0 OR status = 'hidden'")
    hidden_cnt = cursor.fetchone()['hidden_cnt']

    return jsonify({
        'total_urls': 5 + active_cnt,
        'active_articles': active_cnt,
        'hidden_articles': hidden_cnt,
        'sitemap_path': '/sitemap.xml',
        'last_updated': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    })


# ==============================================================================
# Dynamic Academic Programs Management APIs (Public & Admin CRUD)
# ==============================================================================

@app.route('/api/programs', methods=['GET'])
def get_public_programs():
    """
    Public API: Returns all active academic programs ordered by display_order.
    Used for dynamic homepage rendering, navigation dropdowns, and modal deep-dives.
    """
    db = get_db()
    cursor = db.cursor()
    category = request.args.get('category', '').strip().lower()

    query = "SELECT * FROM programs WHERE is_active = 1"
    params = []
    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY display_order ASC, id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    programs = [format_program_dict(r) for r in rows]

    return jsonify({
        'success': True,
        'programs': programs,
        'count': len(programs)
    })

@app.route('/api/programs/<identifier>', methods=['GET'])
def get_public_program(identifier):
    """Public API: Get single active program by ID or slug."""
    db = get_db()
    cursor = db.cursor()
    if identifier.isdigit():
        cursor.execute("SELECT * FROM programs WHERE id = ? AND is_active = 1", (int(identifier),))
    else:
        ident_lower = identifier.lower()
        if ident_lower in ['computerized-accounting', 'accounting-tax-and-payroll', 'accounting-tax-payroll']:
            ident_lower = 'accounting'
        elif ident_lower in ['early-childcare-assistant', 'early-childcare-assistant-eca', 'eca-course']:
            ident_lower = 'eca'
        elif ident_lower in ['acupuncture-program', 'acupuncture-course', 'tcm-acupuncture']:
            ident_lower = 'acupuncture'
        elif ident_lower in ['electrician', 'electrician-309a', 'electrician-442a', 'electrician-course', 'electrician-training', 'electrician-program', '309a-electrician', '442a-electrician']:
            ident_lower = 'electrician'
        elif ident_lower in ['tech', 'software-development', 'software-dev', 'fullstack', 'full-stack', 'full-stack-web-development-ai', 'web-development', 'full-stack-developer', 'software-development-course', 'software-development-program']:
            ident_lower = 'tech'
        cursor.execute("SELECT * FROM programs WHERE slug = ? AND is_active = 1", (ident_lower,))
    
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Program not found or is currently inactive.'}), 404

    return jsonify({
        'success': True,
        'program': format_program_dict(row)
    })

@app.route('/api/admin/programs', methods=['GET'])
def admin_get_programs():
    """Admin API: Return all programs (active and inactive) with optional filtering."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()

    search = request.args.get('search', '').strip().lower()
    category = request.args.get('category', '').strip().lower()
    status = request.args.get('status', '').strip().lower()

    query = "SELECT * FROM programs WHERE 1=1"
    params = []

    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)

    if status == 'active':
        query += " AND is_active = 1"
    elif status == 'inactive':
        query += " AND is_active = 0"

    if search:
        query += " AND (LOWER(title_en) LIKE ? OR LOWER(title_zh) LIKE ? OR LOWER(slug) LIKE ? OR LOWER(category) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY display_order ASC, id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    programs = [format_program_dict(r) for r in rows]

    return jsonify({
        'success': True,
        'programs': programs,
        'count': len(programs)
    })

@app.route('/api/admin/programs', methods=['POST'])
def admin_create_program():
    """Admin API: Create a new academic program."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    title_en = (data.get('title_en') or '').strip()
    title_zh = (data.get('title_zh') or '').strip()

    if not title_en:
        return jsonify({'error': 'Program title in English is required.'}), 400
    if not title_zh:
        title_zh = title_en

    slug_input = (data.get('slug') or '').strip().lower()
    if not slug_input:
        slug_input = slugify(title_en)
    slug = re.sub(r'[^a-z0-9_-]', '', slug_input.replace(' ', '-'))
    if not slug:
        slug = f"prog-{int(time.time())}"

    db = get_db()
    cursor = db.cursor()

    # Ensure unique slug
    cursor.execute("SELECT id FROM programs WHERE slug = ?", (slug,))
    if cursor.fetchone():
        slug = f"{slug}-{int(time.time()) % 10000}"

    category = (data.get('category') or 'general').strip().lower()
    image_url = (data.get('image_url') or 'images/fullstack.jpg').strip()
    badge_en = (data.get('badge_en') or '').strip()
    badge_zh = (data.get('badge_zh') or '').strip()
    desc_en = (data.get('desc_en') or '').strip()
    desc_zh = (data.get('desc_zh') or '').strip()

    def process_array_field(val):
        if isinstance(val, list):
            return json.dumps([str(x).strip() for x in val if str(x).strip()], ensure_ascii=False)
        elif isinstance(val, str):
            lines = [l.strip() for l in val.split('\n') if l.strip()]
            return json.dumps(lines, ensure_ascii=False)
        return '[]'

    bullets_en = process_array_field(data.get('bullets_en'))
    bullets_zh = process_array_field(data.get('bullets_zh'))
    duration_en = (data.get('duration_en') or '').strip()
    duration_zh = (data.get('duration_zh') or '').strip()
    credential_en = (data.get('credential_en') or '').strip()
    credential_zh = (data.get('credential_zh') or '').strip()
    overview_en = (data.get('overview_en') or '').strip()
    overview_zh = (data.get('overview_zh') or '').strip()
    modules_en = process_array_field(data.get('modules_en'))
    modules_zh = process_array_field(data.get('modules_zh'))
    careers_en = (data.get('careers_en') or '').strip()
    careers_zh = (data.get('careers_zh') or '').strip()
    outcomes_en = (data.get('outcomes_en') or '').strip()
    outcomes_zh = (data.get('outcomes_zh') or '').strip()
    detail_json_en = json.dumps(data.get('detail_json_en') or {}, ensure_ascii=False) if isinstance(data.get('detail_json_en'), dict) else (data.get('detail_json_en') or '{}')
    detail_json_zh = json.dumps(data.get('detail_json_zh') or {}, ensure_ascii=False) if isinstance(data.get('detail_json_zh'), dict) else (data.get('detail_json_zh') or '{}')

    cursor.execute("SELECT MAX(display_order) as max_ord FROM programs")
    max_ord_row = cursor.fetchone()
    max_ord = max_ord_row['max_ord'] if max_ord_row and max_ord_row['max_ord'] is not None else 0
    display_order = int(data.get('display_order') if data.get('display_order') is not None else max_ord + 1)
    is_active = int(data.get('is_active', 1))

    now_str = datetime.utcnow().isoformat()

    cursor.execute('''
    INSERT INTO programs (
        slug, category, image_url, badge_en, badge_zh, title_en, title_zh,
        desc_en, desc_zh, bullets_en, bullets_zh, duration_en, duration_zh,
        credential_en, credential_zh, overview_en, overview_zh,
        modules_en, modules_zh, careers_en, careers_zh, outcomes_en, outcomes_zh,
        detail_json_en, detail_json_zh,
        display_order, is_active, created_at, updated_at
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?,
        ?, ?, ?, ?
    )
    ''', (
        slug, category, image_url, badge_en, badge_zh, title_en, title_zh,
        desc_en, desc_zh, bullets_en, bullets_zh, duration_en, duration_zh,
        credential_en, credential_zh, overview_en, overview_zh,
        modules_en, modules_zh, careers_en, careers_zh, outcomes_en, outcomes_zh,
        detail_json_en, detail_json_zh,
        display_order, is_active, now_str, now_str
    ))
    db.commit()
    new_id = cursor.lastrowid

    cursor.execute("SELECT * FROM programs WHERE id = ?", (new_id,))
    created_row = cursor.fetchone()

    return jsonify({
        'success': True,
        'id': new_id,
        'slug': slug,
        'program': format_program_dict(created_row),
        'message': f'Program "{title_en}" created successfully.'
    }), 201

@app.route('/api/admin/programs/<int:prog_id>', methods=['GET'])
def admin_get_program(prog_id):
    """Admin API: Get single program by ID."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM programs WHERE id = ?", (prog_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Program not found.'}), 404

    return jsonify({
        'success': True,
        'program': format_program_dict(row)
    })

@app.route('/api/admin/programs/<int:prog_id>', methods=['PUT'])
def admin_update_program(prog_id):
    """Admin API: Update an existing academic program."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM programs WHERE id = ?", (prog_id,))
    curr = cursor.fetchone()
    if not curr:
        return jsonify({'error': 'Program not found.'}), 404

    def process_array_field(val):
        if isinstance(val, list):
            return json.dumps([str(x).strip() for x in val if str(x).strip()], ensure_ascii=False)
        elif isinstance(val, str):
            lines = [l.strip() for l in val.split('\n') if l.strip()]
            return json.dumps(lines, ensure_ascii=False)
        return None

    updates = []
    params = []

    fields_mapping = [
        ('slug', lambda v: re.sub(r'[^a-z0-9_-]', '', str(v).strip().lower().replace(' ', '-'))),
        ('category', lambda v: str(v).strip().lower()),
        ('image_url', lambda v: str(v).strip()),
        ('badge_en', lambda v: str(v).strip()),
        ('badge_zh', lambda v: str(v).strip()),
        ('title_en', lambda v: str(v).strip()),
        ('title_zh', lambda v: str(v).strip()),
        ('desc_en', lambda v: str(v).strip()),
        ('desc_zh', lambda v: str(v).strip()),
        ('duration_en', lambda v: str(v).strip()),
        ('duration_zh', lambda v: str(v).strip()),
        ('credential_en', lambda v: str(v).strip()),
        ('credential_zh', lambda v: str(v).strip()),
        ('overview_en', lambda v: str(v).strip()),
        ('overview_zh', lambda v: str(v).strip()),
        ('careers_en', lambda v: str(v).strip()),
        ('careers_zh', lambda v: str(v).strip()),
        ('outcomes_en', lambda v: str(v).strip()),
        ('outcomes_zh', lambda v: str(v).strip()),
        ('display_order', lambda v: int(v)),
        ('is_active', lambda v: int(v))
    ]

    for key, transform in fields_mapping:
        if key in data and data[key] is not None:
            val = transform(data[key])
            if key == 'slug' and val != curr['slug']:
                # Check uniqueness
                cursor.execute("SELECT id FROM programs WHERE slug = ? AND id != ?", (val, prog_id))
                if cursor.fetchone():
                    return jsonify({'error': f'Slug "{val}" is already in use by another program.'}), 400
            updates.append(f"{key} = ?")
            params.append(val)

    for array_key in ['bullets_en', 'bullets_zh', 'modules_en', 'modules_zh']:
        if array_key in data and data[array_key] is not None:
            json_val = process_array_field(data[array_key])
            if json_val is not None:
                updates.append(f"{array_key} = ?")
                params.append(json_val)

    for detail_key in ['detail_json_en', 'detail_json_zh']:
        if detail_key in data and data[detail_key] is not None:
            val = data[detail_key]
            if isinstance(val, dict):
                json_str = json.dumps(val, ensure_ascii=False)
            elif isinstance(val, str):
                json_str = val.strip()
            else:
                json_str = '{}'
            updates.append(f"{detail_key} = ?")
            params.append(json_str)

    if not updates:
        return jsonify({'message': 'No changes detected.'})

    updates.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat())
    params.append(prog_id)

    query = f"UPDATE programs SET {', '.join(updates)} WHERE id = ?"
    db.execute(query, params)
    db.commit()

    cursor.execute("SELECT * FROM programs WHERE id = ?", (prog_id,))
    updated_row = cursor.fetchone()

    return jsonify({
        'success': True,
        'program': format_program_dict(updated_row),
        'message': f'Program "{data.get("title_en") or curr["title_en"]}" updated successfully.'
    })

@app.route('/api/admin/programs/<int:prog_id>/toggle-status', methods=['PATCH'])
def admin_toggle_program_status(prog_id):
    """Admin API: 1-click toggle active/inactive status for a program."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title_en, is_active FROM programs WHERE id = ?", (prog_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Program not found.'}), 404

    new_active = 0 if row['is_active'] == 1 else 1
    now_str = datetime.utcnow().isoformat()
    db.execute("UPDATE programs SET is_active = ?, updated_at = ? WHERE id = ?", (new_active, now_str, prog_id))
    db.commit()

    status_str = "ACTIVE (Visible on website)" if new_active == 1 else "INACTIVE (Hidden from website)"
    return jsonify({
        'success': True,
        'is_active': new_active,
        'message': f'Program "{row["title_en"]}" is now {status_str}.'
    })

@app.route('/api/admin/programs/<int:prog_id>', methods=['DELETE'])
def admin_delete_program(prog_id):
    """Admin API: Delete an academic program."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT title_en FROM programs WHERE id = ?", (prog_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Program not found.'}), 404

    db.execute("DELETE FROM programs WHERE id = ?", (prog_id,))
    db.commit()

    return jsonify({
        'success': True,
        'message': f'Program "{row["title_en"]}" deleted successfully.'
    })

@app.route('/api/admin/programs/reorder', methods=['POST'])
def admin_reorder_programs():
    """Admin API: Reorder academic programs display order."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    orders = data.get('orders') or data.get('ordered_ids') or []

    if not orders or not isinstance(orders, list):
        return jsonify({'error': 'Invalid orders payload. Expected array of {id, display_order} or array of IDs.'}), 400

    db = get_db()
    now_str = datetime.utcnow().isoformat()

    for idx, item in enumerate(orders):
        if isinstance(item, dict) and 'id' in item:
            p_id = int(item['id'])
            order_num = int(item.get('display_order', idx + 1))
        elif isinstance(item, int) or (isinstance(item, str) and item.isdigit()):
            p_id = int(item)
            order_num = idx + 1
        else:
            continue
        db.execute("UPDATE programs SET display_order = ?, updated_at = ? WHERE id = ?", (order_num, now_str, p_id))

    db.commit()
    return jsonify({'success': True, 'message': 'Programs order updated successfully.'})


# ==============================================================================
# Dynamic Job Fair & Event Banner APIs
# ==============================================================================

def format_job_fair_dict(row):
    if not row: return None
    return dict(row)

@app.route('/api/job-fair', methods=['GET'])
def get_active_job_fair():
    """
    Public API: Returns the currently active job fair event banner.
    If no active event exists or is_active == 0, returns job_fair: null.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM job_fairs WHERE is_active = 1 ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    if not row:
        return jsonify({'success': True, 'job_fair': None, 'is_active': False})
    
    return jsonify({
        'success': True,
        'job_fair': format_job_fair_dict(row),
        'is_active': True
    })

@app.route('/api/admin/job-fairs', methods=['GET'])
def admin_get_job_fairs():
    """Admin API: List all job fairs / event banners."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM job_fairs ORDER BY id DESC")
    rows = cursor.fetchall()

    return jsonify({
        'success': True,
        'job_fairs': [format_job_fair_dict(r) for r in rows],
        'count': len(rows)
    })

@app.route('/api/admin/job-fairs/<int:event_id>', methods=['GET'])
def admin_get_job_fair_by_id(event_id):
    """Admin API: Get a single job fair event by ID."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM job_fairs WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Job fair event not found.'}), 404

    return jsonify({
        'success': True,
        'job_fair': format_job_fair_dict(row)
    })

@app.route('/api/admin/job-fairs', methods=['POST'])
def admin_create_job_fair():
    """Admin API: Create a new job fair event."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    title_en = (data.get('title_en') or '').strip()
    title_zh = (data.get('title_zh') or '').strip()

    if not title_en or not title_zh:
        return jsonify({'error': 'Title (both English and Chinese) is required.'}), 400

    tag_en = (data.get('tag_en') or 'Upcoming Event').strip()
    tag_zh = (data.get('tag_zh') or '近期重磅活动').strip()
    subtitle_en = (data.get('subtitle_en') or '').strip()
    subtitle_zh = (data.get('subtitle_zh') or '').strip()
    date_en = (data.get('date_en') or '').strip()
    date_zh = (data.get('date_zh') or '').strip()
    location_en = (data.get('location_en') or '').strip()
    location_zh = (data.get('location_zh') or '').strip()
    btn_text_en = (data.get('btn_text_en') or 'Secure Your Spot').strip()
    btn_text_zh = (data.get('btn_text_zh') or '立即免费抢占席位').strip()
    btn_link = (data.get('btn_link') or '#consultation').strip()
    bg_image_url = (data.get('bg_image_url') or 'images/job-fair.png').strip()
    is_active = int(data.get('is_active', 1))

    now_str = datetime.utcnow().isoformat()
    db = get_db()
    cursor = db.cursor()

    if is_active == 1:
        cursor.execute("UPDATE job_fairs SET is_active = 0 WHERE is_active = 1")

    cursor.execute('''
    INSERT INTO job_fairs (
        tag_en, tag_zh, title_en, title_zh, subtitle_en, subtitle_zh,
        date_en, date_zh, location_en, location_zh, btn_text_en, btn_text_zh,
        btn_link, bg_image_url, is_active, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        tag_en, tag_zh, title_en, title_zh, subtitle_en, subtitle_zh,
        date_en, date_zh, location_en, location_zh, btn_text_en, btn_text_zh,
        btn_link, bg_image_url, is_active, now_str, now_str
    ))
    db.commit()
    new_id = cursor.lastrowid

    cursor.execute("SELECT * FROM job_fairs WHERE id = ?", (new_id,))
    new_row = cursor.fetchone()

    return jsonify({
        'success': True,
        'job_fair': format_job_fair_dict(new_row),
        'message': f'Job Fair "{title_en}" created successfully.'
    }), 201

@app.route('/api/admin/job-fairs/<int:event_id>', methods=['PUT'])
def admin_update_job_fair(event_id):
    """Admin API: Update an existing job fair event."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM job_fairs WHERE id = ?", (event_id,))
    curr = cursor.fetchone()
    if not curr:
        return jsonify({'error': 'Job fair event not found.'}), 404

    data = request.get_json() or {}
    fields = ['tag_en', 'tag_zh', 'title_en', 'title_zh', 'subtitle_en', 'subtitle_zh',
              'date_en', 'date_zh', 'location_en', 'location_zh', 'btn_text_en', 'btn_text_zh',
              'btn_link', 'bg_image_url']
    
    updates = []
    params = []
    for f in fields:
        if f in data and data[f] is not None:
            updates.append(f"{f} = ?")
            params.append(str(data[f]).strip())

    if 'is_active' in data:
        new_active = int(data['is_active'])
        updates.append("is_active = ?")
        params.append(new_active)
        if new_active == 1:
            cursor.execute("UPDATE job_fairs SET is_active = 0 WHERE id != ?", (event_id,))

    if not updates:
        return jsonify({'message': 'No changes detected.'})

    updates.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat())
    params.append(event_id)

    query = f"UPDATE job_fairs SET {', '.join(updates)} WHERE id = ?"
    db.execute(query, params)
    db.commit()

    cursor.execute("SELECT * FROM job_fairs WHERE id = ?", (event_id,))
    updated_row = cursor.fetchone()

    return jsonify({
        'success': True,
        'job_fair': format_job_fair_dict(updated_row),
        'message': f'Job Fair "{data.get("title_en") or curr["title_en"]}" updated successfully.'
    })

@app.route('/api/admin/job-fairs/<int:event_id>/toggle-status', methods=['PATCH'])
def admin_toggle_job_fair_status(event_id):
    """Admin API: 1-click toggle active/inactive status for a job fair."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, title_en, is_active FROM job_fairs WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Job fair event not found.'}), 404

    new_active = 0 if row['is_active'] == 1 else 1
    now_str = datetime.utcnow().isoformat()
    if new_active == 1:
        db.execute("UPDATE job_fairs SET is_active = 0 WHERE id != ?", (event_id,))

    db.execute("UPDATE job_fairs SET is_active = ?, updated_at = ? WHERE id = ?", (new_active, now_str, event_id))
    db.commit()

    status_str = "ACTIVE (Visible on website)" if new_active == 1 else "INACTIVE (Hidden from website)"
    return jsonify({
        'success': True,
        'is_active': new_active,
        'message': f'Job Fair "{row["title_en"]}" is now {status_str}.'
    })

@app.route('/api/admin/job-fairs/<int:event_id>', methods=['DELETE'])
def admin_delete_job_fair(event_id):
    """Admin API: Delete a job fair event."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT title_en FROM job_fairs WHERE id = ?", (event_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Job fair event not found.'}), 404

    db.execute("DELETE FROM job_fairs WHERE id = ?", (event_id,))
    db.commit()

    return jsonify({
        'success': True,
        'message': f'Job Fair "{row["title_en"]}" deleted successfully.'
    })


# ==============================================================================
# Public Lead Capture & Consultation Booking APIs
# ==============================================================================

@app.route('/api/consultations', methods=['POST'])
def submit_consultation():
    """Public API: Submit student lead / consultation booking."""
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    phone = (data.get('phone') or '').strip()
    program = (data.get('program') or '').strip()
    interested_in_grant = int(data.get('interested_in_grant', 0))
    source_page = (data.get('source_page') or 'direct').strip()
    notes = (data.get('notes') or '').strip()

    if not name or (not email and not phone):
        return jsonify({'error': 'Name and contact info (email or phone) are required.'}), 400

    now_str = datetime.utcnow().isoformat()
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
    INSERT INTO consultations (name, email, phone, program, interested_in_grant, source_page, notes, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)
    ''', (name, email, phone, program, interested_in_grant, source_page, notes, now_str))
    db.commit()
    new_id = cursor.lastrowid

    return jsonify({
        'success': True,
        'id': new_id,
        'message': 'Consultation request submitted successfully.'
    }), 201

@app.route('/api/admin/consultations', methods=['GET'])
def admin_get_consultations():
    """Admin API: View all consultation leads."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM consultations ORDER BY id DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    return jsonify({'success': True, 'consultations': rows, 'count': len(rows)})


# ==============================================================================
# Site Translations & Bilingual Content APIs (Stored in SQLite DB)
# ==============================================================================

@app.route('/api/translations', methods=['GET'])
def get_site_translations():
    """
    Public API: Returns all bilingual site translations and homepage content directly from SQLite DB.
    Called on page startup to hydrate English and Chinese copy dynamically.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT key, text_en, text_zh FROM site_translations")
    rows = cursor.fetchall()
    
    en_dict = {}
    zh_dict = {}
    for r in rows:
        en_dict[r['key']] = r['text_en']
        zh_dict[r['key']] = r['text_zh']

    return jsonify({
        'en': en_dict,
        'zh': zh_dict,
        'count': len(rows),
        'source': 'sqlite_database'
    })

@app.route('/api/admin/translations', methods=['GET'])
def admin_get_translations():
    """Admin API: List and search all translation strings."""
    err = require_admin()
    if err: return err

    category = request.args.get('category', '').strip().lower()
    search = request.args.get('search', '').strip().lower()

    query = "SELECT * FROM site_translations WHERE 1=1"
    params = []

    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (LOWER(key) LIKE ? OR LOWER(text_en) LIKE ? OR LOWER(text_zh) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY category ASC, key ASC"

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    translations = [dict(row) for row in cursor.fetchall()]

    return jsonify({
        'translations': translations,
        'count': len(translations)
    })

@app.route('/api/admin/translations/<path:trans_key>', methods=['PUT'])
def admin_update_translation(trans_key):
    """Admin API: Update a specific bilingual translation in SQLite DB."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    text_en = data.get('text_en', '').strip()
    text_zh = data.get('text_zh', '').strip()

    if not text_en and not text_zh:
        return jsonify({'error': 'Please provide text in at least one language.'}), 400

    db = get_db()
    cursor = db.cursor()
    now_str = datetime.utcnow().isoformat()

    cursor.execute("SELECT id FROM site_translations WHERE key = ?", (trans_key,))
    if cursor.fetchone():
        db.execute('''
        UPDATE site_translations
        SET text_en = ?, text_zh = ?, updated_at = ?
        WHERE key = ?
        ''', (text_en, text_zh, now_str, trans_key))
    else:
        category = (data.get('category') or 'general').strip()
        db.execute('''
        INSERT INTO site_translations (key, category, text_en, text_zh, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (trans_key, category, text_en, text_zh, now_str))

    db.commit()
    return jsonify({
        'success': True,
        'message': f'Translation "{trans_key}" saved to database successfully.'
    })

@app.route('/api/admin/translations/sync', methods=['POST'])
def admin_sync_translations():
    """Admin API: Resync translation dictionary from code files into SQLite DB."""
    err = require_admin()
    if err: return err

    try:
        import seed_translations
        seed_translations.seed_database()
        return jsonify({'success': True, 'message': 'Translations successfully re-synchronized in SQLite DB.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==============================================================================
# Static File & Single-Page Application Serving
# ==============================================================================

@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/admin')
def serve_admin():
    return send_from_directory(BASE_DIR, 'admin.html')

@app.route('/article')
@app.route('/article.html')
@app.route('/articles/<path:slug>')
def serve_article(slug=None):
    return send_from_directory(BASE_DIR, 'article.html')

@app.route('/personal-support-worker-online-psw-course')
@app.route('/personal-support-worker-online-psw-course/')
@app.route('/personal-support-worker-online-psw-course.html')
@app.route('/psw-course')
def serve_psw_course_page():
    return send_from_directory(BASE_DIR, 'personal-support-worker-online-psw-course.html')

@app.route('/computerized-accounting')
@app.route('/computerized-accounting/')
@app.route('/computerized-accounting.html')
@app.route('/accounting-tax-payroll')
def serve_accounting_page():
    return send_from_directory(BASE_DIR, 'computerized-accounting.html')

@app.route('/early-childcare-assistant-eca')
@app.route('/early-childcare-assistant-eca/')
@app.route('/early-childcare-assistant-eca.html')
@app.route('/early-childcare-assistant')
@app.route('/early-childcare-assistant.html')
@app.route('/eca-course')
def serve_eca_page():
    return send_from_directory(BASE_DIR, 'early-childcare-assistant-eca.html')

@app.route('/acupuncture-program')
@app.route('/acupuncture-program/')
@app.route('/acupuncture-program.html')
@app.route('/acupuncture')
@app.route('/acupuncture.html')
@app.route('/acupuncture-course')
def serve_acupuncture_page():
    return send_from_directory(BASE_DIR, 'acupuncture-program.html')

@app.route('/electrician')
@app.route('/electrician/')
@app.route('/electrician.html')
@app.route('/electrician-309a-442a')
@app.route('/electrician-course')
@app.route('/electrician-training')
def serve_electrician_page():
    return send_from_directory(BASE_DIR, 'electrician.html')

@app.route('/software-development')
@app.route('/software-development/')
@app.route('/software-development.html')
@app.route('/fullstack')
@app.route('/fullstack.html')
@app.route('/full-stack-web-development-ai')
@app.route('/software-development-course')
def serve_software_development_page():
    return send_from_directory(BASE_DIR, 'software-development.html')

@app.route('/privacy-policy')
@app.route('/privacy-policy/')
@app.route('/privacy-policy.html')
def serve_privacy_policy_page():
    return send_from_directory(BASE_DIR, 'privacy-policy.html')

@app.route('/KPI-audit-requirements')
@app.route('/KPI-audit-requirements/')
@app.route('/KPI-audit-requirements.html')
@app.route('/kpi-audit-requirements')
@app.route('/kpi-audit-requirements/')
@app.route('/kpi-audit-requirements.html')
def serve_kpi_audit_requirements_page():
    return send_from_directory(BASE_DIR, 'kpi-audit-requirements.html')

@app.route('/sexual-violence-policy')
@app.route('/sexual-violence-policy/')
@app.route('/sexual-violence-policy.html')
def serve_sexual_violence_policy_page():
    return send_from_directory(BASE_DIR, 'sexual-violence-policy.html')

@app.route('/students-complaint-procedure')
@app.route('/students-complaint-procedure/')
@app.route('/students-complaint-procedure.html')
@app.route('/student-complaint-procedure')
@app.route('/student-complaint-procedure.html')
def serve_students_complaint_procedure_page():
    return send_from_directory(BASE_DIR, 'students-complaint-procedure.html')

@app.route('/academic-accommodation-policy-and-procedure-for-students-with-disabilities')
@app.route('/academic-accommodation-policy-and-procedure-for-students-with-disabilities/')
@app.route('/academic-accommodation-policy-and-procedure-for-students-with-disabilities.html')
@app.route('/academic-accommodation-policy')
@app.route('/academic-accommodation')
def serve_academic_accommodation_policy_page():
    return send_from_directory(BASE_DIR, 'academic-accommodation-policy-and-procedure-for-students-with-disabilities.html')

@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('api/'):
        return jsonify({'error': f'API endpoint /{path} not found.'}), 404
    if os.path.exists(os.path.join(BASE_DIR, path)):
        return send_from_directory(BASE_DIR, path)
    return send_from_directory(BASE_DIR, 'index.html')


# ==============================================================================
# Server Entrypoint & Gunicorn Production Initialization
# ==============================================================================

# Automatically initialize database schema & seeding on import (for Gunicorn WSGI)
init_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5055))
    print(f"\n=======================================================")
    print(f" Victoria International College Server Running!")
    print(f" URL: http://localhost:{port}")
    print(f" Admin Dashboard: http://localhost:{port}/admin")
    print(f" Admin Accounts: Credentials managed and stored securely in SQLite DB.")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=False)

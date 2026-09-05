const translations = {
  en: {
    // Top Bar
    topbar_call: "Call Us: 416-665-6668",
    topbar_email: "info@viccollege.com",
    topbar_address: "7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8",
    topbar_registered: "Registered under Ontario Career Colleges Act, 2005",
    lang_btn: "中文",
    logo_brand_main: "Victoria College",
    logo_brand_sub: "of Business, Healthcare, Technology, & Trades",

    // Navigation
    nav_home: "Home",
    nav_about: "About Us",
    nav_programs: "Programs",
    nav_all_programs: "All Programs",
    nav_health: "Healthcare Programs",
    nav_tech: "Technology Programs",
    nav_business: "Business & Accounting",
    nav_trades: "Skilled Trades & Other",
    nav_aid: "Financial Aid",
    nav_articles: "Career Insights",
    nav_testimonials: "Success Stories",
    nav_contact: "Contact",
    nav_consultation_btn: "Book Free Consultation",

    // Career Insights & News Section
    articles_badge: "LOCAL CAREER INSIGHTS & GUIDES",
    articles_main_title: "Toronto & Markham Career News & Funding Guides",
    articles_subtitle: "Expert analysis on high-demand healthcare, technology, and business careers across the GTA, Ontario grant updates, and certification roadmaps.",
    read_article_btn: "Read Complete Guide",

    // Hero Section
    hero_badge: "Ontario Registered Career College • 22+ Years of Excellence",
    hero_title_1: "Job ready training for careers in-demand",
    hero_title_highlight: "Careers In-Demand",
    hero_subtitle: "Secure a high-paying, rewarding second career with comprehensive practical training. Complimentary assistance for maximum government grants & funding available.",
    hero_cta_book: "Begin Your Future — Book Consultation",
    hero_cta_explore: "Explore Programs",
    hero_stat_years: "22+",
    hero_stat_years_label: "Years of Educational Excellence",
    hero_stat_graduates: "15,000+",
    hero_stat_graduates_label: "Successful Graduates",
    hero_stat_rate: "95%+",
    hero_stat_rate_label: "Job Placement & Internship Rate",

    // Quick Program Cards (Hero Bottom)
    cat_health_title: "Healthcare",
    cat_health_desc: "NACC PSW certified training with direct nursing home & clinical practicum placements.",
    cat_tech_title: "Technology",
    cat_tech_desc: "Full stack web development, Java Spring, React, Cloud AWS & enterprise systems.",
    cat_trades_title: "Skilled Trades",
    cat_trades_desc: "309A / 442A certified electrician exam preparation, hands-on wiring labs & job referrals.",
    cat_biz_title: "Business & Tax",
    cat_biz_desc: "Computerized accounting, Canadian taxation, Sage 50, and certified payroll administration.",

    // Job Fair Announcement Banner
    banner_tag: "Upcoming Event",
    banner_title: "In-Person PSW & Healthcare Job Fair",
    banner_desc: "Connect directly with leading healthcare employers, interview on-site, and secure employment.",
    banner_date: "Friday, 10:00 AM – 12:00 PM",
    banner_location: "306 Consumers Rd., North York / 7050 Woodbine Ave., Markham",
    banner_btn: "Secure Your Free Spot",

    // Value Pillars (Why VIC)
    why_title: "Why Choose Victoria College?",
    why_subtitle: "We combine government funding assistance, industry-certified curriculum, and dedicated job placement support.",
    why_1_title: "Complimentary Grant Guidance",
    why_1_desc: "Full assistance in applying for Better Jobs Ontario (Second Career) and government training grants up to $28,000+ without spending your own money.",
    why_2_title: "High-Demand Practical Skills",
    why_2_desc: "Curriculum designed with industry leaders, offering 1-on-1 practical training and recognized certifications that employers prioritize.",
    why_3_title: "Internship & Career Placement",
    why_3_desc: "Exclusive cooperative placement partnerships, resume polishing, interview coaching, and direct employer referral for high job success.",

    // Programs Section
    programs_section_title: "Featured Career Diploma & Certificate Programs",
    programs_section_subtitle: "Government-approved vocational training with fast-track pathways to top employment sectors in Canada.",
    tab_all: "All Programs",
    tab_health: "Healthcare",
    tab_tech: "Technology",
    tab_business: "Business & Finance",
    tab_trades: "Vocational Trades",

    // Program 1: PSW
    prog_psw_badge: "High Demand • Certificate",
    prog_psw_title: "NACC Personal Support Worker DE 2022",
    prog_psw_desc: "The Personal Support Worker Certificate Program includes classroom lectures, lab simulation, and real-world practicum in long-term care facilities and home care.",
    prog_psw_f1: "Accredited NACC PSW Diploma + CPR & First Aid Certification",
    prog_psw_f2: "Hands-on Clinical Practicum Placement in top Long-term Care Centers",
    prog_psw_f3: "High starting hourly wage ($20–$28/hr) with abundant full-time job openings",
    prog_psw_duration: "Duration: 30 Weeks (Includes Practicum)",

    // Program 2: Full Stack
    prog_tech_badge: "Career Diploma • AI Mini-Credential",
    prog_tech_title: "Full Stack Web Technician",
    prog_tech_desc: "Comprehensive software engineering program providing solid theoretical concepts, hands-on lab work, and an integrated AI Mini-Credential to build modern web, cloud, and AI-powered applications.",
    prog_tech_f1: "Core & Advanced Java, Spring Boot, Spring Cloud, MyBatis, MySQL",
    prog_tech_f2: "Modern Frontend: React, JavaScript/TypeScript, Node.js, HTML5/CSS3",
    prog_tech_f3: "AI Mini-Credential: GenAI, LLM APIs, Prompt Engineering & AI Dev Tools",
    prog_tech_duration: "Duration: 32 Weeks (Live Projects + Labs)",

    // Program 3: Accounting
    prog_acc_badge: "Career Diploma",
    prog_acc_title: "Accounting, Tax and Payroll Administration",
    prog_acc_desc: "Intensive training under the guidance of seasoned CPAs and payroll administrators. Master corporate bookkeeping, Canadian tax returns, and standard accounting software.",
    prog_acc_f1: "Master QuickBooks, Sage 50, Profile, TaxPrep, and Excel modeling",
    prog_acc_f2: "Full cycle bookkeeping, Canadian T1/T2 tax return preparation & audit",
    prog_acc_f3: "Payroll compliance, accounts receivable/payable, and financial reporting",
    prog_acc_duration: "Duration: 30 Weeks (Instructor-led Practical Training)",

    // Program 4: Early Childcare
    prog_eca_badge: "Career Diploma",
    prog_eca_title: "Early Childcare Assistant (ECA)",
    prog_eca_desc: "Prepare for a fulfilling career nurturing child growth and development. Combines child psychology, developmental stages, curriculum planning, and hands-on daycare placement.",
    prog_eca_f1: "Child development, safety, health, nutrition, and emergency procedures",
    prog_eca_f2: "Creative educational programming and positive guidance techniques",
    prog_eca_f3: "Guaranteed field placement in licensed Ontario daycare centers",
    prog_eca_duration: "Duration: 28 Weeks (Includes Field Placement)",

    // Program 5: Acupuncture
    prog_acu_badge: "Non-Vocational Program",
    prog_acu_title: "Acupuncture & Traditional Wellness",
    prog_acu_desc: "Designed for personal interest learning, holistic health wellness, and complementary healing techniques. Learn meridian theory, practical acupressure points, and wellness principles.",
    prog_acu_f1: "Foundational Traditional Chinese Medicine (TCM) meridian theory",
    prog_acu_f2: "Practical point location, safe needle techniques & moxibustion basics",
    prog_acu_f3: "Non-vocational enrichment course for personal and family health",
    prog_acu_duration: "Flexible Scheduling (Evening & Weekend Options)",

    // Program 6: Electrician
    prog_elec_badge: "Skilled Trades Training",
    prog_elec_title: "Electrician (Construction & Maintenance 309A / 442A)",
    prog_elec_desc: "Pre-exam training and hands-on apprenticeship preparation coached by master electricians with 20+ years of Canadian union & commercial project experience.",
    prog_elec_f1: "Canadian Electrical Code (CEC) deep dive and licensing exam prep",
    prog_elec_f2: "Hands-on circuit wiring, conduit bending, industrial control panels",
    prog_elec_f3: "Direct industry referral and job recommendations upon completion",
    prog_elec_duration: "Duration: Comprehensive Weekend & Fast-track Tracks",

    btn_learn_more: "Learn More Details",
    btn_apply_now: "Apply / Inquire Now",

    // Financial Aid Section
    aid_badge: "Government Assistance",
    aid_title: "Study With Zero Financial Burden",
    aid_subtitle: "Did you know you could qualify for government funding of up to $28,000+ for tuition and living allowances?",
    aid_card1_title: "Better Jobs Ontario (Second Career)",
    aid_card1_desc: "Government grant program providing laid-off workers, gig workers, and low-income individuals funding for tuition, books, transportation, and basic living support.",
    aid_card2_title: "100% Free Application Assistance",
    aid_card2_desc: "Our experienced educational counselors guide you through eligibility assessment, resume preparation, research documentation, and submission step-by-step.",
    aid_card3_title: "Flexible Payment & Institutional Aid",
    aid_card3_desc: "Interest-free monthly installment plans and institutional scholarships available for students not eligible for government grants.",
    aid_cta_btn: "Check Your Funding Eligibility",

    // Leadership Section
    lead_badge: "Leadership & Mission",
    lead_title: "Empowering Immigrants & Students Since 2005",
    lead_name: "President Maria Sun",
    lead_role: "President of Victoria Education Group • Dean of Victoria International College",
    lead_point1: "Over 22 years of dedicated leadership in Canadian higher education & career coaching.",
    lead_point2: "Chief Secretary of Canadian Youth Union & Canadian Women's Service Centre.",
    lead_point3: "Helped tens of thousands of new immigrants land professional careers and adapt to Canadian life.",
    lead_point4: "A proud mother who successfully guided her daughter to Harvard University.",
    lead_quote: "“Our mission is not just granting diplomas, but opening genuine career doors, building confidence, and securing high-paying futures for every student.”",

    // Testimonials Section
    test_badge: "Student Reviews",
    test_title: "What Our Graduates Say",
    test_subtitle: "Real stories from students who transformed their careers and lives at Victoria College.",
    test_1_text: "“I am a PSW graduate from Victoria International College. The instructors were patient and professional. They not only helped me overcome language barriers, but also secured an excellent practicum placement in a top nursing home. I was hired immediately before graduation!”",
    test_1_author: "Ms. May",
    test_1_prog: "PSW Certified Graduate",
    test_2_text: "“I transitioned from having zero coding knowledge to working as a software data specialist in Montreal. The teachers structured the Full Stack curriculum with real-world enterprise projects that impressed my hiring manager. Truly life-changing!”",
    test_2_author: "Ms. Huang",
    test_2_prog: "Full Stack Web Graduate",
    test_3_text: "“Thanks to VIC’s dedicated advisors, I successfully secured Second Career government funding covering all my tuition and living costs. The staff handled all my application paperwork seamlessly. I could focus 100% on learning.”",
    test_3_author: "Mr. Luo",
    test_3_prog: "Better Jobs Ontario Recipient",
    test_4_text: "“What sets Victoria College apart is their genuine dedication to job placement. Before I even completed the program, they coordinated resume workshops, mock interviews, and sent my profile to hiring partners. I landed my accounting role in 3 weeks.”",
    test_4_author: "Jennifer L.",
    test_4_prog: "Accounting & Tax Graduate",

    // Free Consultation Form Section
    form_section_title: "Book Your Free 1-on-1 Career Consultation",
    form_section_subtitle: "Speak with our senior admissions & government funding specialists. We will analyze your background, recommend the best program, and assess your grant eligibility.",
    form_name_label: "Your Full Name *",
    form_name_placeholder: "e.g. David Zhang / Sarah Miller",
    form_email_label: "Email Address *",
    form_email_placeholder: "e.g. name@example.com",
    form_phone_label: "Phone Number *",
    form_phone_placeholder: "e.g. 416-665-6668",
    form_program_label: "Program of Interest",
    form_program_select: "-- Select a Program --",
    form_program_psw: "NACC Personal Support Worker (PSW)",
    form_program_tech: "Full Stack Web Technician",
    form_program_acc: "Accounting, Tax & Payroll",
    form_program_eca: "Early Childcare Assistant (ECA)",
    form_program_acu: "Acupuncture & Wellness",
    form_program_elec: "Electrician Licensing & Training",
    form_aid_checkbox: "I want a free evaluation for Better Jobs Ontario / Government Grant eligibility",
    form_submit_btn: "Submit Booking Request",
    form_privacy_note: "🔒 Your information is 100% confidential and protected under privacy policies.",
    form_success_title: "Thank You! Consultation Request Received",
    form_success_msg: "Our admissions advisor will contact you within 24 business hours to confirm your consultation schedule and grant eligibility.",

    // Campus & Contact
    campus_title: "Our Campuses & Contact",
    campus_sub: "Convenient locations in the Greater Toronto Area with modern lab facilities.",
    campus_markham: "Markham Campus (Main)",
    campus_markham_addr: "7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8",
    campus_nyork: "North York Campus",
    campus_nyork_addr: "306 Consumers Rd., North York, ON M2J 1P8",
    campus_hours: "Office Hours: Monday – Saturday, 9:00 AM – 6:00 PM",
    campus_phone: "Phone: 416-665-6668",
    campus_email: "Email: info@viccollege.com",

    // Footer
    footer_desc: "Victoria International College of Business & Technology is registered as a career college under the Ontario Career Colleges Act, 2005. Committed to practical excellence, career outcomes, and community empowerment.",
    footer_col_programs: "Career Programs",
    footer_col_services: "Student Services",
    footer_service_1: "Better Jobs Ontario Grant Assistance",
    footer_service_2: "Resume & Interview Coaching",
    footer_service_3: "Co-op & Practicum Placements",
    footer_service_4: "Job Fair & Employer Networking",
    footer_col_legal: "Compliance & Policies",
    footer_policy_privacy: "Privacy Policy",
    footer_policy_kpi: "KPI Audit Requirements",
    footer_policy_sexual: "Sexual Violence Policy",
    footer_policy_complaint: "Students Complaint Procedure",
    footer_policy_disability: "Academic Accommodation for Students with Disabilities",
    footer_copyright: "Copyright © 2026 Victoria International College of Business & Technology. All rights reserved."
  },

  zh: {
    // Top Bar
    topbar_call: "咨询热线: 416-665-6668",
    topbar_email: "info@viccollege.com",
    topbar_address: "7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8",
    topbar_registered: "依据安省《2005年私立职业学院法》合规注册认证",
    lang_btn: "English",
    logo_brand_main: "维多利亚职业学院",
    logo_brand_sub: "工商 • 护理 • 科技 • 技工职业培训",

    // Navigation
    nav_home: "首页",
    nav_about: "关于学院",
    nav_programs: "热门专业",
    nav_all_programs: "所有专业课程",
    nav_health: "医疗护理系列",
    nav_tech: "IT 与科技开发",
    nav_business: "会计税务与商业",
    nav_trades: "技工与特色课程",
    nav_aid: "政府资助与助学金",
    nav_articles: "职业资讯与行业指南",
    nav_testimonials: "学员就业心声",
    nav_contact: "联系我们",
    nav_consultation_btn: "预约免费职业规划",

    // Career Insights & News Section
    articles_badge: "本地紧缺职业发展与资助指南",
    articles_main_title: "多伦多及万锦最新行业动态与助学金政策",
    articles_subtitle: "深度解析大多伦多地区医疗护理、IT开发与商业财税紧缺岗位、安省 Better Jobs Ontario 助学金最新申请要求与职业证书考取路径。",
    read_article_btn: "阅读完整指南",

    // Hero Section
    hero_badge: "安大略省教育部注册职业学院 • 22年卓越教学声誉",
    hero_title_1: "紧缺高薪职业实战培训",
    hero_title_highlight: "毕业直通高薪就业",
    hero_subtitle: "零负担开启加拿大高薪第二职业！免费协助申请政府培训资助（最高可获 $28,000+ 学费及生活补助），助您快速融入本地职场。",
    hero_cta_book: "开启未来 — 预约免费咨询",
    hero_cta_explore: "浏览热门课程",
    hero_stat_years: "22+",
    hero_stat_years_label: "年加拿大教育培训底蕴",
    hero_stat_graduates: "15,000+",
    hero_stat_graduates_label: "成功就业学子",
    hero_stat_rate: "95%+",
    hero_stat_rate_label: "实习推荐与毕业就业率",

    // Quick Program Cards (Hero Bottom)
    cat_health_title: "医疗护理类",
    cat_health_desc: "NACC 认证 PSW 护工专业，提供正规养老院及医疗机构带薪/实习分配。",
    cat_tech_title: "IT 科技类",
    cat_tech_desc: "全栈网页工程师开发课程，涵盖 Java、Spring、React、云平台 AWS 实战。",
    cat_trades_title: "建筑电工类",
    cat_trades_desc: "安省 309A / 442A 建筑与维护电工考证培训，大师级名师亲授、实操机房与学徒推荐。",
    cat_biz_title: "会计与税务",
    cat_biz_desc: "加拿大电算化会计、企业报税全流程、Sage 50/QuickBooks 真实账目实操。",

    // Job Fair Announcement Banner
    banner_tag: "近期重磅活动",
    banner_title: "维多利亚线下 PSW 护工专场招聘会",
    banner_desc: "知名养老机构 HR 亲临现场直接面试，岗位充足，当天即可锁定实习与工作机会！",
    banner_date: "每周五 上午 10:00 – 中午 12:00",
    banner_location: "306 Consumers Rd., North York / 7050 Woodbine Ave., Markham",
    banner_btn: "立即免费抢占席位",

    // Value Pillars (Why VIC)
    why_title: "为什么选择维多利亚职业学院？",
    why_subtitle: "全方位结合政府资助申请辅导、名师实战教学、及强大的本地雇主直推网络。",
    why_1_title: "全免费政府助学金申请辅导",
    why_1_desc: "专业顾问全程一对一协助申请安省 Better Jobs Ontario（第二职业）培训补贴，最高可得 $28,000+ 学费及生活补贴，免掏个人积蓄。",
    why_2_title: "紧贴市场需求与认证技能",
    why_2_desc: "课程紧扣加拿大主流紧缺行业标准，结合 1对1 动手实验与正规职业资格证书，确保毕业生具备即战力。",
    why_3_title: "保障实习与雇主就业推荐",
    why_3_desc: "拥有广泛的西人与华人企业合作资源，提供简历深度修改、面试模拟，直推合作雇主，实现快速就业。",

    // Programs Section
    programs_section_title: "热门职业文凭与技能证书课程",
    programs_section_subtitle: "安省教育部注册认证文凭，快速掌握高薪行业核心技能，开启职业新篇章。",
    tab_all: "全部专业",
    tab_health: "医疗护理",
    tab_tech: "IT 科技",
    tab_business: "会计金融",
    tab_trades: "专业技能考证",

    // Program 1: PSW
    prog_psw_badge: "极度紧缺 • 证书课程",
    prog_psw_title: "NACC 个人护理护工文凭 (PSW DE 2022)",
    prog_psw_desc: "包含理论教学与正规医院/养老院临床实习。毕业可同时获得安省认可 NACC PSW 文凭及 CPR 急救证书，职场认可度高，待遇优厚。",
    prog_psw_f1: "安省官方 NACC PSW 认证文凭 + CPR/AED 急救证书",
    prog_psw_f2: "安排安省正规长期护理中心（LTC）实地临床实习",
    prog_psw_f3: "时薪高达 $20–$28/小时，医院与养老院全职岗位紧缺",
    prog_psw_duration: "学制周期: 30 周（含实操与机构临床实习）",

    // Program 2: Full Stack
    prog_tech_badge: "职业文凭 • 含 AI 微证书",
    prog_tech_title: "全栈网页开发技术员 (Full Stack Web)",
    prog_tech_desc: "理论与企业级项目实验深度融合，系统掌握现代全栈工程架构，并深度融入 AI 微证书（生成式 AI、大模型开发实战与云端微服务）。",
    prog_tech_f1: "核心与进阶 Java、Spring Boot、Spring Cloud、MySQL 数据库",
    prog_tech_f2: "现代前端技术栈：React、JavaScript/TypeScript、Node.js",
    prog_tech_f3: "AI 微证书：生成式 AI、大模型 LLM API、Prompt 提示词与智能辅助编程",
    prog_tech_duration: "学制周期: 32 周（含企业级项目实操演练）",

    // Program 3: Accounting
    prog_acc_badge: "职业文凭",
    prog_acc_title: "会计、税务与薪资管理 (Accounting & Tax)",
    prog_acc_desc: "资深加国 CPA 及持牌会计师亲自授课，30周高强度实战演练，全面掌握簿记员、应收应付主管及税务专员核心专业技能。",
    prog_acc_f1: "精通 QuickBooks、Sage 50、Profile、TaxPrep 及 Excel 财务建模",
    prog_acc_f2: "全流程簿记、加拿大个人 T1 及公司 T2 报税申报实战",
    prog_acc_f3: "薪资合规发放、往来款项管理、财务报表编制与审计应对",
    prog_acc_duration: "学制周期: 30 周（名师带教全真账目实操）",

    // Program 4: Early Childcare
    prog_eca_badge: "职业文凭",
    prog_eca_title: "早期幼儿教育助理 (ECA)",
    prog_eca_desc: "为热爱幼教事业人士量身打造。学习儿童各发展阶段心理、健康营养与教学活动策划，毕业安排安省正规日托中心实习。",
    prog_eca_f1: "儿童发展心理学、安全与营养、人际沟通与突发应对",
    prog_eca_f2: "幼儿创意教学活动设计与积极引导技巧",
    prog_eca_f3: "保障进入安省持牌日托中心与幼教机构实地实习",
    prog_eca_duration: "学制周期: 28 周（含幼教中心实地跟岗实习）",

    // Program 5: Acupuncture
    prog_acu_badge: "特色非职业课程",
    prog_acu_title: "中医针灸与传统养生保健课程",
    prog_acu_desc: "专为个人兴趣、家庭健康养生及辅助保健知识学习者设计。系统学习经络学说、常用穴位定位及传统养生手法演示。",
    prog_acu_f1: "中医基础理论与经络循行穴位精讲",
    prog_acu_f2: "实用经络推拿、艾灸与家庭常见亚健康调理实操",
    prog_acu_f3: "非职业普及类兴趣课程，丰富身心健康技能",
    prog_acu_duration: "上课形式: 灵活业余班（晚班/周末班）",

    // Program 6: Electrician
    prog_elec_badge: "持牌技工培训",
    prog_elec_title: "建筑与维护电工考证培训班 (309A / 442A)",
    prog_elec_desc: "安省20余年资深西人/华人电气工程专家执教，结合安省官方学徒基地1对1动手教学与考题精讲，助您快速考取安省电工执照。",
    prog_elec_f1: "加拿大电气规范（CEC）深度剖析与考证真题精练",
    prog_elec_f2: "真实电路配线、弯管、工业配电柜与控制系统动手操作",
    prog_elec_f3: "结业学员独家推荐至政府与商业建筑工程项目就业",
    prog_elec_duration: "学制周期: 强化周末班与考证冲刺班",

    btn_learn_more: "查看专业详情",
    btn_apply_now: "立即报名 / 咨询",

    // Financial Aid Section
    aid_badge: "政府培训资助",
    aid_title: "零经济负担 轻松入读名牌专业",
    aid_subtitle: "您知道吗？符合条件的居民可申请高达 $28,000+ 的政府学费及生活补贴！",
    aid_card1_title: "安省 Better Jobs Ontario 资助",
    aid_card1_desc: "安省政府面向失业人士、零工人员（Gig Workers）及低收入居民设立的重返职场培训补助，全额涵盖学费、教材、交通及日常家庭生活津贴。",
    aid_card2_title: "100% 免费申请全程辅导",
    aid_card2_desc: "维多利亚资深教育规划师为您提供资格评估、市场调研报告准备、申请文书整理及面试辅导，确保高成功率获批。",
    aid_card3_title: "灵活分期与学院奖学金",
    aid_card3_desc: "针对未申请政府资助的自费学员，学院提供免息月度分期付款计划及专项优秀学员奖学金支持。",
    aid_cta_btn: "免费评估我的资助资格",

    // Leadership Section
    lead_badge: "领导团队与办学初心",
    lead_title: "自2005年起 专注赋能移民与学子职业成长",
    lead_name: "孙善勤 (Maria Sun) 院长",
    lead_role: "维多利亚教育集团总裁 • 维多利亚国际学院院长",
    lead_point1: "深耕加拿大职业教育与职业规划培训逾22年，业界声誉卓著。",
    lead_point2: "兼任加拿大青年联合会秘书长、加拿大华人妇女联合会理事长。",
    lead_point3: "累计帮助数以万计的新老移民与毕业生成功跨入加国专业领域高薪白领阶层。",
    lead_point4: "一位培养女儿成功考入美国哈佛大学的卓越母亲与教育名师。",
    lead_quote: "“我们的宗旨绝不仅仅是发出一张文凭，而是为每一位学员真正推开高薪职场大门，重塑自信，赢在加拿大！”",

    // Testimonials Section
    test_badge: "学子心声",
    test_title: "听听维多利亚毕业生的成功故事",
    test_subtitle: "他们在这里重塑技能、获得资助、顺利跨入心仪职业大门。",
    test_1_text: "“我是维多利亚学院 PSW 护工班的学员。老师们特别有耐心和责任心，不仅帮我克服了英语专业词汇障碍，还帮我联系到一流西人养老院实习，毕业前我就拿到了全职 Offer！”",
    test_1_author: "May 女士",
    test_1_prog: "PSW 护工专业优秀毕业生",
    test_2_text: "“我原本零IT基础，通过维多利亚全栈开发课程系统学习，导师带着做商业真实项目，结业后成功斩获蒙特利尔软件数据分析师职位，雇主对我的技术实力非常认可。”",
    test_2_author: "Huang 同学",
    test_2_prog: "全栈开发专业毕业生",
    test_3_text: "“在维多利亚老师的专业协助下，我顺利拿到了政府 Second Career 全额资助，学费生活费全免！老师们帮我精心准备了全部评估材料，省去了我大量摸索时间，非常感恩！”",
    test_3_author: "Luo 先生",
    test_3_prog: "政府第二职业资助获批学员",
    test_4_text: "“维多利亚最突出的特色就是切实解决学员就业问题。快毕业时学院就业老师就开始为我改简历、模拟面试并推荐岗位，让我在面试 HR 时充满底气，三周内就入职了会计岗位。”",
    test_4_author: "Jennifer",
    test_4_prog: "会计与税务专业毕业生",

    // Free Consultation Form Section
    form_section_title: "预约一对一免费职业与资助规划",
    form_section_subtitle: "维多利亚资深职业规划师与政府资助专家为您定制个人职业路径，精准评估资助申请资格。",
    form_name_label: "您的姓名 *",
    form_name_placeholder: "例如：张先生 / 李女士 / Alex Zhang",
    form_email_label: "电子邮箱 *",
    form_email_placeholder: "例如：yourname@example.com",
    form_phone_label: "联系电话 *",
    form_phone_placeholder: "例如：416-665-6668",
    form_program_label: "意向咨询专业",
    form_program_select: "-- 请选择意向专业 --",
    form_program_psw: "NACC 个人护理护工 (PSW)",
    form_program_tech: "全栈网页开发技术员 (Full Stack)",
    form_program_acc: "会计、税务与薪资管理 (Accounting)",
    form_program_eca: "早期幼儿教育助理 (ECA)",
    form_program_acu: "中医针灸与养生保健 (Acupuncture)",
    form_program_elec: "建筑与维护电工考证培训 (Electrician)",
    form_aid_checkbox: "我需要免费评估 Better Jobs Ontario / 政府培训助学金申请资格",
    form_submit_btn: "立即提交预约申请",
    form_privacy_note: "🔒 您的个人信息将严格保密，仅用于本次职业咨询与课程规划。",
    form_success_title: "提交成功！我们已收到您的预约",
    form_success_msg: "维多利亚课程顾问将在24小时内与您电话/微信联系，为您安排专属咨询时间与资助方案评估。",

    // Campus & Contact
    campus_title: "校区分布与联系方式",
    campus_sub: "大多伦多地区便利校区，配备先进教学机房与实训设备。",
    campus_markham: "万锦主校区 (Markham Campus)",
    campus_markham_addr: "7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8",
    campus_nyork: "北约克校区 (North York Campus)",
    campus_nyork_addr: "306 Consumers Rd., North York, ON M2J 1P8",
    campus_hours: "办公时间: 周一至周六 9:00 AM – 6:00 PM",
    campus_phone: "联系电话: 416-665-6668",
    campus_email: "电子邮箱: info@viccollege.com",

    // Footer
    footer_desc: "维多利亚国际学院（Victoria International College of Business & Technology）依据安省《2005年私立职业学院法》合规注册，22年专注职业技能培训、助学金申请与就业推荐。",
    footer_col_programs: "重点专业",
    footer_col_services: "学员服务",
    footer_service_1: "Better Jobs Ontario 资助全程协助",
    footer_service_2: "专业简历精修与模拟面试辅导",
    footer_service_3: "专业对口带薪/实地实习安排",
    footer_service_4: "专场招聘会与雇主直荐渠道",
    footer_col_legal: "合规与规章制度",
    footer_policy_privacy: "隐私政策 (Privacy Policy)",
    footer_policy_kpi: "KPI 绩效审计指标 (KPI Audit)",
    footer_policy_sexual: "反性暴力防范政策",
    footer_policy_complaint: "学生申诉处理规程",
    footer_copyright: "版权所有 © 2026 维多利亚国际职业教育学院 (Victoria International College). 保留所有权利。"
  }
};

// Expose globally
window.translations = translations;

// Asynchronously pull live translations directly from SQLite Database on startup
async function fetchDatabaseTranslations() {
  try {
    const apiUrl = typeof window.getVicApiUrl === 'function' 
      ? window.getVicApiUrl('/api/translations') 
      : (window.location.protocol === 'file:' || (window.location.port !== '5055' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) 
        ? 'http://127.0.0.1:5055/api/translations' 
        : '/api/translations');
    const res = await fetch(apiUrl);
    if (!res.ok) return;
    const data = await res.json();
    if (data && data.en && data.zh) {
      // Merge database strings into translation dictionaries
      Object.assign(translations.en, data.en);
      Object.assign(translations.zh, data.zh);

      // Re-apply language to DOM if app.js is already running
      const curLang = localStorage.getItem('vic_lang') || 'en';
      if (typeof window.applyLanguage === 'function') {
        window.applyLanguage(curLang);
      }
    }
  } catch (err) {
    console.warn('Could not fetch SQLite database translations, using built-in defaults:', err);
  }
}

// Automatically fetch on script execution
fetchDatabaseTranslations();
window.fetchDatabaseTranslations = fetchDatabaseTranslations;

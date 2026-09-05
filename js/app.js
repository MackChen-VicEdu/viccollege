// Victoria College Application Logic & Language Switcher

let currentLanguage = localStorage.getItem('vic_lang') || 'en';

// Program Deep Dive Data for Modal
const programDetailsData = {
  psw: {
    en: {
      title: "NACC Personal Support Worker DE 2022",
      badge: "Certificate Program • Ontario Regulated",
      duration: "30 Weeks (Classroom + Lab + Practicum)",
      credential: "NACC PSW Diploma + Standard First Aid & CPR Level C",
      overview: "The Personal Support Worker Certificate Program prepares students to master the required personal and occupational qualities needed to care for individuals in long-term care homes, retirement communities, hospitals, and home care environments.",
      modules: [
        "PSW Foundations & Individuality of the Person",
        "Role of the PSW in Healthcare Settings",
        "Interpersonal Communications & Working Relationships",
        "Safety and Mobility & Abuse Prevention",
        "Assisting with Personal Hygiene and Daily Living Activities",
        "Assisting with Medications & Care Planning",
        "Cognitive and Mental Health Issues and Brain Disorders",
        "Clinical Practicum: 300+ Hours in Long-Term Care and Community Care"
      ],
      careers: "Personal Support Worker (PSW), Long-term Care Aide, Home Support Worker, Respite Caregiver, Hospital Patient Attendant.",
      outcomes: "High demand across Ontario with starting wages from $20 to $28/hour. Government incentive grants and sign-on bonuses often available."
    },
    zh: {
      title: "NACC 个人护理护工文凭 (PSW DE 2022)",
      badge: "安省官方职业证书 • 紧缺高薪",
      duration: "30 周（理论课 + 实验室模拟 + 机构临床实习）",
      credential: "安省 NACC PSW 官方文凭 + CPR / AED 急救证书",
      overview: "PSW（Personal Support Worker）是安省长期紧缺的黄金医疗护理职业。维多利亚学院配备先进模拟病房，由安省资深护士名师亲授，包含扎实理论、实操技能及正规养老机构/医院实习。",
      modules: [
        "PSW 职业基础与个体照护原则",
        "安省医疗护理体系与护工职责规范",
        "医患沟通技巧与跨专业团队协作",
        "病患安全防护、转运技巧与防虐待规程",
        "个人卫生照料与日常生活辅助实训",
        "服药辅助规程与照护计划（Care Plan）执行",
        "认知障碍、阿尔茨海默症及心理健康支持",
        "临床实地实习：300+小时安省持牌长期护理院（LTC）实训"
      ],
      careers: "养老院私人护理员（PSW）、医院病患护理助理、社区家庭护理员、日间照料中心护理专员。",
      outcomes: "安省各公立/私立医疗养老机构长期极度紧缺，时薪高达 $20–$28/小时，福利完善，常年具备全职高薪就业机会。"
    }
  },
  tech: {
    en: {
      title: "Full Stack Web Technician",
      badge: "Career Diploma • Enterprise Level",
      duration: "32 Weeks (Intensive Labs + Commercial Projects)",
      credential: "Full Stack Web Technician Diploma",
      overview: "An intensive software engineering diploma blending theoretical computer science foundations with modern enterprise web development, server architecture, cloud platforms, and full-stack project building.",
      modules: [
        "Programming Fundamentals & Core Java (OOP, Data Structures, JVM)",
        "Advanced Java, Multithreading & Network Socket Programming",
        "Enterprise Backend: Spring Boot 3, Spring Cloud, RESTful APIs, MyBatis",
        "Database Architecture: MySQL, PostgreSQL, Query Optimization, Redis Caching",
        "Modern Frontend Architecture: React, Hooks, Redux Toolkit, TypeScript, HTML5/CSS3",
        "Cloud Infrastructure: AWS (EC2, S3, RDS, Lambda), Docker Containers, CI/CD",
        "System Design, Software Design Patterns & Agile Development Workflow",
        "Full Stack Capstone Project: Production-grade E-Commerce / SaaS Platform"
      ],
      careers: "Full Stack Developer, Java Backend Engineer, Frontend React Developer, Web Applications Specialist, Cloud Software Associate.",
      outcomes: "Average entry salary $65,000–$85,000/year. Direct preparation for technical white-boarding and system design interviews."
    },
    zh: {
      title: "全栈网页开发技术员 (Full Stack Web)",
      badge: "加国紧缺高薪 IT 职业文凭",
      duration: "32 周（高强度实战机房 + 商业级项目交付）",
      credential: "安省教育部认证 Full Stack Web Technician 职业文凭",
      overview: "紧扣北美一线大厂与金融机构用人标准，从编程底层基础到企业级微服务架构、React 前端开发与 AWS 云端部署，手把手带领学员打造高含金量商业项目作品集。",
      modules: [
        "计算机编程核心与 Java 深度进阶（面向对象、数据结构、JVM 调优）",
        "多线程高并发网络编程与性能瓶颈诊断",
        "企业级后端微服务架构：Spring Boot、Spring Cloud、RESTful API、MyBatis",
        "数据库架构与优化：MySQL 分库分表、PostgreSQL、Redis 缓存与消息队列",
        "现代前端全家桶：React、TypeScript、Next.js、Tailwind、状态管理",
        "云原生架构：AWS 云服务（EC2, S3, RDS）、Docker 容器化与 CI/CD 自动化",
        "软件工程设计模式、系统架构设计与敏捷开发流程",
        "毕业大项目：工业级大型分布式电商 / 敏捷 SaaS 云平台全栈实战"
      ],
      careers: "全栈开发工程师（Full Stack Developer）、Java 后端工程师、React 前端工程师、Web 软件技术专员。",
      outcomes: "加国起薪约 $65,000–$85,000/年。名师辅导 LeetCode 刷题、简历深度技术包装与大厂模拟面试。"
    }
  },
  accounting: {
    en: {
      title: "Accounting, Tax and Payroll Administration",
      badge: "Career Diploma • CPA Mentorship",
      duration: "30 Weeks (Hands-on Corporate Software)",
      credential: "Computerized Accounting, Tax & Payroll Diploma",
      overview: "Comprehensive vocational training designed for individuals aiming to work as corporate bookkeepers, payroll coordinators, and tax associates across Canadian commercial enterprises and CPA accounting firms.",
      modules: [
        "Canadian Financial Accounting Principles & Double-Entry Bookkeeping",
        "QuickBooks Desktop & QuickBooks Online (QBO) Master Certification",
        "Sage 50 Cloud Accounting & Enterprise ERP Overview",
        "Canadian Payroll Administration: CRA Rules, CPP, EI, WSIB, ROE & T4 Filing",
        "Canadian Taxation Part 1: Personal Tax (T1) & Wealth Planning (Profile / TaxPrep)",
        "Canadian Taxation Part 2: Corporate Tax (T2), GST/HST Reporting & Audits",
        "Advanced Excel for Financial Modeling, Pivot Tables, VLOOKUP & Analytics",
        "Full Cycle Accounting Case Study & Year-end Working Papers"
      ],
      careers: "Bookkeeper, Accounts Receivable / Payable Clerk, Payroll Specialist, Tax Preparer, Junior Accountant, Financial Assistant.",
      outcomes: "High placement rate across small-to-medium businesses and accounting firms with clear progression paths to CPA designation."
    },
    zh: {
      title: "会计、税务与薪资管理 (Accounting, Tax & Payroll)",
      badge: "加国高稳定度白领职业文凭",
      duration: "30 周（名师带教 + 真账实操演练）",
      credential: "安省认证 Computerized Accounting & Payroll 职业文凭",
      overview: "由加国资深 CPA 及持牌会计师团队授课，针对加拿大本地公司日常全流程账务、员工工资税核算、CRA 个人与公司税申报进行深度全真演练，毕业即具备 2-3 年实际工作经验水准。",
      modules: [
        "加拿大商业会计基础与复式记账法原理",
        "QuickBooks 桌面版与云端版（QBO）全账套实战",
        "Sage 50 财务软件企业级应用与库存/往来账管理",
        "加拿大薪资法规管理：CRA 税务扣缴、CPP、EI、WSIB、ROE 与 T4 表格制作",
        "加拿大税务实战 1：个人所得税（T1）申报、自雇税收与税务规划（Profile/TaxPrep）",
        "加拿大税务实战 2：公司税（T2）申报、GST/HST 税务核算及 CRA 审计应对",
        "高级 Excel 财务建模、数据透视表、VLOOKUP 与商业报表分析",
        "企业全流程真账实操与年终结账底稿（Working Papers）编制"
      ],
      careers: "全盘簿记员（Bookkeeper）、应收应付账款主管、薪资管理专员、报税专员、会计助理。",
      outcomes: "大多伦多地区各类企事业单位常年刚需，就业面极广，工作环境稳定舒适，并为考取 CPA 提供坚实基石。"
    }
  },
  eca: {
    en: {
      title: "Early Childcare Assistant (ECA)",
      badge: "Career Diploma • Daycare Placement",
      duration: "28 Weeks (Classroom Theory + Daycare Placement)",
      credential: "Early Childcare Assistant Diploma + Child CPR & First Aid",
      overview: "Equips students with the practical competencies, child psychology understanding, and health & safety expertise required to support Early Childhood Educators (ECEs) in licensed Ontario daycare facilities.",
      modules: [
        "Introduction to Early Childhood Education & Ontario Daycare Regulations",
        "Child Growth and Development: Infancy to School-Age",
        "Health, Safety and Nutritional Guidelines in Childcare",
        "Creative Expressions: Art, Music, Storytelling & Sensory Activities",
        "Positive Behavior Guidance & Conflict Resolution in Classrooms",
        "Interpersonal Communications with Parents, Staff and Inspectors",
        "Observations, Pedagogical Documentation and Program Planning",
        "Guaranteed Field Placement in Licensed Ontario Childcare Centers (200+ Hours)"
      ],
      careers: "Early Childcare Assistant, Daycare Room Assistant, Nursery Assistant, Before/After School Program Leader, Private Family Care Specialist.",
      outcomes: "With Ontario's $10-a-day childcare expansion, certified early childcare staff are in historic high demand across the province."
    },
    zh: {
      title: "早期幼儿教育助理 (Early Childcare Assistant - ECA)",
      badge: "安省热门幼教职业文凭 • 保障实习",
      duration: "28 周（理论课 + 正规持牌日托中心跟岗实习）",
      credential: "安省 ECA 幼教助理文凭 + 儿童急救与 CPR 证书",
      overview: "随着安省日托政策普及，持证幼教助理需求激增。课程系统培养学员在持牌日托中心配合主班幼教（ECE）开展日常照料、安全监管、早期启蒙游戏及家校沟通的专业能力。",
      modules: [
        "加拿大幼儿教育发展概况与安省日托管理法规",
        "婴幼儿至学龄前儿童生理与心理发展阶段特征",
        "日托中心健康、安全防护、儿童营养与过敏管理",
        "幼儿创意启蒙活动：绘画、音乐律动、故事会与感统游戏设计",
        "儿童行为积极引导策略与情商培养技巧",
        "家园共育沟通技能与多文化背景团队协作",
        "儿童日常行为观察、成长档案记录与教案编制",
        "安省持牌正规幼儿园/日托中心 200+ 小时实地跟岗实习"
      ],
      careers: "持证幼教助理（ECA）、幼儿园班级助理、课后托管班（After-School）主管、早教中心活动辅导员。",
      outcomes: "政府日托补贴政策推动下全省幼教机构大量扩招，工作稳定，假期充裕，福利待遇良好。"
    }
  },
  acupuncture: {
    en: {
      title: "Acupuncture & Traditional Wellness Program",
      badge: "Non-Vocational Enrichment Course",
      duration: "Flexible Schedule (Evening & Weekend Options)",
      credential: "Certificate of Course Completion",
      overview: "Designed for individuals seeking personal health empowerment, natural wellness knowledge, and traditional healing foundations. Learn meridians, acupressure techniques, and herbal wellness principles.",
      modules: [
        "Foundations of Traditional Chinese Medicine (Yin-Yang, Five Elements)",
        "Major Meridian Channels and Key Acupoint Locations",
        "Basic Acupressure & Therapeutic Massage Principles",
        "Moxibustion, Cupping & Non-Invasive Wellness Practices",
        "Holistic Dietary Therapy & Seasonal Health Maintenance",
        "Safety, Clean Needle Concepts and Health Sanitation Guidelines"
      ],
      careers: "Wellness Enthusiast, Holistic Health Consultant, Natural Spa Care Assistant, Personal/Family Health Manager.",
      outcomes: "Ideal enrichment course for wellness hobbyists, massage therapists, and natural health advocates."
    },
    zh: {
      title: "中医针灸与传统养生保健课程",
      badge: "非职业特色兴趣课程 • 强身健体",
      duration: "灵活课时安排（晚班 / 周末兴趣班）",
      credential: "维多利亚学院结业证书",
      overview: "为弘扬传统中医养生精髓、满足大众对自主健康管理与非药物疗法需求打造。深入浅出学习十四经络走形、常用保健要穴、艾灸拔罐及四季节气调养。",
      modules: [
        "中医阴阳五行学说与脏腑经络基础概论",
        "人体主要经络循行路线与 100+ 常用保健特效穴位精确定位",
        "实用经络推拿、点穴按摩手法与家庭保健技巧",
        "艾灸温灸、拔罐疗法、刮痧操作规范与禁忌",
        "中医体质辨识与四季节气食疗养生调理方案",
        "操作卫生防护、无菌消毒与家庭安全保健指南"
      ],
      careers: "养生保健爱好者、推拿理疗从业人员技能拓展、家庭健康管理专员。",
      outcomes: "掌握终身受用的中医养生绝活，调理个人与家人亚健康，拓宽自然健康视野。"
    }
  },
  electrician: {
    en: {
      title: "Electrician (Construction & Maintenance 309A / 442A)",
      badge: "Pre-Exam & Apprenticeship Coaching",
      duration: "Comprehensive Weekend & Fast-Track Intensive",
      credential: "Certificate of Pre-Exam Training & Job Referral",
      overview: "Coached by master electricians with 20+ years of Canadian union, commercial, and residential contracting experience. Combines Canadian Electrical Code (CEC) mastery with hands-on wiring labs.",
      modules: [
        "Canadian Electrical Code (CEC) Complete Analysis & Code Book Navigation",
        "Single-phase and Three-phase AC/DC Circuits & Power Calculations",
        "Residential Wiring, Service Panels, Grounding & Bonding",
        "Commercial Conduit Bending, Transformers, Motors & Motor Controls",
        "Industrial Automation, Relays, Contactors & Control Schematics",
        "Red Seal 309A / 442A Licensing Examination Question Drills",
        "1-on-1 Hands-on Labs in Recognized Apprenticeship Training Facility",
        "Canadian Job Market Navigation, Safety Certification & Employer Referral"
      ],
      careers: "Licensed Construction Electrician (309A), Industrial Electrician (442A), Electrical Maintenance Specialist, Solar/Green Energy Installer.",
      outcomes: "Top-tier trade with hourly wages ranging from $35 to $55+/hour in Ontario. High demand in commercial and residential developments."
    },
    zh: {
      title: "建筑与维护电工考证培训班 (309A / 442A)",
      badge: "安省持牌技工高薪黄金专业",
      duration: "考证冲刺班 / 实用周末班（灵活随到随学）",
      credential: "结业证书 + 红宝书真题库 + 雇主直推信",
      overview: "由安省 20 余年一线西人大型工程公司项目主管与资深华人电工名师联袂授课。将加国电气规范（CEC）考点精讲与安省学徒实训基地真机实操融为一体，助学员一次性高效通关拿牌。",
      modules: [
        "加拿大电气规范（CEC Code Book）结构深度拆解与查表秘籍",
        "单相与三相交直流电路分析、负荷计算与变压器选型",
        "民用住宅电气布线、主配电箱配线、接地与防雷保护",
        "商业建筑电气施工：各种口径管道弯管（Conduit Bending）、电缆桥架",
        "工业电机控制（Motor Controls）、继电器控制柜接线与电气原理图识图",
        "安省 309A / 442A 执照考试核心题库高频考点全真模考解析",
        "官方认可学徒基地 1对1 动手实操教学，快速累积实战操作技能",
        "协助申报学徒工时（Apprenticeship Hours）及大多伦多工程项目就业直推"
      ],
      careers: "安省持牌建筑电工（309A）、工业维护电工（442A）、电气工程承包商、太阳能与新能源技师。",
      outcomes: "加国薪资最高的金牌技工之一，持牌时薪普遍达 $35–$55+/小时，工会福利完善，收入稳定抗周期。"
    }
  }
};

// Testimonials Data
const testimonialsList = [
  {
    quote_key: "test_1_text",
    author_key: "test_1_author",
    prog_key: "test_1_prog"
  },
  {
    quote_key: "test_2_text",
    author_key: "test_2_author",
    prog_key: "test_2_prog"
  },
  {
    quote_key: "test_3_text",
    author_key: "test_3_author",
    prog_key: "test_3_prog"
  },
  {
    quote_key: "test_4_text",
    author_key: "test_4_author",
    prog_key: "test_4_prog"
  }
];

let testIndex = 0;

// Dynamic programs & Job Fair store
let dynamicProgramsList = [];
let activeJobFairData = null;

// Helper HTML escaping for public app
function escapeAppHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  initLanguage();
  initTestimonialNav();
  initModals();
  loadDynamicPrograms();
  loadDynamicJobFair();
  initPublicArticles();
  initConsultationForm();
  initMobileMenu();
  initSmoothScroll();
  
  // Initialize Victoria AI Assistant
  if (typeof window.initVicChatbot === 'function') {
    window.initVicChatbot();
  }
});

// 1. Language Switcher Logic
function initLanguage() {
  const langToggles = document.querySelectorAll('.js-lang-toggle');
  
  applyLanguage(currentLanguage);

  langToggles.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      currentLanguage = currentLanguage === 'en' ? 'zh' : 'en';
      window.currentLanguage = currentLanguage;
      localStorage.setItem('vic_lang', currentLanguage);
      applyLanguage(currentLanguage);

      // Update testimonial text
      updateTestimonialDisplay();

      // Update modal if open
      const modal = document.getElementById('program-modal');
      if (modal && modal.classList.contains('active') && modal.dataset.currentProg) {
        openProgramModal(modal.dataset.currentProg);
      }

      // Update AI Chatbot language
      if (typeof window.updateChatbotLanguage === 'function') {
        window.updateChatbotLanguage(currentLanguage);
      }
    });
  });
}

function applyLanguage(lang) {
  const langData = translations[lang];
  if (!langData) return;

  document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';

  // Translate elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (langData[key] !== undefined) {
      el.innerHTML = langData[key];
    }
  });

  // Translate placeholders with data-i18n-ph
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const key = el.getAttribute('data-i18n-ph');
    if (langData[key] !== undefined) {
      el.placeholder = langData[key];
    }
  });

  // Update dynamic programs cards and navigation if loaded
  if (dynamicProgramsList && dynamicProgramsList.length > 0) {
    renderDynamicPrograms(lang);
    updateProgramNavigationAndDropdowns(lang);
  }

  // Update dynamic job fair banner if loaded
  if (activeJobFairData) {
    renderDynamicJobFair(lang);
  }

  // Update language button labels
  document.querySelectorAll('.js-lang-toggle').forEach(btn => {
    const labelSpan = btn.querySelector('.lang-label');
    const badgeSpan = btn.querySelector('.lang-badge');
    if (labelSpan) {
      labelSpan.textContent = lang === 'en' ? '中文' : 'English';
    }
    if (badgeSpan) {
      badgeSpan.textContent = lang === 'en' ? 'EN' : '中文';
    }
    btn.setAttribute('aria-label', lang === 'en' ? 'Switch to Chinese' : 'Switch to English');
  });
}

// Expose globally
window.applyLanguage = applyLanguage;

// 2. Testimonial Navigation
function initTestimonialNav() {
  const prevBtn = document.getElementById('test-prev');
  const nextBtn = document.getElementById('test-next');

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      testIndex = (testIndex - 1 + testimonialsList.length) % testimonialsList.length;
      updateTestimonialDisplay();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      testIndex = (testIndex + 1) % testimonialsList.length;
      updateTestimonialDisplay();
    });
  }

  // Autoplay
  setInterval(() => {
    testIndex = (testIndex + 1) % testimonialsList.length;
    updateTestimonialDisplay();
  }, 7000);
}

function updateTestimonialDisplay() {
  const item = testimonialsList[testIndex];
  const langData = translations[currentLanguage];
  if (!item || !langData) return;

  const quoteEl = document.getElementById('student-quote');
  const nameEl = document.getElementById('student-name');
  const titleEl = document.getElementById('student-title');

  if (quoteEl) quoteEl.innerHTML = langData[item.quote_key];
  if (nameEl) nameEl.innerHTML = langData[item.author_key];
  if (titleEl) titleEl.innerHTML = langData[item.prog_key];
}

// 3. Modals (Program Details Deep Dive)
function initModals() {
  const modal = document.getElementById('program-modal');
  const closeBtn = modal?.querySelector('.modal-close-vic');

  document.querySelectorAll('.js-open-prog-modal').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const progKey = btn.getAttribute('data-program');
      openProgramModal(progKey);
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeProgramModal);
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeProgramModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal?.classList.contains('active')) {
      closeProgramModal();
    }
  });
}

function openProgramModal(progKey) {
  const modal = document.getElementById('program-modal');
  if (!modal || !programDetailsData[progKey]) return;

  modal.dataset.currentProg = progKey;
  const data = programDetailsData[progKey][currentLanguage] || programDetailsData[progKey]['en'];

  document.getElementById('modal-prog-badge').textContent = data.badge;
  document.getElementById('modal-prog-title').textContent = data.title;
  document.getElementById('modal-prog-duration').textContent = data.duration;
  document.getElementById('modal-prog-credential').textContent = data.credential;
  document.getElementById('modal-prog-overview').textContent = data.overview;
  document.getElementById('modal-prog-careers').textContent = data.careers;
  document.getElementById('modal-prog-outcomes').textContent = data.outcomes;

  const modulesList = document.getElementById('modal-prog-modules');
  modulesList.innerHTML = '';
  data.modules.forEach(mod => {
    const li = document.createElement('li');
    li.style.padding = '6px 0';
    li.style.borderBottom = '1px solid #eee';
    li.style.fontSize = '14px';
    li.innerHTML = `<span style="color: var(--vic-red); font-weight: bold; margin-right: 8px;">✓</span> ${mod}`;
    modulesList.appendChild(li);
  });

  const consultBtn = document.getElementById('modal-book-cta');
  if (consultBtn) {
    consultBtn.onclick = () => {
      closeProgramModal();
      const select = document.getElementById('consult-program');
      if (select) select.value = progKey;
      const consultSection = document.getElementById('consultation');
      if (consultSection) consultSection.scrollIntoView({ behavior: 'smooth' });
    };
  }

  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeProgramModal() {
  const modal = document.getElementById('program-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Expose globally for AI Chatbot deep linking
window.openProgramModal = openProgramModal;
window.closeProgramModal = closeProgramModal;

// 4. Consultation Form Handling
function initConsultationForm() {
  const form = document.getElementById('consultation-form');
  const successBox = document.getElementById('consultation-success');

  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    form.style.display = 'none';
    if (successBox) successBox.style.display = 'block';
  });
}

// 5. Mobile Menu
function initMobileMenu() {
  const toggleBtn = document.querySelector('.mobile-toggle-btn');
  const navDrawer = document.querySelector('.mobile-nav-drawer');
  const drawerOverlay = document.querySelector('.mobile-drawer-overlay');
  const closeBtn = document.querySelector('.mobile-drawer-close');
  const navLinks = document.querySelectorAll('.mobile-nav-drawer a');

  if (!toggleBtn || !navDrawer) return;

  function openDrawer() {
    navDrawer.classList.add('open');
    if (drawerOverlay) drawerOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    navDrawer.classList.remove('open');
    if (drawerOverlay) drawerOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  toggleBtn.addEventListener('click', openDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);

  navLinks.forEach(link => link.addEventListener('click', closeDrawer));
}

// 6. Smooth Scroll & CTA Actions
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || targetId === '') return;
      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        const headerOffset = 80;
        const elementPosition = targetEl.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });

        // If clicking Check Aid CTA, automatically check the grant checkbox in form
        if (anchor.classList.contains('js-check-aid-cta')) {
          const aidCheck = document.getElementById('consult-grant-check');
          if (aidCheck) aidCheck.checked = true;
        }
      }
    });
  });
}

// 7. SEO & GEO Career Insights Public Section
let publicArticlesData = [];

async function initPublicArticles() {
  const container = document.getElementById('public-articles-grid');
  if (!container) return;

  try {
    const apiUrl = typeof window.getVicApiUrl === 'function' ? window.getVicApiUrl('/api/articles') : '/api/articles';
    const res = await fetch(apiUrl);
    const data = await res.json();

    if (res.ok && data.articles && data.articles.length > 0) {
      publicArticlesData = data.articles;
      renderPublicArticlesGrid(data.articles);
    } else {
      container.innerHTML = `
        <div style="text-align: center; padding: 40px; grid-column: 1 / -1; color: #888;">
          <p>Stay tuned! Our academic team is preparing new career and grant insights for 2026.</p>
        </div>
      `;
    }
  } catch (err) {
    console.warn('Failed to load public articles:', err);
    if (container) {
      container.innerHTML = `
        <div style="text-align: center; padding: 30px; grid-column: 1 / -1; color: #888;">
          <p>Career insights and grant guides will be available shortly.</p>
        </div>
      `;
    }
  }

  // Bind Public Article Reader Modal Close
  const modal = document.getElementById('modal-public-article');
  const closeBtns = document.querySelectorAll('.js-close-public-art-modal');
  closeBtns.forEach(btn => {
    btn.onclick = () => {
      if (modal) modal.classList.remove('active');
    };
  });
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });
  }
}

function renderPublicArticlesGrid(articles) {
  const container = document.getElementById('public-articles-grid');
  if (!container) return;

  const categoryIcons = {
    healthcare: 'fa-heartbeat',
    technology: 'fa-laptop-code',
    financial_aid: 'fa-hand-holding-dollar',
    business: 'fa-briefcase',
    programs: 'fa-graduation-cap'
  };

  container.innerHTML = articles.map(art => {
    const icon = categoryIcons[art.category] || 'fa-newspaper';
    const dateStr = (art.published_at || art.created_at || '2026').substring(0, 10);
    const summaryClean = (art.summary || '').length > 130 
      ? art.summary.substring(0, 130) + '...' 
      : art.summary;

    return `
      <div class="article-card-public" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 2px 10px rgba(0,0,0,0.03); transition: transform 0.2s, box-shadow 0.2s;">
        <div>
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <span class="geo-badge-pill" style="font-size: 11px; padding: 2px 7px;">
              <i class="fa-solid fa-location-dot"></i> ${art.geo_target || 'Toronto & GTA'}
            </span>
            <span style="font-size: 11.5px; color: #94A3B8; font-weight: 500;">
              ${dateStr}
            </span>
          </div>

          <h3 style="font-size: 1.15rem; font-family: var(--font-serif); color: #0F172A; margin: 0 0 10px; line-height: 1.4;">
            ${art.title}
          </h3>

          <p style="font-size: 13.5px; color: #64748B; line-height: 1.55; margin-bottom: 18px;">
            ${summaryClean}
          </p>
        </div>

        <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #F1F5F9; padding-top: 14px; margin-top: 6px;">
          <button type="button" class="js-open-public-art-btn" data-id="${art.id}" style="background: transparent; border: none; color: var(--vic-red); font-size: 13px; font-weight: 700; cursor: pointer; padding: 0; display: inline-flex; align-items: center; gap: 4px;">
            Read Overview <i class="fa-solid fa-angle-right" style="font-size: 11px;"></i>
          </button>
          <a href="/article.html?slug=${art.slug}" style="font-size: 12px; color: #64748B; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
            Full Page <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 10px;"></i>
          </a>
        </div>
      </div>
    `;
  }).join('');

  // Attach button click listeners
  container.querySelectorAll('.js-open-public-art-btn').forEach(btn => {
    btn.onclick = () => {
      const artId = parseInt(btn.dataset.id);
      const article = publicArticlesData.find(a => a.id === artId);
      if (article) openPublicArticleModal(article);
    };
  });
}

function openPublicArticleModal(article) {
  const modal = document.getElementById('modal-public-article');
  if (!modal || !article) return;

  const geoEl = document.getElementById('pub-modal-geo');
  if (geoEl) geoEl.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${article.geo_target || 'Toronto, Ontario'}`;

  const catEl = document.getElementById('pub-modal-category');
  if (catEl) catEl.textContent = article.category || 'Programs';

  const dateEl = document.getElementById('pub-modal-date');
  if (dateEl) dateEl.textContent = (article.published_at || article.created_at || '2026').substring(0, 10);

  const titleEl = document.getElementById('pub-modal-title');
  if (titleEl) titleEl.textContent = article.title;

  const summaryEl = document.getElementById('pub-modal-summary');
  if (summaryEl) summaryEl.textContent = article.summary || '';

  const bodyEl = document.getElementById('pub-modal-body');
  if (bodyEl) bodyEl.innerHTML = article.content || '';

  const directLinkEl = document.getElementById('pub-modal-direct-link');
  if (directLinkEl) {
    directLinkEl.href = `/article.html?slug=${article.slug}`;
  }

  modal.classList.add('active');
}

// 8. Dynamic Academic Programs Loader & Renderer
async function loadDynamicPrograms() {
  const container = document.getElementById('programs-dynamic-container');
  try {
    const apiUrl = typeof window.getVicApiUrl === 'function' ? window.getVicApiUrl('/api/programs') : '/api/programs';
    const res = await fetch(apiUrl);
    const data = await res.json();

    if (res.ok && data.programs && data.programs.length > 0) {
      dynamicProgramsList = data.programs;

      // Populate programDetailsData for the deep-dive popup modal
      dynamicProgramsList.forEach(p => {
        programDetailsData[p.slug] = {
          en: {
            title: p.title_en || '',
            badge: p.badge_en || '',
            duration: p.duration_en || '',
            credential: p.credential_en || '',
            overview: p.overview_en || '',
            modules: Array.isArray(p.modules_en) ? p.modules_en : [],
            careers: p.careers_en || '',
            outcomes: p.outcomes_en || ''
          },
          zh: {
            title: p.title_zh || p.title_en || '',
            badge: p.badge_zh || p.badge_en || '',
            duration: p.duration_zh || p.duration_en || '',
            credential: p.credential_zh || p.credential_en || '',
            overview: p.overview_zh || p.overview_en || '',
            modules: Array.isArray(p.modules_zh) && p.modules_zh.length > 0 ? p.modules_zh : (Array.isArray(p.modules_en) ? p.modules_en : []),
            careers: p.careers_zh || p.careers_en || '',
            outcomes: p.outcomes_zh || p.outcomes_en || ''
          }
        };
      });

      renderDynamicPrograms(currentLanguage);
      updateProgramNavigationAndDropdowns(currentLanguage);
    }
  } catch (err) {
    console.warn('Failed to load dynamic programs:', err);
  }
}

function renderDynamicPrograms(lang = currentLanguage) {
  const container = document.getElementById('programs-dynamic-container');
  if (!container || !dynamicProgramsList || dynamicProgramsList.length === 0) return;

  container.innerHTML = dynamicProgramsList.map((prog, index) => {
    const isReverse = index % 2 === 1;
    const rowClass = isReverse ? 'program-row reverse-layout' : 'program-row';
    const title = (lang === 'zh' ? prog.title_zh : prog.title_en) || prog.title_en || '';
    const desc = (lang === 'zh' ? prog.desc_zh : prog.desc_en) || prog.desc_en || '';
    const bullets = (lang === 'zh' ? prog.bullets_zh : prog.bullets_en) || prog.bullets_en || [];
    const btnText = lang === 'zh' ? '了解更多' : 'Learn More';
    const imgUrl = prog.image_url || 'images/fullstack.jpg';

    let bulletsHtml = '';
    if (Array.isArray(bullets) && bullets.length > 0) {
      const isSingleCol = bullets.length <= 4;
      bulletsHtml = `
        <ul class="program-bullet-list" ${isSingleCol ? 'style="grid-template-columns: 1fr;"' : ''}>
          ${bullets.map(b => `<li>${escapeAppHtml(b)}</li>`).join('')}
        </ul>
      `;
    }

    return `
      <!-- Program ${index + 1}: ${escapeAppHtml(prog.slug)} -->
      <div id="${escapeAppHtml(prog.slug)}" class="${rowClass}">
        <div class="program-img-wrapper">
          <img src="${escapeAppHtml(imgUrl)}" alt="${escapeAppHtml(title)}" onerror="this.src='images/fullstack.jpg'">
        </div>
        <div class="program-info-col">
          <h2 class="program-heading">${escapeAppHtml(title)}</h2>
          <div class="vic-divider"></div>
          <p class="program-text">${escapeAppHtml(desc)}</p>
          ${bulletsHtml}
          <button type="button" class="btn-learn-more js-open-prog-modal" data-program="${escapeAppHtml(prog.slug)}">
            <span>${btnText}</span> <i class="fa-solid fa-arrow-right"></i>
          </button>
        </div>
      </div>
    `;
  }).join('');

  // Re-bind modal click events for dynamically generated buttons
  container.querySelectorAll('.js-open-prog-modal').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const progKey = btn.getAttribute('data-program');
      openProgramModal(progKey);
    });
  });
}

function updateProgramNavigationAndDropdowns(lang = currentLanguage) {
  if (!dynamicProgramsList || dynamicProgramsList.length === 0) return;

  // 1. Header Dropdown
  const headerDropdown = document.querySelector('.main-nav-item .nav-dropdown');
  if (headerDropdown) {
    headerDropdown.innerHTML = dynamicProgramsList.map(p => {
      const title = (lang === 'zh' ? p.title_zh : p.title_en) || p.title_en;
      return `<a href="#${p.slug}">${escapeAppHtml(title)}</a>`;
    }).join('');
  }

  // 2. Consultation Dropdown
  const consultSelect = document.getElementById('consult-program');
  if (consultSelect) {
    const selectedVal = consultSelect.value;
    const defaultOptionText = lang === 'zh' ? '-- 请选择意向专业 --' : '-- Select a Program --';
    consultSelect.innerHTML = `<option value="">${defaultOptionText}</option>` + 
      dynamicProgramsList.map(p => {
        const title = (lang === 'zh' ? p.title_zh : p.title_en) || p.title_en;
        return `<option value="${p.slug}" ${p.slug === selectedVal ? 'selected' : ''}>${escapeAppHtml(title)}</option>`;
      }).join('');
  }

  // 3. Footer Program Links
  const footerList = document.querySelector('.footer-prog-list');
  if (footerList) {
    footerList.innerHTML = dynamicProgramsList.map(p => {
      const title = (lang === 'zh' ? p.title_zh : p.title_en) || p.title_en;
      return `<li><a href="#${p.slug}">${escapeAppHtml(title)}</a></li>`;
    }).join('');
  }
}

// 9. Dynamic Job Fair Banner Loader & Renderer
async function loadDynamicJobFair() {
  const section = document.getElementById('job-fair-banner-section');
  if (!section) return;

  try {
    const apiUrl = typeof window.getVicApiUrl === 'function' ? window.getVicApiUrl('/api/job-fair') : '/api/job-fair';
    const res = await fetch(apiUrl);
    const data = await res.json();

    if (res.ok && data.success) {
      activeJobFairData = data.job_fair;
      renderDynamicJobFair(currentLanguage);
    }
  } catch (err) {
    console.warn('Failed to load dynamic job fair banner:', err);
  }
}

function renderDynamicJobFair(lang = currentLanguage) {
  const section = document.getElementById('job-fair-banner-section');
  if (!section) return;

  if (!activeJobFairData || activeJobFairData.is_active === 0) {
    section.style.display = 'none';
    return;
  }

  section.style.display = '';

  const isZh = lang === 'zh';
  const title = (isZh ? activeJobFairData.title_zh : activeJobFairData.title_en) || activeJobFairData.title_en || '';
  const subtitle = (isZh ? activeJobFairData.subtitle_zh : activeJobFairData.subtitle_en) || activeJobFairData.subtitle_en || '';
  const date = (isZh ? activeJobFairData.date_zh : activeJobFairData.date_en) || activeJobFairData.date_en || '';
  const location = (isZh ? activeJobFairData.location_zh : activeJobFairData.location_en) || activeJobFairData.location_en || '';
  const btnText = (isZh ? activeJobFairData.btn_text_zh : activeJobFairData.btn_text_en) || activeJobFairData.btn_text_en || 'Secure Your Spot';
  const btnLink = activeJobFairData.btn_link || '#consultation';
  const bgImage = activeJobFairData.bg_image_url || 'images/job-fair.png';

  if (bgImage) {
    section.style.backgroundImage = `url("${bgImage}")`;
  }

  const titleEl = document.getElementById('job-fair-title');
  if (titleEl) titleEl.textContent = title;

  const subtitleEl = document.getElementById('job-fair-subtitle');
  if (subtitleEl) subtitleEl.textContent = subtitle;

  const dateEl = document.getElementById('job-fair-date');
  if (dateEl) dateEl.textContent = date;

  const locEl = document.getElementById('job-fair-location');
  if (locEl) locEl.textContent = location;

  const btnEl = document.getElementById('job-fair-btn');
  if (btnEl) {
    btnEl.textContent = btnText;
    btnEl.href = btnLink;
  }
}




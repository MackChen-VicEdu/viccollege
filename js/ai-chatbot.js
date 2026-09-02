/**
 * Victoria International College - AI Career & Admissions Assistant
 * Intelligent bilingual conversational agent for program information, government grants, and admissions.
 */

(function() {
  'use strict';

  // Victoria College Comprehensive Domain Knowledge Base
  const VIC_KB = {
    general: {
      en: {
        intro: "Victoria International College of Business & Technology is an Ontario registered career college (under the Ontario Career Colleges Act, 2005) with over 22 years of educational excellence and 15,000+ successful alumni across Canada.",
        contact: "📞 Phone: 416-665-6668 | ✉️ Email: info@viccollege.com | 🕒 Hours: Monday – Saturday, 9:00 AM – 6:00 PM.",
        campuses: "📍 Markham Main Campus: 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n📍 North York Campus: 306 Consumers Rd., North York, ON M2J 1P8",
        leadership: "President Maria Sun is the Dean of Victoria International College and President of Victoria Education Group, with 22+ years of leadership empowering new immigrants and youth in Canada."
      },
      zh: {
        intro: "维多利亚职业学院（Victoria International College of Business & Technology）是经安大略省教育部（Ontario Career Colleges Act, 2005）正式注册认可的正规职业学院，办学逾22年，累计培养并协助15,000多名优秀毕业学员在加国高薪就业。",
        contact: "📞 咨询热线：416-665-6668 | ✉️ 邮箱：info@viccollege.com | 🕒 办公时间：周一至周六 9:00 AM – 6:00 PM",
        campuses: "📍 万锦主校区：7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n📍 北约克校区：306 Consumers Rd., North York, ON M2J 1P8",
        leadership: "孙善勤（Maria Sun）校长为维多利亚教育集团总裁、维多利亚职业学院院长，深耕加国职业教育22年，帮助成千上万华人新移民和学子成功融入加国职场。"
      }
    },
    grant: {
      en: {
        title: "Better Jobs Ontario (Second Career) & Government Grants",
        summary: "You could qualify for up to **$28,000+ in non-repayable government funding** to cover 100% of your tuition, books, transportation, daycare, and monthly living allowances!",
        eligibility: "• Laid-off workers or former EI recipients\n• Gig workers, self-employed, or contract workers\n• Low-income or underemployed individuals\n• Permanent Residents & Canadian Citizens",
        help: "Our senior admissions advisors provide **100% complimentary step-by-step assistance** from documentation research to submission.",
        cta_label: "Apply for Grant Evaluation"
      },
      zh: {
        title: "安省政府免费培训补助 Better Jobs Ontario (Second Career)",
        summary: "符合资格者可申请最高 **$28,000+ 加币全额政府无偿资助**，涵盖 100% 学费、书本费、交通费、托儿补贴及每月基本生活津贴，**无需自掏腰包**！",
        eligibility: "• 近期被解雇（Layoff）或曾领过 EI 的人士\n• 零工/自雇/兼职或合约工人士\n• 低收入或无固定全职工作者\n• 加拿大永久居民（PR）或公民",
        help: "维多利亚学院拥有20余年政府补助申请辅导经验，提供**全程1对1免费规划与材料整理**，获批率极高！",
        cta_label: "免费评估补助资格"
      }
    },
    programs: {
      psw: {
        en: {
          name: "NACC Personal Support Worker (PSW DE 2022)",
          duration: "30 Weeks (Classroom + Simulation Lab + Clinical Practicum)",
          credential: "NACC PSW Diploma + Standard First Aid & CPR Level C",
          salary: "$20 – $28 / hour with strong job security",
          highlights: "Accredited curriculum, 300+ hours guaranteed clinical practicum in top long-term care homes, direct hiring fairs.",
          overview: "Prepares you for immediate employment in hospitals, nursing homes, and home healthcare agencies. Highly in-demand across Ontario."
        },
        zh: {
          name: "NACC 个人护理护工文凭 (PSW DE 2022)",
          duration: "30 周（理论课 + 实验室模拟实操 + 300+小时持牌养老院临床实习）",
          credential: "安省 NACC PSW 官方职业文凭 + CPR / First Aid 急救证书",
          salary: "起薪时薪 $20 – $28 加元/小时，各大公立私立养老院紧缺",
          highlights: "配备标准病房模拟实验室，安省持牌资深护士亲授，毕业直接对接西人养老机构实习就业。",
          overview: "安省长期特缺黄金医疗岗位，工作稳定，福利健全，适合希望快速转行医疗领域人士。"
        }
      },
      tech: {
        en: {
          name: "Full Stack Web Technician",
          duration: "32 Weeks (Intensive Labs + Commercial Capstone Project)",
          credential: "Full Stack Web Technician Career Diploma",
          salary: "$65,000 – $85,000 / year entry starting salary",
          highlights: "Core Java, Spring Boot 3, Spring Cloud microservices, React, TypeScript, AWS Cloud, Docker, LeetCode coaching & mock interviews.",
          overview: "Enterprise-grade software engineering curriculum designed for landing modern IT jobs across Canadian banks, tech firms, and enterprises."
        },
        zh: {
          name: "全栈网页开发技术员 (Full Stack Web Technician)",
          duration: "32 周（高强度代码实训 + 商业级大型云端微服务项目）",
          credential: "安省教育部认证 Full Stack Web 职业文凭",
          salary: "加国毕业起薪 $65,000 – $85,000 加元/年",
          highlights: "涵盖 Java、Spring Boot 微服务架构、React 前端全家桶、TypeScript、AWS 云原生与 Docker 容器化部署，名师辅导 LeetCode 刷题与大厂面试。",
          overview: "零基础到企业级实战开发，助您高效进入加国高薪科技与金融 IT 行业。"
        }
      },
      accounting: {
        en: {
          name: "Accounting, Tax and Payroll Administration",
          duration: "30 Weeks (Hands-on Corporate Accounting Software)",
          credential: "Computerized Accounting & Payroll Diploma",
          salary: "$48,000 – $65,000 / year with clear CPA progression",
          highlights: "QuickBooks Desktop & Online, Sage 50, Profile, TaxPrep, Canadian Payroll (CRA, EI, CPP, T4), Personal (T1) & Corporate (T2) Tax.",
          overview: "Taught by practicing Canadian CPAs. Master Canadian tax returns and corporate accounting workflows with real corporate ledgers."
        },
        zh: {
          name: "会计、税务与薪资管理文凭 (Accounting, Tax & Payroll)",
          duration: "30 周（资深持牌 CPA 亲授 + 企业真实账套实训）",
          credential: "安省认证 Computerized Accounting & Payroll 职业文凭",
          salary: "加国起薪 $48,000 – $65,000 加元/年，稳定白领晋升路径",
          highlights: "精通 QuickBooks、Sage 50 财务软件，加拿大全流程工资税（CPP, EI, T4），CRA 个人税（T1）与公司税（T2）实操申报及税务审计应对。",
          overview: "适合希望在加国事务所、中小企业及金融财务部门从事全盘会计与税务工作的学员。"
        }
      },
      eca: {
        en: {
          name: "Early Childcare Assistant (ECA)",
          duration: "28 Weeks (Includes Field Practicum in Licensed Daycares)",
          credential: "Early Childcare Assistant Career Diploma",
          salary: "$19 – $25 / hour with rewarding child care growth",
          highlights: "Child psychology, developmental milestones, safety & nutrition, CPR, direct daycare placements.",
          overview: "Develop essential skills to care for infants, toddlers, and preschool children in licensed Ontario daycare facilities."
        },
        zh: {
          name: "早期幼儿教育助理 (Early Childcare Assistant - ECA)",
          duration: "28 周（理论学习 + 安省持牌正规幼儿园实习）",
          credential: "安省认证 Early Childcare Assistant 职业文凭",
          salary: "时薪 $19 – $25 加元/小时，托儿所长青热门需求",
          highlights: "儿童心理学、幼儿行为引导、膳食营养与紧急救护，100%安排安省持牌幼儿园实地实习。",
          overview: "喜爱幼儿与教育工作人士的理想文凭课程，工作环境温馨，就业前景广阔。"
        }
      },
      elec: {
        en: {
          name: "Electrician Licensing & Training (309A / 442A)",
          duration: "Weekend & Flexible Fast-Track Schedules",
          credential: "Canadian Electrical Code (CEC) Pre-Exam & Apprenticeship Prep",
          salary: "$35 – $55+ / hour as licensed journeyperson",
          highlights: "Taught by Canadian Master Electricians (20+ yrs experience), hands-on circuit wiring, conduit bending, code book mastery.",
          overview: "Coaches both domestic/commercial (309A) and industrial (442A) electrician license examination and Canadian apprenticeships."
        },
        zh: {
          name: "电工考证与上岗实训班 (309A / 442A Electrician)",
          duration: "周末实操班与强化考证班，时间灵活",
          credential: "加拿大电气规范 CEC 考证辅导与学徒工技能认证",
          salary: "持牌电工时薪高达 $35 – $55+ 加币/小时，工会及商业项目薪资丰厚",
          highlights: "20余年加国老牌持牌 Master Electrician 名师带教，真刀实枪接线布管、工业配电盘组装，精准攻克考题重点。",
          overview: "适合工科背景或希望进入加拿大高收入建筑、工程与工业电气技工行业的学员。"
        }
      },
      acu: {
        en: {
          name: "Acupuncture & Traditional Wellness (Non-Vocational)",
          duration: "Flexible Evening & Weekend Enrichment",
          credential: "TCM Holistic Wellness Certificate",
          salary: "Holistic health practice & personal wellness enhancement",
          highlights: "TCM Meridian theory, acupressure points, safe needle techniques, moxibustion & cupping basics.",
          overview: "Popular enrichment course for individuals passionate about holistic Chinese healthcare and wellness preservation."
        },
        zh: {
          name: "中医针灸与传统养生班 (Acupuncture & Wellness)",
          duration: "晚班/周末班，弹性课时",
          credential: "中医养生与实用针灸结业证书（非职业兴趣课程）",
          salary: "健康保健、家庭调理与中医诊所辅助技能",
          highlights: "中医经络学说、十四经腧穴精讲、安全针法实操、艾灸拔罐推拿配穴实用技巧。",
          overview: "适合注重自身与家人健康调养、热爱传统中医养生文化的爱好者深入学习。"
        }
      }
    }
  };

  // Quick prompt suggestions
  const QUICK_PROMPTS = {
    en: [
      "💰 How do I get the $28,000 grant?",
      "🩺 Tell me about PSW Program",
      "💻 Full Stack Web duration & salary",
      "📊 Accounting & Payroll diploma",
      "📍 Campus locations & phone",
      "📅 Book a consultation"
    ],
    zh: [
      "💰 如何申请 $28,000 政府免费补助？",
      "🩺 了解 PSW 个人护理护工文凭",
      "💻 全栈开发课程学多久？起薪多少？",
      "📊 会计与税务管理文凭详情",
      "📍 校区地址与联系电话",
      "📅 预约 1对1 免费规划咨询"
    ]
  };

  // DOM Elements holder
  let elements = {};
  let chatHistory = [];
  let isTyping = false;

  // Initialize Chatbot
  function init() {
    createChatbotDOM();
    bindEvents();
    loadHistory();
    updateAuthUIState();

    // Listen to real-time auth changes from VicAuth
    window.addEventListener('vic-auth-changed', () => {
      updateAuthUIState();
      // If history is just the initial welcome, refresh greeting for logged in state
      if (chatHistory.length <= 1) {
        renderInitialWelcome();
      }
    });
  }

  // Create UI Structure
  function createChatbotDOM() {
    if (document.getElementById('vic-chatbot-container')) return;

    const lang = (window.currentLanguage || localStorage.getItem('vic_lang') || 'en');

    const container = document.createElement('div');
    container.id = 'vic-chatbot-container';
    container.className = 'vic-chatbot-container';
    container.innerHTML = `
      <!-- Floating Action Button Launcher -->
      <button type="button" id="vic-chat-launcher" class="vic-chat-launcher" aria-label="Open AI Career Assistant">
        <div class="vic-launcher-glow"></div>
        <div class="vic-launcher-icon">
          <i class="fa-solid fa-comments"></i>
        </div>
        <span class="vic-launcher-badge">AI</span>
        <div class="vic-launcher-tooltip">
          <span class="pulse-dot"></span>
          <span id="vic-launcher-tooltip-text">${lang === 'zh' ? '有疑问？问问 VIC 智能升学助手' : 'Have questions? Ask VIC AI Advisor'}</span>
        </div>
      </button>

      <!-- Chatbot Popup Window -->
      <div id="vic-chat-window" class="vic-chat-window" aria-hidden="true">
        <!-- Header -->
        <div class="vic-chat-header">
          <div class="vic-chat-header-info">
            <div class="vic-chat-avatar">
              <img src="images/favicon.gif" alt="VIC AI">
              <span class="status-indicator"></span>
            </div>
            <div>
              <div class="vic-chat-title">
                <span>VIC AI Advisor</span>
                <span class="vic-ai-chip">24/7 Live</span>
              </div>
              <div class="vic-chat-subtitle" id="vic-chat-status">
                ${lang === 'zh' ? '维多利亚职业学院 • 智能问答系统' : 'Victoria College • Career & Grant Assistant'}
              </div>
            </div>
          </div>

          <div class="vic-chat-header-actions">
            <button type="button" class="chat-hdr-btn js-clear-chat" title="Clear conversation" aria-label="Clear chat">
              <i class="fa-solid fa-rotate-right"></i>
            </button>
            <button type="button" class="chat-hdr-btn js-minimize-chat" title="Minimize" aria-label="Minimize chat">
              <i class="fa-solid fa-minus"></i>
            </button>
            <button type="button" class="chat-hdr-btn js-close-chat" title="Close" aria-label="Close chat">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </div>
        </div>

        <!-- Notification / Aid Banner inside Chat -->
        <div class="vic-chat-banner">
          <i class="fa-solid fa-award"></i>
          <span id="vic-chat-banner-text">
            ${lang === 'zh' ? '💡 Better Jobs Ontario 政府资助最高可达 $28,000+' : '💡 Qualify for up to $28,000+ Government Training Grants'}
          </span>
        </div>

        <!-- Chat Messages Container -->
        <div class="vic-chat-messages" id="vic-chat-messages">
          <!-- Initial Welcome Message inserted dynamically -->
        </div>

        <!-- Quick Prompts Row -->
        <div class="vic-chat-suggestions" id="vic-chat-suggestions">
          <!-- Suggested Pills -->
        </div>

        <!-- Auth Gate Container (Injected dynamically when unauthenticated) -->
        <div id="vic-chat-auth-slot"></div>

        <!-- Input Area -->
        <form class="vic-chat-input-area" id="vic-chat-form">
          <input 
            type="text" 
            id="vic-chat-input" 
            class="vic-chat-input" 
            placeholder="${lang === 'zh' ? '输入您的问题（如：PSW就业、政府补助、学费）...' : 'Ask about programs, grants, tuition, admissions...'}" 
            autocomplete="off"
            required
          />
          <button type="submit" id="vic-chat-send" class="vic-chat-send-btn" aria-label="Send Message">
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </form>

        <div class="vic-chat-footer-brand">
          <span>Ontario Registered Career College • Powered by Victoria AI</span>
        </div>
      </div>
    `;

    document.body.appendChild(container);

    elements = {
      container: container,
      launcher: container.querySelector('#vic-chat-launcher'),
      window: container.querySelector('#vic-chat-window'),
      messages: container.querySelector('#vic-chat-messages'),
      suggestions: container.querySelector('#vic-chat-suggestions'),
      authSlot: container.querySelector('#vic-chat-auth-slot'),
      form: container.querySelector('#vic-chat-form'),
      input: container.querySelector('#vic-chat-input'),
      closeBtn: container.querySelector('.js-close-chat'),
      minimizeBtn: container.querySelector('.js-minimize-chat'),
      clearBtn: container.querySelector('.js-clear-chat'),
      tooltipText: container.querySelector('#vic-launcher-tooltip-text'),
      statusText: container.querySelector('#vic-chat-status'),
      bannerText: container.querySelector('#vic-chat-banner-text')
    };

    renderSuggestions();
  }

  // Update Auth Gate UI
  function updateAuthUIState() {
    if (!elements.window) return;

    const lang = (window.currentLanguage || localStorage.getItem('vic_lang') || 'en');
    const token = window.VicAuth?.getToken();
    const user = window.VicAuth?.getUser();
    const isAuthenticated = !!token;

    if (!isAuthenticated) {
      if (elements.statusText) {
        elements.statusText.innerHTML = `<span style="color:#b45309;"><i class="fa-solid fa-lock"></i> ${lang === 'zh' ? '请先登录即可开启智能咨询' : 'Login Required to Chat'}</span>`;
      }

      if (elements.input) {
        elements.input.disabled = true;
        elements.input.placeholder = lang === 'zh' ? '🔒 请先登录即可开启智能咨询...' : '🔒 Please sign in to chat with AI Advisor...';
      }

      if (elements.authSlot) {
        elements.authSlot.innerHTML = `
          <div class="vic-chat-auth-gate">
            <div class="vic-auth-gate-text">
              <i class="fa-solid fa-lock"></i>
              <span>${lang === 'zh' ? '仅限注册及登录用户使用 AI 顾问系统' : 'Sign in required to chat with Victoria College AI Assistant'}</span>
            </div>
            <div class="vic-auth-gate-buttons">
              <button type="button" class="vic-gate-btn vic-gate-btn-auth js-gate-login">
                <i class="fa-solid fa-right-to-bracket"></i> ${lang === 'zh' ? '登录 / 注册' : 'Sign In / Register'}
              </button>
              <button type="button" class="vic-gate-btn vic-gate-btn-google js-gate-google">
                <i class="fa-brands fa-google"></i> Google
              </button>
              <button type="button" class="vic-gate-btn vic-gate-btn-linkedin js-gate-linkedin">
                <i class="fa-brands fa-linkedin"></i> LinkedIn
              </button>
            </div>
          </div>
        `;

        const loginBtn = elements.authSlot.querySelector('.js-gate-login');
        const googleBtn = elements.authSlot.querySelector('.js-gate-google');
        const linkedinBtn = elements.authSlot.querySelector('.js-gate-linkedin');

        if (loginBtn) loginBtn.onclick = () => window.VicAuth?.openAuthModal('login');
        if (googleBtn) googleBtn.onclick = () => window.VicAuth?.loginWithGoogle();
        if (linkedinBtn) linkedinBtn.onclick = () => window.VicAuth?.loginWithLinkedIn();
      }
    } else {
      if (elements.statusText) {
        const userName = user?.name ? user.name.split(' ')[0] : 'Student';
        elements.statusText.innerHTML = `<span style="color:#15803d;"><i class="fa-solid fa-circle-check"></i> ${lang === 'zh' ? `已登录: ${userName}` : `Connected as ${userName}`}</span>`;
      }

      if (elements.input) {
        elements.input.disabled = false;
        elements.input.placeholder = lang === 'zh' ? '输入您的问题（如：PSW就业、政府补助、学费）...' : 'Ask about programs, grants, tuition, admissions...';
      }

      if (elements.authSlot) {
        elements.authSlot.innerHTML = '';
      }
    }
  }

  // Bind Listeners
  function bindEvents() {
    if (!elements.launcher) return;

    elements.launcher.addEventListener('click', toggleChat);
    elements.closeBtn.addEventListener('click', closeChat);
    elements.minimizeBtn.addEventListener('click', closeChat);
    
    elements.clearBtn.addEventListener('click', () => {
      clearHistory();
    });

    // If unauthenticated, clicking the form triggers login
    elements.form.addEventListener('click', () => {
      if (!window.VicAuth?.getToken()) {
        window.VicAuth?.openAuthModal('login');
      }
    });

    elements.form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!window.VicAuth?.getToken()) {
        window.VicAuth?.openAuthModal('login');
        return;
      }
      const text = elements.input.value.trim();
      if (!text || isTyping) return;
      handleUserMessage(text);
      elements.input.value = '';
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && elements.window.classList.contains('active')) {
        closeChat();
      }
    });

    // Delegate deep action clicks inside messages
    elements.messages.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-chat-action]');
      if (!btn) return;
      
      const action = btn.getAttribute('data-chat-action');
      const param = btn.getAttribute('data-chat-param');

      handleChatAction(action, param);
    });
  }

  // Toggle Chat Window
  function toggleChat() {
    if (!elements.window) return;
    const isOpen = elements.window.classList.contains('active');
    if (isOpen) {
      closeChat();
    } else {
      openChat();
    }
  }

  function openChat() {
    if (!elements.window || !elements.launcher) return;
    elements.window.classList.add('active');
    elements.launcher.classList.add('chat-open');
    elements.window.setAttribute('aria-hidden', 'false');
    updateAuthUIState();
    
    if (window.VicAuth?.getToken() && elements.input) {
      elements.input.focus();
    }
    
    // Hide tooltip when opened
    const tooltip = elements.launcher.querySelector('.vic-launcher-tooltip');
    if (tooltip) tooltip.style.display = 'none';

    scrollToBottom();
  }

  function closeChat() {
    if (!elements.window || !elements.launcher) return;
    elements.window.classList.remove('active');
    elements.launcher.classList.remove('chat-open');
    elements.window.setAttribute('aria-hidden', 'true');
  }

  // Render Prompt Suggestions
  function renderSuggestions() {
    if (!elements.suggestions) return;
    const lang = (window.currentLanguage || localStorage.getItem('vic_lang') || 'en');
    const list = QUICK_PROMPTS[lang] || QUICK_PROMPTS.en;

    elements.suggestions.innerHTML = '';
    list.forEach(promptText => {
      const pill = document.createElement('button');
      pill.type = 'button';
      pill.className = 'vic-suggestion-pill';
      pill.textContent = promptText;
      pill.addEventListener('click', () => {
        if (!window.VicAuth?.getToken()) {
          window.VicAuth?.openAuthModal('login');
          if (window.VicAuth?.showToast) {
            window.VicAuth.showToast(lang === 'zh' ? '请先登录以咨询 AI 顾问' : 'Please sign in to chat with the AI Advisor', 'warning');
          }
          return;
        }
        handleUserMessage(promptText.replace(/^[^\w\u4e00-\u9fa5$]+/, '').trim());
      });
      elements.suggestions.appendChild(pill);
    });
  }

  // Handle User Message
  async function handleUserMessage(userText) {
    if (!userText) return;

    // Check authentication
    const token = window.VicAuth?.getToken();
    if (!token) {
      window.VicAuth?.openAuthModal('login');
      updateAuthUIState();
      return;
    }

    // Add user bubble
    appendMessage({
      role: 'user',
      text: userText,
      timestamp: new Date()
    });

    scrollToBottom();

    // Show AI typing indicator
    showTypingIndicator();

    let backendResult = null;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: userText,
          history: chatHistory.slice(-6)
        })
      });

      if (res.status === 401) {
        const data = await res.json();
        hideTypingIndicator();
        updateAuthUIState();
        appendMessage({
          role: 'bot',
          text: `🔒 **Sign In Required**\n\nPlease sign in with your Google, LinkedIn, or Email account to continue chatting with the Victoria College AI Advisor.`,
          actions: [
            { label: '🔑 Sign In / Register', action: 'auth', param: 'login' },
            { label: '🌐 Continue with Google', action: 'auth_google', param: '' },
            { label: '💼 Continue with LinkedIn', action: 'auth_linkedin', param: '' }
          ],
          timestamp: new Date()
        });
        scrollToBottom();
        saveHistory();
        return;
      }

      if (res.ok) {
        backendResult = await res.json();
      }
    } catch (e) {
      console.log("Chat backend communication error:", e);
    }

    let responseText = '';
    let responseActions = [];

    if (backendResult && backendResult.response) {
      responseText = backendResult.response;
      responseActions = getContextualActions(userText, responseText);
    } else {
      const local = generateAIResponse(userText);
      responseText = local.text;
      responseActions = local.actions;
    }

    hideTypingIndicator();

    appendMessage({
      role: 'bot',
      text: responseText,
      actions: responseActions,
      timestamp: new Date()
    });

    scrollToBottom();
    saveHistory();
  }

  // Derive smart contextual action buttons from conversation topic
  function getContextualActions(query, responseText) {
    const combined = (query + " " + responseText).toLowerCase();
    const lang = detectLanguage(query);
    const actions = [];

    if (combined.includes('grant') || combined.includes('second career') || combined.includes('28,000') || combined.includes('28000') || combined.includes('补助') || combined.includes('资助')) {
      actions.push({ label: lang === 'zh' ? '💰 免费评估政府补助' : '💰 Check $28,000 Grant', action: 'consult', param: 'aid' });
    }
    if (combined.includes('psw') || combined.includes('support worker') || combined.includes('护工') || combined.includes('护理')) {
      actions.push({ label: lang === 'zh' ? '🔍 查看 PSW 课程详情' : '🔍 View PSW Details', action: 'open_modal', param: 'psw' });
    }
    if (combined.includes('full stack') || combined.includes('java') || combined.includes('web') || combined.includes('全栈') || combined.includes('编程')) {
      actions.push({ label: lang === 'zh' ? '🔍 查看 Full Stack 大纲' : '🔍 View Full Stack Details', action: 'open_modal', param: 'tech' });
    }
    if (combined.includes('account') || combined.includes('tax') || combined.includes('payroll') || combined.includes('会计') || combined.includes('报税')) {
      actions.push({ label: lang === 'zh' ? '🔍 查看会计文凭大纲' : '🔍 View Accounting Details', action: 'open_modal', param: 'accounting' });
    }
    if (combined.includes('childcare') || combined.includes('eca') || combined.includes('幼教')) {
      actions.push({ label: lang === 'zh' ? '🔍 查看幼教 ECA 详情' : '🔍 View ECA Details', action: 'open_modal', param: 'eca' });
    }
    if (combined.includes('electric') || combined.includes('309a') || combined.includes('442a') || combined.includes('电工')) {
      actions.push({ label: lang === 'zh' ? '🔍 查看电工班实训' : '🔍 View Electrician Details', action: 'open_modal', param: 'electrician' });
    }

    if (actions.length === 0) {
      actions.push({ label: lang === 'zh' ? '📅 预约 1对1 咨询' : '📅 Book Free Consultation', action: 'consult', param: '' });
      actions.push({ label: lang === 'zh' ? '📞 致电顾问 416-665-6668' : '📞 Call 416-665-6668', action: 'call', param: '4166656668' });
    }

    return actions;
  }

  // AI Knowledge & Reasoning Engine
  function generateAIResponse(query) {
    const lang = detectLanguage(query);
    const q = query.toLowerCase().trim();

    // 0. BJO vs OSAP Differences
    if (
      (q.includes('bjo') && (q.includes('osap') || q.includes('diff') || q.includes('vs') || q.includes('区别') || q.includes('对比') || q.includes('不同'))) ||
      (q.includes('osap') && (q.includes('grant') || q.includes('better jobs') || q.includes('bjo') || q.includes('区别') || q.includes('补助') || q.includes('不同'))) ||
      (q.includes('osap'))
    ) {
      if (lang === 'zh') {
        return {
          text: `### ⚖️ Better Jobs Ontario (BJO) 与 OSAP 的核心区别\n\n<div class="chat-compare-container">
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
      <span class="chat-compare-value">最高 <strong>$28,000+</strong> (涵盖学费、生活费、托儿与交通)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">偿还要求:</span>
      <span class="chat-compare-value"><strong>$0 无需偿还</strong> (白给补贴)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">目标群体:</span>
      <span class="chat-compare-value">被解雇失业、零工/合约工、低收入人士 (PR/公民)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">培训学制:</span>
      <span class="chat-compare-value">快速职业文凭 (30-32周，PSW/IT/会计/电工)</span>
    </div>
  </div>

  <div class="chat-compare-card card-osap">
    <div class="chat-compare-field">
      <span class="chat-compare-label">资助项目:</span>
      <span class="chat-compare-value"><span class="badge-osap">OSAP 安省学生资助</span></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">资金性质:</span>
      <span class="chat-compare-value"><strong>学生贷款 (Loan) + 助学金 (Grant)</strong></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">最高额度:</span>
      <span class="chat-compare-value">依家庭收入与学费动态核算</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">偿还要求:</span>
      <span class="chat-compare-value"><strong>贷款部分毕业后必须按期连本带息偿还</strong></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">目标群体:</span>
      <span class="chat-compare-value">大学/大专全日制或非全日制学生</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">培训学制:</span>
      <span class="chat-compare-value">传统多学年高等教育学位/文凭</span>
    </div>
  </div>
</div>\n\n💡 **维多利亚职业学院建议**：若您目前处于失业、领过 EI 或收入偏低，申请 **Better Jobs Ontario** 能够享受 **100% 零还款政府无偿全额资助**，远比背负 OSAP 学生贷款更划算！`,
          actions: [
            { label: '💰 免费评估 BJO $28,000 资助', action: 'consult', param: 'aid' },
            { label: '📞 电话咨询顾问 416-665-6668', action: 'call', param: '4166656668' }
          ]
        };
      } else {
        return {
          text: `### ⚖️ Comparison: Better Jobs Ontario (BJO) vs. OSAP\n\n<div class="chat-compare-container">
  <div class="chat-compare-card card-bjo">
    <div class="chat-compare-field">
      <span class="chat-compare-label">Program:</span>
      <span class="chat-compare-value"><span class="badge-bjo">Better Jobs Ontario (BJO)</span></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Funding Type:</span>
      <span class="chat-compare-value"><strong>100% Non-Repayable Grant</strong></span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Funding Max:</span>
      <span class="chat-compare-value">Up to <strong>$28,000+</strong> (100% Tuition, Books, Childcare & Living)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Repayment:</span>
      <span class="chat-compare-value"><strong>$0 Repayment</strong> (Never pay back)</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Eligibility:</span>
      <span class="chat-compare-value">Laid-off workers, gig/contract workers, underemployed, PR/Citizens</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Program:</span>
      <span class="chat-compare-value">Fast-track vocational diplomas (30-32 weeks, PSW/IT/Accounting)</span>
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
      <span class="chat-compare-label">Funding Max:</span>
      <span class="chat-compare-value">Calculated based on family income & institution costs</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Repayment:</span>
      <span class="chat-compare-value"><strong>Loan portion MUST be repaid</strong> with interest</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Eligibility:</span>
      <span class="chat-compare-value">College & university degree/diploma students</span>
    </div>
    <div class="chat-compare-field">
      <span class="chat-compare-label">Program:</span>
      <span class="chat-compare-value">Traditional multi-year academic degrees/diplomas</span>
    </div>
  </div>
</div>\n\n💡 **Victoria College Advisor Tip:** If you are currently laid off, underemployed, or a contract worker, **Better Jobs Ontario** is vastly superior because it is **100% free gift money** with **no debt**, unlike OSAP which requires student loan repayment!`,
          actions: [
            { label: '💰 Free BJO $28,000 Eligibility Check', action: 'consult', param: 'aid' },
            { label: '📞 Call Advisor 416-665-6668', action: 'call', param: '4166656668' }
          ]
        };
      }
    }

    // 1. Government Grant / Better Jobs Ontario / Second Career
    if (
      q.includes('grant') || q.includes('28,000') || q.includes('28000') || q.includes('second career') || 
      q.includes('better jobs') || q.includes('funding') || q.includes('financial aid') || q.includes('free money') ||
      q.includes('补助') || q.includes('政府资助') || q.includes('第二职业') || q.includes('免费学') || q.includes('津贴') || q.includes('ei')
    ) {
      const g = VIC_KB.grant[lang];
      return {
        text: `### 🎯 ${g.title}\n\n${g.summary}\n\n**${lang === 'zh' ? '申请资格要求' : 'Key Eligibility Criteria'}:**\n${g.eligibility}\n\n${g.help}`,
        actions: [
          { label: lang === 'zh' ? '📝 立即免费评估补助资格' : '📝 Check Grant Eligibility', action: 'consult', param: 'aid' },
          { label: lang === 'zh' ? '📞 致电顾问 (416-665-6668)' : '📞 Call Admissions (416-665-6668)', action: 'call', param: '4166656668' }
        ]
      };
    }

    // 2. PSW Program
    if (
      q.includes('psw') || q.includes('personal support') || q.includes('caregiver') || 
      q.includes('护工') || q.includes('护理') || q.includes('养老院')
    ) {
      const p = VIC_KB.programs.psw[lang];
      return {
        text: `### 🩺 ${p.name}\n\n${p.overview}\n\n⏱ **${lang === 'zh' ? '学制' : 'Duration'}:** ${p.duration}\n📜 **${lang === 'zh' ? '毕业证书' : 'Credential'}:** ${p.credential}\n💵 **${lang === 'zh' ? '薪资待遇' : 'Salary Range'}:** ${p.salary}\n\n⭐ **${lang === 'zh' ? '课程亮点' : 'Highlights'}:** ${p.highlights}`,
        actions: [
          { label: lang === 'zh' ? '🔍 查看 PSW 完整大纲与实习' : '🔍 View PSW Full Details', action: 'open_modal', param: 'psw' },
          { label: lang === 'zh' ? '📅 预约 PSW 升学咨询' : '📅 Book PSW Consultation', action: 'consult', param: 'psw' }
        ]
      };
    }

    // 3. Full Stack Web / IT / Computer / Coding
    if (
      q.includes('full stack') || q.includes('tech') || q.includes('code') || q.includes('coding') || 
      q.includes('java') || q.includes('react') || q.includes('developer') || q.includes('software') || q.includes('it') ||
      q.includes('全栈') || q.includes('网页开发') || q.includes('编程') || q.includes('软件') || q.includes('前端') || q.includes('后端')
    ) {
      const p = VIC_KB.programs.tech[lang];
      return {
        text: `### 💻 ${p.name}\n\n${p.overview}\n\n⏱ **${lang === 'zh' ? '学制' : 'Duration'}:** ${p.duration}\n📜 **${lang === 'zh' ? '毕业证书' : 'Credential'}:** ${p.credential}\n💵 **${lang === 'zh' ? '就业起薪' : 'Starting Salary'}:** ${p.salary}\n\n⭐ **${lang === 'zh' ? '核心技术栈' : 'Key Stack'}:** ${p.highlights}`,
        actions: [
          { label: lang === 'zh' ? '🔍 查看 Full Stack 完整大纲' : '🔍 View Full Stack Curriculum', action: 'open_modal', param: 'tech' },
          { label: lang === 'zh' ? '📅 预约 IT 课程咨询' : '📅 Book IT Consultation', action: 'consult', param: 'tech' }
        ]
      };
    }

    // 4. Accounting, Tax & Payroll
    if (
      q.includes('account') || q.includes('tax') || q.includes('payroll') || q.includes('bookkeep') || q.includes('cpa') ||
      q.includes('quickbooks') || q.includes('sage') ||
      q.includes('会计') || q.includes('报税') || q.includes('薪资') || q.includes('出纳') || q.includes('账房')
    ) {
      const p = VIC_KB.programs.accounting[lang];
      return {
        text: `### 📊 ${p.name}\n\n${p.overview}\n\n⏱ **${lang === 'zh' ? '学制' : 'Duration'}:** ${p.duration}\n📜 **${lang === 'zh' ? '毕业证书' : 'Credential'}:** ${p.credential}\n💵 **${lang === 'zh' ? '薪资前景' : 'Career Salary'}:** ${p.salary}\n\n⭐ **${lang === 'zh' ? '实操技能' : 'Software & Tools'}:** ${p.highlights}`,
        actions: [
          { label: lang === 'zh' ? '🔍 查看会计文凭大纲' : '🔍 View Accounting Curriculum', action: 'open_modal', param: 'accounting' },
          { label: lang === 'zh' ? '📅 预约会计课程规划' : '📅 Book Consultation', action: 'consult', param: 'accounting' }
        ]
      };
    }

    // 5. Early Childcare Assistant (ECA)
    if (
      q.includes('childcare') || q.includes('eca') || q.includes('daycare') || q.includes('kindergarten') ||
      q.includes('幼教') || q.includes('幼儿园') || q.includes('托儿') || q.includes('儿童')
    ) {
      const p = VIC_KB.programs.eca[lang];
      return {
        text: `### 👶 ${p.name}\n\n${p.overview}\n\n⏱ **${lang === 'zh' ? '学制' : 'Duration'}:** ${p.duration}\n📜 **${lang === 'zh' ? '毕业证书' : 'Credential'}:** ${p.credential}\n💵 **${lang === 'zh' ? '薪资水平' : 'Hourly Wage'}:** ${p.salary}\n\n⭐ **${lang === 'zh' ? '实训优势' : 'Practicum'}:** ${p.highlights}`,
        actions: [
          { label: lang === 'zh' ? '🔍 查看 ECA 幼教课程' : '🔍 View ECA Details', action: 'open_modal', param: 'eca' },
          { label: lang === 'zh' ? '📅 预约幼教升学咨询' : '📅 Book Consultation', action: 'consult', param: 'eca' }
        ]
      };
    }

    // 6. Electrician (309A / 442A)
    if (
      q.includes('electric') || q.includes('309a') || q.includes('442a') || q.includes('trades') || q.includes('license') ||
      q.includes('电工') || q.includes('考证') || q.includes('技工') || q.includes('配电')
    ) {
      const p = VIC_KB.programs.elec[lang];
      return {
        text: `### ⚡ ${p.name}\n\n${p.overview}\n\n⏱ **${lang === 'zh' ? '班型安排' : 'Schedule'}:** ${p.duration}\n📜 **${lang === 'zh' ? '证书方向' : 'Target Credential'}:** ${p.credential}\n💵 **${lang === 'zh' ? '持牌时薪' : 'Licensed Wage'}:** ${p.salary}\n\n⭐ **${lang === 'zh' ? '教学特色' : 'Course Features'}:** ${p.highlights}`,
        actions: [
          { label: lang === 'zh' ? '🔍 查看电工班实训详情' : '🔍 View Electrician Details', action: 'open_modal', param: 'electrician' },
          { label: lang === 'zh' ? '📅 预约电工名师咨询' : '📅 Inquire Electrician Prep', action: 'consult', param: 'electrician' }
        ]
      };
    }

    // 7. Acupuncture & Wellness
    if (
      q.includes('acupuncture') || q.includes('tcm') || q.includes('wellness') || q.includes('needle') ||
      q.includes('针灸') || q.includes('中医') || q.includes('经络') || q.includes('养生') || q.includes('艾灸')
    ) {
      const p = VIC_KB.programs.acu[lang];
      return {
        text: `### 🌿 ${p.name}\n\n${p.overview}\n\n⏱ **${lang === 'zh' ? '时间安排' : 'Schedule'}:** ${p.duration}\n📜 **${lang === 'zh' ? '结业证书' : 'Credential'}:** ${p.credential}\n\n⭐ **${lang === 'zh' ? '核心教学' : 'Key Modules'}:** ${p.highlights}`,
        actions: [
          { label: lang === 'zh' ? '🔍 查看针灸养生大纲' : '🔍 View Acupuncture Details', action: 'open_modal', param: 'acupuncture' },
          { label: lang === 'zh' ? '📅 预约课程试听' : '📅 Book Consultation', action: 'consult', param: 'acupuncture' }
        ]
      };
    }

    // 8. Campus, Location, Address, Phone, Hours
    if (
      q.includes('campus') || q.includes('location') || q.includes('address') || q.includes('where') || 
      q.includes('phone') || q.includes('call') || q.includes('email') || q.includes('hours') || q.includes('markham') || q.includes('north york') ||
      q.includes('校区') || q.includes('地址') || q.includes('在哪') || q.includes('电话') || q.includes('联系') || q.includes('万锦') || q.includes('北约克') || q.includes('营业时间')
    ) {
      const g = VIC_KB.general[lang];
      return {
        text: `### 🏫 ${lang === 'zh' ? '校区分布与联系方式' : 'Campus Locations & Contact'}\n\n${g.campuses}\n\n${g.contact}`,
        actions: [
          { label: lang === 'zh' ? '📍 浏览校区地图与详情' : '📍 View Campus Map & Info', action: 'scroll', param: 'campus' },
          { label: lang === 'zh' ? '📞 立即拨打电话' : '📞 Call 416-665-6668', action: 'call', param: '4166656668' }
        ]
      };
    }

    // 9. Booking Consultation / Admission / How to Apply
    if (
      q.includes('book') || q.includes('consult') || q.includes('apply') || q.includes('admission') || q.includes('register') || q.includes('enroll') ||
      q.includes('预约') || q.includes('咨询') || q.includes('申请') || q.includes('报名') || q.includes('怎么报') || q.includes('入学')
    ) {
      return {
        text: lang === 'zh' 
          ? `### 📅 预约 1对1 免费职业规划与升学评估\n\n我们的资深顾问将根据您的背景、兴趣及过往经历，为您：\n1. 量身定制紧缺高薪职业规划\n2. 免费评估安省政府最高 **$28,000+** 助学金资格\n3. 协助完成申请材料、简历梳理与实习对接`
          : `### 📅 Book Your Free 1-on-1 Career Consultation\n\nOur admissions specialists will analyze your background to:\n1. Recommend high-demand vocational pathways\n2. Check your eligibility for **up to $28,000+** in government grants\n3. Provide step-by-step application and practicum support`,
        actions: [
          { label: lang === 'zh' ? '📝 填写免费预约表单' : '📝 Open Consultation Form', action: 'scroll', param: 'consultation' },
          { label: lang === 'zh' ? '📞 直接致电 416-665-6668' : '📞 Direct Call 416-665-6668', action: 'call', param: '4166656668' }
        ]
      };
    }

    // 10. Tuition / Fee / Cost / Installments
    if (
      q.includes('tuition') || q.includes('fee') || q.includes('cost') || q.includes('price') || q.includes('how much') ||
      q.includes('学费') || q.includes('多少钱') || q.includes('费用') || q.includes('分期')
    ) {
      return {
        text: lang === 'zh'
          ? `### 💳 学费与资金支持\n\n• **政府资助 (Better Jobs Ontario)**：符合条件者可申请政府最高 **$28,000+** 全额资助，涵盖学费、生活补贴与书本费，**个人无需支付**。\n• **分期付款**：学院为自费学员提供 0 利息灵活月度分期付款计划与助学金。\n• **精准报价**：不同课程（如 PSW、全栈开发、会计）根据课时与认证有所差异。`
          : `### 💳 Tuition & Financial Solutions\n\n• **Government Grants (Better Jobs Ontario)**: Eligible candidates can receive up to **$28,000+** covering 100% of tuition, books, and living expenses with zero personal repayment.\n• **Flexible Installments**: Interest-free monthly installment plans and college scholarships available.\n• **Detailed Quote**: Specific fees vary by program (PSW, Full Stack, Accounting). Contact our admissions advisor for an accurate assessment.`,
        actions: [
          { label: lang === 'zh' ? '💰 免费评估政府学费资助' : '💰 Check Grant Eligibility', action: 'consult', param: 'aid' },
          { label: lang === 'zh' ? '📞 咨询学费与分期详情' : '📞 Inquire Tuition Options', action: 'call', param: '4166656668' }
        ]
      };
    }

    // 11. President / Leadership / History
    if (
      q.includes('president') || q.includes('maria sun') || q.includes('history') || q.includes('about') ||
      q.includes('校长') || q.includes('孙善勤') || q.includes('历史') || q.includes('简介') || q.includes('维多利亚')
    ) {
      const g = VIC_KB.general[lang];
      return {
        text: `### 🎓 ${lang === 'zh' ? '关于维多利亚职业学院' : 'About Victoria International College'}\n\n${g.intro}\n\n🌟 **${lang === 'zh' ? '领导团队' : 'Leadership'}:**\n${g.leadership}`,
        actions: [
          { label: lang === 'zh' ? '🏆 浏览所有高薪专业' : '🏆 Explore All Programs', action: 'scroll', param: 'programs' },
          { label: lang === 'zh' ? '📅 预约 1对1 咨询' : '📅 Book Free Consultation', action: 'scroll', param: 'consultation' }
        ]
      };
    }

    // Fallback: General helpful guidance
    return {
      text: lang === 'zh'
        ? `您好！我是维多利亚职业学院的智能升学顾问。我可以为您提供：\n\n• 💰 **政府补助评估**（最高可获 $28,000+ 免费学费与生活补贴）\n• 🩺 **热门专业文凭**（PSW 护工、全栈开发、会计税务、幼教、电工）\n• 🏫 **校区与联系方式**（万锦 & 北约克两大校区）\n• 📅 **1对1 职业规划预约**\n\n请问您对哪个专业或政府补助感兴趣？`
        : `Hello! I am your Victoria College AI Advisor. I can assist you with:\n\n• 💰 **Government Grants** (Up to $28,000+ for tuition & living allowances)\n• 🩺 **Career Programs** (PSW, Full Stack Web, Accounting & Tax, Early Childcare, Electrician)\n• 🏫 **Campus & Contact Info** (Markham & North York)\n• 📅 **1-on-1 Career Consultation Booking**\n\nWhich program or funding topic would you like to explore?`,
      actions: [
        { label: lang === 'zh' ? '💰 评估 $28,000 政府补助' : '💰 Check $28,000 Grant', action: 'consult', param: 'aid' },
        { label: lang === 'zh' ? '🩺 查看 PSW 护工专业' : '🩺 View PSW Program', action: 'open_modal', param: 'psw' },
        { label: lang === 'zh' ? '💻 查看 Full Stack IT' : '💻 View Full Stack Web', action: 'open_modal', param: 'tech' },
        { label: lang === 'zh' ? '📊 查看会计税务文凭' : '📊 View Accounting Diploma', action: 'open_modal', param: 'accounting' }
      ]
    };
  }

  // Detect query language (Chinese characters vs English)
  function detectLanguage(str) {
    if (/[\u4e00-\u9fa5]/.test(str)) {
      return 'zh';
    }
    const currentSiteLang = window.currentLanguage || localStorage.getItem('vic_lang');
    return currentSiteLang === 'zh' ? 'zh' : 'en';
  }

  // Format message text (Markdown bold, headers, lists, line breaks, and responsive DIV comparison cards)
  function formatMarkdown(rawText) {
    if (!rawText) return '';
    let html = rawText;

    // 1. Transform Markdown tables (| col1 | col2 |) into responsive DIV cards (No cramped tables)
    html = html.replace(/((?:\|[^\n]+\|\r?\n?)+)/g, (match) => {
      const lines = match.trim().split(/\r?\n/).filter(l => l.includes('|'));
      if (lines.length < 2) return match;

      const headerCells = lines[0].split('|').map(s => s.trim()).filter(s => s.length > 0);
      const dataLines = lines.slice(1).filter(l => !l.replace(/[\|\-\:\s]/g, '').length === 0 && !l.includes('---'));

      if (dataLines.length === 0) return match;

      let divHtml = '<div class="chat-compare-container">';
      dataLines.forEach((line, idx) => {
        const cells = line.split('|').map(s => s.trim()).filter(s => s.length > 0);
        if (cells.length > 0) {
          const isFirstCard = idx === 0 || (cells[0] && cells[0].toLowerCase().includes('bjo'));
          const cardClass = isFirstCard ? 'chat-compare-card card-bjo' : 'chat-compare-card card-osap';
          divHtml += `<div class="${cardClass}">`;
          cells.forEach((cell, cellIdx) => {
            const label = headerCells[cellIdx] || `Feature ${cellIdx + 1}`;
            divHtml += `
              <div class="chat-compare-field">
                <span class="chat-compare-label">${label}:</span>
                <span class="chat-compare-value">${cell}</span>
              </div>
            `;
          });
          divHtml += '</div>';
        }
      });
      divHtml += '</div>';
      return divHtml;
    });

    // 2. Transform any raw <table> HTML tags into responsive DIV cards
    html = html.replace(/<table[^>]*>([\s\S]*?)<\/table>/gi, (match, tableContent) => {
      let cleaned = tableContent
        .replace(/<thead[^>]*>[\s\S]*?<\/thead>/gi, '') // Remove redundant thead
        .replace(/<tr[^>]*>/gi, '<div class="chat-compare-card">')
        .replace(/<\/tr>/gi, '</div>')
        .replace(/<td[^>]*>/gi, '<div class="chat-compare-field"><span class="chat-compare-value">')
        .replace(/<\/td>/gi, '</span></div>')
        .replace(/<th[^>]*>/gi, '<div class="chat-compare-field"><span class="chat-compare-label">')
        .replace(/<\/th>/gi, '</span></div>');
      return `<div class="chat-compare-container">${cleaned}</div>`;
    });

    // 3. Headers ### Title
    html = html.replace(/^### (.*$)/gim, '<h4 class="chat-msg-heading">$1</h4>');
    html = html.replace(/^## (.*$)/gim, '<h3 class="chat-msg-heading">$1</h3>');

    // 4. Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // 5. Bullet points • or -
    html = html.replace(/^[•\-] (.*$)/gim, '<div class="chat-bullet"><span class="chat-bullet-dot">•</span> $1</div>');

    // 6. Newlines (Only outside comparison divs)
    html = html.replace(/\n\n/g, '<div class="chat-spacer"></div>');
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  // Append Message to DOM
  function appendMessage(msg) {
    const isUser = msg.role === 'user';
    const msgDiv = document.createElement('div');
    msgDiv.className = `vic-chat-msg vic-chat-msg-${isUser ? 'user' : 'bot'}`;

    let html = '';
    if (!isUser) {
      html += `
        <div class="vic-chat-bot-avatar">
          <i class="fa-solid fa-graduation-cap"></i>
        </div>
      `;
    }

    html += `<div class="vic-chat-bubble">`;
    html += formatMarkdown(msg.text);

    // Render action buttons if any
    if (msg.actions && msg.actions.length > 0) {
      html += `<div class="vic-chat-actions-group">`;
      msg.actions.forEach(act => {
        html += `
          <button type="button" class="vic-chat-action-btn" data-chat-action="${act.action}" data-chat-param="${act.param}">
            ${act.label}
          </button>
        `;
      });
      html += `</div>`;
    }

    // Time stamp
    const timeStr = new Date(msg.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    html += `<span class="vic-chat-time">${timeStr}</span>`;
    html += `</div>`;

    msgDiv.innerHTML = html;
    elements.messages.appendChild(msgDiv);

    chatHistory.push(msg);
  }

  // Handle Interactive Deep Action Clicks
  function handleChatAction(action, param) {
    if (action === 'auth') {
      if (window.VicAuth) window.VicAuth.openAuthModal(param || 'login');
    } else if (action === 'auth_google') {
      if (window.VicAuth) window.VicAuth.loginWithGoogle();
    } else if (action === 'auth_linkedin') {
      if (window.VicAuth) window.VicAuth.loginWithLinkedIn();
    } else if (action === 'open_modal') {
      if (typeof window.openProgramModal === 'function') {
        window.openProgramModal(param);
      } else {
        const modal = document.getElementById('program-modal');
        if (modal) modal.classList.add('active');
      }
    } else if (action === 'consult') {
      const formSection = document.getElementById('consultation');
      if (formSection) {
        formSection.scrollIntoView({ behavior: 'smooth' });
        const select = document.getElementById('consult-program');
        if (select && param !== 'aid') {
          select.value = param;
        }
        if (param === 'aid') {
          const aidCheck = document.getElementById('consult-grant-check');
          if (aidCheck) aidCheck.checked = true;
        }
      }
    } else if (action === 'scroll') {
      const target = document.getElementById(param);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    } else if (action === 'call') {
      window.location.href = `tel:${param}`;
    }
  }

  // Typing Indicator
  function showTypingIndicator() {
    isTyping = true;
    const typingDiv = document.createElement('div');
    typingDiv.id = 'vic-chat-typing';
    typingDiv.className = 'vic-chat-msg vic-chat-msg-bot typing-bubble';
    typingDiv.innerHTML = `
      <div class="vic-chat-bot-avatar">
        <i class="fa-solid fa-graduation-cap"></i>
      </div>
      <div class="vic-chat-bubble vic-typing-dots">
        <span></span><span></span><span></span>
      </div>
    `;
    elements.messages.appendChild(typingDiv);
    scrollToBottom();
  }

  function hideTypingIndicator() {
    isTyping = false;
    const typingDiv = document.getElementById('vic-chat-typing');
    if (typingDiv) typingDiv.remove();
  }

  function scrollToBottom() {
    if (elements.messages) {
      elements.messages.scrollTop = elements.messages.scrollHeight;
    }
  }

  // Storage and History
  function saveHistory() {
    try {
      localStorage.setItem('vic_chat_history', JSON.stringify(chatHistory.slice(-20)));
    } catch (e) {
      // ignore
    }
  }

  function loadHistory() {
    try {
      const saved = localStorage.getItem('vic_chat_history');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          chatHistory = [];
          elements.messages.innerHTML = '';
          parsed.forEach(msg => appendMessage(msg));
          scrollToBottom();
          return;
        }
      }
    } catch (e) {
      // ignore
    }

    // Default welcome message if empty
    renderInitialWelcome();
  }

  function renderInitialWelcome() {
    elements.messages.innerHTML = '';
    chatHistory = [];
    const lang = (window.currentLanguage || localStorage.getItem('vic_lang') || 'en');
    const token = window.VicAuth?.getToken();
    const user = window.VicAuth?.getUser();

    if (!token) {
      if (lang === 'zh') {
        appendMessage({
          role: 'bot',
          text: `### 🔒 维多利亚职业学院 • 智能升学顾问\n\n💡 **咨询范围：** 评估 **$28,000+ 政府助学金**、**PSW 护理 / IT 全栈 / 会计文凭** 及 **校区升学规划**。\n\n请先登录您的账号开启智能咨询：`,
          actions: [
            { label: '🔑 立即登录 / 注册账号', action: 'auth', param: 'login' },
            { label: '🌐 使用 Google 账号登录', action: 'auth_google', param: '' },
            { label: '💼 使用 LinkedIn 账号登录', action: 'auth_linkedin', param: '' }
          ],
          timestamp: new Date()
        });
      } else {
        appendMessage({
          role: 'bot',
          text: `### 🔒 Victoria College AI Career & Admissions Assistant\n\n💡 **Purpose:** Instant guidance on **$28,000+ Government Grants**, **PSW / IT / Business Diplomas**, and **campus admissions**.\n\nPlease sign in with your account to start chatting:`,
          actions: [
            { label: '🔑 Sign In / Register Account', action: 'auth', param: 'login' },
            { label: '🌐 Continue with Google', action: 'auth_google', param: '' },
            { label: '💼 Continue with LinkedIn', action: 'auth_linkedin', param: '' }
          ],
          timestamp: new Date()
        });
      }
    } else {
      const userName = user?.name ? user.name.split(' ')[0] : 'there';
      if (lang === 'zh') {
        appendMessage({
          role: 'bot',
          text: `### 👋 您好${user?.name ? '，' + user.name : ''}！欢迎咨询维多利亚职业学院\n\n💡 **咨询范围：** 快捷评估 **$28,000+ 政府助学金**、**PSW 护理 / IT 全栈 / 会计文凭** 及 **校区升学规划**。\n\n请在下方输入您想咨询的问题，或点击快捷推荐：`,
          actions: [
            { label: '💰 评估 $28,000 政府补助', action: 'consult', param: 'aid' },
            { label: '🩺 了解 PSW 护工专业', action: 'open_modal', param: 'psw' },
            { label: '💻 了解 Full Stack 全栈 IT', action: 'open_modal', param: 'tech' }
          ],
          timestamp: new Date()
        });
      } else {
        appendMessage({
          role: 'bot',
          text: `### 👋 Welcome back, ${userName}!\n\n💡 **Purpose:** Instant guidance on **$28,000+ Government Grants**, **PSW / IT / Accounting Diplomas**, and **campus admissions**.\n\nSelect a quick topic below or type your question:`,
          actions: [
            { label: '💰 Check $28,000 Grant', action: 'consult', param: 'aid' },
            { label: '🩺 Explore PSW Healthcare', action: 'open_modal', param: 'psw' },
            { label: '💻 Explore Full Stack Web', action: 'open_modal', param: 'tech' }
          ],
          timestamp: new Date()
        });
      }
    }

    scrollToBottom();
  }

  function clearHistory() {
    localStorage.removeItem('vic_chat_history');
    renderInitialWelcome();
  }

  // Public method to update language on site language switch
  window.updateChatbotLanguage = function(lang) {
    if (!elements.container) return;

    if (elements.tooltipText) {
      elements.tooltipText.textContent = lang === 'zh' ? '有疑问？问问 VIC 智能升学助手' : 'Have questions? Ask VIC AI Advisor';
    }
    if (elements.statusText) {
      elements.statusText.textContent = lang === 'zh' ? '维多利亚职业学院 • 智能问答系统' : 'Victoria College • Career & Grant Assistant';
    }
    if (elements.bannerText) {
      elements.bannerText.textContent = lang === 'zh' ? '💡 Better Jobs Ontario 政府资助最高可达 $28,000+' : '💡 Qualify for up to $28,000+ Government Training Grants';
    }
    if (elements.input) {
      elements.input.placeholder = lang === 'zh' ? '输入您的问题（如：PSW就业、政府补助、学费）...' : 'Ask about programs, grants, tuition, admissions...';
    }

    renderSuggestions();

    // If chat history only contains initial greeting, update it
    if (chatHistory.length <= 1) {
      renderInitialWelcome();
    }
  };

  // Expose initialization and control methods globally
  window.initVicChatbot = init;
  window.openVicChatbot = openChat;
  window.closeVicChatbot = closeChat;
  window.toggleVicChatbot = toggleChat;

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      init();
    });
  } else {
    init();
  }

})();

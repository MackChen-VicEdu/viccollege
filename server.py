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

AUTH_SALT = os.environ.get('AUTH_SALT', 'vic_college_salt_2026')

def hash_password(password: str) -> str:
    return hashlib.sha256((password + AUTH_SALT).encode('utf-8')).hexdigest()

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
                'psw, personal support worker, healthcare, nursing home, clinic, practicum placement, cpr, first aid, nacc, caregiving, hospital, medical',
                'The NACC Personal Support Worker (PSW) DE 2022 Certificate Program consists of intensive classroom theory and hands-on clinical practicum placement in top Ontario nursing homes and healthcare facilities. Graduates receive their NACC PSW Certificate, Standard First Aid & CPR Level C certification. High employment demand across hospitals, long-term care homes, and community healthcare with $20-$28/hr starting wage. Financial aid and Second Career grants are applicable.',
                2, now_str, now_str
            ),
            (
                'programs',
                'Full Stack Web Technician Diploma Program',
                'full stack, web development, software, programming, java, springboot, react, javascript, nodejs, aws, mysql, cloud, coding, developer, diploma',
                'The Full Stack Web Technician Diploma covers core & advanced Java, SpringBoot, Spring Cloud, React, Node.js, Webpack, MySQL, Netty, AWS Cloud deployment, and enterprise software engineering design patterns. Includes hands-on real-world capstone projects and resume/interview preparation for high-paying tech careers ($65k-$85k/yr) in Canada.',
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
                'Victoria International College Campuses, Addresses & Contact Info',
                'address, location, campus, phone, contact, email, markham, north york, hours, opening hours, directions, where are you located',
                'Victoria International College has two convenient Greater Toronto Area campuses:\n1) Markham Campus (Main): 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n2) North York Campus: 306 Consumers Rd., North York, ON M2J 1P8\nPhone: 416-665-6668 | Email: info@viccollege.com\nOpening Hours: Monday – Saturday: 9:00 AM – 6:00 PM.',
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
                "2026 Ontario PSW Job Demand & $28,000 Free Training Grants Guide (Toronto & North York)",
                "psw-training-grant-toronto-north-york",
                "Complete 2026 guide for Ontario residents seeking high-demand Personal Support Worker (PSW) certification with up to $28,000+ government funding in Toronto and North York.",
                """<h2>High Demand for Personal Support Workers in the Greater Toronto Area</h2>
<p>As Ontario's healthcare system expands to meet the needs of an aging population, the demand for certified <strong>Personal Support Workers (PSW)</strong> across Toronto, North York, Scarborough, and Markham has reached unprecedented levels. Hospitals, long-term care homes, and community healthcare agencies are actively recruiting qualified caregivers offering competitive wages from <strong>$20 to $28 per hour</strong>, complete benefit packages, and flexible shifts.</p>

<h3>How to Access Up to $28,000+ in Better Jobs Ontario Funding</h3>
<p>Through the Ontario provincial government's <em>Better Jobs Ontario</em> (formerly Second Career) program, eligible residents can receive non-repayable grants covering:</p>
<ul>
  <li><strong>100% Tuition & Exam Fees</strong> for the accredited NACC PSW DE 2022 Certificate program</li>
  <li><strong>Required Medical Textbooks, Scrubs & Clinical Supplies</strong></li>
  <li><strong>Monthly Transportation & Childcare Allowances</strong></li>
  <li><strong>Basic Living Allowance Support</strong> during your 30 weeks of training</li>
</ul>

<blockquote>
  <p><strong>Did You Know?</strong> Victoria International College provides 100% complimentary step-by-step grant evaluation and document submission assistance for all prospective students.</p>
</blockquote>

<h3>Hands-on Clinical Practicum in Top Ontario Facilities</h3>
<p>Our comprehensive 30-week program includes standard classroom theory, simulation lab practice at our North York and Markham campuses, and <strong>300+ hours of guaranteed clinical placement</strong> in leading long-term care facilities. Graduates receive both the NACC PSW Certificate and Standard First Aid & CPR Level C credentials.</p>

<h3>North York & Markham Campus Locations</h3>
<p>Conveniently accessible by TTC and YRT transit:</p>
<ul>
  <li><strong>North York Campus:</strong> 306 Consumers Rd., North York, ON M2J 1P8 (Near Victoria Park & Sheppard)</li>
  <li><strong>Markham Main Campus:</strong> 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8 (Near Steeles & Woodbine)</li>
</ul>

<div class="article-cta-box" style="margin-top: 30px; padding: 24px; background: linear-gradient(135deg, #8B0000 0%, #B22222 100%); color: #fff; border-radius: 12px; text-align: center;">
  <h3 style="color: #fff; margin-bottom: 10px;">Ready to Start Your High-Paying Healthcare Career?</h3>
  <p style="color: #ffd2d2; margin-bottom: 18px;">Book a free consultation with our senior admissions advisors to evaluate your grant eligibility today.</p>
  <a href="/#consultation" class="btn-vic-red" style="background: #fff; color: #8B0000; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-decoration: none; display: inline-block;">Book Free Consultation • Call 416-665-6668</a>
</div>""",
                "healthcare",
                "psw training toronto, better jobs ontario psw, nacc psw certificate, free psw grant markham, healthcare careers ontario",
                "Toronto & North York, Ontario",
                43.7758,
                -79.3458,
                "images/news_1.jpg",
                "active",
                1,
                "Victoria College Editorial",
                "Ontario PSW Training & $28,000 Government Grants Guide 2026 | Victoria College",
                "Learn how to qualify for up to $28,000+ in Ontario government grants for NACC PSW training in Toronto & North York. Free tuition and guaranteed clinical placement.",
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
   - NACC Personal Support Worker (PSW DE 2022): 30 weeks, clinical practicum (300+ hrs), $20-$28/hr starting wage.
   - Full Stack Web Technician: 32 weeks, Java, Spring Boot 3, React, TypeScript, AWS, $65k-$85k/yr.
   - Accounting, Tax and Payroll Administration: 30 weeks, QuickBooks, Sage 50, Canadian T1/T2 tax, CPA mentorship.
   - Early Childcare Assistant (ECA): 28 weeks, child psychology, daycare practicum.
   - Electrician 309A / 442A: Canadian Electrical Code (CEC) exam prep, hands-on wiring labs, $35-$55+/hr.
   - Acupuncture & Wellness: TCM meridian theory, holistic health.
3. Campuses:
   - Markham Campus: 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8
   - North York Campus: 306 Consumers Rd., North York, ON M2J 1P8
   - Phone: 416-665-6668 | Email: info@viccollege.com
4. Support both English and Chinese fluently. Format responses with clean bullet points and markdown headers."""
    }

    for k, v in default_settings.items():
        cursor.execute("SELECT key FROM settings WHERE key = ?", (k,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)", (k, v, now_str))

    cursor.execute("UPDATE settings SET value = 'true' WHERE key = 'require_login'")

    # 7. Homepage Sections Table (Dynamic CMS)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS homepage_sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_key TEXT UNIQUE NOT NULL,
        section_name TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        title_en TEXT,
        title_zh TEXT,
        subtitle_en TEXT,
        subtitle_zh TEXT,
        badge_en TEXT,
        badge_zh TEXT,
        content_en TEXT,
        content_zh TEXT,
        cta_text_en TEXT,
        cta_text_zh TEXT,
        cta_link TEXT,
        image_url TEXT,
        order_index INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    cursor.execute("SELECT COUNT(*) as cnt FROM homepage_sections")
    hs_row = cursor.fetchone()
    hs_count = hs_row['cnt'] if hs_row else 0
    if hs_count == 0:
        initial_sections = [
            (
                'hero',
                'Hero Banner & Main Headline',
                'hero',
                'Job ready training for careers in-demand',
                '高薪紧缺职业培训 助您开启辉煌未来',
                'Secure A High-Paying Second Career Without Spending Your Own Money. Highest grant amounts available, check with us.',
                '零自费开启高薪第二职业，最高可获政府 $28,000+ 免费学费与生活补贴，全程 1对1 免费规划与申请。',
                'Ontario Registered Career College • 22+ Years of Excellence',
                '安省正规注册私立职业学院 • 22年卓越办学历程',
                '<p>Join thousands of successful graduates who transitioned into top Canadian healthcare, technology, and accounting roles with full government grant assistance.</p>',
                '<p>维多利亚职业学院累计助力逾 15,000 名学员成功转行，进入大多伦多地区医疗护理、IT大厂与会计事务所工作，提供全程 100% 免费助学金评估与文凭培训。</p>',
                'Begin your future today, book consultation',
                '立即预约 1对1 免费职业规划与评估',
                '#consultation',
                'images/home_banner.jpg',
                1, 1, now_str, now_str
            ),
            (
                'hero_strip',
                'Hero 3-Card Category Highlights',
                'programs',
                'Top Career Training Categories',
                '三大核心高薪热门专业方向',
                'Healthcare, Business, and Technology fast-track diplomas designed for immediate employment',
                '涵盖医疗护理、会计财税、全栈 IT 开发等安省紧缺文凭，配备实战机房与实地实习',
                'FEATURED PATHWAYS',
                '核心专业',
                '',
                '',
                'Explore Programs',
                '浏览所有专业',
                '#programs',
                '',
                2, 1, now_str, now_str
            ),
            (
                'job_fair',
                'In-Person PSW Job Fair & Event Banner',
                'banner',
                'IN-PERSON PSW JOB FAIR',
                '大型线下 PSW 护工专场招聘会',
                'Connect with employers, find jobs • Friday, 12 May | 10:00AM – 12:00PM • 306 Consumers Rd. North York',
                '名企雇主现场直聘，直通高薪岗位 • 周五 5月12日 10:00AM – 12:00PM • 北约克校区 306 Consumers Rd.',
                'EXCLUSIVE EVENT',
                '重磅就业活动',
                '<p>Meet directly with hiring managers from top long-term care facilities, retirement homes, and healthcare agencies across the GTA. Bring your resume!</p>',
                '<p>大多伦多地区顶级持牌长期护理院、西人养老机构及医疗中介机构 HR 亲临现场直招，现场面试签约，毕业即就业！</p>',
                'Secure Your Spot',
                '立即抢占名额',
                '#consultation',
                'images/job-fair.png',
                3, 1, now_str, now_str
            ),
            (
                'value_props',
                'Why Choose Victoria College (3 Value Props)',
                'about',
                'Why Victoria International College',
                '为什么选择维多利亚职业学院',
                'Complimentary Assistant • Meet Your Career Needs • Practical Internship Placements',
                '全程免费助学金规划 • 紧扣市场紧缺需求 • 名企实地实习与就业推荐',
                'WHY CHOOSE US',
                '学院优势',
                '<p>With over 22 years of educational excellence, accredited simulation labs, and certified CPA and Nursing faculty, we ensure you achieve lasting career success.</p>',
                '<p>深耕加拿大职业教育 22 载，标准病房与机房实训，持牌资深导师手把手教学，全方位简历面试指导与企业内推。</p>',
                'Learn More About Us',
                '了解更多学院优势',
                '#about',
                '',
                4, 1, now_str, now_str
            ),
            (
                'free_class',
                'Join Our Free Class / Trial Registration',
                'admissions',
                'Join Our Free Class',
                '免费试听公开课与升学评估',
                'Jump-start your career today with free consultations and demo classes',
                '名师面对面指导，免费体验高质量实战教学与个性化升学辅导',
                'FREE WORKSHOPS',
                '免费公开课',
                '<p>Experience our live teaching sessions for PSW healthcare, Full Stack Java development, and Canadian tax returns. No obligation!</p>',
                '<p>免费试听 PSW 护理实操、全栈编程开发及个人与公司报税真账实操课，提前了解就业前景与学习路径。</p>',
                'Sign up',
                '立即预约试听',
                '#free-class-form',
                '',
                5, 1, now_str, now_str
            ),
            (
                'financial_aid',
                'Financial Aid & Better Jobs Ontario Guide',
                'aid',
                'Study With Zero Financial Burden',
                '零经济负担 开启安省政府全额资助培训',
                'Did you know you could qualify for government funding of up to $28,000+ for tuition and living allowances?',
                '您知道您可能符合资格申请最高 $28,000+ 加币全额政府无偿资助吗？涵盖 100% 学费、书本与生活津贴！',
                'Government Assistance',
                '安省政府助学金',
                '<p>Our experienced financial advisors provide 100% complimentary step-by-step assistance in navigating Better Jobs Ontario (formerly Second Career) applications.</p>',
                '<p>维多利亚职业学院资深助学金顾问团队为您提供一对一精准评估、材料准备及申请辅导，助您轻松获批政府助学金。</p>',
                'Free Grant Assessment',
                '免费评估助学金资格',
                '#consultation',
                '',
                6, 1, now_str, now_str
            ),
            (
                'president_msg',
                'President Maria Sun Welcome Message',
                'about',
                'Welcome to Victoria International College',
                '维多利亚职业学院 孙善勤校长致辞',
                'Empowering over 15,000 graduates to achieve rewarding Canadian careers',
                '22年砥砺前行，累计助力逾 15,000 名学员成功斩获加拿大本地高薪职业文凭与名企 Offer',
                '22+ YEARS OF EXCELLENCE',
                '校长寄语',
                '<p>At Victoria College, our mission has always been singular: empowering individuals with real-world, high-demand skills that lead directly to meaningful employment and career transformation in Canada.</p>',
                '<p>维多利亚学院始终秉持“实战实用、注重就业”的办学宗旨。无论您是初到加拿大的新移民，还是寻求职业突破的职场人士，我们都将是您最坚实的后盾！</p>',
                'Explore Programs',
                '了解热门课程',
                '#programs',
                'images/president_maria_sun.jpg',
                7, 1, now_str, now_str
            ),
            (
                'campuses',
                'Markham & North York Campus Locations',
                'campuses',
                'Our Campuses Across the GTA',
                '大多伦多地区两大核心校区',
                'Markham Main Campus: 7050 Woodbine Ave. • North York Campus: 306 Consumers Rd.',
                '万锦主校区：7050 Woodbine Ave. • 北约克校区：306 Consumers Rd.',
                'CAMPUS LOCATIONS',
                '校区地址',
                '<p>Both campuses feature modern multimedia lecture rooms, computer labs, and clinical nursing simulation labs with convenient TTC & YRT transit access.</p>',
                '<p>两大校区均配备先进多媒体教室、高配电脑实训机房及标准医疗护理模拟实验室，交通便利，停车位充裕。</p>',
                'Contact Campus',
                '联系校区顾问',
                '#contact',
                '',
                8, 1, now_str, now_str
            )
        ]
        cursor.executemany('''
        INSERT INTO homepage_sections (
            section_key, section_name, category, title_en, title_zh,
            subtitle_en, subtitle_zh, badge_en, badge_zh, content_en, content_zh,
            cta_text_en, cta_text_zh, cta_link, image_url, order_index, is_active,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', initial_sections)
        print(f">> Seeded {len(initial_sections)} Dynamic Homepage Sections into SQLite DB.")

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

    if user['password_hash'] != hash_password(password):
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
            response_text = f"{top_match['content']}\n\n💡 *For detailed admissions planning or grant eligibility assessment, please contact Victoria College at 416-665-6668 or book a consultation on our website.*"
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
      <span class="chat-compare-value">快速职业大专文凭 (30-32周，如 PSW 护工、全栈 IT、会计税务)</span>
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
      <span class="chat-compare-value">Fast-track career diplomas (30-32 weeks, PSW, IT, Accounting)</span>
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
        return "### 🩺 NACC Personal Support Worker (PSW DE 2022)\n\n• **学制：** 30 周（包含 300+ 小时持牌长期护理院临床实地实习）\n• **毕业证书：** NACC PSW 官方文凭 + CPR/AED 急救证书\n• **薪资待遇：** 起薪时薪 $20 – $28 加元/小时\n• **亮点：** 安省持牌资深护士带教，配备标准病房模拟实验室，毕业直接对接西人养老机构就业。" if is_zh else "### 🩺 NACC Personal Support Worker (PSW DE 2022)\n\n• **Duration:** 30 Weeks (Includes 300+ hours clinical practicum)\n• **Credential:** NACC PSW Diploma + CPR & First Aid Certification\n• **Salary:** $20 – $28 / hour with strong demand across Ontario\n• **Highlights:** Fully accredited, hands-on simulation labs, and direct placement in top healthcare facilities."

    if any(k in q for k in ['tech', 'full stack', 'web', 'code', 'java', 'react', 'developer', '全栈', '编程', '前端', '后端', '软件']):
        return "### 💻 Full Stack Web Technician (全栈开发文凭)\n\n• **学制：** 32 周（高强度实战机房 + 商业级微服务大项目）\n• **技术栈：** Java, Spring Boot 3, React, TypeScript, AWS 云原生, Docker, MySQL, Redis\n• **起薪前景：** 加拿大毕业起薪 $65,000 – $85,000 加元/年\n• **就业支持：** 名师辅导 LeetCode 刷题与大厂模拟面试，直通金融与科技名企。" if is_zh else "### 💻 Full Stack Web Technician Diploma\n\n• **Duration:** 32 Weeks (Live Projects + Intensive Labs)\n• **Stack:** Core Java, Spring Boot 3, React, TypeScript, AWS Cloud, Docker, MySQL\n• **Starting Salary:** $65,000 – $85,000 / year in Canadian tech & banking sectors\n• **Support:** 1-on-1 resume polish, LeetCode algorithms, and mock interview coaching."

    if any(k in q for k in ['account', 'tax', 'payroll', 'bookkeep', 'cpa', '会计', '报税', '薪资']):
        return "### 📊 Accounting, Tax and Payroll Administration (会计与税务文凭)\n\n• **学制：** 30 周（资深持牌 CPA 亲授 + 真账实训）\n• **软件技能：** QuickBooks Desktop/Online, Sage 50, Profile, TaxPrep, Advanced Excel\n• **核心业务：** 全流程记账、加拿大个人税 (T1) 与公司税 (T2)、CRA 工资税 (CPP, EI, T4)\n• **薪资待遇：** 起薪 $48,000 – $65,000 加元/年，稳健白领晋升路径。" if is_zh else "### 📊 Accounting, Tax & Payroll Administration\n\n• **Duration:** 30 Weeks (Hands-on corporate accounting software)\n• **Software:** QuickBooks Desktop/Online, Sage 50, Profile, TaxPrep, Excel\n• **Core Skills:** Full-cycle bookkeeping, Canadian T1/T2 tax returns, CRA payroll filings\n• **Salary:** $48,000 – $65,000 / year with clear progression to CPA designation."

    if any(k in q for k in ['campus', 'location', 'address', 'where', 'phone', '校区', '地址', '电话', '万锦', '北约克']):
        return "### 🏫 校区地址与联系电话\n\n📍 **万锦主校区 (Markham Campus):**\n7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n\n📍 **北约克校区 (North York Campus):**\n306 Consumers Rd., North York, ON M2J 1P8\n\n📞 咨询电话：416-665-6668\n🕒 办公时间：周一至周六 9:00 AM – 6:00 PM" if is_zh else "### 🏫 Campus Locations & Contact Info\n\n📍 **Markham Main Campus:**\n7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n\n📍 **North York Campus:**\n306 Consumers Rd., North York, ON M2J 1P8\n\n📞 Phone: 416-665-6668\n🕒 Hours: Monday – Saturday, 9:00 AM – 6:00 PM"

    return "您好！我是维多利亚职业学院智能升学顾问。请问您想咨询哪一方面？\n\n• 💰 **政府最高 $28,000+ 免费培训助学金**\n• 🩺 **PSW 护工、全栈开发、会计税务、幼教、电工** 热门高薪专业\n• 🏫 **万锦与北约克校区信息及预约规划**" if is_zh else "Hello! I am your Victoria College AI Advisor. How can I help you today?\n\n• 💰 **Better Jobs Ontario ($28,000+ Government Grants)**\n• 🩺 **Diplomas in PSW Healthcare, Full Stack Web, Accounting, Early Childcare, Electrician**\n• 🏫 **Markham & North York Campus Details & Free Consultation Booking**"


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

    cursor.execute("SELECT COUNT(*) as total_sec FROM homepage_sections")
    total_sec = cursor.fetchone()['total_sec']

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
        'homepage_sections': total_sec,
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
<p>学院两大校区交通极为便利，TTC 与 YRT 直达：</p>
<ul>
  <li><strong>万锦主校区 (Markham Campus)：</strong> 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8 (Woodbine & Steeles)</li>
  <li><strong>北约克校区 (North York Campus)：</strong> 306 Consumers Rd., North York, ON M2J 1P8 (Victoria Park & Sheppard)</li>
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
  <li><strong>Modern Simulation Ward Labs:</strong> Master patient mobility, infection control, vital signs, and compassionate care on-campus in Markham and North York.</li>
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

<h3>4. Campus Locations & Contact Information</h3>
<ul>
  <li><strong>Markham Main Campus:</strong> 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8</li>
  <li><strong>North York Campus:</strong> 306 Consumers Rd., North York, ON M2J 1P8</li>
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
  <li>🩺 <strong>NACC Personal Support Worker (PSW DE 2022) 医疗护工文凭</strong>（30周，高薪紧缺）</li>
  <li>💻 <strong>Full Stack Web Technician 全栈开发技术员文凭</strong>（32周，起薪 $65k-$85k）</li>
  <li>📊 <strong>Accounting, Tax and Payroll 会计与税务管理文凭</strong>（30周，CPA 带教）</li>
  <li>👶 <strong>Early Childcare Assistant (ECA) 幼教助理文凭</strong>（28周，持牌托儿所实习）</li>
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
  <li>🩺 <strong>NACC Personal Support Worker (PSW DE 2022):</strong> 30 weeks with guaranteed clinical practicum.</li>
  <li>💻 <strong>Full Stack Web Technician:</strong> 32 weeks, Java, React, TypeScript, AWS cloud.</li>
  <li>📊 <strong>Accounting, Tax and Payroll Administration:</strong> 30 weeks with CPA mentorship.</li>
  <li>👶 <strong>Early Childcare Assistant (ECA):</strong> 28 weeks with licensed daycare placement.</li>
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
  "content": "Rich HTML content with <h2>, <h3>, <p>, <ul>, <li>, <blockquote>, wage facts ($20-$28/hr for PSW, $65k-$85k for IT, $48k-$65k for Accounting), Better Jobs Ontario grants up to $28,000+, Markham/North York campus addresses, and a closing CTA consultation box with phone 416-665-6668.",
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
# Dynamic Homepage Content Management (CMS) APIs
# ==============================================================================

@app.route('/api/homepage/sections', methods=['GET'])
def public_get_homepage_sections():
    """
    Public API: Returns all ACTIVE homepage sections for dynamic rendering.
    Ordered by order_index ASC.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT * FROM homepage_sections 
        WHERE is_active = 1 
        ORDER BY order_index ASC, id ASC
    """)
    sections = [dict(row) for row in cursor.fetchall()]
    return jsonify({
        'sections': sections,
        'count': len(sections)
    })

@app.route('/api/admin/homepage/sections', methods=['GET'])
def admin_get_homepage_sections():
    """Admin API: List all homepage sections with stats and filter."""
    err = require_admin()
    if err: return err

    category = request.args.get('category', '').strip().lower()
    search = request.args.get('search', '').strip().lower()

    query = "SELECT * FROM homepage_sections WHERE 1=1"
    params = []

    if category and category != 'all':
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (LOWER(section_name) LIKE ? OR LOWER(section_key) LIKE ? OR LOWER(title_en) LIKE ? OR LOWER(title_zh) LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY order_index ASC, id ASC"

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    sections = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) as total FROM homepage_sections")
    total_cnt = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as active_cnt FROM homepage_sections WHERE is_active = 1")
    active_cnt = cursor.fetchone()['active_cnt']
    cursor.execute("SELECT COUNT(*) as hidden_cnt FROM homepage_sections WHERE is_active = 0")
    hidden_cnt = cursor.fetchone()['hidden_cnt']

    return jsonify({
        'sections': sections,
        'count': len(sections),
        'stats': {
            'total': total_cnt,
            'active': active_cnt,
            'hidden': hidden_cnt
        }
    })

@app.route('/api/admin/homepage/sections/<int:sec_id>', methods=['GET'])
def admin_get_homepage_section(sec_id):
    """Admin API: Get single section by ID."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM homepage_sections WHERE id = ?", (sec_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Homepage section not found.'}), 404

    return jsonify({'section': dict(row)})

@app.route('/api/admin/homepage/sections', methods=['POST'])
def admin_create_homepage_section():
    """Admin API: Create a new dynamic homepage section or announcement banner."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    section_name = (data.get('section_name') or '').strip()
    section_key = (data.get('section_key') or '').strip().lower()
    category = (data.get('category') or 'custom').strip().lower()

    if not section_name:
        return jsonify({'error': 'Section Name is required.'}), 400

    if not section_key:
        section_key = slugify(section_name)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM homepage_sections WHERE section_key = ?", (section_key,))
    if cursor.fetchone():
        section_key = f"{section_key}-{int(time.time())}"

    title_en = (data.get('title_en') or '').strip()
    title_zh = (data.get('title_zh') or '').strip()
    subtitle_en = (data.get('subtitle_en') or '').strip()
    subtitle_zh = (data.get('subtitle_zh') or '').strip()
    badge_en = (data.get('badge_en') or '').strip()
    badge_zh = (data.get('badge_zh') or '').strip()
    content_en = (data.get('content_en') or '').strip()
    content_zh = (data.get('content_zh') or '').strip()
    cta_text_en = (data.get('cta_text_en') or '').strip()
    cta_text_zh = (data.get('cta_text_zh') or '').strip()
    cta_link = (data.get('cta_link') or '').strip()
    image_url = (data.get('image_url') or '').strip()
    order_index = int(data.get('order_index') or 99)
    is_active = 1 if data.get('is_active') in [1, True, '1', 'true'] else 0

    now_str = datetime.utcnow().isoformat()

    cursor.execute('''
    INSERT INTO homepage_sections (
        section_key, section_name, category, title_en, title_zh,
        subtitle_en, subtitle_zh, badge_en, badge_zh, content_en, content_zh,
        cta_text_en, cta_text_zh, cta_link, image_url, order_index, is_active,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        section_key, section_name, category, title_en, title_zh,
        subtitle_en, subtitle_zh, badge_en, badge_zh, content_en, content_zh,
        cta_text_en, cta_text_zh, cta_link, image_url, order_index, is_active,
        now_str, now_str
    ))
    db.commit()

    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM homepage_sections WHERE id = ?", (new_id,))
    new_section = dict(cursor.fetchone())

    return jsonify({
        'success': True,
        'id': new_id,
        'message': f'Homepage section "{section_name}" created successfully.',
        'section': new_section
    }), 201

@app.route('/api/admin/homepage/sections/<int:sec_id>', methods=['PUT'])
def admin_update_homepage_section(sec_id):
    """Admin API: Update an existing homepage section."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM homepage_sections WHERE id = ?", (sec_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Homepage section not found.'}), 404

    data = request.get_json() or {}
    updates = []
    params = []

    fields = [
        'section_name', 'category', 'title_en', 'title_zh',
        'subtitle_en', 'subtitle_zh', 'badge_en', 'badge_zh',
        'content_en', 'content_zh', 'cta_text_en', 'cta_text_zh',
        'cta_link', 'image_url'
    ]

    for f in fields:
        if f in data and data[f] is not None:
            updates.append(f"{f} = ?")
            params.append(str(data[f]).strip())

    if 'section_key' in data and data['section_key']:
        new_key = data['section_key'].strip().lower()
        cursor.execute("SELECT id FROM homepage_sections WHERE section_key = ? AND id != ?", (new_key, sec_id))
        if cursor.fetchone():
            new_key = f"{new_key}-{int(time.time())}"
        updates.append("section_key = ?")
        params.append(new_key)

    if 'order_index' in data and data['order_index'] is not None:
        updates.append("order_index = ?")
        params.append(int(data['order_index']))

    if 'is_active' in data and data['is_active'] is not None:
        updates.append("is_active = ?")
        params.append(1 if data['is_active'] in [1, True, '1', 'true'] else 0)

    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(sec_id)
        query = f"UPDATE homepage_sections SET {', '.join(updates)} WHERE id = ?"
        db.execute(query, params)
        db.commit()

    cursor.execute("SELECT * FROM homepage_sections WHERE id = ?", (sec_id,))
    updated_section = dict(cursor.fetchone())

    return jsonify({
        'success': True,
        'message': 'Homepage section updated successfully.',
        'section': updated_section
    })

@app.route('/api/admin/homepage/sections/<int:sec_id>/toggle', methods=['PATCH'])
def admin_toggle_homepage_section(sec_id):
    """Admin API: 1-click active/hidden toggle for a section."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, section_name, is_active FROM homepage_sections WHERE id = ?", (sec_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Homepage section not found.'}), 404

    new_active = 0 if row['is_active'] == 1 else 1
    now_str = datetime.utcnow().isoformat()
    db.execute("UPDATE homepage_sections SET is_active = ?, updated_at = ? WHERE id = ?", (new_active, now_str, sec_id))
    db.commit()

    msg = f'Section "{row["section_name"]}" is now ACTIVE (visible on home page).' if new_active == 1 else f'Section "{row["section_name"]}" is now HIDDEN.'

    return jsonify({
        'success': True,
        'is_active': new_active,
        'message': msg
    })

@app.route('/api/admin/homepage/sections/<int:sec_id>', methods=['DELETE'])
def admin_delete_homepage_section(sec_id):
    """Admin API: Delete a homepage section."""
    err = require_admin()
    if err: return err

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, section_name FROM homepage_sections WHERE id = ?", (sec_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Homepage section not found.'}), 404

    db.execute("DELETE FROM homepage_sections WHERE id = ?", (sec_id,))
    db.commit()

    return jsonify({
        'success': True,
        'message': f'Homepage section "{row["section_name"]}" deleted.'
    })

@app.route('/api/admin/homepage/sections/reorder', methods=['POST'])
def admin_reorder_homepage_sections():
    """Admin API: Reorder multiple sections in batch."""
    err = require_admin()
    if err: return err

    data = request.get_json() or {}
    orders = data.get('orders') or [] # list of {'id': int, 'order_index': int}

    if not isinstance(orders, list):
        return jsonify({'error': 'Invalid orders format.'}), 400

    db = get_db()
    now_str = datetime.utcnow().isoformat()
    for item in orders:
        if isinstance(item, dict) and 'id' in item and 'order_index' in item:
            db.execute("UPDATE homepage_sections SET order_index = ?, updated_at = ? WHERE id = ?", (int(item['order_index']), now_str, int(item['id'])))

    db.commit()
    return jsonify({
        'success': True,
        'message': 'Section display order updated successfully.'
    })


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

@app.route('/<path:path>')
def serve_static(path):
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

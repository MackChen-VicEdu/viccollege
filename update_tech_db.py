import sqlite3
import json
from server import get_default_tech_detail_en, get_default_tech_detail_zh, DB_PATH

def update_tech_in_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    detail_en = json.dumps(get_default_tech_detail_en(), ensure_ascii=False)
    detail_zh = json.dumps(get_default_tech_detail_zh(), ensure_ascii=False)
    
    modules_en = json.dumps([
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
    ], ensure_ascii=False)
    
    modules_zh = json.dumps([
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
    ], ensure_ascii=False)
    
    cursor.execute("""
    UPDATE programs
    SET detail_json_en = ?,
        detail_json_zh = ?,
        modules_en = ?,
        modules_zh = ?,
        badge_en = 'Career Diploma • AI Mini-Credential',
        badge_zh = '加国紧缺高薪 IT 职业文凭 • 含 AI 微证书',
        duration_en = '32 Weeks (Intensive Labs + Commercial Projects)',
        duration_zh = '32 周（高强度实战机房 + 商业级项目交付）',
        credential_en = 'Full Stack Web Technician Diploma + AI Mini-Credential',
        credential_zh = '安省教育部认证 Full Stack Web Technician 职业文凭 + AI 微证书'
    WHERE slug = 'tech'
    """, (detail_en, detail_zh, modules_en, modules_zh))
    
    conn.commit()
    print(f"Updated tech program in DB. Rows affected: {cursor.rowcount}")
    conn.close()

if __name__ == '__main__':
    update_tech_in_db()

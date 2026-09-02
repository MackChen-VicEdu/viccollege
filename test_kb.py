import requests
import json
import time

BASE_URL = "http://localhost:5055"

def run_kb_tests():
    print("\n=======================================================")
    print(" Running Knowledge Base Database & Local-First AI Tests")
    print("=======================================================\n")

    # 1. Login as Super Admin (Mack Chen)
    login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "mack.chen@viccollege.com",
        "password": "Admin@123456"
    })
    assert login_res.status_code == 200, f"Super admin login failed: {login_res.text}"
    admin_token = login_res.json()['token']
    auth_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] 1. Super Admin Authentication: SUCCESS")

    # 2. Verify Stats includes Knowledge Articles Count
    stats_res = requests.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats.get('knowledge_articles', 0) >= 11, f"Expected at least 11 KB articles, got {stats.get('knowledge_articles')}"
    print(f"[PASS] 2. Admin Statistics: {stats['knowledge_articles']} Knowledge Articles Active in SQLite DB")

    # 3. Retrieve All Knowledge Articles
    kb_res = requests.get(f"{BASE_URL}/api/admin/knowledge", headers=auth_headers)
    assert kb_res.status_code == 200
    kb_data = kb_res.json()
    articles = kb_data['articles']
    assert len(articles) >= 11
    print(f"[PASS] 3. Knowledge Base List Retrieval: {len(articles)} articles found")

    # 4. Create New Knowledge Base Article (CRUD: Create)
    new_art_res = requests.post(f"{BASE_URL}/api/admin/knowledge", headers=auth_headers, json={
        "title": "Co-op & Career Placement Guarantee QA",
        "category": "admissions",
        "priority": 2,
        "keywords": "co-op, career placement, job guarantee, hiring, internship, qa",
        "content": "Victoria College partners with over 150+ Canadian employers to guarantee structured practicum and resume referrals for all diploma students."
    })
    assert new_art_res.status_code == 200
    new_art_id = new_art_res.json()['id']
    print(f"[PASS] 4. Admin Knowledge Article Creation: Created Article ID {new_art_id}")

    # 5. Update Knowledge Base Article (CRUD: Update)
    update_res = requests.put(f"{BASE_URL}/api/admin/knowledge/{new_art_id}", headers=auth_headers, json={
        "title": "Co-op & Career Placement Guarantee (Updated)",
        "priority": 3
    })
    assert update_res.status_code == 200
    print(f"[PASS] 5. Admin Knowledge Article Update: Successfully updated ID {new_art_id}")

    # 6. Test Query Search Scoring Endpoint
    test_query_res = requests.post(f"{BASE_URL}/api/admin/knowledge/test-query", headers=auth_headers, json={
        "query": "How much grant money can I get for second career in Ontario?"
    })
    if test_query_res.status_code != 200:
        print(f"FAILED Step 6: Status={test_query_res.status_code}, Text={test_query_res.text}")
    assert test_query_res.status_code == 200, f"Status: {test_query_res.status_code}, Text: {test_query_res.text}"
    tq_data = test_query_res.json()
    assert len(tq_data['matches']) > 0
    top_match = tq_data['matches'][0]
    print(f"[PASS] 6. Query Match Test: Query scored {tq_data['top_score']*100:.1f}% -> Top Match: '{top_match['title']}' ({tq_data['action_preview']})")
    assert top_match['score'] >= 0.70, f"Expected high confidence score for second career query, got {top_match['score']}"

    # 7. Delete Test Article (CRUD: Delete)
    del_res = requests.delete(f"{BASE_URL}/api/admin/knowledge/{new_art_id}", headers=auth_headers)
    assert del_res.status_code == 200
    print(f"[PASS] 7. Admin Knowledge Article Deletion: Deleted Article ID {new_art_id}")

    # Set require_login to false for open chatbot access
    requests.post(f"{BASE_URL}/api/admin/settings", headers=auth_headers, json={"require_login": "false"})

    # 8. Test Chatbot Local-First Knowledge Response: Better Jobs Ontario Query
    chat_aid_res = requests.post(f"{BASE_URL}/api/chat", headers=auth_headers, json={
        "query": "What is the grant amount for Better Jobs Ontario second career?"
    })
    assert chat_aid_res.status_code == 200, f"Chat aid query failed: {chat_aid_res.text}"
    aid_data = chat_aid_res.json()
    print(f"[PASS] 8. Chatbot Grant Query: Model='{aid_data['model']}', Source='{aid_data['knowledge_source']}'")
    assert "$28,000" in aid_data['response'] or "28,000" in aid_data['response']
    assert aid_data['model'] == "vic-knowledge-base-direct"

    # 9. Test Chatbot Local-First Knowledge Response: Campus Address Query
    chat_campus_res = requests.post(f"{BASE_URL}/api/chat", headers=auth_headers, json={
        "query": "Where is your Markham campus located?"
    })
    assert chat_campus_res.status_code == 200
    campus_data = chat_campus_res.json()
    print(f"[PASS] 9. Chatbot Campus Query: Model='{campus_data['model']}', Source='{campus_data['knowledge_source']}'")
    assert "7050 Woodbine" in campus_data['response'] or "Markham" in campus_data['response']

    # 10. Test Chatbot Local-First Knowledge Response: PSW Healthcare Program
    chat_psw_res = requests.post(f"{BASE_URL}/api/chat", headers=auth_headers, json={
        "query": "Tell me about your Personal Support Worker PSW program"
    })
    assert chat_psw_res.status_code == 200
    psw_data = chat_psw_res.json()
    print(f"[PASS] 10. Chatbot PSW Query: Model='{psw_data['model']}', Source='{psw_data['knowledge_source']}'")
    assert "PSW" in psw_data['response'] or "Personal Support Worker" in psw_data['response']

    # 11. Verify Conversation Logs in SQLite
    logs_res = requests.get(f"{BASE_URL}/api/admin/logs", headers=auth_headers)
    assert logs_res.status_code == 200
    logs = logs_res.json()['logs']
    assert len(logs) >= 3
    print(f"[PASS] 11. SQLite Chat Logging: {len(logs)} queries logged with model tracking")

    print("\n=======================================================")
    print(" ALL 11 KNOWLEDGE BASE & LOCAL-FIRST AI TESTS PASSED! [OK]")
    print("=======================================================\n")

if __name__ == "__main__":
    run_kb_tests()

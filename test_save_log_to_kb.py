import requests
import json

BASE_URL = "http://localhost:5055"

def test_save_log_to_kb():
    print("\n=======================================================")
    print(" Testing: Save Conversation Log into Knowledge Base")
    print("=======================================================\n")

    # 1. Login as Super Admin
    login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "mack.chen@viccollege.com",
        "password": "Admin@123456"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()['token']
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] 1. Super Admin Login: SUCCESS")

    # 2. Post a realistic user inquiry to generate a fresh chat log
    chat_res = requests.post(f"{BASE_URL}/api/chat", headers=auth_headers, json={
        "query": "Does Victoria College offer Construction and Maintenance Electrician 309A license preparation?"
    })
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    print("[PASS] 2. Chatbot Query Sent: SUCCESS")

    # 3. Retrieve latest log from database
    logs_res = requests.get(f"{BASE_URL}/api/admin/logs", headers=auth_headers)
    assert logs_res.status_code == 200
    logs = logs_res.json()['logs']
    assert len(logs) > 0
    latest_log = logs[0]
    log_id = latest_log['id']
    print(f"[PASS] 3. Retrieved Latest Log #{log_id}: '{latest_log['query']}'")

    # 4. Save Conversation Log into Knowledge Base (POST /api/admin/knowledge/from-log/<id>)
    save_res = requests.post(f"{BASE_URL}/api/admin/knowledge/from-log/{log_id}", headers=auth_headers, json={
        "priority": 2
    })
    assert save_res.status_code == 200, f"Save log to KB failed: {save_res.text}"
    save_data = save_res.json()
    new_kb_id = save_data['id']
    print(f"[PASS] 4. Save Log to Knowledge Base: Created Article ID #{new_kb_id} - {save_data['message']}")

    # 5. Fetch Article and Verify Inferred Category and Keywords
    kb_item_res = requests.get(f"{BASE_URL}/api/admin/knowledge/{new_kb_id}", headers=auth_headers)
    assert kb_item_res.status_code == 200
    article = kb_item_res.json()['article']
    print(f"[PASS] 5. Verified Saved Article: Category='{article['category']}', Keywords='{article['keywords']}'")
    assert article['category'] == 'programs'
    assert len(article['content']) > 20

    # 6. Test Query Match against the newly saved Knowledge Base article
    test_q_res = requests.post(f"{BASE_URL}/api/admin/knowledge/test-query", headers=auth_headers, json={
        "query": "Electrician 309A license preparation"
    })
    assert test_q_res.status_code == 200
    tq = test_q_res.json()
    assert len(tq['matches']) > 0
    print(f"[PASS] 6. Query Match Verification: Score={tq['top_score']*100:.1f}% -> Top Match: '{tq['matches'][0]['title']}'")

    # 7. Clean up the test article
    del_res = requests.delete(f"{BASE_URL}/api/admin/knowledge/{new_kb_id}", headers=auth_headers)
    assert del_res.status_code == 200
    print(f"[PASS] 7. Cleaned up Test Article ID #{new_kb_id}")

    print("\n=======================================================")
    print(" ALL SAVE CONVERSATION LOG TO KB TESTS PASSED! [OK]")
    print("=======================================================\n")

if __name__ == "__main__":
    test_save_log_to_kb()

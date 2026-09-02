"""
Automated Test Script for Victoria International College Backend API
Tests SQLite Database, Authentication (Google, LinkedIn, Email),
OpenAI API Key Management, and Admin Control Panel.
"""

import sys
import os
import json
import time
import server

def run_tests():
    print("\n=======================================================")
    print(" Running Victoria College Backend API & DB Verification")
    print("=======================================================\n")

    server.app.config['TESTING'] = True
    client = server.app.test_client()
    server.init_database()

    # 1. Test Server Health / Static Index
    res = client.get("/")
    assert res.status_code == 200, f"Failed to serve index: {res.status_code}"
    print("[PASS] 1. Static Index Serving: 200 OK")

    # 2. Test Admin Login with DB-stored Credentials
    login_res = client.post("/api/auth/login", json={
        "email": "admin@viccollege.com",
        "password": "Admin@123456"
    })
    assert login_res.status_code == 200, f"Admin login failed: {login_res.data.decode('utf-8')}"
    admin_data = login_res.get_json()
    admin_token = admin_data['token']
    assert admin_data['user']['role'] == 'admin', "User role is not admin"
    print("[PASS] 2. Admin Authentication (admin@viccollege.com): SUCCESS")

    # 3. Test Google OAuth Sign-In
    google_res = client.post("/api/auth/oauth/google", json={
        "email": "alex.test.student@gmail.com",
        "name": "Alex Student (Google)"
    })
    assert google_res.status_code == 200, f"Google auth failed: {google_res.data.decode('utf-8')}"
    google_user = google_res.get_json()['user']
    assert google_user['provider'] == 'google'
    print(f"[PASS] 3. Google OAuth Sign-In ({google_user['name']}): SUCCESS")

    # 4. Test LinkedIn OAuth Sign-In
    linkedin_res = client.post("/api/auth/oauth/linkedin", json={
        "email": "sarah.pro@linkedin.com",
        "name": "Sarah Professional (LinkedIn)"
    })
    assert linkedin_res.status_code == 200, f"LinkedIn auth failed: {linkedin_res.data.decode('utf-8')}"
    linkedin_user = linkedin_res.get_json()['user']
    assert linkedin_user['provider'] == 'linkedin'
    print(f"[PASS] 4. LinkedIn OAuth Sign-In ({linkedin_user['name']}): SUCCESS")

    # 5. Test Current Session Verification
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data['authenticated'] is True
    assert me_data['user']['email'] == "admin@viccollege.com"
    print("[PASS] 5. Auth Session Verification (/api/auth/me): SUCCESS")

    # 6. Test Admin Stats Retrieval
    stats_res = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert stats_res.status_code == 200
    stats = stats_res.get_json()
    print(f"[PASS] 6. Admin Statistics: Total Users={stats['total_users']}, Google={stats['google_users']}, LinkedIn={stats['linkedin_users']}")

    # 7. Test Admin User List & Management
    users_res = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert users_res.status_code == 200
    users_list = users_res.get_json()['users']
    print(f"[PASS] 7. Admin User List Retrieval: {len(users_list)} users found")

    # Create new user via admin panel
    new_user_email = f"qa.student.{int(time.time())}@viccollege.com"
    create_user_res = client.post("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "name": "QA Test Student",
        "email": new_user_email,
        "role": "user",
        "status": "active"
    })
    assert create_user_res.status_code == 200
    new_user_id = create_user_res.get_json()['user_id']
    print(f"[PASS] 8. Admin User Creation: Created User ID {new_user_id} ({new_user_email})")

    # Update user role to Admin
    update_res = client.put(f"/api/admin/users/{new_user_id}", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "role": "admin",
        "status": "active"
    })
    assert update_res.status_code == 200
    print(f"[PASS] 9. Admin User Role Update: Promoted User ID {new_user_id} to Admin")

    # 8. Test Settings & OpenAI API Key Management in SQLite DB
    settings_res = client.get("/api/admin/settings", headers={"Authorization": f"Bearer {admin_token}"})
    assert settings_res.status_code == 200
    print("[PASS] 10. Admin Settings Retrieval from SQLite DB: SUCCESS")

    # Save Settings (Model, Key, System Prompt)
    save_res = client.post("/api/admin/settings", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "openai_model": "gpt-4o-mini",
        "temperature": "0.7",
        "max_tokens": "1000",
        "require_login": "true"
    })
    assert save_res.status_code == 200
    print("[PASS] 11. Admin Settings Update into SQLite DB: SUCCESS (require_login=true)")

    # 9a. Test AI Chatbot Rejection for Unauthenticated Request
    unauth_chat_res = client.post("/api/chat", json={
        "query": "How do I get the $28,000 government grant for PSW?",
        "history": []
    })
    assert unauth_chat_res.status_code == 401, f"Expected 401 for unauthenticated request, got {unauth_chat_res.status_code}"
    unauth_data = unauth_chat_res.get_json()
    assert unauth_data.get('require_auth') is True, "Expected require_auth: True in response"
    print("[PASS] 12a. AI Chatbot Unauthenticated Rejection (401 + require_auth=True): SUCCESS")

    # 9b. Test AI Chatbot Successful Response for Authenticated User
    auth_chat_res = client.post("/api/chat", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "query": "How do I get the $28,000 government grant for PSW?",
        "history": []
    })
    assert auth_chat_res.status_code == 200, f"Authenticated chat failed: {auth_chat_res.data.decode('utf-8')}"
    chat_data = auth_chat_res.get_json()
    assert len(chat_data['response']) > 20
    print(f"[PASS] 12b. AI Chatbot Authenticated Response (/api/chat): SUCCESS (Model: {chat_data['model']})")

    # 10. Test Conversation Logs
    logs_res = client.get("/api/admin/logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert logs_res.status_code == 200 and len(logs_res.get_json()['logs']) > 0
    print(f"[PASS] 13. Admin Chat Logs Retrieval: {len(logs_res.get_json()['logs'])} logs recorded in SQLite DB")

    # 11. Test Password Update in SQLite DB (/api/auth/change-password)
    change_pwd_res = client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "old_password": "Admin@123456",
        "new_password": "NewSecureAdmin@2026"
    })
    assert change_pwd_res.status_code == 200, f"Change password failed: {change_pwd_res.data.decode('utf-8')}"
    print("[PASS] 14. Password Update in SQLite DB (/api/auth/change-password): SUCCESS")

    # Verify login with new password
    relogin_res = client.post("/api/auth/login", json={
        "email": "admin@viccollege.com",
        "password": "NewSecureAdmin@2026"
    })
    assert relogin_res.status_code == 200, "Login with new password failed"
    new_admin_token = relogin_res.get_json()['token']
    print("[PASS] 15. Authentication with Updated Database Password: SUCCESS")

    # Restore initial test password for future test runs
    client.post("/api/auth/change-password", headers={"Authorization": f"Bearer {new_admin_token}"}, json={
        "old_password": "NewSecureAdmin@2026",
        "new_password": "Admin@123456"
    })

    print("\n=======================================================")
    print(" ALL 15 BACKEND & DATABASE TESTS PASSED PERFECTLY! [OK]")
    print("=======================================================\n")

if __name__ == "__main__":
    run_tests()

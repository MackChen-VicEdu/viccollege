"""
Automated unit & integration tests for AI Chatbot disclaimer and college contact reminder.
"""
import unittest
import os
import re
import server

class TestChatbotDisclaimer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()
        server.init_database()

    def test_01_chatbot_js_footer_disclaimer_markup(self):
        """Verify js/ai-chatbot.js has the permanent disclaimer in footer and element binding."""
        js_path = os.path.join(os.path.dirname(__file__), 'js', 'ai-chatbot.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check footer markup
        self.assertIn('id="vic-chat-footer-disclaimer"', content)
        self.assertIn('id="vic-chat-disclaimer-text"', content)
        self.assertIn('fa-triangle-exclamation', content)

        # Check disclaimer text in both languages
        self.assertIn('AI-generated responses for guidance only', content)
        self.assertIn('416-665-6668', content)
        self.assertIn('info@viccollege.com', content)
        self.assertIn('本系统为 AI 智能助手，回复仅供参考', content)

        # Check elements dictionary has disclaimerText
        self.assertIn("disclaimerText: container.querySelector('#vic-chat-disclaimer-text')", content)

    def test_02_chatbot_js_initial_welcome_disclaimer(self):
        """Verify initial welcome messages in English and Chinese contain the AI reminder note."""
        js_path = os.path.join(os.path.dirname(__file__), 'js', 'ai-chatbot.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check unauthenticated & authenticated welcome notices
        self.assertIn('⚠️ *温馨提示：本系统为 AI 智能顾问', content)
        self.assertIn('⚠️ *Please Note: This is an AI assistant', content)

    def test_03_chatbot_js_dynamic_language_switch(self):
        """Verify updateChatbotLanguage updates elements.disclaimerText dynamically."""
        js_path = os.path.join(os.path.dirname(__file__), 'js', 'ai-chatbot.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('elements.disclaimerText.textContent', content)

    def test_04_server_system_prompt_includes_ai_reminder_instruction(self):
        """Verify server system_prompt directs the AI to remind users and refer to advisors."""
        with server.app.app_context():
            db = server.get_db()
            cursor = db.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'system_prompt'")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            prompt_text = row['value']

            self.assertIn('Remind users that you are an AI assistant', prompt_text)
            self.assertIn('416-665-6668', prompt_text)
            self.assertIn('info@viccollege.com', prompt_text)

    def test_05_server_local_knowledge_reply_includes_ai_reminder(self):
        """Verify fallback reply in server.py reminds user that this is an AI."""
        reply_zh = server.generate_local_knowledge_reply("你好，介绍一下你们学校")
        self.assertIn('AI 智能', reply_zh)
        self.assertIn('416-665-6668', reply_zh)
        self.assertIn('info@viccollege.com', reply_zh)

        reply_en = server.generate_local_knowledge_reply("Hello, can you help me?")
        self.assertIn('AI assistant', reply_en)
        self.assertIn('416-665-6668', reply_en)
        self.assertIn('info@viccollege.com', reply_en)

    def test_06_css_footer_disclaimer_styling(self):
        """Verify css/style.css styles .vic-chat-footer-brand with readable contrast."""
        css_path = os.path.join(os.path.dirname(__file__), 'css', 'style.css')
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()

        self.assertIn('.vic-chat-footer-brand', css)
        self.assertIn('#64748b', css)
        self.assertIn('#f8fafc', css)

if __name__ == '__main__':
    unittest.main()

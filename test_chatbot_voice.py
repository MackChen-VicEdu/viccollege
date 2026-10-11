"""
Automated unit tests for AI Chatbot Text-to-Voice (TTS) and Voice-to-Text (STT) features.
"""
import unittest
import os

class TestChatbotVoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(__file__)
        cls.js_path = os.path.join(cls.base_dir, 'js', 'ai-chatbot.js')
        cls.css_path = os.path.join(cls.base_dir, 'css', 'style.css')
        with open(cls.js_path, 'r', encoding='utf-8') as f:
            cls.js_content = f.read()
        with open(cls.css_path, 'r', encoding='utf-8') as f:
            cls.css_content = f.read()

    def test_01_markup_voice_elements(self):
        """Verify DOM markup contains Voice Toggle button and Microphone input button."""
        # Voice toggle button in header
        self.assertIn('id="vic-chat-voice-toggle"', self.js_content)
        self.assertIn('js-voice-toggle', self.js_content)

        # Microphone button in input area
        self.assertIn('id="vic-chat-mic"', self.js_content)
        self.assertIn('vic-chat-mic-btn', self.js_content)
        self.assertIn('fa-microphone', self.js_content)

        # Listening status indicator
        self.assertIn('id="vic-chat-listening-status"', self.js_content)
        self.assertIn('listening-wave', self.js_content)
        self.assertIn('js-cancel-listen', self.js_content)

        # Elements dictionary references
        self.assertIn("micBtn: container.querySelector('#vic-chat-mic')", self.js_content)
        self.assertIn("voiceToggleBtn: container.querySelector('#vic-chat-voice-toggle')", self.js_content)
        self.assertIn("listeningStatus: container.querySelector('#vic-chat-listening-status')", self.js_content)

    def test_02_speech_to_text_recognition_logic(self):
        """Verify Web Speech Recognition is wired up with start/stop/toggle methods."""
        self.assertIn('SpeechRecognition', self.js_content)
        self.assertIn('webkitSpeechRecognition', self.js_content)
        self.assertIn('function toggleListening()', self.js_content)
        self.assertIn('function startListening()', self.js_content)
        self.assertIn('function stopListening()', self.js_content)
        self.assertIn('recognitionInstance.interimResults = true', self.js_content)
        self.assertIn('zh-CN', self.js_content)
        self.assertIn('en-US', self.js_content)

    def test_03_text_to_speech_synthesis_logic(self):
        """Verify Web Speech Synthesis (TTS) is wired up for message read-aloud and auto narration."""
        self.assertIn('speechSynthesis', self.js_content)
        self.assertIn('SpeechSynthesisUtterance', self.js_content)
        self.assertIn('function speakMessage(', self.js_content)
        self.assertIn('function stopSpeaking()', self.js_content)
        self.assertIn('function cleanTextForSpeech(', self.js_content)
        self.assertIn('function toggleAutoVoice()', self.js_content)
        self.assertIn('function updateAutoVoiceUI()', self.js_content)
        self.assertIn('vic_chat_tts_auto', self.js_content)

    def test_04_message_read_aloud_button(self):
        """Verify bot messages append the Listen / TTS button with event listener."""
        self.assertIn('vic-chat-tts-btn', self.js_content)
        self.assertIn('js-tts-btn', self.js_content)
        self.assertIn('speakMessage(msg.text, ttsBtn)', self.js_content)
        self.assertIn('autoVoiceEnabled', self.js_content)

    def test_05_css_styling_for_voice_elements(self):
        """Verify css/style.css contains responsive and accessible styling for voice features."""
        # Header voice toggle active state
        self.assertIn('.chat-hdr-btn.js-voice-toggle.active', self.css_content)

        # Microphone button & pulsing animation
        self.assertIn('.vic-chat-mic-btn', self.css_content)
        self.assertIn('.vic-chat-mic-btn.listening', self.css_content)
        self.assertIn('@keyframes vicMicPulse', self.css_content)

        # Listening status & wave
        self.assertIn('.vic-chat-listening-status', self.css_content)
        self.assertIn('.listening-wave', self.css_content)

        # TTS read-aloud button & speaking pulse
        self.assertIn('.vic-chat-tts-btn', self.css_content)
        self.assertIn('.vic-chat-tts-btn.speaking', self.css_content)
        self.assertIn('@keyframes vicSpeakingPulse', self.css_content)

        # Chat feedback toast
        self.assertIn('.vic-chat-toast', self.css_content)

if __name__ == '__main__':
    unittest.main()

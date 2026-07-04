import os

from ai.summary_generator import SummaryGenerator
from ai.chatbot import HealthChatbot
from report_processing.extractor import BloodReportExtractor
from auth import derive_username_from_email


def test_summary_generator_falls_back_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    generator = SummaryGenerator(api_key=None)
    summary = generator.generate_summary({
        "results": [{"parameter": "hemoglobin", "value": 12.5, "status": "Low"}],
        "risk_assessment": {"risk_level": "Moderate"},
    })

    assert generator.llm is None
    assert "Unable to generate AI summary" in summary


def test_chatbot_falls_back_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    chatbot = HealthChatbot(api_key=None)
    response = chatbot.chat("What does this mean?")

    assert chatbot.llm is None
    assert "I can help" in response


def test_extractor_parses_abbreviated_lab_line():
    extractor = BloodReportExtractor()
    text = "Patient Report\nHb: 12.5 g/dL\nTotal Cholesterol: 180 mg/dL"

    parsed = extractor._parse_text(text)

    assert parsed["hemoglobin"]["value"] == 12.5
    assert parsed["cholesterol"]["value"] == 180.0


def test_derive_username_from_email():
    assert derive_username_from_email("User.Name+Test@Example.com") == "user_name_test"


def test_register_user_uses_json_fallback(tmp_path, monkeypatch):
    from auth import register_user

    monkeypatch.setattr("auth.USERS_FILE", tmp_path / "users.json")
    success, message = register_user("demo_user", "demo12345", email="demo@example.com")

    assert success is True
    assert message == "Registration successful!"

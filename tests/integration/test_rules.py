# tests/test_rules.py
from rakshagrid.ai_scam.model.rules import score_lexicon

def test_legitimate_text():
    text = "Hello, how are you? I wanted to discuss the project update for next week."
    res = score_lexicon(text)
    assert res["score"] == 0.0
    assert res["band"] == "low"
    assert len(res["fired"]) == 0

def test_digital_arrest_scam_text():
    text = "This is the CBI officer calling. You are under digital arrest due to a narcotics case. You must cooperate immediately."
    res = score_lexicon(text)
    assert res["score"] > 0.4
    assert res["band"] in ["medium", "high", "needs_review"]
    
    # Verify that specific features fired
    fired_features = [f["feature"] for f in res["fired"]]
    assert any("authority" in f or "arrest" in f for f in fired_features)
    assert any("urgency" in f for f in fired_features)

def test_financial_fraud_text():
    text = "Please transfer the money to our verification bank account immediately or your connection will be blocked."
    res = score_lexicon(text)
    assert res["score"] > 0.2
    
    fired_features = [f["feature"] for f in res["fired"]]
    assert "payment_channel_switch" in fired_features or "money" in fired_features

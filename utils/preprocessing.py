import re
from utils.scam_lexicon import URGENCY_WORDS, MONEY_WORDS, AUTHORITY_WORDS

def count_turns(text: str) -> int:
    """Count number of conversational turns based on caller: or receiver: prefixes."""
    return len(re.findall(r"\b(caller|receiver):", text, flags=re.IGNORECASE))

def extract_features(text: str) -> dict:
    """
    Extract the exact 9 engineered features used in training.
    Must match feature names and logic in prep_data.ipynb exactly.
    """
    text_lower = text.lower()
    
    char_len = len(text)
    word_count = len(text.split())
    turn_count = count_turns(text)
    
    # Matching notebooks/prep_data.ipynb logic
    # df["placeholder_count"] = df["text"].str.count(r"\[[A-Za-z]+\]")
    placeholder_count = len(re.findall(r"\[[A-Za-z]+\]", text))
    
    # df["urgency_word_count"] = df["text"].str.lower().str.count(URGENCY_WORDS)
    urgency_word_count = len(re.findall(URGENCY_WORDS, text_lower))
    
    # df["money_word_count"] = df["text"].str.lower().str.count(MONEY_WORDS)
    money_word_count = len(re.findall(MONEY_WORDS, text_lower))
    
    # df["authority_word_count"] = df["text"].str.lower().str.count(AUTHORITY_WORDS)
    authority_word_count = len(re.findall(AUTHORITY_WORDS, text_lower))
    
    # df["has_phone_number"] = df["text"].str.contains(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b").astype(int)
    has_phone = bool(re.search(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", text))
    has_phone_number = 1 if has_phone else 0
    
    # df["exclaim_count"] = df["text"].str.count("!")
    exclaim_count = text.count("!")
    
    return {
        "turn_count": turn_count,
        "char_len": char_len,
        "word_count": word_count,
        "placeholder_count": placeholder_count,
        "urgency_word_count": urgency_word_count,
        "money_word_count": money_word_count,
        "authority_word_count": authority_word_count,
        "has_phone_number": has_phone_number,
        "exclaim_count": exclaim_count
    }

def compute_rules_score(rules_result: dict) -> float:
    """Helper to convert lexical rules score to the float expected by the ensemble."""
    return float(rules_result.get("score", 0.0))

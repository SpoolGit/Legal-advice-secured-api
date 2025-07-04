import re
import json
import os
from typing import List, Tuple
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


# Load word lists from JSON files
def load_word_list(filename: str) -> List[str]:
    """Load word list from JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, filename)

    print(f"DEBUG: Looking for file at: {filepath}")
    print(f"DEBUG: File exists: {os.path.exists(filepath)}")
    print(f"DEBUG: Current working directory: {os.getcwd()}")
    print(f"DEBUG: Script directory: {current_dir}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"DEBUG: Successfully loaded {len(data)} items from {filename}")
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {filepath}: {e}")
    except Exception as e:
        raise Exception(f"Error loading {filepath}: {e}")


# Load the lists with caching
@lru_cache(maxsize=1)
def get_banned_words() -> List[str]:
    return load_word_list("banned_words.json")


@lru_cache(maxsize=1)
def get_legal_keywords() -> List[str]:
    return load_word_list("legal_keywords.json")


@lru_cache(maxsize=1)
def get_legal_phrases() -> List[str]:
    return load_word_list("legal_phrases.json")


# Additional patterns for advanced evasion detection
EVASION_PATTERNS = [
    r"k.{0,3}i.{0,3}l.{0,3}l",  # kill with characters in-between
    r"m.{0,3}u.{0,3}r.{0,3}d.{0,3}e.{0,3}r",  # murder with characters in-between
    r"b.{0,3}r.{0,3}i.{0,3}b.{0,3}e",  # bribe with characters in-between
    r"h.{0,3}a.{0,3}c.{0,3}k",  # hack with characters in-between
]


def contains_banned_words(text: str) -> List[str]:
    """
    Check for banned words in text, including advanced evasion techniques.

    Args:
        text: Input text to check

    Returns:
        List of banned words found
    """
    found = []
    text_lower = text.lower()
    banned_words = get_banned_words()

    # Direct word matching with word boundaries
    for word in banned_words:
        # Use word boundaries to avoid false positives
        pattern = r"\b" + re.escape(word.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(word)

    # Check for spacing/punctuation evasion
    found.extend(_check_spacing_evasion(text_lower))

    # Check for leetspeak and common substitutions
    found.extend(_check_leetspeak(text_lower))

    return list(set(found))  # Remove duplicates


def _check_spacing_evasion(text: str) -> List[str]:
    """Check for spacing and punctuation evasion (e.g., k i l l, k-i-l-l)"""
    found = []
    banned_words = get_banned_words()

    # Remove common separators and check again
    cleaned_text = re.sub(r"[\s\-_\.]+", "", text)

    for word in banned_words:
        if word.lower() in cleaned_text:
            found.append(word)

    return found


def _check_leetspeak(text: str) -> List[str]:
    """Check for leetspeak variations"""
    found = []
    banned_words = get_banned_words()

    leet_map = {
        "4": "a",
        "@": "a",
        "3": "e",
        "1": "i",
        "!": "i",
        "0": "o",
        "5": "s",
        "$": "s",
        "7": "t",
        "|": "l",
    }

    # Convert leet-speak to normal text
    normalized_text = text
    for leet, normal in leet_map.items():
        normalized_text = normalized_text.replace(leet, normal)

    for word in banned_words:
        if word.lower() in normalized_text:
            found.append(word)

    return found


def is_legal_topic(text: str) -> bool:
    """
    Determine if the input text is related to legal topics.

    Args:
        text: Input text to analyze

    Returns:
        Boolean indicating if text is legal-related
    """
    legal_keywords = get_legal_keywords()
    legal_phrases = get_legal_phrases()

    text_lower = text.lower()

    # Debug logging
    logger.debug(f"Checking text: {text_lower}")
    logger.debug(f"Legal keywords count: {len(legal_keywords)}")
    logger.debug(f"Legal phrases count: {len(legal_phrases)}")

    # Check for legal keywords
    for keyword in legal_keywords:
        if keyword.lower() in text_lower:
            logger.debug(f"Found legal keyword: {keyword}")
            return True

    # Check for legal phrases
    for phrase in legal_phrases:
        if phrase.lower() in text_lower:
            logger.debug(f"Found legal phrase: {phrase}")
            return True

    logger.debug("No legal keywords or phrases found")
    return False


def validate_input_safety(text: str) -> Tuple[bool, List[str], str]:
    """
    Comprehensive input validation for safety and relevance.

    Args:
        text: Input text to validate

    Returns:
        Tuple of (is_safe, banned_words_found, reason)
    """
    # Check for banned words
    banned_words_found = contains_banned_words(text)
    if banned_words_found:
        logger.warning(f"Banned words detected: {banned_words_found}")
        return False, banned_words_found, "Contains banned words"

    # Check if topic is legal-related
    if not is_legal_topic(text):
        logger.info("Input determined to be off-topic")
        return False, [], "Off-topic request"

    # Check for prompt injection attempts
    injection_patterns = [
        r"ignore.{0,10}(previous|above|system|all).{0,10}instructions?",
        r"act.{0,10}as.{0,10}(?:if|though)",
        r"pretend.{0,10}(?:to|that).{0,10}be",
        r"roleplay.{0,10}as",
        r"you.{0,10}are.{0,10}(?:now|actually)",
        r"forget.{0,10}(?:everything|all|what)",
        r"override.{0,10}(?:your|the).{0,10}(?:instructions|rules|guidelines)",
        r"jailbreak",
        r"developer.{0,10}mode",
        r"admin.{0,10}mode",
        r"root.{0,10}access",
    ]

    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning("Potential prompt injection detected")
            return False, [], "Potential prompt injection detected"

    return True, [], "Input is safe and relevant"


# Test function to debug
def test_validator():
    """Test function to debug the validator"""
    test_cases = [
        "I need legal advice about my contract",
        "What are my rights as a tenant?",
        "Can I sue my employer?",
        "How to cook pasta",
        "What's the weather like?",
        "I want to kill someone",
        "How to hack a system",
    ]

    print("Testing validator...")
    for test in test_cases:
        result = validate_input_safety(test)
        print(f"Text: '{test}' -> Result: {result}")


if __name__ == "__main__":
    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)
    test_validator()

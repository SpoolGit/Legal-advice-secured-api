import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# This list is fro Demo and needs to be updated for production & real-world usage
BANNED_WORDS = [
    "kill", "murder", "assault", "torture", "bomb", "weapon", "shoot", "stab", "bribe",
    "launder", "embezzle", "defraud", "counterfeit", "forge", "tax evasion", "hack",
    "phish", "crack", "exploit", "DDoS", "malware", "ransomware", "smuggle", "traffick",
    "contraband", "fake ID", "passport", "visa", "notarize fraud", "practice law",
    "unauthorized practice", "attorney-client privilege", "retainer", "billable hours",
    "give legal advice", "jailbreak", "ignore previous", "system instructions", "override"
]

# Additional patterns for advanced evasion detection
EVASION_PATTERNS = [
    r'k.{0,3}i.{0,3}l.{0,3}l',  # kill with characters in-between
    r'm.{0,3}u.{0,3}r.{0,3}d.{0,3}e.{0,3}r',  # murder with characters in-between
    r'b.{0,3}r.{0,3}i.{0,3}b.{0,3}e',  # bribe with characters in-between
    r'h.{0,3}a.{0,3}c.{0,3}k',  # hack with characters in-between
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
    
    # Direct word matching with word boundaries
    for word in BANNED_WORDS:
        # Use word boundaries to avoid false posiitves
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
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
    
    # Remove common separators and check again
    cleaned_text = re.sub(r'[\s\-_\.]+', '', text)
    
    for word in BANNED_WORDS:
        if word.lower() in cleaned_text:
            found.append(word)
    
    return found

def _check_leetspeak(text: str) -> List[str]:
    """Check for leetspeak variations"""
    found = []
    
    leet_map = {
        '4': 'a', '@': 'a', '3': 'e', '1': 'i', '!': 'i',
        '0': 'o', '5': 's', '$': 's', '7': 't', '|': 'l'
    }
    
    # Convert leet-speak to normal text
    normalized_text = text
    for leet, normal in leet_map.items():
        normalized_text = normalized_text.replace(leet, normal)
    
    for word in BANNED_WORDS:
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
    
    # A list for demo purpose. This list can be updates to allow more keywords or
    # restrict a particular keyword. 
    legal_keywords = [
        'law', 'legal', 'attorney', 'lawyer', 'court', 'judge', 'trial', 'case',
        'contract', 'agreement', 'rights', 'liability', 'lawsuit', 'litigation',
        'statute', 'regulation', 'compliance', 'violation', 'penalty', 'fine',
        'property', 'estate', 'will', 'trust', 'divorce', 'custody', 'adoption',
        'immigration', 'visa', 'patent', 'trademark', 'copyright', 'employment',
        'discrimination', 'harassment', 'wage', 'overtime', 'benefits', 'insurance',
        'criminal', 'civil', 'constitutional', 'administrative', 'family', 'corporate',
        'business', 'commercial', 'real estate', 'personal injury', 'medical malpractice', 'corporation',
        'bankruptcy', 'debt', 'collection', 'foreclosure', 'eviction', 'landlord', 'tenant',
        'tax', 'file tax', 'income tax', 'tax return', 'withholding', 'irs', 'hmrc', 'audit'
    ]
    
    text_lower = text.lower()
    
    # Check for legal keywords
    for keyword in legal_keywords:
        if keyword in text_lower:
            return True
    
    # Check for legal phrases. Similarly like keywords, these phrases need to be updated
    legal_phrases = [
        'can i sue', 'is it legal', 'what are my rights', 'legal advice',
        'against the law', 'legal consequences', 'file a lawsuit', 'legal action',
        'court case', 'legal document', 'legal requirement', 'legal obligation', 'file tax'
    ]
    
    for phrase in legal_phrases:
        if phrase in text_lower:
            return True
    
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
        r'ignore.{0,10}(previous|above|system|all).{0,10}instructions?',
        r'act.{0,10}as.{0,10}(?:if|though)',
        r'pretend.{0,10}(?:to|that).{0,10}be',
        r'roleplay.{0,10}as',
        r'you.{0,10}are.{0,10}(?:now|actually)',
        r'forget.{0,10}(?:everything|all|what)',
        r'override.{0,10}(?:your|the).{0,10}(?:instructions|rules|guidelines)',
        r'jailbreak',
        r'developer.{0,10}mode',
        r'admin.{0,10}mode',
        r'root.{0,10}access'
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning("Potential prompt injection detected")
            return False, [], "Potential prompt injection detected"
    
    return True, [], "Input is safe and relevant"
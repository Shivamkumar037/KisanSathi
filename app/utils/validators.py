"""
Input Validators
"""

import re


def validate_required_fields(data: dict, required: list) -> str:
    """
    Check all required fields are present and non-empty.
    Returns error message string or None.
    """
    if not data:
        return 'Request body is empty'

    for field in required:
        if field not in data or not str(data[field]).strip():
            return f"'{field}' is required"

    return None


def validate_phone(phone: str) -> bool:
    """Validate Indian mobile number (10 digits, may start with +91)"""
    phone = str(phone).strip()
    # Remove +91 or 91 prefix
    if phone.startswith('+91'):
        phone = phone[3:]
    elif phone.startswith('91') and len(phone) == 12:
        phone = phone[2:]

    # Must be 10 digits starting with 6-9
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email).strip()))


def validate_password(password: str) -> tuple:
    """
    Validate password strength.
    Returns (is_valid: bool, message: str)
    """
    if len(password) < 6:
        return False, 'Password must be at least 6 characters'
    return True, 'OK'


def sanitize_string(value: str, max_length: int = 500) -> str:
    """Sanitize and truncate string input"""
    if not value:
        return ''
    # Strip dangerous HTML/script tags (basic)
    value = re.sub(r'<[^>]+>', '', str(value))
    return value.strip()[:max_length]

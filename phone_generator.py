"""
Generator for E.164-like fake phone numbers for testing.

This intentionally generates digit-only phone numbers in E.164 form:
    +{country_code}{national_digits}

It uses python-phonenumbers when available to try to normalize/validate,
but it never queries any external service.
"""

from typing import Optional, List
import random

try:
    import phonenumbers
    from phonenumbers import PhoneNumberFormat
    _HAS_PHONENUM = True
except Exception:
    _HAS_PHONENUM = False


def _random_digits(n: int, rng: random.Random) -> str:
    return "".join(str(rng.randint(0, 9)) for _ in range(n))


def generate_e164(country_code: str = "1", national_length: int = 10, seed: Optional[int] = None) -> str:
    """
    Generate a single E.164-like phone number as a string.

    Args:
        country_code: digits for country code (no leading +).
        national_length: number of digits in the national significant number.
        seed: optional integer seed for deterministic output.

    Returns:
        A string like "+1XXXXXXXXXX"
    """
    rng = random.Random(seed)
    digits = _random_digits(national_length, rng)
    number = f"+{country_code}{digits}"

    if _HAS_PHONENUM:
        try:
            parsed = phonenumbers.parse(number, None)
            # If parse fails, phonenumbers raises; otherwise format
            return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)
        except Exception:
            return number
    return number


def generate_batch(count: int = 1, country_code: str = "1", national_length: int = 10, seed: Optional[int] = None) -> List[str]:
    """
    Generate a batch of numbers. If seed is provided, the batch is deterministic.
    """
    if seed is not None:
        rng = random.Random(seed)
        seeds = [rng.randint(0, 2**32 - 1) for _ in range(count)]
    else:
        seeds = [None] * count

    return [generate_e164(country_code=country_code, national_length=national_length, seed=s) for s in seeds]


def is_valid_e164(number: str) -> bool:
    """
    Try to validate an E.164-like string using phonenumbers if available.
    Otherwise, do a lightweight check: starts with '+' and all remaining chars are digits.
    """
    if _HAS_PHONENUM:
        try:
            parsed = phonenumbers.parse(number, None)
            return phonenumbers.is_possible_number(parsed)  # conservative check
        except Exception:
            return False
    if not number or not number.startswith("+"):
        return False
    return number[1:].isdigit()

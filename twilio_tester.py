"""
twilio_tester.py

Send test SMS messages or make test calls to numbers you own
using the Twilio REST API. Requires a Twilio account and credentials.

Install dependency:
    pip3 install twilio

Set environment variables before running:
    export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxx"
    export TWILIO_AUTH_TOKEN="your_auth_token"
    export TWILIO_FROM="+1XXXXXXXXXX"   # your Twilio number

WARNING: Only use against numbers you own or have explicit written
authorization to test. Unauthorized use may violate the TCPA and FCC rules.
"""

import os
from typing import List, Optional

try:
    from twilio.rest import Client
    _HAS_TWILIO = True
except ImportError:
    _HAS_TWILIO = False

from phone_generator import is_valid_e164


def _get_client() -> "Client":
    if not _HAS_TWILIO:
        raise RuntimeError("twilio package not installed. Run: pip3 install twilio")
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        raise RuntimeError("Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")
    return Client(sid, token)


def send_sms(to: str, body: str = "Test message from pentest suite.", from_: Optional[str] = None) -> dict:
    """
    Send a test SMS to a number you own.

    Args:
        to: E.164 destination number (must be yours or authorized).
        body: SMS body text.
        from_: sending Twilio number; falls back to TWILIO_FROM env var.

    Returns:
        Dict with message SID and status.
    """
    if not is_valid_e164(to):
        raise ValueError(f"Invalid E.164 number: {to}")
    from_number = from_ or os.environ.get("TWILIO_FROM")
    if not from_number:
        raise RuntimeError("Set TWILIO_FROM environment variable or pass from_ argument.")
    client = _get_client()
    msg = client.messages.create(body=body, from_=from_number, to=to)
    print(f"[+] SMS sent to {to} | SID: {msg.sid} | Status: {msg.status}")
    return {"sid": msg.sid, "status": msg.status}


def make_call(to: str, twiml_url: str, from_: Optional[str] = None) -> dict:
    """
    Initiate a test call to a number you own.

    Args:
        to: E.164 destination number (must be yours or authorized).
        twiml_url: publicly accessible URL returning TwiML instructions.
        from_: sending Twilio number; falls back to TWILIO_FROM env var.

    Returns:
        Dict with call SID and status.
    """
    if not is_valid_e164(to):
        raise ValueError(f"Invalid E.164 number: {to}")
    from_number = from_ or os.environ.get("TWILIO_FROM")
    if not from_number:
        raise RuntimeError("Set TWILIO_FROM environment variable or pass from_ argument.")
    client = _get_client()
    call = client.calls.create(url=twiml_url, from_=from_number, to=to)
    print(f"[+] Call initiated to {to} | SID: {call.sid} | Status: {call.status}")
    return {"sid": call.sid, "status": call.status}


def batch_sms(targets: List[str], body: str = "Test message.", from_: Optional[str] = None) -> List[dict]:
    """
    Send SMS to a list of authorized numbers.

    Args:
        targets: list of E.164 numbers.
        body: SMS body text.
        from_: sending Twilio number.

    Returns:
        List of result dicts.
    """
    results = []
    for number in targets:
        try:
            result = send_sms(to=number, body=body, from_=from_)
            results.append({"number": number, **result})
        except Exception as e:
            print(f"[-] Failed for {number}: {e}")
            results.append({"number": number, "error": str(e)})
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 twilio_tester.py <to_number> <message>")
        sys.exit(1)
    send_sms(to=sys.argv[1], body=sys.argv[2])

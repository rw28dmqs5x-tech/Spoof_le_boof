"""
sipvicious_output.py

Formats phone number lists into formats compatible with SIPVicious tools
(svwar, svcrack, svmap) for use in authorized VoIP/SIP penetration testing.

SIPVicious tools: https://github.com/EnableSecurity/sipvicious

Install SIPVicious:
    pip3 install sipvicious

WARNING: Only use against SIP infrastructure you own or have explicit written
authorization to test. Unauthorized SIP scanning may be illegal.
"""

import sys
import subprocess
from typing import List, Optional
from phone_generator import generate_batch, is_valid_e164
from target_loader import load_from_file, save_to_file


def to_extension_range(numbers: List[str], strip_country: bool = True) -> List[str]:
    """
    Convert E.164 numbers to bare extension strings for svwar.
    SIPVicious svwar expects plain numeric extension ranges, not E.164.

    Args:
        numbers: list of E.164 strings like +14085551234
        strip_country: if True, strips leading + and country code (first 1-3 digits)

    Returns:
        List of extension strings like ["4085551234", ...]
    """
    extensions = []
    for n in numbers:
        if not is_valid_e164(n):
            continue
        digits = n[1:]  # strip leading +
        if strip_country:
            # Heuristic: strip 1-digit CC for +1, 2-digit for +44/+49, etc.
            if digits.startswith("1") and len(digits) == 11:
                digits = digits[1:]   # US/CA: strip 1
            elif len(digits) > 10:
                digits = digits[2:]   # 2-digit CC
        extensions.append(digits)
    return extensions


def write_extension_file(numbers: List[str], filepath: str, strip_country: bool = True) -> None:
    """
    Write extensions to a file for use with svwar -e or as input wordlist.

    Args:
        numbers: list of E.164 strings.
        filepath: output file path.
        strip_country: strip country code from numbers.
    """
    extensions = to_extension_range(numbers, strip_country=strip_country)
    with open(filepath, "w") as f:
        for ext in extensions:
            f.write(ext + "\n")
    print(f"[+] Wrote {len(extensions)} extensions to {filepath}")


def build_svwar_command(
    host: str,
    extension_file: str,
    port: int = 5060,
    method: str = "REGISTER",
    extra_args: Optional[List[str]] = None
) -> List[str]:
    """
    Build a svwar command for authorized VoIP extension enumeration.

    Args:
        host: target SIP server IP or hostname (must be authorized).
        extension_file: path to file containing extensions (one per line).
        port: SIP port (default 5060).
        method: SIP method to use — REGISTER or INVITE.
        extra_args: any additional svwar arguments.

    Returns:
        List of command parts ready for subprocess.
    """
    cmd = [
        "svwar",
        "-e", f"file:{extension_file}",
        "-m", method,
        "-p", str(port),
        host
    ]
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def build_svmap_command(
    target: str,
    port: int = 5060,
    extra_args: Optional[List[str]] = None
) -> List[str]:
    """
    Build a svmap command for authorized SIP host discovery.

    Args:
        target: IP, CIDR range, or hostname of authorized target.
        port: SIP port.
        extra_args: additional svmap arguments.

    Returns:
        List of command parts ready for subprocess.
    """
    cmd = ["svmap", "-p", str(port), target]
    if extra_args:
        cmd.extend(extra_args)
    return cmd


def run_command(cmd: List[str], dry_run: bool = False) -> Optional[str]:
    """
    Run a SIPVicious command. Use dry_run=True to print without executing.

    Args:
        cmd: command list from build_svwar_command or build_svmap_command.
        dry_run: if True, print the command instead of running it.

    Returns:
        stdout output string, or None on dry run.
    """
    print(f"[{'DRY RUN' if dry_run else '+'}] Command: {' '.join(cmd)}")
    if dry_run:
        return None
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[-] Error: {result.stderr.strip()}")
    return result.stdout


if __name__ == "__main__":
    """
    Example usage:
        # Generate 20 fake numbers and write extensions for svwar
        python3 sipvicious_output.py generate 20 extensions.txt

        # Load from existing file and write extensions
        python3 sipvicious_output.py load targets.txt extensions.txt

        # Build and dry-run a svwar command
        python3 sipvicious_output.py svwar 192.168.1.1 extensions.txt
    """
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    mode = sys.argv[1]

    if mode == "generate":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        outfile = sys.argv[3] if len(sys.argv) > 3 else "extensions.txt"
        numbers = generate_batch(count=count)
        write_extension_file(numbers, outfile)

    elif mode == "load":
        if len(sys.argv) < 4:
            print("Usage: python3 sipvicious_output.py load <input_file> <output_file>")
            sys.exit(1)
        numbers = load_from_file(sys.argv[2])
        write_extension_file(numbers, sys.argv[3])

    elif mode == "svwar":
        if len(sys.argv) < 4:
            print("Usage: python3 sipvicious_output.py svwar <host> <extension_file>")
            sys.exit(1)
        cmd = build_svwar_command(host=sys.argv[2], extension_file=sys.argv[3])
        run_command(cmd, dry_run=True)  # dry_run=True for safety; remove to execute

    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

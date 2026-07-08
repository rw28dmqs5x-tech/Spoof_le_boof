"""
target_loader.py

Load and validate a list of E.164 phone numbers from a file or list.
Used to feed validated targets into other modules.
"""

from typing import List, Optional
from phone_generator import is_valid_e164


def load_from_file(filepath: str) -> List[str]:
    """
    Load newline-separated E.164 numbers from a text file.
    Lines that are empty or fail validation are silently skipped.

    Args:
        filepath: path to a plain text file, one number per line.

    Returns:
        List of validated E.164 strings.
    """
    results = []
    with open(filepath, "r") as f:
        for line in f:
            number = line.strip()
            if number and is_valid_e164(number):
                results.append(number)
    return results


def load_from_list(numbers: List[str]) -> List[str]:
    """
    Validate a list of number strings and return only valid E.164 entries.

    Args:
        numbers: list of strings to validate.

    Returns:
        Filtered list of valid E.164 strings.
    """
    return [n.strip() for n in numbers if is_valid_e164(n.strip())]


def save_to_file(numbers: List[str], filepath: str) -> None:
    """
    Write a list of E.164 numbers to a file, one per line.

    Args:
        numbers: list of E.164 strings.
        filepath: output file path.
    """
    with open(filepath, "w") as f:
        for number in numbers:
            f.write(number + "\n")
    print(f"[+] Saved {len(numbers)} numbers to {filepath}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 target_loader.py <input_file> [output_file]")
        sys.exit(1)

    loaded = load_from_file(sys.argv[1])
    print(f"[+] Loaded {len(loaded)} valid numbers:")
    for n in loaded:
        print(n)

    if len(sys.argv) == 3:
        save_to_file(loaded, sys.argv[2])

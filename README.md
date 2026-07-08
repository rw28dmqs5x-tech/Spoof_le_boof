# Spoof_le_boof

A modular phone number toolkit for security testing and penetration testing.

> ⚠️ **Authorization Required**: All network interaction features must only be used against systems you own or have explicit written authorization to test. Unauthorized use may violate the CFAA, TCPA, and FCC regulations.

---

## Modules

### `phone_generator.py`
Generates fake E.164-format phone numbers for test data.

```python
from phone_generator import generate_e164, generate_batch, is_valid_e164

# Single number
print(generate_e164())                          # +1XXXXXXXXXX (random)
print(generate_e164(seed=42))                   # deterministic
print(generate_e164(country_code="44", national_length=10))  # UK-style

# Batch
numbers = generate_batch(count=10, seed=99)

# Validate
print(is_valid_e164("+14085551234"))  # True
```

---

### `target_loader.py`
Load and validate a list of target numbers from a file.

```bash
# Validate a file of numbers
python3 target_loader.py targets.txt

# Validate and save clean output
python3 target_loader.py targets.txt clean_targets.txt
```

```python
from target_loader import load_from_file, load_from_list

targets = load_from_file("targets.txt")
targets = load_from_list(["+14085551234", "badnumber", "+442071234567"])
```

---

### `twilio_tester.py`
Send test SMS or calls via Twilio to numbers you own.

```bash
pip3 install twilio
export TWILIO_ACCOUNT_SID="ACxxxx"
export TWILIO_AUTH_TOKEN="your_token"
export TWILIO_FROM="+1XXXXXXXXXX"

python3 twilio_tester.py +1YOURNUMBER "Test message"
```

```python
from twilio_tester import send_sms, make_call, batch_sms

send_sms(to="+1YOURNUMBER", body="Test")
make_call(to="+1YOURNUMBER", twiml_url="https://yourserver.com/twiml")
```

---

### `sipvicious_output.py`
Format number lists for SIPVicious (`svwar`, `svmap`) VoIP enumeration.

```bash
pip3 install sipvicious

# Generate fake extensions and write to file
python3 sipvicious_output.py generate 20 extensions.txt

# Load from your own target file
python3 sipvicious_output.py load targets.txt extensions.txt

# Dry-run a svwar command (prints command, does not execute)
python3 sipvicious_output.py svwar 192.168.1.1 extensions.txt
```

```python
from sipvicious_output import build_svwar_command, build_svmap_command, run_command

cmd = build_svwar_command(host="192.168.1.1", extension_file="extensions.txt")
run_command(cmd, dry_run=False)  # set dry_run=False to actually execute
```

---

## Installation

```bash
git clone https://github.com/rw28dmqs5x-tech/Spoof_le_boof.git
cd Spoof_le_boof
pip3 install phonenumbers          # for validation
pip3 install twilio                # for Twilio module
pip3 install sipvicious            # for SIPVicious module
```

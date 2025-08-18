# social_dm

A modular, compliant scaffold for social DM workflows. **No platform automation is implemented**—only placeholders and a queue. Plug in official APIs later.

## Quickstart
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

python -m pip install pytest -q || echo "pytest optional"

python app.py collect --sample --csv data/sample_users.csv
python app.py queue --size
python app.py send --limit 3 --message "Hello from social_dm!"
```

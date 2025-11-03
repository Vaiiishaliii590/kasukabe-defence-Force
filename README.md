# Historical Character Interview — Flask MVP

A minimal Flask app that renders three hard-coded historical character cards (Einstein, Newton, Aryabhatta) using HTML templates and CSS only.

## Run locally (Windows PowerShell)

```powershell
cd "C:\Users\Vaish\OneDrive\Desktop\Data"

# 1) Create and activate a virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
flask run
```

Then open `http://127.0.0.1:5000` in your browser.

## Configure Gemini API key

Preferred: use a `.env` file (not committed to git):

1) Copy the example and add your key
```powershell
Copy-Item .env.example .env
# edit .env and set GEMINI_API_KEY
```

2) Or set the variable in your shell
```powershell
$env:GEMINI_API_KEY = "YOUR_KEY_HERE"
```

macOS/Linux:
```bash
export GEMINI_API_KEY="YOUR_KEY_HERE"
```

The page buttons (Ask Einstein/Newton/Aryabhatta) call `/api/interview?character=...` which uses Gemini to generate the intro.

### Configure Gemini API Key
Set your Gemini API key before running:

```powershell
$env:GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```

Buttons on the cards will call the backend to generate the self-introduction using Gemini.

## Notes
- No JavaScript; all content is static and hard-coded for MVP.
- Styling is embedded in `templates/base.html` for simplicity.
- Future enhancements (interactivity, JSON data, filters) can be added later.

## Alternate run (direct)

```powershell
python app.py
```

Environment overrides:

```powershell
$env:HOST = "0.0.0.0"   # bind to all interfaces (optional)
$env:PORT = "5000"      # change port (optional)
$env:FLASK_DEBUG = "0"  # disable debug in production
python app.py
```

## Deployment entrypoint
- WSGI module: `wsgi:application`
- Health check path: `/health`


"# kasukabe-defence-Force" 
"# kasukabe-defence-Force" 

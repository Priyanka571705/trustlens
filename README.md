# TrustLens - AI Scam Detector

## Local Setup
1. Install dependencies: pip install -r requirements.txt
2. Create .env file: copy .env.example to .env and add your Gemini API key
3. Run: python app.py
4. Open: http://127.0.0.1:5000

## Deploy on Render (Free)
1. Push this project to GitHub
2. Go to render.com → New Web Service
3. Connect your GitHub repo
4. Set Environment Variable: GEMINI_API_KEY = your key
5. Start Command: gunicorn app:app
6. Click Deploy → get your public URL!

## Project Structure
trustlens/
├── app.py              # Flask backend + Gemini API call
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Keeps .env secret from GitHub
└── templates/
    └── index.html      # Frontend UI

# Unnamed Project - M1

A full-stack application for analyzing Tokopedia product reviews with AI-powered insights.

## Quick Start

### Prerequisites

- Python 3.10+ (Python 3.12 recommended)
- Node.js 16+ & npm
- Chrome browser (web scraping)
- LLM API Key

### 1. Backend Setup

```bash
# Install dependencies required
pip install -r requirements.txt

# Start backend server
python -m uvicorn app.main:app --reload
```

Backend will run at: `http://localhost:8000`

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Frontend will run at: `http://localhost:5173`

## How To Use

1. Open `http://localhost:5173` in your browser
2. Paste a Tokopedia product URL
3. Click "Analyze Product" and wait for results
4. Use the AI chat to ask questions about the analysis

## API Endpoints

- `GET /` - API welcome message
- `POST /api/v1/analyze` - Analyze product reviews
- `POST /api/v1/chat` - Chat with AI about analysis


## Troubleshooting

**Backend won't start:**

- Check if virtual environment is activated
- Verify API keys in `.env` file
- Ensure port 8000 is not in use

**Frontend won't connect:**

- Verify backend is running on port 8000
- Check CORS settings in backend `.env`
- Confirm `VITE_API_BASE_URL` in frontend `.env`

**Scraping fails:**

- Ensure Chrome browser is installed
- Check if Tokopedia URL is valid and accessible
- Some products may not have reviews

## Architecture

- **Frontend**: Vite + React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python + Selenium + BeautifulSoup
- **AI**: Google Gemini 2.5 Flash + ChromaDB vector store
- **Scraping**: Selenium WebDriver for dynamic content

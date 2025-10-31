# Market Data Dashboard

Personal trading dashboard built with FastAPI and Next.js.

## Setup

### Backend

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment file:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run server:
```bash
uvicorn main:app --reload --port 8000
```


### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run dev server:
```bash
npm run dev
```

Front-end run on local 

## Current Features

- Health check endpoint
- Basic frontend that connects to backend
- Configuration management via environment variables


# Buffett Portfolio Analyzer

A web application that analyzes stock portfolios using Warren Buffett's investment principles.

## Live Demo
[Visit the website](https://buffett-portfolio-analyzer-iiitd.vercel.app)

## Features
- Add and track multiple stocks
- Analyze stocks based on fundamental metrics
- View detailed stock information including P/E ratio, ROE, and more
- Real-time stock data updates
- Mobile-responsive design

## Tech Stack
- Frontend: React + Vite with Material-UI
- Backend: Flask
- Database: SQLite
- APIs: Alpha Vantage for stock data

## Setup

### Backend
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file in the root directory with:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

3. Run the backend:
```bash
python src/app.py
```

### Frontend
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```
VITE_API_URL=http://localhost:5001
```

4. Run the development server:
```bash
npm run dev
```

## Deployment
- Backend: Deployed on Render.com
- Frontend: Deployed on Vercel

## Environment Variables
### Backend
- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key

### Frontend
- `VITE_API_URL`: Backend API URL 

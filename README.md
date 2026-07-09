# RTK Dashboard

A cloud dashboard for monitoring token savings from [RTK](https://github.com/anomalyco/rtk) across multiple machines.

```
RTK-Dashboard/
├── api/          # FastAPI backend
├── frontend/     # React + Vite + Tailwind
└── sync/         # Python CLI sync agent
```

## Quick Start

```bash
# 1. Setup API
cd api
cp .env.example .env  # edit JWT_SECRET
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Setup Frontend
cd ../frontend
npm install
npm run dev

# 3. Setup Sync Agent
cd ../sync
pip install -e .
rtk-dash-sync init --api-url http://localhost:8000
rtk-dash-sync sync --watch
```

- **Frontend:** http://localhost:5173
- **API:** http://localhost:8000
- **Admin:** `admin@rtk.ai` / `admin123`
- **Demo:** `demo@rtk.ai` / `demo123`

## Docker

```bash
docker compose up -d
```

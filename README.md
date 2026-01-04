# 🚀 ShortIt - Your real-world URL Shortener

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D.svg?logo=vue.js)
![Redis](https://img.shields.io/badge/Redis-Caching-red.svg?logo=redis)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Relational_DB-blue.svg?logo=postgresql)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-Styling-38B2AC.svg?logo=tailwind-css)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A production-grade, scalable URL shortener featuring a **Decoupled Full-Stack Architecture**. Combines a high-performance **FastAPI** backend (handling 150+ RPS) with a modern **Vue.js** frontend dashboard. The system features real-time **Geo-Analytics**, QR code generation, and a non-blocking architecture optimized for speed.

---

## System Architecture

The system uses a **Decoupled Architecture**, separating the UI from the API to allow independent scaling and deployment.

### High-Level Design
1. **Frontend (SPA):** A lightweight Vue.js application running on Port 8080. Handles UI state, data visualization, and communicates via REST API.
2. **Backend (API):** A stateless FastAPI server running on Port 8000. Handles business logic, caching, and background processing.
3. **Geo-Intelligence:** Background workers resolve user IP addresses to physical locations (City/Country) asynchronously to prevent latency.

```mermaid
graph TD
    User[User / Browser]
    
    subgraph "Frontend Layer (Port 8080)"
        UI[Vue.js Dashboard]
    end

    subgraph "Backend Layer (Port 8000)"
        API[FastAPI Server]
        Worker[Background Worker]
    end

    subgraph "Data & External"
        Redis[(Redis Cache)]
        DB[(PostgreSQL)]
        GeoAPI[IP-Location Service]
    end

    User -->|Visits UI| UI
    UI -->|REST API Calls| API
    User -->|Redirect Link| API
    
    API -->|1. Check Cache| Redis
    API -->|2. DB Fallback| DB
    API -.->|3. Async Event| Worker
    
    Worker -->|4. Resolve IP| GeoAPI
    Worker -->|5. Save Analytics| DB
```

---

## ⚡ Performance & Stress Testing

We benchmarked the system using **Locust** to simulate high-concurrency traffic under a sustained load of **100 concurrent users** with zero wait time.

### 📊 Load Test Results

* **Tool:** Locust.io
* **Scenario:** High-Traffic Viral Event
* **Concurrency:** 100 Users (Zero Sleep)
* **Endpoint:** `GET /{short_code}` (Redirect + Analytics)

| Metric | Result |
|:---|:---|
| **Total Requests** | **312,123** |
| **Throughput (RPS)** | **~157 req/sec** (Localhost limited) |
| **Failure Rate** | **0%** (Zero 5xx/4xx errors) |
| **P50 Latency (Median)** | 610ms |
| **P99 Latency** | 1100ms |

> *Note: Tests performed on a local Windows development machine. Cloud deployment expected to yield significantly higher throughput due to OS networking optimizations.*

---

## 🛠️ Key Features

### 1. 🌍 Geo-Analytics & Intelligence

* **Location Tracking:** Automatically resolves user IP to Country and City using async HTTP clients.
* **Non-Blocking Writes:** Uses `BackgroundTasks` to perform Geo-Lookups and DB writes after the response is sent, ensuring instant user redirects.
* **Visual Analytics:** Dashboard displays real-time click data with geographic information.
* **Privacy-Aware:** IP addresses are resolved to city-level data, not stored raw for privacy compliance.

### 2. 📊 Modern Frontend Dashboard

* **Vue.js 3:** Reactive UI for creating links and viewing stats without page reloads using Composition API.
* **Visual Analytics:** View real-time click tables with timestamp, country, and city data.
* **UX Enhancements:** Loading spinners, copy-to-clipboard functionality, and comprehensive error handling.
* **Responsive Design:** Tailwind CSS ensures seamless experience across desktop, tablet, and mobile devices.

### 3. 🚀 Backend Optimizations

* **Redis Look-Aside Cache:** Hot URLs served from memory (~5ms response time).
* **Connection Pooling:** SQLAlchemy engine tuned with `pool_size=20` for handling concurrent requests.
* **Rate Limiting:** Token-bucket algorithm prevents API abuse with configurable limits.
* **Async Processing:** All I/O operations use async/await for maximum throughput.

### 4. 📦 Few More Extras

* **QR Codes:** Instant on-the-fly QR generation for every shortened link using Pillow.
* **CORS Security:** Configured to allow secure cross-origin requests between Frontend and Backend.
* **Custom Aliases:** Support for vanity URLs (e.g., `/my-brand-link`).
* **Secret Keys:** Admin management endpoints protected by unique secret keys.

---

## 🔧 Tech Stack

### Frontend

* **Framework:** Vue.js 3 (Composition API)
* **Styling:** Tailwind CSS (CDN)
* **HTTP Client:** Fetch API
* **Hosting:** Static Server (Port 8080) / CDN-ready

### Backend

* **Language:** Python 3.12
* **Framework:** FastAPI (ASGI)
* **Server:** Uvicorn
* **Database:** PostgreSQL 16
* **Cache:** Redis (Memurai on Windows)
* **HTTP Client:** HTTPX (Async)
* **Testing:** Locust (Load), Pytest (Unit)
* **Image Processing:** Pillow (QR Codes)
* **Deployment:** Docker / Railway.app

---

## Quick Start

### Prerequisites

* Python 3.11+
* PostgreSQL 14+
* Redis 6+
* Node.js (optional, for npm-based frontend setup)

### 1. Backend Setup (Port 8000)

```bash
# Clone and Install
git clone https://github.com/yourusername/url-shortener.git
cd url-shortener
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

**Configure `.env`:**

```ini
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/shortener_db

# Redis
REDIS_URL=redis://localhost:6379

# Server
HOST=0.0.0.0
PORT=8000
```

**Run Backend Server:**

```bash
uvicorn src.main:app --reload
```

### 2. Frontend Setup (Port 8080)

Open a new terminal window:

```bash
cd frontend
python -m http.server 8080
```

Alternatively, use any static server:

```bash
# Using Node.js
npx serve frontend -p 8080

# Using PHP
php -S localhost:8080 -t frontend
```

### 3. Usage

1. Open browser to `http://localhost:8080`
2. Create a shortened link through the dashboard
3. View real-time analytics with geographic data
4. Test the redirect by visiting `http://localhost:8000/{short_code}`

---

## API Endpoints

### Core Functionality

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/shorten` | Create a new shortened URL with optional custom alias |
| `GET` | `/{short_code}` | Redirect to original URL and track analytics |
| `GET` | `/{short_code}/stats` | **(Protected)** Get detailed analytics with geo data |
| `GET` | `/{short_code}/qr` | Generate and download QR code |
| `DELETE` | `/{short_code}` | **(Protected)** Delete shortened URL |

### Example Request

```bash
# Create Short URL
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/very/long/url",
    "custom_alias": "my-link"
  }'

# Get Analytics
curl -X GET "http://localhost:8000/my-link/stats" \
  -H "X-Secret-Key: your_secret_key_here"
```

---

## 🌍 Geo-Analytics Dashboard

The Vue.js dashboard provides real-time insights into link performance:

### Features

* **Click Timeline:** Chronological list of all clicks with timestamps
* **Geographic Distribution:** See which countries and cities are clicking your links
* **Device Analytics:** User-Agent parsing shows browser and device types
* **Real-Time Updates:** Dashboard fetches latest data on page load
* **Export Ready:** Data formatted for easy export to CSV/Excel

### Sample Analytics View

```
┌───────────────────────────────────────────────────────────┐
│ Link: https://short.url/abc123                            │
│ Original: https://example.com/very/long/url               │
│ Total Clicks: 1,234                                       │
├───────────────────────────────────────────────────────────┤
│ Timestamp           │ Country    │ City          │ Device │
├─────────────────────┼────────────┼───────────────┼────────┤
│ 2024-12-03 14:23:01 │ USA        │ New York      │ Chrome │
│ 2024-12-03 14:22:45 │ India      │ Mumbai        │ Safari │
│ 2024-12-03 14:22:12 │ UK         │ London        │ Firefox│
└───────────────────────────────────────────────────────────┘
```

---

## 🔗 Live Demo

Access the production application:

* **Frontend Dashboard:** `https://short-it-rosy.vercel.app/`
* **Backend API Docs:** `https://url-shortener-production.up.railway.app/docs`

---

## 🚀 Future Scope & Improvements

* **User Authentication:** Add JWT-based user accounts to manage personal links and team workspaces.
* **Advanced Analytics:** Implement conversion tracking, referrer analysis, and A/B testing capabilities.
* **Link Expiration:** Add TTL support for temporary links that auto-expire after set duration.
* **Webhooks:** Real-time notifications when links reach click milestones or specific events occur.
* **Browser Extension:** Chrome/Firefox extension for one-click URL shortening from any webpage.
* **API Rate Limiting Tiers:** Implement tiered rate limits for free/premium users.
* **Custom Domains:** Allow users to use their own domains for branded short links.
* **Bulk Operations:** Upload CSV of URLs for batch shortening and management.

"In production, each organization has their own secure account. For this demo the app runs in single-tenant mode so judges can use it immediately."

# 🛡 VendorGuard AI
### Third-Party Vendor Risk Intelligence Agent

> **"Know when any of your vendors becomes a risk — before it becomes your problem."**

Built for the **Web Data UNLOCKED Hackathon 2026** — powered by Bright Data infrastructure.

---

## 🎯 The Problem

Every company works with dozens of external vendors — payment processors, cloud providers, HR software, logistics partners. If any one of those vendors gets hacked, breaks a law, faces bankruptcy, or leaks data — your company is also at risk.

**Right now, most companies find out weeks later. Sometimes never.**

- A vendor's credentials leak on a dark web forum → you find out in 3 weeks
- A vendor faces an SEC investigation → you find out when it's on the news
- A vendor's employees are mass-resigning → you find out when service degrades

**VendorGuard AI solves this.**

---

## ✅ The Solution

VendorGuard AI is an intelligent agent that monitors all your vendors 24/7 on the live web. It collects risk signals from multiple sources, analyzes them with AI, and gives each vendor a **Risk Score (0–100)** with a full intelligence report.

When a vendor's risk jumps — you get an **instant email alert** before it makes the news.

---

## 🚀 Key Features

### 🔍 Real-Time Risk Scanning
- Scans Google News for vendor scandals, hacks, lawsuits, fines
- Monitors regulatory signals (SEC, FTC, government enforcement)
- Detects early warning signals — layoffs, CEO exits, legal hiring spikes
- Directly scrapes Wikipedia for verified factual risk data
- Checks vendor's own website for incident notices

### 📊 AI Risk Scoring (0–100)
- Every vendor gets a risk score powered by Groq (Llama 3.3 70B)
- Score breakdown by category: Cybersecurity, Regulatory, Financial, Reputational
- Risk timeline chart showing score history over time
- Confidence level indicator

### 🚨 Instant Email Alerts
- Automatic email alert when vendor risk score jumps 10+ points
- Beautiful HTML email with full risk report
- Critical alerts for scores above 61/100

### 📄 PDF Report Export
- One-click professional PDF report download
- Ready to present to CEO, board, or compliance team
- Includes executive summary, key findings, risk breakdown, recommended actions

### 📂 Bulk CSV Import
- Import hundreds of vendors at once via CSV file
- Download sample template to get started instantly
- Perfect for enterprises with large vendor lists

### 🔄 Rescan All Vendors
- One-click rescan of entire vendor portfolio
- Automatic risk comparison with previous scores
- Alert generation when scores change significantly

---

## 🛠 Bright Data Tools Used

| Tool | How We Use It |
|---|---|
| **SERP API** | Real-time Google News search for vendor risk signals |
| **Browser API** | Direct Wikipedia scraping for verified primary source data |
| **Browser API** | Direct vendor website scanning for incident notices |
| **MCP Server** | Connected to AI agent for live web intelligence |

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React.js + Recharts + Lucide Icons |
| Backend | Python + FastAPI |
| AI Brain | Groq API (Llama 3.3 70B) — FREE |
| Data Collection | Bright Data SERP API + Browser API |
| Database | SQLite |
| Email Alerts | Gmail SMTP |
| PDF Generation | ReportLab |

---

## 📁 Project Structure

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Bright Data account with $250 credits
- Groq API key (free)
- Gmail account with App Password

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/vendorguard-ai
cd vendorguard-ai/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat  # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install fastapi uvicorn requests python-dotenv groq reportlab playwright python-multipart

# Install Playwright browser
playwright install chromium

# Create .env file
cp .env.example .env
# Fill in your API keys

# Start backend
python -m uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend/vendorguard-ui
npm install
npm start
```

### Environment Variables

Create a `.env` file in the backend folder:

```env
GROQ_API_KEY=your_groq_api_key
BRIGHTDATA_API_KEY=your_brightdata_api_key
BRIGHTDATA_SERP_ZONE=serp_zone
BRIGHTDATA_BROWSER_USER=your_browser_zone_username
BRIGHTDATA_BROWSER_PASS=your_browser_zone_password
BRIGHTDATA_BROWSER_HOST=brd.superproxy.io
BRIGHTDATA_BROWSER_PORT=9222
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENT=alerts@yourcompany.com
```

---

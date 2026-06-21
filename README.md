# 🌱 CarbonPulse - Real-time Carbon Footprint Analytics Platform

**CarbonPulse** is a production-grade, highly-responsive carbon footprint estimator and analytical tracker. It empowers users to monitor, simulate, and ledger their personal environmental impact through real-time mathematical computations and sleek visual interfaces.

The project features a unified mathematical core compliant with standard EPA and Greenhouse Gas (GHG) Protocol guidelines, available as both a compiled **React + TypeScript SPA** and a fully standalone **Python + Streamlit dashboard**.

---

## 🚀 Key Features

*   **Real-time Computations**: As you slide parameters or check checkboxes, emission breakdowns and totals update instantly without blocking popups.
*   **Dual-Implementation**:
    *   **TypeScript + React Frontend**: Rich client-side single-page app utilizing Vanilla CSS and modern layout controls.
    *   **Python + Streamlit App**: A sleek Python dashboard built using custom columns, real-time SVG charts, and interactive metric components.
*   **Calculations & Offsets Simulator**: Integrate customized offset checklist actions (such as switching to EVs or adopting composting) to see your projected footprints dynamically.
*   **Historical Ledger & SQLite Integration**: Save calculation logs directly into a local SQLite ledger database and view trends with dynamic SVG sparkline charts.

---

## 🛠️ Tech Stack

*   **Frontend**: React, TypeScript, Vite, Vanilla CSS.
*   **Python Dashboard**: Streamlit, Uvicorn.
*   **Database**: SQLite (`carbonpulse.db`).
*   **Core Logic**: EPA / GHG Protocol conversion factors.

---

## 📂 Project Structure

```text
├── app.py                      # Streamlit Application
├── server.py                   # Python Static Web Server + REST APIs
├── requirements.txt            # Python Dependencies
├── package.json                # Node/React Dependencies
├── src/
│   ├── components/             # Estimator, Dashboard, and History UI
│   ├── utils/
│   │   └── emissionFactors.ts  # Mathematical Core Formulas
│   └── tests/
│       └── calculation.test.ts # Core Mathematical Unit Tests
└── dist/                       # Compiled React Production Assets
```

---

## ⚡ Quick Start

### Python Streamlit Application
Activate the virtual environment and launch Streamlit:
```bash
source .venv/bin/activate
STREAMLIT_SERVER_HEADLESS=true streamlit run app.py --server.port 8501
```
Open **`http://localhost:8501`** in your browser.

### React + Python Backend
Launch the API backend to serve production compiled assets:
```bash
python3 server.py
```
Open **`http://localhost:8000`** in your browser.

---

## 🧪 Testing

Run core conversion logic unit tests:
```bash
node dist/tests/tests/calculation.test.cjs
```

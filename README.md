# 🏔️ Everest Brewing — Enterprise RAG AI Assistant & SCADA Operational Dashboard
### *Pure Python & SQL Edition (Streamlit + SQLite + Plotly)*

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit)](https://everest-brewing-rag.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.61%2B-FF4B4B.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)](https://www.sqlite.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-3F4F75.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Production-Ready-success.svg)]()

> 🚀 **Live Cloud App**: **[https://everest-brewing-rag.streamlit.app/](https://everest-brewing-rag.streamlit.app/)**  
> An end-to-end **Retrieval-Augmented Generation (RAG) AI Chatbot** and **Real-Time SCADA Operations Control Center** built entirely in **Python & SQL**.  
> Features employee authentication, Quality & Rework Control, comprehensive HR Benefits & Vacation Policies, interactive Plotly industrial gauges, live telemetry historian logging, direct SQLite analytics explorer, and runtime SOP document ingestion.

> [!IMPORTANT]
> **⚖️ Legal Disclaimer & Notice**:  
> This open-source repository and demonstration application are developed **solely for independent academic, educational, and technical research purposes**.  
> All operational benchmarks, standard operating procedures (SOPs), and SCADA telemetry data are synthetic, fictitious approximations designed solely to illustrate Retrieval-Augmented Generation (RAG) software architectures.

---

## 🔐 Employee Authentication & Access Control

Access to the portal is restricted to authenticated company employees via Company Employee ID and password:

| Employee ID | Name | Role / Department | Security Clearance | Default Password |
|---|---|---|---|---|
| `EVR-1001` | Marcus Vance | Lead Packaging Operator (Production) | Level 2 - Plant Operations | `Everest2026!` |
| `EVR-1042` | Dr. Sarah Lin | Master Brewer & QA Director (Quality) | Level 4 - Quality & Cellar Lead | `Everest2026!` |
| `EVR-2005` | David Tremblay | EHS & Safety Compliance Manager (HR) | Level 4 - EHS Administrator | `Everest2026!` |
| `ADMIN-001` | System Administrator | Enterprise Operations Admin | Level 5 - Master Access | `Everest2026!` |

---

## 🌟 Key Departmental Modules

| Pillar / Component | Feature Details |
|---|---|
| 🔬 **Quality & Rework Control** | **Analytical Quality Gate** (ABV 5.0% ± 0.1%, IBU 12.0, DO < 20 ppb, Micro 0 CFU/100mL, 5-member sensory release), **Double Seam Teardown** (Overlap >55%, Tightness >90%), **Line 4 Optical Inspector (EBI)** (99.98% accuracy), **Quarantine Holds & Rework SOPs** (deaerated CO₂ sparging, decanting), and **Live SQLite Non-Conformance Report (NCR) Rework Ticket Creator**. |
| 🛡️ **HR, Benefits & Safety** | **Tenure Vacation Tiers** (1-3 yrs = 15 days; 4-7 yrs = 20 days; 8-12 yrs = 25 days; 13+ yrs = 30 days), **5 Paid Sick/Personal Days**, **10 Statutory Holidays (2.0x pay)**, **100% 16-Week Parental Top-Up**, **Healthcare & Dental Benefits** ($2,500/yr major dental, $450 vision, $1,000 mental health), **6% Pension Match**, **Shift Premiums** (+$1.25 afternoon, +$2.50 night), **EHS Gas Sensors** (NH₃, CO₂, CSE O₂ 20.9%), and **Live Near-Miss Incident Portal**. |
| 🏭 **Production & Packaging** | 3 Dedicated Packaging Lines: **Line 1 Can** (~2,000 hL/8h), **Line 3 Can** (~1,800 hL/8h), **Line 4 Bottle** (1,000 bpm / 800–1,200 hL/8h), total shift throughput (~4,800 to 5,000 hL/8h). |
| 🍺 **Brewing Science** | Mashing profiles (65°C rest), yeast pitching (*S. pastorianus* EVR-04), fermentation temp gauges, diacetyl reduction, pasteurization PU target (18 PU). |
| 🚚 **Logistics & Fleet** | Cold-chain transit monitoring (-1.5°C to 4.0°C), distribution hubs, reverse logistics keg return cycle ($30 deposit). |
| 💼 **Administration & ESG** | ERP PO 3-way matching, CapEx approval matrices, 2026 ESG goals (2.10 L/L water-to-beer ratio, 100% renewable power). |
| 🤖 **RAG AI Assistant** | Jaccard + TF-IDF hybrid vector search with confidence scoring, execution time tracking, and expandable source citation cards. |
| 🗄️ **SQL Database & Analytics** | Built-in SQLite database (`database/everest.db`) storing all chat queries, SCADA telemetry time series, incident reports, quality rework logs, and ingested documents with live SQL editor. |

---

## 📐 System Architecture (100% Python & SQL)

```
┌─────────────────────────────────────────────────────────────────┐
│               STREAMLIT WEB UI — app.py                         │
│  ├── Employee Authentication Wall (Role-based ID & Password)    │
│  ├── Executive Overview (KPI Metrics + Plotly SCADA Trends)     │
│  ├── 🔬 Quality & Rework Hub (Analytical Lab + Double Seam)     │
│  ├── 🛡️ HR, Benefits & Safety Hub (Vacation Tiers + EHS)        │
│  ├── 3 Packaging Lines (Line 1 Can, Line 3 Can, Line 4 Bottle)  │
│  ├── Department Control Panels (Brewing, Prod, Log, Admin, HR)  │
│  ├── RAG AI Assistant (st.chat_message + Source Citations)      │
│  └── SQL Database & Analytics Explorer (SQL Query Runner + CSV) │
└────────────────────────┬────────────────────────────────────────┘
                         │ Calls directly in Python
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON ENGINE LAYER                          │
│  ├── rag_engine.py      (Hybrid vector search & context synthesis)│
│  ├── kb_loader.py       (JSON ingestion + runtime memory sync)  │
│  ├── live_telemetry.py  (SCADA sensor simulator & stream)        │
│  └── everest_db.py      (SQLite ORM, Rework & Incident Logging) │
└──────────────────┬─────────────────────────────┬────────────────┘
                   │                             │
                   ▼                             ▼
┌──────────────────────────────────┐ ┌────────────────────────────┐
│      SQLITE DATABASE             │ │   KNOWLEDGE BASE (JSON)    │
│      database/everest.db         │ │   data/everest_kb/         │
│  ├── chat_history table          │ │   ├── 01_logistics.json    │
│  ├── telemetry_log table         │ │   ├── 02_brewing.json      │
│  ├── incident_reports table      │ │   ├── 03_production.json   │
│  ├── quality_rework_log table    │ │   ├── 04_administration.json│
│  └── ingested_documents table    │ │   ├── 05_hr_compliance.json│
│                                  │ │   └── 06_quality.json      │
└──────────────────────────────────┘ └────────────────────────────┘
```

---

## 🚀 Quick Start & Installation

### Step 1: Install Requirements
```powershell
python -m pip install streamlit plotly pydantic requests pandas
```

### Step 2: Run the Streamlit Application
```powershell
python -m streamlit run app.py
```
*(Or double-click `run_streamlit.bat` on Windows)*

The application opens automatically in your browser at:
👉 **`http://localhost:8501`**

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) — © 2026 Everest Brewing RAG AI Platform Contributors.

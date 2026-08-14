import streamlit as st
import sys
import os
import time
import json
import uuid
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Add backend directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
sys.path.insert(0, os.path.join(BASE_DIR, "database"))

from app.kb_loader import KBLoader
from app.rag_engine import RAGEngine
from app.live_telemetry import TelemetryManager
from everest_db import EverestDB

# Page Config
st.set_page_config(
    page_title="Everest Brewing | Enterprise Operations & RAG AI Platform",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Demo Employee Accounts Database
EMPLOYEE_DIRECTORY = {
    "EVR-1001": {
        "password": "Everest2026!",
        "name": "Marcus Vance",
        "title": "Lead Packaging Line Operator",
        "department": "Production",
        "shift": "Shift 1 - Day (07:00 - 15:00)",
        "clearance": "Level 2 - Plant Operations",
        "tenure": "3 Years of Service",
        "vacation_entitlement": "15 Days / Year (3 Weeks)",
        "pto_balance": "12.5 Days Remaining",
        "certifications": ["WHMIS 2015", "LOTO Energy Isolation", "Forklift Certified"]
    },
    "EVR-1042": {
        "password": "Everest2026!",
        "name": "Dr. Sarah Lin",
        "title": "Master Brewer & Quality Director",
        "department": "Quality",
        "shift": "Shift 1 - Day (07:00 - 15:00)",
        "clearance": "Level 4 - Quality & Cellar Lead",
        "tenure": "6 Years of Service",
        "vacation_entitlement": "20 Days / Year (4 Weeks)",
        "pto_balance": "16.0 Days Remaining",
        "certifications": ["HACCP Lead Auditor", "Confined Space Supervisor", "Microbiology Gate Specialist"]
    },
    "EVR-2005": {
        "password": "Everest2026!",
        "name": "David Tremblay",
        "title": "EHS & Safety Compliance Manager",
        "department": "Other",
        "shift": "Executive / All Shifts",
        "clearance": "Level 4 - EHS Compliance Administrator",
        "tenure": "9 Years of Service",
        "vacation_entitlement": "25 Days / Year (5 Weeks)",
        "pto_balance": "21.0 Days Remaining",
        "certifications": ["CRSP Safety Professional", "Ammonia PSM Lead", "CSE Tripod Rescue", "LOTO Auditor"]
    },
    "ADMIN-001": {
        "password": "Everest2026!",
        "name": "System Administrator",
        "title": "Enterprise Operations Admin",
        "department": "Administration",
        "shift": "24/7 Operations",
        "clearance": "Level 5 - Full System Master Access",
        "tenure": "10+ Years of Service",
        "vacation_entitlement": "30 Days / Year (6 Weeks)",
        "pto_balance": "28.0 Days Remaining",
        "certifications": ["All Certifications Active"]
    }
}

# Initialize singletons in session_state
if "db" not in st.session_state:
    st.session_state.db = EverestDB()

if "kb_loader" not in st.session_state:
    data_dir = os.path.join(BASE_DIR, "data", "everest_kb")
    st.session_state.kb_loader = KBLoader(data_dir)

if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine(st.session_state.kb_loader)

if "telemetry_mgr" not in st.session_state:
    st.session_state.telemetry_mgr = TelemetryManager()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "Hello! I am your **Everest Brewing Enterprise RAG AI Assistant**. Ask me anything regarding quality standards & rework protocols, vacation & leave policies, health & pension benefits, 3 packaging lines (Lines 1, 3, 4), brewing recipes, cold chain logistics, or WHMIS safety protocols.",
            "sources": [],
            "confidence": 1.0,
            "exec_ms": 0.0
        }
    ]

# Custom CSS styling for Everest branding
st.markdown("""
<style>
    .brand-header {
        display: flex;
        align-items: center;
        gap: 15px;
        background: linear-gradient(135deg, #001C38, #070D18);
        border: 1px solid rgba(0, 229, 255, 0.2);
        padding: 18px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .brand-badge {
        background: linear-gradient(135deg, #002B49, #001222);
        border: 1px solid #E6C200;
        color: #E6C200;
        font-weight: 800;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 1.3rem;
        letter-spacing: 1px;
    }
    .status-live {
        background: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .login-box {
        background: rgba(13, 25, 43, 0.95);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 14px;
        padding: 30px;
        max-width: 500px;
        margin: 40px auto;
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.15);
    }
    .user-card {
        background: rgba(7, 13, 24, 0.7);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# AUTHENTICATION WALL (COMPANY EMPLOYEE ACCESS ONLY)
# -------------------------------------------------------------
if st.session_state.logged_in_user is None:
    st.markdown("""
    <div style="text-align:center; margin-top:20px;">
        <div style="display:inline-block; background:linear-gradient(135deg, #002B49, #001222); border:1px solid #E6C200; color:#E6C200; font-weight:800; padding:10px 24px; border-radius:10px; font-size:1.8rem; letter-spacing:2px;">
            🏔️ EVEREST BREWING COMPANY
        </div>
        <h2 style="color:#FFF; margin-top:15px;">Employee Operations, Quality & AI Portal</h2>
        <p style="color:#00E5FF; font-size:0.95rem;">Internal Access Only — Authenticated Employee Credentials Required</p>
    </div>
    """, unsafe_allow_html=True)

    c_center = st.columns([1, 2, 1])[1]
    with c_center:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("🔐 Company Employee Sign In")
        
        emp_id = st.text_input("Employee Company ID", placeholder="e.g. EVR-1001", key="login_emp_id")
        emp_pwd = st.text_input("Company Password", type="password", placeholder="Enter your corporate password", key="login_emp_pwd")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔓 Sign In to Portal", use_container_width=True):
                emp_id_clean = emp_id.strip().upper()
                if emp_id_clean in EMPLOYEE_DIRECTORY and EMPLOYEE_DIRECTORY[emp_id_clean]["password"] == emp_pwd:
                    st.session_state.logged_in_user = {
                        "id": emp_id_clean,
                        **EMPLOYEE_DIRECTORY[emp_id_clean]
                    }
                    st.success(f"Welcome, {EMPLOYEE_DIRECTORY[emp_id_clean]['name']}!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid Employee ID or Password. Please check your credentials.")
        
        with col_btn2:
            if st.button("⚡ Quick Demo Sign In", use_container_width=True):
                st.session_state.logged_in_user = {
                    "id": "EVR-1001",
                    **EMPLOYEE_DIRECTORY["EVR-1001"]
                }
                st.rerun()

        st.markdown("---")
        with st.expander("📋 View Demo Company Credentials"):
            st.markdown("""
            | Employee ID | Name | Role / Department | Default Password |
            |---|---|---|---|
            | `EVR-1001` | Marcus Vance | Packaging Lead (Production) | `Everest2026!` |
            | `EVR-1042` | Dr. Sarah Lin | Master Brewer & QA Director (Quality) | `Everest2026!` |
            | `EVR-2005` | David Tremblay | EHS & Safety Manager (HR) | `Everest2026!` |
            | `ADMIN-001` | Admin User | Operations System Admin | `Everest2026!` |
            """)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# -------------------------------------------------------------
# MAIN APPLICATION (AUTHENTICATED SESSION)
# -------------------------------------------------------------
user = st.session_state.logged_in_user

# Fetch latest SCADA telemetry and log to SQLite
tele_packet = st.session_state.telemetry_mgr.get_live_telemetry()
tele = tele_packet["data"]
ts = tele_packet["timestamp"]

# Periodic DB telemetry logger
st.session_state.db.log_telemetry("Production", "total_shift_volume_hl", float(tele["production"]["total_shift_volume_hl"]))
st.session_state.db.log_telemetry("Production", "line_1_can_hl_shift", float(tele["production"]["line_1_can_hl_shift"]))
st.session_state.db.log_telemetry("Production", "line_3_can_hl_shift", float(tele["production"]["line_3_can_hl_shift"]))
st.session_state.db.log_telemetry("Production", "line_4_bottle_hl_shift", float(tele["production"]["line_4_bottle_hl_shift"]))
st.session_state.db.log_telemetry("Quality", "finished_abv_percent", float(tele["quality"]["finished_abv_percent"]))
st.session_state.db.log_telemetry("Quality", "bright_beer_do_ppb", float(tele["quality"]["bright_beer_do_ppb"]))

# Sidebar
with st.sidebar:
    st.markdown("### 🏔️ Everest Control Center")
    
    # Authenticated User Badge
    st.markdown(f"""
    <div class="user-card">
        <div style="font-size:0.75rem; color:#00E5FF; font-weight:700;">AUTHENTICATED EMPLOYEE</div>
        <div style="font-size:1rem; font-weight:700; color:#FFF;">{user['name']}</div>
        <div style="font-size:0.8rem; color:#94A3B8;">{user['title']} ({user['id']})</div>
        <div style="font-size:0.75rem; color:#E6C200; margin-top:4px;">🛡️ {user['clearance']}</div>
        <div style="font-size:0.72rem; color:#10B981; margin-top:2px;">🌴 PTO: {user['pto_balance']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state.logged_in_user = None
        st.rerun()

    st.markdown(f"<span class='status-live'>● SCADA Connected</span> &nbsp; `{ts}`", unsafe_allow_html=True)
    st.markdown("---")
    
    nav_option = st.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "🔬 Quality & Rework Control",
            "🛡️ HR, Benefits & Safety",
            "🏭 Production & Packaging",
            "🍺 Brewing Operations",
            "🚚 Logistics & Fleet",
            "💼 Administration & ESG",
            "🤖 RAG AI Assistant",
            "🗄️ SQL Database & Analytics"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 📥 Runtime SOP Ingestion")
    with st.expander("Ingest Live Document", expanded=False):
        with st.form("ingest_form"):
            in_id = st.text_input("Document ID", f"QLT-LIVE-{int(time.time())%10000}")
            in_dept = st.selectbox("Department", ["Quality", "Production", "Brewing", "Logistics", "Administration", "Other"])
            in_title = st.text_input("Title", "Bright Beer Oxygen Surge Rework SOP")
            in_subsec = st.text_input("Subsection", "Quality Non-Conformance")
            in_content = st.text_area("Content / SOP Rules", "In case DO in BBT exceeds 25 ppb, engage in-line CO2 sparging stone at -1.0°C and recirculate for 4 hours.")
            submitted = st.form_submit_button("Ingest to RAG & SQL")
            
            if submitted:
                doc_payload = {
                    "id": in_id,
                    "department": in_dept,
                    "title": in_title,
                    "subsection": in_subsec,
                    "content": in_content
                }
                st.session_state.kb_loader.add_live_document(doc_payload)
                st.session_state.db.insert_ingested_document(in_id, in_dept, in_title, in_subsec, in_content)
                st.success(f"Ingested '{in_title}' into RAG & SQLite!")

    st.markdown("---")
    st.caption("⚖️ **Legal Notice**: Independent educational and technical research project. Created solely for academic and demonstration purposes. All data is simulated.")

# Brand Banner
st.markdown(f"""
<div class="brand-header">
    <div class="brand-badge">EVEREST</div>
    <div>
        <h2 style="margin:0; color:#FFFFFF; font-size:1.5rem;">Everest Brewing Company — Operations & Quality AI Platform</h2>
        <p style="margin:0; color:#00E5FF; font-size:0.85rem;">Retrieval-Augmented Generation (RAG), SCADA IoT Control & Quality Rework Center</p>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
if nav_option == "📊 Executive Overview":
    st.subheader("📊 Executive Operational Overview")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Shift Output", f"{tele['production']['total_shift_volume_hl']:,} hL", "Target: ~4,800 - 5,000 hL/8h")
    with col2:
        st.metric("Packaging OEE", f"{tele['production']['overall_oee_percent']}%", "+0.7% vs Benchmark")
    with col3:
        st.metric("Bright Beer DO", f"{tele['quality']['bright_beer_do_ppb']} ppb", "Spec < 20 ppb (Optimal)")
    with col4:
        st.metric("Finished ABV", f"{tele['quality']['finished_abv_percent']}%", "Target: 5.0% ± 0.1%")
    with col5:
        st.metric("Fleet OTIF", f"{tele['logistics']['on_time_in_full_otif_percent']}%", "SLA: 98.5%")
    with col6:
        st.metric("Zero Harm Streak", f"{tele['hr_compliance']['days_without_lost_time_injury']} Days", "Target Zero Culture")

    st.markdown("---")
    
    # 3 Production Lines Overview Chart
    st.subheader("🏭 3 Production Lines Throughput Breakdown (8-Hour Shift)")
    df_lines_overview = pd.DataFrame([
        {"Production Line": "Line 1 (Can)", "Shift Output (hL)": tele['production']['line_1_can_hl_shift'], "Format": "Cans (Standard & Sleek)", "Shift Benchmark": "2,000 hL / 8 hrs"},
        {"Production Line": "Line 3 (Can)", "Shift Output (hL)": tele['production']['line_3_can_hl_shift'], "Format": "Cans (Core & Specialty)", "Shift Benchmark": "1,800 hL / 8 hrs"},
        {"Production Line": "Line 4 (Bottling)", "Shift Output (hL)": tele['production']['line_4_bottle_hl_shift'], "Format": "Glass Bottles (1,000 bpm)", "Shift Benchmark": "800 - 1,200 hL / 8 hrs"}
    ])
    
    c_chart, c_table = st.columns([3, 2])
    with c_chart:
        fig_lines = px.bar(
            df_lines_overview, 
            x="Production Line", 
            y="Shift Output (hL)", 
            color="Production Line",
            text="Shift Output (hL)",
            title="Current Shift Volume by Packaging Line (hL / 8 Hours)",
            color_discrete_sequence=["#00E5FF", "#E6C200", "#10B981"]
        )
        fig_lines.update_traces(texttemplate='%{text:,.0f} hL', textposition='outside')
        fig_lines.update_layout(template="plotly_dark", height=320, margin=dict(l=20, r=20, t=50, b=20), showlegend=False)
        st.plotly_chart(fig_lines, use_container_width=True)
    
    with c_table:
        st.markdown("#### ⚙️ Packaging Lines Specifications")
        st.dataframe(df_lines_overview[["Production Line", "Shift Output (hL)", "Format", "Shift Benchmark"]], use_container_width=True, hide_index=True)
        st.info(f"**Total Plant Shift Capacity**: Currently producing **{tele['production']['total_shift_volume_hl']:,} hL** per 8-hour shift across all 3 active packaging lines.")

# -------------------------------------------------------------
# TAB 2: QUALITY & REWORK CONTROL (NEW DEDICATED DEPARTMENT)
# -------------------------------------------------------------
elif nav_option == "🔬 Quality & Rework Control":
    st.subheader("🔬 Quality Assurance, Analytical Lab & Rework Management")
    st.markdown("Real-time monitoring of microbiological gates, dissolved oxygen, double-seam teardowns, and non-conformance quarantine rework.")

    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    with q_col1:
        st.metric("Finished ABV", f"{tele['quality']['finished_abv_percent']}%", "Spec: 5.0% ± 0.1%")
    with q_col2:
        st.metric("Bright Beer DO", f"{tele['quality']['bright_beer_do_ppb']} ppb", "Spec < 20 ppb (180d Shelf-life)")
    with q_col3:
        st.metric("Bitterness (IBU)", f"{tele['quality']['bitterness_ibu']} IBU", "Spec: 12.0 ± 1.0 IBU")
    with q_col4:
        st.metric("Microbiology Screening", f"{tele['quality']['micro_cfu_count']} CFU", "0 CFU Target (HACCP Pass)")

    st.markdown("---")

    q_tab1, q_tab2, q_tab3, q_tab4 = st.tabs([
        "🧪 Analytical Quality & Sensory Gate",
        "🥫 Double Seam & Optical Inspection",
        "♻️ Non-Conformance & Rework Protocols",
        "📝 Log New Rework / Non-Conformance Ticket"
    ])

    # 1. Analytical & Sensory Gate
    with q_tab1:
        st.markdown("### 🧪 Analytical Lab Release Specifications & Sensory Panel")
        aq_c1, aq_c2 = st.columns(2)
        with aq_c1:
            st.markdown("#### 📊 Current Batch Analytical Gate Status")
            st.write(f"• **Active Tank Lot:** `BBT-04 (Everest Premium Lager)`")
            st.write(f"• **Original Gravity:** `11.20 °Plato` (1.045 SG) — **PASS**")
            st.write(f"• **Apparent Extract:** `2.00 °Plato` (1.008 SG) — **PASS**")
            st.write(f"• **Dissolved CO₂:** `2.65 volumes` (5.2 g/L) — **PASS**")
            st.write(f"• **Diacetyl via GC:** `0.018 ppm` (Spec < 0.030 ppm) — **PASS**")
        with aq_c2:
            st.markdown("#### 👅 Certified 5-Member Sensory Panel Release")
            st.write("• **Sensory Panel Status:** `PASSED — FULL RELEASE`")
            st.write("• **Off-Flavor Screen (DMS, Acetaldehyde, Oxidation):** `0.0 (None Detected)`")
            st.write("• **Foam Stability (NIBEM Score):** `285 Seconds` (Target ≥ 260s)")
            st.write("• **HACCP Food Safety Critical Control Point (CCP):** `VALIDATED`")

    # 2. Double Seam & Optical Inspection
    with q_tab2:
        st.markdown("### 🥫 Double Seam Teardown & EBI Optical Bottle Inspection")
        s_c1, s_c2 = st.columns(2)
        with s_c1:
            st.markdown("#### 🔍 Line 1 & Line 3 Can Double-Seam Teardown")
            st.metric("Seam Overlap %", f"{tele['quality']['can_seam_overlap_percent']}%", "Spec: > 55% (Min 45%)")
            st.metric("Seam Tightness Score", f"{tele['quality']['can_seam_tightness_percent']}%", "Wrinkle Rating 90-100%")
            st.progress(min(tele['quality']['can_seam_overlap_percent'] / 65.0, 1.0))
            st.caption("Destructive seam teardown inspections performed every 2 hours with digital optical seam projector.")
        with s_c2:
            st.markdown("#### 🍾 Line 4 Empty Bottle Inspector (EBI)")
            st.metric("EBI Optical Rejections (24h)", f"{tele['quality']['ebi_optical_rejections_24h']} Defective Bottles", "99.98% Inspection Accuracy")
            st.write("• **Inspection Points:** Finish chipping, sidewall scuffing, base residual liquid detector.")
            st.write("• **Filler Gamma Fill-Level Inspector:** Active (Tolerance ± 3ml).")

    # 3. Non-Conformance & Rework Protocols
    with q_tab3:
        st.markdown("### ♻️ Standard Rework & Blending Operating Procedures")
        st.markdown("""
        | Defect / Breach Scenario | Root Cause | Mandatory Rework Action | Gate Authority |
        |---|---|---|---|
        | **High DO in Bright Tank (20–35 ppb)** | In-line transfer pump seal aeration | In-line CO₂ sparging stone at -1.0°C + slow recirculation | Quality Lead |
        | **Low Carbonation (< 2.4 vol)** | Carbonation stone saturation drop | Repressurize BBT head space & recirculate through carbonator | Packaging Supervisor |
        | **High Diacetyl (> 0.030 ppm)** | Incomplete lagering reduction | Warm krausening with 5% active fermenting wort at 14°C for 48h | Master Brewer |
        | **Seamer Jam / Low Overlap (< 45%)** | Seamer roll wear / misaligned pin | Quarantine lot, decant under sterile CO₂ blanket, centrifuge recovery | EHS & QA Lead |
        | **Microbial Contamination (> 1 CFU)** | Pasteurizer temp breach / valve leak | Total discard & autoclave sanitization. **No rework permitted.** | Quality Director |
        """)

    # 4. Log New Rework Ticket
    with q_tab4:
        st.markdown("### 📝 Non-Conformance Report (NCR) & Rework Ticket Creator")
        with st.form("ncr_form"):
            n_c1, n_c2 = st.columns(2)
            with n_c1:
                ncr_batch = st.text_input("Batch / Lot Number", "EVR-LOT-2026-0814-B")
                ncr_location = st.selectbox("Line / Tank Affected", ["Line 1 Canning", "Line 3 Mega Can", "Line 4 Bottling", "Bright Tank BBT-01", "Bright Tank BBT-04", "Fermenter CCV-08"])
                ncr_defect = st.selectbox("Defect Category", ["High Dissolved Oxygen (DO)", "Under-Carbonation (< 2.4 vol)", "Seam Overlap Failure (< 45%)", "Diacetyl Rest Incomplete", "Fill Height Under-fill", "Labeling / Packaging Defect"])
            with n_c2:
                ncr_param = st.text_input("Measured Parameter & Variance", "DO measured at 24.2 ppb (Spec < 20 ppb)")
                ncr_action = st.text_area("Authorized Rework Action", "Recirculate through CO2 sparging loop at -1.0°C for 3.5 hours. Re-test DO prior to packaging release.")
                ncr_status = st.selectbox("Ticket Status", ["IN_REWORK", "QUARANTINE_HOLD", "RESOLVED_RELEASED"])

            submit_ncr = st.form_submit_button("📝 Submit Quality Non-Conformance Ticket")
            if submit_ncr:
                ncr_id = f"NCR-{int(time.time())%100000}"
                success = st.session_state.db.insert_quality_rework(
                    ncr_id=ncr_id,
                    batch_id=ncr_batch,
                    line_or_tank=ncr_location,
                    defect_type=ncr_defect,
                    parameter=ncr_param,
                    action_taken=ncr_action,
                    status=ncr_status
                )
                if success:
                    st.success(f"Quality NCR Ticket `{ncr_id}` logged into database successfully!")

        st.markdown("#### 📋 Active Quality Non-Conformance & Rework Tickets (SQLite Database)")
        rework_logs = st.session_state.db.get_quality_rework_logs(limit=10)
        if rework_logs:
            df_ncr = pd.DataFrame(rework_logs)
            st.dataframe(df_ncr, use_container_width=True, hide_index=True)
        else:
            st.info("No active quality quarantine holds. All lines running on-spec!")

    st.markdown("---")
    st.markdown("#### 📋 Quality Standard Operating Procedures (Knowledge Base)")
    qlt_docs = st.session_state.kb_loader.get_documents_by_department("Quality")
    for doc in qlt_docs:
        with st.expander(f"📌 {doc['id']}: {doc['title']} ({doc.get('subsection', 'N/A')})"):
            st.write(doc["content"])

# -------------------------------------------------------------
# TAB 3: HR, BENEFITS & SAFETY (COMPREHENSIVE EMPLOYEE CENTER)
# -------------------------------------------------------------
elif nav_option == "🛡️ HR, Benefits & Safety":
    st.subheader("🛡️ Everest Employee HR, Benefits, Vacation & Safety Hub")
    st.markdown(f"**Logged in Employee:** `{user['name']}` ({user['title']}) | **Tenure:** `{user['tenure']}` | **Shift:** `{user['shift']}`")

    # Top KPI metrics
    k_col1, k_col2, k_col3, k_col4 = st.columns(4)
    with k_col1:
        st.metric("LTI-Free Days", f"{tele['hr_compliance']['days_without_lost_time_injury']} Days", "Target Zero Safety Goal")
    with k_col2:
        st.metric("Safety Audit Score", f"{tele['hr_compliance']['whmis_compliance_audit_score']}%", "Chemical & PPE Compliant")
    with k_col3:
        st.metric("My Vacation Balance", user['pto_balance'], f"Annual Entitlement: {user['vacation_entitlement']}")
    with k_col4:
        st.metric("Ammonia (NH₃) Sensor", "0.0 ppm", "Safe (Alarm Threshold 25 ppm)")

    st.markdown("---")

    hr_tab1, hr_tab2, hr_tab3, hr_tab4, hr_tab5 = st.tabs([
        "🌴 Vacation, Leave & PTO Entitlements",
        "💊 Health, Dental & Pension Benefits",
        "🕒 24/7 Shift Schedules & Overtime",
        "⚠️ EHS Real-Time Safety Sensors & PPE",
        "🚨 Safety Hazard Reporting"
    ])

    # 1. Vacation & Leave Entitlements
    with hr_tab1:
        st.markdown("### 🌴 Corporate Vacation & Leave Entitlement Policy")
        st.markdown("Annual vacation accrual is determined by years of completed service:")
        
        df_vacation = pd.DataFrame([
            {"Service Tenure Tier": "Years 1 to 3 of Service", "Vacation Days": "15 Days (3 Weeks)", "Accrual Rate": "1.25 Days / Month", "Carryover Max": "5 Days"},
            {"Service Tenure Tier": "Years 4 to 7 of Service", "Vacation Days": "20 Days (4 Weeks)", "Accrual Rate": "1.67 Days / Month", "Carryover Max": "5 Days"},
            {"Service Tenure Tier": "Years 8 to 12 of Service", "Vacation Days": "25 Days (5 Weeks)", "Accrual Rate": "2.08 Days / Month", "Carryover Max": "10 Days"},
            {"Service Tenure Tier": "Years 13+ of Service", "Vacation Days": "30 Days (6 Weeks)", "Accrual Rate": "2.50 Days / Month", "Carryover Max": "10 Days"}
        ])
        st.dataframe(df_vacation, use_container_width=True, hide_index=True)

        st.markdown("#### 📋 Additional Paid & Protected Leave Categories")
        v_c1, v_c2 = st.columns(2)
        with v_c1:
            st.write("• **Personal / Sick Days:** `5 Fully Paid Days` per calendar year (granted Jan 1).")
            st.write("• **Statutory Holidays:** `10 Paid Company Holidays` (2.0x double-time if rostered).")
            st.write("• **Bereavement Leave:** `Up to 5 Consecutive Paid Days` for immediate family.")
        with v_c2:
            st.write("• **Parental & Maternity Top-Up:** `100% Base Salary Top-Up for 16 Weeks`.")
            st.write("• **Compassionate Care Leave:** `Up to 28 Weeks Job-Protected Leave`.")
            st.write("• **Jury Duty & Subpoena Leave:** `Up to 10 Paid Working Days`.")

    # 2. Health & Pension Benefits
    with hr_tab2:
        st.markdown("### 💊 Comprehensive Health, Dental & Pension Plan")
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            st.markdown("#### 🏥 Medical, Dental & Vision Coverage")
            st.write("• **Prescription Drugs:** `100% Employer-Funded` (Direct pay card, $0 deductible).")
            st.write("• **Dental Plan:** `100% Basic Dental` (cleanings every 6 months) + `80% Major Restorative` up to $2,500/year.")
            st.write("• **Vision Care:** `$450 every 24 months` for prescription glasses/contacts + annual eye exam.")
            st.write("• **Paramedical & Physio:** `$750/year` for physiotherapy, chiropractic, and massage.")
            st.write("• **Mental Health Stipend:** `$1,000/year per family member` for registered psychologists.")
        with b_c2:
            st.markdown("#### 💰 Group Retirement Pension & Savings Plan")
            st.write("• **Company Pension Matching:** Everest matches **100% of employee contributions up to 6.0%** of annual base salary.")
            st.write("• **Vesting Schedule:** `100% Immediate Vesting` upon enrollment.")
            st.write("• **Employee Assistance Program (EAP):** 24/7 confidential counseling for employees and dependents.")

    # 3. 24/7 Shift Schedules & Overtime
    with hr_tab3:
        st.markdown("### 🕒 24/7 Shift Operations & Overtime Rules")
        s_c1, s_c2 = st.columns(2)
        with s_c1:
            st.markdown("#### 🕒 Plant Shift Schedule & Premiums")
            st.write("• **Shift 1 (Morning):** `07:00 - 15:00` (Base hourly rate)")
            st.write("• **Shift 2 (Afternoon):** `15:00 - 23:00` (**+$1.25 / hr** shift differential)")
            st.write("• **Shift 3 (Night):** `23:00 - 07:00` (**+$2.50 / hr** night shift differential)")
        with s_c2:
            st.markdown("#### ⏱️ Overtime & Premium Pay Rules")
            st.write("• **Daily Overtime (Over 8 hrs/day):** `1.5× Regular Rate`")
            st.write("• **Weekly Overtime (Over 40 hrs/week):** `1.5× Regular Rate`")
            st.write("• **Statutory Holiday Overtime:** `2.0× Double-Time` + 8 hours statutory credit.")
            st.write("• **Rest Interval Mandate:** Minimum `12 Hours Rest` required between consecutive shifts.")

    # 4. EHS Safety Sensors & PPE
    with hr_tab4:
        st.markdown("### ⚠️ EHS Gas Sensors & Zone PPE Protection Matrix")
        ehs_c1, ehs_c2 = st.columns(2)
        with ehs_c1:
            st.markdown("#### 📡 Real-Time Environmental Gas & Atmospheric Sensors")
            st.write("• **Ammonia Refrigeration (NH₃):** `0.0 ppm` (Nominal | Warning at 25 ppm, Evac at 50 ppm)")
            st.write("• **Cellar & Fermentation Ambient CO₂:** `0.04%` (Normal Atmospheric | Warning at 0.50%)")
            st.write("• **CCV / Bright Tank Confined Space O₂:** `20.9%` (Safe Range 19.5% - 23.5%)")
            st.write("• **Emergency Eyewash Stations:** `VERIFIED & TESTED` (Weekly Inspection Log Complete)")
        with ehs_c2:
            st.markdown("#### 🔒 Confined Space Entry (CSE) Active Permits")
            st.write("• **CCV-08 Tank Cleaning Entry:** Permit `#CSE-2026-0814` (Active | Attendant: D. Tremblay)")
            st.write("• **Grain Silo #2 Inspection:** `CLOSED` (Zero Energy LOTO Signed Off)")
            st.info("💡 Under OSHA 29 CFR 1910.146 and CSA standards, all vessel entries require atmospheric gas testing and dedicated harness attendants.")

    # 5. Incident Reporting
    with hr_tab5:
        st.markdown("### 🚨 Safety Hazard & Near-Miss Reporting Portal")
        with st.form("incident_form"):
            r_c1, r_c2 = st.columns(2)
            with r_c1:
                haz_type = st.selectbox("Hazard Classification", ["Slip / Trip / Fall Hazard", "Chemical / Chemical Splashing", "Machine Guarding / Pinch Point", "Gas / Air Quality Concern", "Ergonomic / Material Handling", "Electrical / LOTO Hazard"])
                haz_loc = st.text_input("Exact Facility Location", "Packaging Hall - Conveyor Line 1 Outfeed")
            with r_c2:
                haz_sev = st.selectbox("Severity Level", ["LOW - Minor Hazard / Near Miss", "MEDIUM - Moderate Risk", "HIGH - Immediate Intervention Needed"])
                haz_desc = st.text_area("Detailed Hazard Description", "Water pooling on the floor near the outfeed conveyor. Squeegee required to prevent slip hazard.")
            
            submit_incident = st.form_submit_button("🚨 Submit Safety Incident Report")
            if submit_incident:
                rep_id = f"INC-{int(time.time())%100000}"
                success = st.session_state.db.insert_incident_report(
                    report_id=rep_id,
                    employee_id=user['id'],
                    department=user['department'],
                    hazard_type=haz_type,
                    location=haz_loc,
                    description=haz_desc,
                    severity=haz_sev.split(" ")[0]
                )
                if success:
                    st.success(f"Safety Report `{rep_id}` successfully submitted to EHS Manager for investigation!")

        st.markdown("#### 📋 Recent Safety Incident Log (SQLite Database)")
        logged_reps = st.session_state.db.get_incident_reports(limit=10)
        if logged_reps:
            df_reps = pd.DataFrame(logged_reps)
            st.dataframe(df_reps, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 📋 HR & Safety Standard Operating Procedures (Knowledge Base)")
    hr_docs = st.session_state.kb_loader.get_documents_by_department("Other")
    for doc in hr_docs:
        with st.expander(f"📌 {doc['id']}: {doc['title']} ({doc.get('subsection', 'N/A')})"):
            st.write(doc["content"])

# -------------------------------------------------------------
# TAB 4: PRODUCTION & PACKAGING
# -------------------------------------------------------------
elif nav_option == "🏭 Production & Packaging":
    st.subheader("🏭 Packaging Facility: Line 1, Line 3 & Line 4 Detailed Control Center")
    st.markdown("Real-time monitoring across Everest's 3 primary packaging lines with live SCADA IoT telemetry.")

    p1, p2, p3 = st.columns(3)
    
    # Line 1 Card
    with p1:
        st.markdown("### 🥫 Line 1 (Canning)")
        st.metric("8-Hour Output", f"{tele['production']['line_1_can_hl_shift']:,} hL", "Target: ~2,000 hL / 8h")
        st.write("**Packaging Format:** 355ml Sleeks & 473ml Tallboys")
        st.write("**Rated OEE:** 86.5% Benchmark")
        st.progress(min(tele['production']['line_1_can_hl_shift'] / 2000, 1.0))

    # Line 3 Card
    with p2:
        st.markdown("### 🥫 Line 3 (Canning)")
        st.metric("8-Hour Output", f"{tele['production']['line_3_can_hl_shift']:,} hL", "Target: ~1,800 hL / 8h")
        st.write("**Packaging Format:** Standard Cans (Core & Specialty)")
        st.write("**Shift Volume:** Optimized Brand Changeover Line")
        st.progress(min(tele['production']['line_3_can_hl_shift'] / 1800, 1.0))

    # Line 4 Card
    with p3:
        st.markdown("### 🍾 Line 4 (Glass Bottling)")
        st.metric("Speed & Output", f"{tele['production']['line_4_bottle_bpm']} bpm", f"{tele['production']['line_4_bottle_hl_shift']} hL / 8h (800-1200 hL)")
        st.write("**Packaging Format:** 341ml Returnable Stubby & NR")
        st.write("**Inspection:** Empty Bottle Inspector (EBI) Active")
        st.progress(min(tele['production']['line_4_bottle_hl_shift'] / 1200, 1.0))

    st.markdown("---")
    
    # Line 4 Bottling Speed Gauge
    g_col1, g_col2 = st.columns([1, 1])
    with g_col1:
        fig_bottle_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=tele['production']['line_4_bottle_bpm'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Line 4 Bottling Speed (bpm)"},
            gauge={
                'axis': {'range': [0, 1300]},
                'bar': {'color': "#10B981"},
                'steps': [
                    {'range': [0, 800], 'color': "rgba(239, 68, 68, 0.3)"},
                    {'range': [800, 950], 'color': "rgba(245, 158, 11, 0.3)"},
                    {'range': [950, 1300], 'color': "rgba(16, 185, 129, 0.3)"}
                ],
                'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': 1000}
            }
        ))
        fig_bottle_gauge.update_layout(template="plotly_dark", height=280, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_bottle_gauge, use_container_width=True)

    with g_col2:
        st.markdown("#### 🧹 Clean-In-Place (CIP) & Maintenance Historian")
        st.write("• **Next Scheduled CIP:** In 38 Hours (Full 5-Step Loop: NaOH 2.2% + PAA 0.5%)")
        st.write("• **SCADA Line Status:** `RUNNING_OPTIMAL` (1 Micro-stoppage in last 24h)")
        st.write("• **Active Shift Schedule:** Shift 1 (Day - 8 Hours) Staffed")
        st.write("• **Total 8-Hour Facility Throughput:** **" + f"{tele['production']['total_shift_volume_hl']:,} hL**")

# -------------------------------------------------------------
# TAB 5: BREWING OPERATIONS
# -------------------------------------------------------------
elif nav_option == "🍺 Brewing Operations":
    st.subheader("🍺 Brewing Science & Cellar Operations")
    
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        st.metric("Active Fermenters", f"{tele['brewing']['active_fermenters']} Vessels", f"Batch: {tele['brewing']['current_batch']}")
        st.metric("Bright Beer Dissolved O₂", f"{tele['brewing']['bright_beer_dissolved_o2_ppb']} ppb", "Spec < 20 ppb (180d Shelf-life)")
    with b_col2:
        st.metric("Fermentation Temp", f"{tele['brewing']['avg_fermentation_temp_c']}°C", "Target: 10.5°C")
        st.metric("Diacetyl Reduction", f"{tele['brewing']['diacetyl_ppm']} ppm", "Spec < 0.030 ppm")
    with b_col3:
        st.metric("Lager Yeast Status", tele['brewing']['lager_spec_status'], "Strain: S. pastorianus EVR-04")
        st.metric("Pasteurization Target", "18 PU", "Flash: 72°C for 20s (15-25 PU)")

    st.markdown("---")
    st.markdown("#### 📋 Standard Operating Procedures (Brewing Knowledge Base)")
    brewing_docs = st.session_state.kb_loader.get_documents_by_department("Brewing")
    for doc in brewing_docs:
        with st.expander(f"📌 {doc['id']}: {doc['title']} ({doc.get('subsection', 'N/A')})"):
            st.write(doc["content"])

# -------------------------------------------------------------
# TAB 6: LOGISTICS & FLEET
# -------------------------------------------------------------
elif nav_option == "🚚 Logistics & Fleet":
    st.subheader("🚚 Logistics, Cold Chain Fleet & Supply Chain")
    
    l1, l2, l3 = st.columns(3)
    with l1:
        st.metric("Active Freight Trucks", f"{tele['logistics']['active_fleet_trucks']} Units", "Regional Distribution Hubs")
    with l2:
        st.metric("Cold Chain Compliance", f"{tele['logistics']['cold_chain_compliance_rate']}%", f"Avg Temp: {tele['logistics']['avg_transit_temp_c']}°C (-1.5°C to 2°C)")
    with l3:
        st.metric("Keg Return Turnaround", f"{tele['logistics']['keg_recycling_turnaround_days']} Days", "Target: ≤ 21 Days ($30 Deposit)")

    st.markdown("---")
    st.markdown("#### 📋 Standard Operating Procedures (Logistics Knowledge Base)")
    log_docs = st.session_state.kb_loader.get_documents_by_department("Logistics")
    for doc in log_docs:
        with st.expander(f"📌 {doc['id']}: {doc['title']} ({doc.get('subsection', 'N/A')})"):
            st.write(doc["content"])

# -------------------------------------------------------------
# TAB 7: ADMINISTRATION & ESG
# -------------------------------------------------------------
elif nav_option == "💼 Administration & ESG":
    st.subheader("💼 ERP Procurement, Corporate Finance & 2026 ESG Goals")
    
    a1, a2, a3 = st.columns(3)
    with a1:
        st.metric("Water-to-Beer Ratio", f"{tele['administration']['water_to_beer_ratio_l_l']} L/L", "2026 Target: ≤ 2.10 L/L")
    with a2:
        st.metric("Renewable Electricity", f"{tele['administration']['renewable_power_percent']}%", "Solar & Wind PPA")
    with a3:
        st.metric("Pending ERP POs", f"{tele['administration']['active_sap_pos_pending']} Requisitions", "3-Way Match Net 60")

    st.markdown("---")
    st.markdown("#### 📋 Standard Operating Procedures (Administration Knowledge Base)")
    adm_docs = st.session_state.kb_loader.get_documents_by_department("Administration")
    for doc in adm_docs:
        with st.expander(f"📌 {doc['id']}: {doc['title']} ({doc.get('subsection', 'N/A')})"):
            st.write(doc["content"])

# -------------------------------------------------------------
# TAB 8: RAG AI ASSISTANT (CHATBOT)
# -------------------------------------------------------------
elif nav_option == "🤖 RAG AI Assistant":
    st.subheader("🤖 Everest Enterprise RAG AI Assistant")
    
    c_filter, c_chip = st.columns([1, 3])
    with c_filter:
        dept_choice = st.selectbox("Department Filter", ["All", "Quality", "Other", "Production", "Brewing", "Logistics", "Administration"])
    
    with c_chip:
        st.markdown("**Suggested Quick Prompts:**")
        chip_cols = st.columns(3)
        with chip_cols[0]:
            if st.button("🌴 Vacation & Leave Policy"):
                st.session_state.user_prompt_input = "How many vacation days, sick days, and statutory holidays do employees receive based on tenure?"
        with chip_cols[1]:
            if st.button("🔬 Quality & Rework SOP"):
                st.session_state.user_prompt_input = "What are the non-conformance quarantine and rework procedures for high DO or low carbonation batches?"
        with chip_cols[2]:
            if st.button("💊 Health & Pension Benefits"):
                st.session_state.user_prompt_input = "What dental, vision, prescription drug, and pension matching benefits does Everest provide?"

    # Display chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                st.markdown(f"**📚 Retrieved Sources ({round(msg['confidence']*100)}% Confidence | {msg['exec_ms']}ms):**")
                for s in msg["sources"]:
                    with st.expander(f"📄 {s['id']}: {s['title']} ({s['department']} - {s.get('subsection', 'N/A')}) [Score: {round(s['score']*100)}%]"):
                        st.write(s['excerpt'])

    # Handle input query
    prompt = st.chat_input("Ask a question about vacation policies, quality rework, benefits, packaging lines, brewing, or safety...")
    if "user_prompt_input" in st.session_state and st.session_state.user_prompt_input:
        prompt = st.session_state.user_prompt_input
        st.session_state.user_prompt_input = None

    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Run RAG Query
        with st.spinner("Searching Everest Knowledge Base & computing vector embeddings..."):
            start_t = time.time()
            rag_res = st.session_state.rag_engine.query(
                query=prompt,
                department=dept_choice,
                top_k=3,
                live_telemetry=tele
            )
            exec_time = round((time.time() - start_t) * 1000, 2)

            sources_list = [
                {
                    "id": s.id,
                    "department": s.department,
                    "title": s.title,
                    "subsection": s.subsection,
                    "score": s.score,
                    "excerpt": s.excerpt
                } for s in rag_res.sources
            ]

            # Save in SQLite
            st.session_state.db.log_chat(
                session_id=st.session_state.session_id,
                query=prompt,
                department=dept_choice,
                answer=rag_res.answer,
                confidence=rag_res.confidence_score,
                sources=sources_list,
                exec_ms=exec_time
            )

            # Append to session state
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": rag_res.answer,
                "sources": sources_list,
                "confidence": rag_res.confidence_score,
                "exec_ms": exec_time
            })
            st.rerun()

# -------------------------------------------------------------
# TAB 9: SQL DATABASE & ANALYTICS EXPLORER
# -------------------------------------------------------------
elif nav_option == "🗄️ SQL Database & Analytics":
    st.subheader("🗄️ SQLite Database Explorer & Analytics Engine")
    st.markdown("Direct SQL interface connected to `database/everest.db`. Great for demonstrating SQL querying & analytics skills!")

    st.markdown("#### ⚡ Preset Analytical Queries")
    sql_preset = st.selectbox(
        "Choose an analytical query",
        [
            "SELECT * FROM quality_rework_log ORDER BY id DESC",
            "SELECT * FROM incident_reports ORDER BY id DESC",
            "SELECT * FROM chat_history ORDER BY id DESC LIMIT 10",
            "SELECT department, COUNT(*) AS query_count, AVG(confidence) AS avg_confidence, AVG(exec_ms) AS avg_ms FROM chat_history GROUP BY department",
            "SELECT * FROM telemetry_log ORDER BY id DESC LIMIT 25",
            "SELECT * FROM ingested_documents ORDER BY id DESC"
        ]
    )

    custom_sql = st.text_area("SQL Query Editor", sql_preset, height=100)
    
    if st.button("▶️ Execute SQL Query"):
        try:
            cols, rows = st.session_state.db.run_custom_query(custom_sql)
            if cols:
                df_result = pd.DataFrame(rows, columns=cols)
                st.success(f"Query returned {len(df_result)} row(s) successfully!")
                st.dataframe(df_result, use_container_width=True)
                
                # If numeric summary, show quick bar chart
                if "department" in cols and "query_count" in cols:
                    fig_sql = px.bar(df_result, x="department", y="query_count", title="Query Count by Department", color="department")
                    fig_sql.update_layout(template="plotly_dark", height=300)
                    st.plotly_chart(fig_sql, use_container_width=True)
            else:
                st.info("Query executed successfully (0 rows returned).")
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

    st.markdown("---")
    st.markdown("#### 📥 Download Chat History Table (CSV)")
    raw_chats = st.session_state.db.get_chat_history(limit=200)
    if raw_chats:
        df_chats = pd.DataFrame(raw_chats)
        csv_data = df_chats.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download SQLite Chat History as CSV",
            data=csv_data,
            file_name=f"everest_rag_chat_history_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

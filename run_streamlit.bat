@echo off
title Everest Brewing - Streamlit Python RAG Platform
color 1F
echo.
echo ============================================================
echo  Everest Brewing Enterprise RAG AI Assistant & SCADA Dashboard
echo  Pure Python & SQL Edition (Streamlit + SQLite + Plotly)
echo ============================================================
echo.
cd /d "%~dp0"
python -m streamlit run app.py --server.port 8501
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Streamlit failed to launch.
    pause
)

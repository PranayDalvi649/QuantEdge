@echo off
echo =======================================================
echo          Starting QuantEdge Servers
echo =======================================================
echo.

echo [1/2] Starting Python Backend Server...
start cmd /k "cd backend && venv\Scripts\python main.py"

echo [2/2] Starting React Frontend Server...
cd frontend && npm run dev

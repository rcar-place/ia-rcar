@echo off
echo =========================================
echo      Iniciando ML AutoResponder...
echo =========================================

echo.
echo [1/2] Iniciando o Servidor Backend (FastAPI)...
start "ML AutoResponder - Backend" cmd /k "cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

echo.
echo [2/2] Iniciando o Servidor Frontend (React/Vite)...
start "ML AutoResponder - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo =========================================
echo  Servidores iniciados em novas janelas!
echo  Backend: http://localhost:8000
echo  Frontend: http://localhost:5173
echo =========================================
echo.
pause

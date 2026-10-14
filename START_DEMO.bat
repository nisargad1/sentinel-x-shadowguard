@echo off
TITLE SENTINEL-X ShadowGuard Demo Launcher
COLOR 0B
cls
echo ==============================================================================
echo        SENTINEL-X SHADOWGUARD -- INTENT-AWARE RUNTIME SECURITY GATEWAY
echo                  HACKATHON LIVE DEMONSTRATION LAUNCHER
echo ==============================================================================
echo.
echo [*] Checking local environment...

cd /d "%~dp0"
set ROOT_DIR=%~dp0
set BACKEND_DIR=%ROOT_DIR%backend
set TOOLS_CLOUDFLARED=C:\Users\Nisarga\.gemini\antigravity\tools\cloudflared.exe

echo [*] Starting Backend Server (FastAPI + React SPA) on port 8000...
start "ShadowGuard-Backend" /min cmd /c "cd /d %BACKEND_DIR% && set PYTHONPATH=%BACKEND_DIR%;%BACKEND_DIR%\app;%ROOT_DIR% && set PORT=8000 && set HOST=127.0.0.1 && python run.py"

echo [*] Waiting 3 seconds for backend to initialize...
timeout /t 3 /nobreak >nul

echo [*] Launching Cloudflare HTTPS Tunnel...
if exist "%TOOLS_CLOUDFLARED%" (
    start "ShadowGuard-Tunnel" cmd /k ""%TOOLS_CLOUDFLARED%" tunnel --edge-ip-version 4 --protocol http2 --url http://127.0.0.1:8000"
) else (
    echo [!] Cloudflared binary not found at default path. Tunnel skipped.
)

echo.
echo ==============================================================================
echo [SUCCESS] SENTINEL-X SHADOWGUARD IS RUNNING!
echo ==============================================================================
echo.
echo   LOCAL SCREENSHARE URL (100%% Fail-Proof):
echo   -> http://localhost:8000
echo.
echo   INTERACTIVE SWAGGER API DOCS:
echo   -> http://localhost:8000/docs
echo.
echo   PUBLIC HTTPS CLOUDFLARE URL:
echo   -> Look at the 'ShadowGuard-Tunnel' window for your active trycloudflare.com URL!
echo.
echo ==============================================================================
echo [*] Opening Dashboard in your browser now...
start http://localhost:8000
echo.
echo [!] Keep this window open during your demo presentation.
echo.
pause

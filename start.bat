@echo off
REM 🚀 Script de Démarrage Rapide - Navbar Améliorée (Windows)
REM Fresh & Green - Bootstrap 5 Enhancement

setlocal enabledelayedexpansion

cls
echo 🌿 ============================================== 🌿
echo    NAVBAR AMÉLIORA - DÉMARRAGE RAPIDE (Windows)
echo 🌿 ============================================== 🌿
echo.

REM Vérification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8+
    pause
    exit /b 1
)

REM Afficher un menu
echo Que voulez-vous faire?
echo.
echo 1 = Démarrer l'application (python manage.py runserver)
echo 2 = Consulter la documentation (NAVBAR_GUIDE.html)
echo 3 = Vérifier l'installation
echo 4 = Quitter
echo.
set /p choice="Sélectionnez une option (1-4): "

if "%choice%"=="1" goto start_app
if "%choice%"=="2" goto open_guide
if "%choice%"=="3" goto verify
if "%choice%"=="4" goto quit
echo Option invalide!
pause
exit /b 1

:start_app
cls
echo.
echo 🚀 Démarrage de l'application...
echo 📍 Ouvrez votre navigateur: http://localhost:8000
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.
python manage.py runserver
pause
exit /b 0

:open_guide
cls
echo.
echo 📖 Ouverture du guide interactif...
start NAVBAR_GUIDE.html
echo ✅ Le guide s'ouvre dans votre navigateur par défaut
echo.
pause
exit /b 0

:verify
cls
echo.
echo 🔍 Vérification de l'installation...
echo.
python verify_navbar.py
echo.
pause
exit /b 0

:quit
cls
echo.
echo 👋 Au revoir! 🌿
echo.
exit /b 0

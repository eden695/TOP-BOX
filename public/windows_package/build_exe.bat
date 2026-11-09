@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title TOP-BOX — Générateur d'Exécutable et Installateur Windows
color 0B
cd /d "%~dp0"

echo ========================================================================
echo        TOP-BOX — COMPILATION OFFICIELLE WINDOWS (EXE + SETUP)
echo ========================================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    color 0C
    echo [ERREUR] Python est introuvable sur votre système ou absent du PATH.
    echo Veuillez installer Python 3.11 ou 3.12 depuis https://www.python.org/
    echo en prenant soin de cocher la case "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo [1/5] Vérification et installation des dépendances...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    color 0C
    echo [ERREUR] Impossible d'installer les dépendances pip.
    pause
    exit /b 1
)

echo [2/5] Vérification de la syntaxe de app.py...
python -m py_compile app.py
if errorlevel 1 (
    color 0C
    echo [ERREUR] Le code Python contient une anomalie de syntaxe.
    pause
    exit /b 1
)
echo      -> Code Python vérifié avec succès.

echo [3/5] Compilation de l'exécutable TOP-BOX avec PyInstaller...
if exist "build_temp" rmdir /s /q "build_temp"
if exist "dist" rmdir /s /q "dist"

python -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name "TOP-BOX" ^
    --distpath "dist" ^
    --workpath "build_temp" ^
    --icon "data\assets\app.ico" ^
    --add-data "data;data" ^
    --collect-all PIL ^
    app.py

if errorlevel 1 (
    color 0C
    echo [ERREUR] Échec de la compilation PyInstaller.
    pause
    exit /b 1
)

if not exist "dist\TOP-BOX.exe" (
    color 0C
    echo [ERREUR] Le fichier dist\TOP-BOX.exe n'a pas été généré.
    pause
    exit /b 1
)
echo      -> Exécutable autonome dist\TOP-BOX.exe prêt !

echo [4/5] Recherche du compilateur Inno Setup 6...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    color 0E
    echo.
    echo ========================================================================
    echo INFORMATION : L'exécutable autonome a été généré :
    echo   -> %CD%\dist\TOP-BOX.exe
    echo.
    echo Pour créer l'installateur d'un clic (Setup_TOP_BOX.exe), installez
    echo Inno Setup 6 depuis https://jrsoftware.org/isdl.php puis relancez ce script.
    echo ========================================================================
    echo.
    pause
    exit /b 0
)

echo [5/5] Création de l'installateur commercial Setup_TOP_BOX.exe...
if not exist "output" mkdir "output"
"%ISCC%" "installer.iss"
if errorlevel 1 (
    color 0C
    echo [ERREUR] Erreur lors de la génération de l'installateur Inno Setup.
    pause
    exit /b 1
)

color 0A
echo.
echo ========================================================================
echo        SUCCÈS : TOP-BOX EST PRÊT POUR LA COMMERCIALISATION !
echo ========================================================================
echo.
echo 1. Exécutable standalone : %CD%\dist\TOP-BOX.exe
echo 2. Fichier d'installation : %CD%\output\Setup_TOP_BOX.exe
echo.
echo Données SQLite protégées des commerçants :
echo    %%LOCALAPPDATA%%\TOP_BOX\caisse.db
echo ========================================================================
echo.
pause
exit /b 0

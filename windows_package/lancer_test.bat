@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title TOP-BOX — Lancement en Mode Test (Python)
color 0B
cd /d "%~dp0"

echo ========================================================================
echo               TOP-BOX POS — TEST IMMÉDIAT DU LOGICIEL
echo ========================================================================
echo.
echo Ce script lance directement TOP-BOX avec Python pour tester toutes les
echo fonctionnalités (Caisse, Produits, Ventes, Caissiers, Mobile Money, etc.)
echo avant de générer le fichier .exe final.
echo.

:: Vérification de la présence de Python
where python >nul 2>nul
if errorlevel 1 (
    color 0C
    echo [ERREUR] Python n'est pas installé ou n'a pas été ajouté au PATH Windows.
    echo.
    echo Comment corriger cela simplement :
    echo 1. Téléchargez Python (3.11 ou 3.12 recommandé) sur : https://www.python.org/
    echo 2. Lors de l'installation, COCHEZ impérativement la case :
    echo    "Add python.exe to PATH" (Ajouter Python au PATH).
    echo 3. Relancez ce fichier "lancer_test.bat".
    echo.
    pause
    exit /b 1
)

:: Affichage de la version Python détectée
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo [OK] %PY_VER% détecté avec succès.
echo.

:: Vérification / Installation automatique des bibliothèques nécessaires
echo [1/2] Vérification des modules requis (customtkinter, pillow)...
python -c "import customtkinter, PIL" >nul 2>nul
if errorlevel 1 (
    echo      Installation des modules nécessaires depuis requirements.txt...
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo.
        echo [ATTENTION] Échec du téléchargement automatique des bibliothèques pip.
        echo Veuillez vérifier votre connexion Internet puis relancer ce script.
        echo.
        pause
        exit /b 1
    )
    echo      -> Modules installés avec succès !
) else (
    echo      -> Tous les modules nécessaires sont déjà installés.
)

echo.
echo [2/2] Démarrage de TOP-BOX...
echo ========================================================================
echo   Identifiants de test pré-configurés :
echo   - Administrateur : admin / admin123
echo   - Caissier 1     : grace / 1234
echo   - Caissier 2     : junior / 1234
echo ========================================================================
echo.

:: Lancement effectif de app.py
python app.py

:: Si l'application se ferme avec une anomalie
if errorlevel 1 (
    color 0C
    echo.
    echo [INFO] L'application s'est fermée avec un code d'erreur.
    echo Consultez les messages ci-dessus si un message d'erreur est apparu.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Session TOP-BOX terminée normalement.
exit /b 0

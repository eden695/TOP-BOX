@echo off
chcp 65001 >nul
setlocal
title MINI SUPERMARCHE - EXE et installateur Windows
cd /d "%~dp0"
echo ===================================================
echo MINI SUPERMARCHE - CREATION EXE + INSTALLATEUR
echo ===================================================
where python >nul 2>nul
if errorlevel 1 (
 echo ERREUR : Python n'est pas installe ou absent du PATH.
 echo Installe Python 3.11 ou 3.12 depuis python.org, avec "Add Python to PATH".
 pause
 exit /b 1
)
echo [1/5] Installation des dependances...
python -m pip install --upgrade pip
if errorlevel 1 goto erreur
python -m pip install -r requirements.txt
if errorlevel 1 goto erreur
python -m pip install pyinstaller
if errorlevel 1 goto erreur
echo [2/5] Verification du code...
python -m py_compile app.py
if errorlevel 1 goto erreur
echo [3/5] Compilation de l'application...
if exist "build_temp" rmdir /s /q "build_temp"
if exist "dist" rmdir /s /q "dist"
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "MINI SUPERMARCHE" --distpath "dist" --workpath "build_temp" --icon "data\assets\app.ico" --add-data "data;data" --collect-all PIL app.py
if errorlevel 1 goto erreur
if not exist "dist\MINI SUPERMARCHE.exe" (echo ERREUR : EXE non genere.& goto erreur)
echo [4/5] Recherche d'Inno Setup...
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC (
 echo L'EXE a ete cree, mais Inno Setup 6 est necessaire pour fabriquer Setup.exe.
 echo Installe Inno Setup 6, puis relance ce fichier.
 echo EXE : "%CD%\dist\MINI SUPERMARCHE.exe"
 pause
 exit /b 2
)
echo [5/5] Creation de l'installateur...
"%ISCC%" "installer.iss"
if errorlevel 1 goto erreur
echo TERMINE !
echo INSTALLATEUR : %CD%\output\Setup_MINI_SUPERMARCHE.exe
echo Donnees client : %%LOCALAPPDATA%%\MINI_SUPERMARCHE
pause
exit /b 0
:erreur
echo ECHEC. Copie le texte de cette fenetre pour diagnostic.
pause
exit /b 1

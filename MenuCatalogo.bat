@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE="
if exist ".venv\Scripts\python.exe" set "PYTHON_EXE=.venv\Scripts\python.exe"

if not defined PYTHON_EXE (
    where py >nul 2>nul
    if not errorlevel 1 set "PYTHON_EXE=py"
)

if not defined PYTHON_EXE (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
    echo No se encontro un interprete de Python.
    pause
    exit /b 1
)

:menu
cls
echo ================================
echo         MENU DE OPCIONES
echo ================================
echo.
echo 1^) Generar catalogo
echo 2^) Descargar imagenes
echo 3^) Guardar y desplegar
echo 0^) Salir
echo.

choice /c 1230 /n /m "Selecciona una opcion: "

if errorlevel 4 goto salir
if errorlevel 3 goto desplegar
if errorlevel 2 goto descargar
if errorlevel 1 goto generar

goto menu

:generar
echo.
"%PYTHON_EXE%" "GenerarCatalogo.py"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo Error al ejecutar GenerarCatalogo.py
    pause
    goto menu
)

echo.
echo Catalogo generado correctamente.
pause
goto menu

:descargar
echo.
"%PYTHON_EXE%" "DescargarImagenes.py"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo Error al ejecutar DescargarImagenes.py
    pause
    goto menu
)

echo.
echo Descarga de imagenes completada.
pause
goto menu

:desplegar
echo.
"%PYTHON_EXE%" "GuardarYDesplegar.py"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo Error al ejecutar GuardarYDesplegar.py
    pause
    goto menu
)

echo.
echo Proyecto enviado correctamente.
pause
goto menu

:salir
exit /b 0
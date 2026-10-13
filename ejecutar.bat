@echo off
chcp 65001 > nul
echo ======================================================================
echo    SISTEMA DE TRADUCCIÓN DE LENGUAJE DE SEÑAS A VOZ EN ESPAÑOL
echo ======================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [!] No se encontro el entorno virtual .venv.
    echo Asegurate de crearlo con: uv venv --python 3.11 .venv
    pause
    exit /b
)

if not exist "models\best_model.pth" (
    echo [*] Descargando archivos del modelo preentrenado...
    .venv\Scripts\python.exe src\download_model.py
)

echo.
echo Selecciona el modo de ejecucion:
echo   [1] Iniciar Interfaz Web en Streamlit (Recomendado)
echo   [2] Iniciar Aplicacion de Escritorio Ligera (OpenCV nativo)
echo.
set /p opt="Opcion (1 o 2): "

if "%opt%"=="2" (
    echo.
    echo [*] Iniciando ventana de escritorio OpenCV...
    .venv\Scripts\python.exe app_desktop.py
) else (
    echo.
    echo [*] Iniciando servidor web de Streamlit...
    .venv\Scripts\python.exe -m streamlit run app.py
)

pause

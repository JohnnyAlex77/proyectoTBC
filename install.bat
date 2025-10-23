@echo off
echo ============================================
echo INSTALADOR AUTOMATICO - SISTEMA TBC
echo ============================================
echo.

echo 1. Actualizando pip...
python -m pip install --upgrade pip

echo.
echo 2. Instalando dependencias de Django...
pip install -r requirements.txt

echo.
echo ============================================
echo INSTALACION COMPLETADA EXITOSAMENTE!
echo ============================================
echo.
pause
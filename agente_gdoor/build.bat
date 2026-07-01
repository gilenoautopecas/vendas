@echo off
REM Gera o agente_gdoor.exe (rodar este script no Windows).
REM Requer Python instalado e este venv com pyinstaller (veja requirements-build.txt).

pip install -r requirements.txt
pip install -r requirements-build.txt

pyinstaller --onefile --console --name agente_gdoor agente.py

echo.
echo Build concluido. O executavel esta em dist\agente_gdoor.exe
echo Copie tambem o config.ini.example para a mesma pasta do .exe e renomeie para config.ini.
pause

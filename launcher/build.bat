@echo off
REM Gera o GSales.exe (rodar este script no Windows).
REM Requer Python instalado com pyinstaller: pip install pyinstaller

pip install pyinstaller --quiet

REM Com icone (descomente e ajuste o caminho se tiver um .ico):
REM pyinstaller --onefile --windowed --icon=launcher.ico --name GSales launcher.py

pyinstaller --onefile --windowed --name GSales launcher.py

echo.
echo ====================================================
echo  Build concluido!
echo  Executavel gerado em: dist\GSales.exe
echo.
echo  Copie GSales.exe para a pasta raiz do projeto
echo  (onde esta o manage.py) e crie um atalho dele
echo  na area de trabalho.
echo ====================================================
pause

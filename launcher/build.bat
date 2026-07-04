@echo off
REM Gera o GSales.exe (rodar este script no Windows).
REM Requer Python instalado.

pip install pyinstaller pystray pillow --quiet

pyinstaller --onefile --windowed --icon=gsales.ico --name GSales --add-data "gsales.ico;." --add-data "gsales.png;." launcher.py

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

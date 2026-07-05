@echo off
title Atualizando GSales...
echo ====================================================
echo   ATUALIZACAO DO GSALES
echo ====================================================
echo.

cd /d "%~dp0"

echo [1/4] Baixando atualizacoes...
git pull
if errorlevel 1 (
    echo.
    echo ERRO: Nao foi possivel baixar as atualizacoes.
    echo Verifique sua conexao com a internet.
    pause
    exit /b 1
)

echo.
echo [2/4] Atualizando dependencias...
venv\Scripts\pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo [3/4] Atualizando banco de dados...
venv\Scripts\python manage.py migrate --no-input
if errorlevel 1 (
    echo ERRO: Falha ao atualizar banco de dados.
    pause
    exit /b 1
)

echo.
echo [4/4] Concluido!
echo.
echo ====================================================
echo   GSales atualizado com sucesso!
echo   Abra o sistema normalmente pelo atalho.
echo ====================================================
echo.
pause

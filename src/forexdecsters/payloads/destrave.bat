@echo off
chcp 65001 >nul
title Destrave - desativar bloqueio por tentativas

:: Solicita privilegios de administrador se ainda nao estiver elevado
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   DESTRAVE
    echo ========================================
    echo.
    echo Este script precisa rodar como ADMINISTRADOR.
    echo.
    echo Em seguida o Windows vai perguntar:
    echo   "Deseja permitir que este aplicativo faca
    echo    alteracoes no dispositivo?"
    echo.
    echo Se voce deseja continuar, clique em SIM.
    echo.
    timeout /t 3 >nul
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo.
echo ========================================
echo   DESTRAVE - politica de bloqueio
echo ========================================
echo.
echo Aplicando: net accounts /lockoutthreshold:0
echo Aguarde...
echo.

net accounts /lockoutthreshold:0
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   CONCLUIDO COM SUCESSO
    echo ========================================
    echo.
    echo Sua VPS nao tera mais trava por tentativas
    echo de login erradas ^(bloqueio por forca bruta^).
    echo.
    echo O cliente podera acessar normalmente sem ficar
    echo preso em "conta bloqueada temporariamente".
    echo.
) else (
    echo.
    echo ========================================
    echo   ERRO
    echo ========================================
    echo.
    echo Nao foi possivel alterar a politica.
    echo Verifique se esta executando como administrador.
    echo Codigo do erro: %errorlevel%
    echo.
)

echo Se deseja continuar, aperte qualquer tecla para fechar...
pause >nul

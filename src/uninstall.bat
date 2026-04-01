@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Background Remover Studio Uninstall

call :find_python
if not defined PY_EXE (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Python nao foi encontrado.\n\nNada sera removido do ambiente Python.\nSe quiser limpar totalmente a versao portatil, apague esta pasta manualmente.','Background Remover Studio',[System.Windows.MessageBoxButton]::OK,[System.Windows.MessageBoxImage]::Information) | Out-Null"
    exit /b 0
)

call :find_pythonw
if defined PYW_EXE (
    start "" "%PYW_EXE%" "%~dp0setup_assistant.pyw" --uninstall
) else (
    start "" "%PY_EXE%" "%~dp0setup_assistant.pyw" --uninstall
)
exit /b 0

:find_python
set "PY_EXE="
for /f "delims=" %%I in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
    if not defined PY_EXE call :try_python "%%I"
)
if not defined PY_EXE (
    for /f "delims=" %%I in ('where python 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
if not defined PY_EXE (
    for /f "delims=" %%I in ('dir /b /s "%LocalAppData%\Programs\Python\Python*\python.exe" 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
if not defined PY_EXE (
    for /f "delims=" %%I in ('dir /b /s "%ProgramFiles%\Python*\python.exe" 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
if not defined PY_EXE (
    for /f "delims=" %%I in ('dir /b /s "%ProgramFiles(x86)%\Python*\python.exe" 2^>nul') do (
        if not defined PY_EXE call :try_python "%%I"
    )
)
exit /b 0

:find_pythonw
set "PYW_EXE="
if defined PY_EXE (
    set "PYW_EXE=%PY_EXE:python.exe=pythonw.exe%"
    if exist "%PYW_EXE%" exit /b 0
)
set "PYW_EXE="
for /f "delims=" %%I in ('where pythonw 2^>nul') do (
    if not defined PYW_EXE set "PYW_EXE=%%I"
)
if not defined PYW_EXE (
    for /f "delims=" %%I in ('dir /b /s "%LocalAppData%\Programs\Python\Python*\pythonw.exe" 2^>nul') do (
        if not defined PYW_EXE set "PYW_EXE=%%I"
    )
)
exit /b 0

:try_python
if defined PY_EXE exit /b 0
set "PY_CANDIDATE=%~1"
if not exist "%PY_CANDIDATE%" exit /b 0
"%PY_CANDIDATE%" -c "import sys" >nul 2>nul
if errorlevel 1 exit /b 0
set "PY_EXE=%PY_CANDIDATE%"
exit /b 0

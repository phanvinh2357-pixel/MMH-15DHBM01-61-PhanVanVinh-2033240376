@echo off
chcp 65001 >nul
title KIỂM THỬ TỰ ĐỘNG 15 CA AN TOÀN - BÀI TẬP 22 (HKDF)
cd /d "%~dp0"

set "PYTHON_EXE=python"
if exist "..\venv\Scripts\python.exe" (
    set "PYTHON_EXE=..\venv\Scripts\python.exe"
)

echo ======================================================================
echo   HỌC PHẦN: MẬT MÃ HỌC - TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP.HCM
echo   CHƯƠNG TRÌNH CHẠY TỰ ĐỘNG BỘ KIỂM THỬ (TEST SUITE - 15 CA KIỂM THỬ)
echo ======================================================================
echo.
echo [*] Đang kích hoạt kiểm thử tự động từ tệp: 03_SourceCode/test_suite.py...
echo.

"%PYTHON_EXE%" ..\03_SourceCode\test_suite.py -v

echo.
echo ======================================================================
echo   HOÀN TẤT KIỂM THỬ TOÀN DIỆN.
echo ======================================================================
pause
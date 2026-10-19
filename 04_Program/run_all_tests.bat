@echo off
chcp 65001 >nul
title KIỂM THỬ TỰ ĐỘNG 15 CA AN TOÀN - BÀI TẬP 22 (HKDF)
cd /d "%~dp0"

echo ======================================================================
echo   HỌC PHẦN: MẬT MÃ HỌC (0101100111) - ĐẠI HỌC CÔNG THƯƠNG TP.HCM (HUIT)
echo   CHƯƠNG TRÌNH CHẠY TỰ ĐỘNG BỘ KIỂM THỬ (TEST SUITE - 15 CA KIỂM THỬ)
echo ======================================================================
echo.
echo [*] Đang kích hoạt kiểm thử tự động từ tệp: 03_SourceCode/test_suite.py...
echo.

python ..\03_SourceCode\test_suite.py

echo.
echo ======================================================================
echo   HOÀN TẤT KIỂM THỬ TOÀN DIỆN.
echo ======================================================================
pause
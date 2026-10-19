@echo off
chcp 65001 >nul
title MÔ PHỎNG 3 KÊNH & 3 KỊCH BẢN TẤN CÔNG - BÀI TẬP 22 (HKDF)
cd /d "%~dp0"

echo ======================================================================
echo   HỌC PHẦN: MẬT MÃ HỌC (0101100111) - ĐẠI HỌC CÔNG THƯƠNG TP.HCM (HUIT)
echo   MÔ PHỎNG TRUYỀN THÔNG CLIENT - SERVER VÀ KIỂM THỬ TẤN CÔNG FAIL-CLOSED
echo ======================================================================
echo.
echo [*] Đang khởi chạy mô phỏng từ tệp: 03_SourceCode/simulation_runner.py...
echo.

python ..\03_SourceCode\simulation_runner.py

echo.
echo ======================================================================
echo   HOÀN TẤT MÔ PHỎNG QUY TRÌNH VÀ KIỂM CHỨNG TẤN CÔNG.
echo ======================================================================
pause
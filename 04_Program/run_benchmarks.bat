@echo off
chcp 65001 >nul
title ĐO LƯỜNG HIỆU NĂNG 5 KỊCH BẢN & XUẤT BIỂU ĐỒ - BÀI TẬP 22 (HKDF)
cd /d "%~dp0"

set "PYTHON_EXE=python"
if exist "..\venv\Scripts\python.exe" (
    set "PYTHON_EXE=..\venv\Scripts\python.exe"
)

echo ======================================================================
echo   HỌC PHẦN: MẬT MÃ HỌC (0101100111) - ĐẠI HỌC CÔNG THƯƠNG TP.HCM (HUIT)
echo   THỰC NGHIỆM ĐO KIỂM HIỆU NĂNG ĐỊNH LƯỢNG HKDF (5 KỊCH BẢN, N = 50)
echo ======================================================================
echo.
echo [1/2] Đang thực thi đo lường thời gian trễ và xuất tệp CSV...
"%PYTHON_EXE%" ..\03_SourceCode\benchmark_harness.py

if %errorlevel% neq 0 (
    echo.
    echo [!] LỖI: Quá trình đo lường hiệu năng gặp sự cố. Đã dừng bước vẽ biểu đồ.
    pause
    exit /b %errorlevel%
)

echo.
echo [2/2] Đang tự động vẽ biểu đồ phân tích thống kê (chuẩn 300 DPI)...
"%PYTHON_EXE%" ..\03_SourceCode\plot_benchmarks.py

echo.
echo ======================================================================
echo   HOÀN TẤT ĐO KIỂM VÀ XUẤT TOÀN BỘ KẾT QUẢ VÀO 06_ExperimentalResults/
echo ======================================================================
pause
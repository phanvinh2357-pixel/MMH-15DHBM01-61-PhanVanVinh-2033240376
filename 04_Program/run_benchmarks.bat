@echo off
chcp 65001 >nul
title ĐO LƯỜNG HIỆU NĂNG 5 KỊCH BẢN & XUẤT BIỂU ĐỒ - BÀI TẬP 22 (HKDF)
cd /d "%~dp0"

echo ======================================================================
echo   HỌC PHẦN: MẬT MÃ HỌC (0101100111) - ĐẠI HỌC CÔNG THƯƠNG TP.HCM (HUIT)
echo   THỰC NGHIỆM ĐO KIỂM HIỆU NĂNG ĐỊNH LƯỢNG HKDF (5 KỊCH BẢN, N >= 30)
echo ======================================================================
echo.
echo [1/2] Đang thực thi đo lường thời gian trễ và xuất tệp CSV...
python ..\03_SourceCode\benchmark_harness.py

echo.
echo [2/2] Đang tự động vẽ biểu đồ phân tích thống kê (chuẩn 300 DPI)...
python ..\03_SourceCode\plot_benchmarks.py

echo.
echo ======================================================================
echo   HOÀN TẤT ĐO KIỂM VÀ XUẤT TOÀN BỘ KẾT QUẢ VÀO 06_ExperimentalResults/
echo ======================================================================
pause
# PowerShell启动脚本
$Host.UI.RawUI.WindowTitle = "Markdown图片管家"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Markdown图片管家" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "正在启动应用程序..." -ForegroundColor Yellow
Write-Host ""

try {
    python markdown_image_manager.py
    Write-Host ""
    Write-Host "应用程序正常关闭。" -ForegroundColor Green
    Start-Sleep -Seconds 2
}
catch {
    Write-Host ""
    Write-Host "发生错误: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "按任意键退出..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
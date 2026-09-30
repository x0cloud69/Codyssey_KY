# =============================================================================
# verify-external.ps1 — 내 PC(Windows)에서 외부 접속 검증  [요구사항 4-5 (B)]
#   사용법:  powershell -ExecutionPolicy Bypass -File scripts\verify-external.ps1 -PublicIp 3.35.x.x
# =============================================================================
param(
    [Parameter(Mandatory = $true)][string]$PublicIp
)

$ErrorActionPreference = 'Stop'
$targets = @(
    @{ Name = '(A) 메인 페이지'; Url = "http://$PublicIp/" },
    @{ Name = '(B) 헬스체크';     Url = "http://$PublicIp/health" }
)

Write-Host "=== Task7 외부 접속 검증 ($(Get-Date -Format s)) ===" -ForegroundColor Cyan
$fail = 0
foreach ($t in $targets) {
    try {
        $r = Invoke-WebRequest -Uri $t.Url -UseBasicParsing -TimeoutSec 10
        $body = ($r.Content.Trim() -split "`n")[0]
        if ($body.Length -gt 60) { $body = $body.Substring(0, 60) + '...' }
        Write-Host ("[PASS] {0}  GET {1}  → {2}  body: {3}" -f $t.Name, $t.Url, $r.StatusCode, $body) -ForegroundColor Green
    } catch {
        $fail++
        Write-Host ("[FAIL] {0}  GET {1}  → {2}" -f $t.Name, $t.Url, $_.Exception.Message) -ForegroundColor Red
    }
}

# 22번 포트는 "내 IP"에서만 열려 있어야 함 — 여기서는 내 PC 기준 도달 여부만 표시
$ssh = Test-NetConnection -ComputerName $PublicIp -Port 22 -WarningAction SilentlyContinue
Write-Host ("[INFO] 22/tcp (내 IP에서) 연결 가능: {0}" -f $ssh.TcpTestSucceeded)

if ($fail -gt 0) {
    Write-Host "`n실패 항목이 있습니다. docs/troubleshooting.md 의 점검 순서를 참고하세요." -ForegroundColor Yellow
    exit 1
}

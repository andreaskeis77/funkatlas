# Register the probe as a per-user Scheduled Task (no elevation needed).
#   .\ops\autostart_install.ps1          -> install + start at logon
#   .\ops\autostart_install.ps1 -Remove  -> unregister
# NOTE: the task runs only while the user is logged on, and the laptop must
# stay awake during measurement windows — see docs/RUNBOOK.md (E9 checklist).
param([switch]$Remove)
$ErrorActionPreference = 'Stop'
$taskName = 'funkatlas-probe'
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

if ($Remove) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "$taskName removed"
    exit 0
}

$py = Join-Path $root '.venv\Scripts\pythonw.exe'
if (-not (Test-Path $py)) { throw "venv python not found: $py (run pip install -e . first)" }
$action = New-ScheduledTaskAction -Execute $py -Argument '-m funkatlas probe' -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -AtLogOn
# ExecutionTimeLimit 0 = unlimited: the Task Scheduler default (72h) would
# silently kill a multi-night continuous run — and a time-limit stop is not a
# "failure", so RestartCount would not bring it back.
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings | Out-Null
Write-Host "$taskName registered (runs at logon; restart on crash, 3x)."
Write-Host "Start now:  Start-ScheduledTask -TaskName $taskName"

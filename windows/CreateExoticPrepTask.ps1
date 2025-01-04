# Change {USERNAME} to your Windows username
# Open PowerShell as an administrator.
# Navigate to the directory where you saved the script.
# Run the script by typing .\CreateExoticPrepTask.ps1 and pressing Enter.

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c doskey exotic-prep=python C:\Users\{USERNAME}\exotic-prep\exotic-prep.py"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings -TaskName "ExoticPrepTCommand" -Description "Runs doskey command at logon for exotic-prep"

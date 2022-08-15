WHERE python3
IF %ERRORLEVEL% NEQ 0 (
    start cmd.exe /k "%~d0 && cd %~p0 && python bot.py"
) ELSE (
    start cmd.exe /k "%~d0 && cd %~p0 && python3 bot.py"
)
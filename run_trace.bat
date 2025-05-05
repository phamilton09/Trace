@echo off
echo Starting Trace...

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run the application
python Trace_v3.py

:: Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause 
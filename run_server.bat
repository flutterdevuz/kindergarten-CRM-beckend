@echo off
echo KinderCRM serverini 4455 portida ishga tushirish (Production)...
C:\Users\mobil\AppData\Local\Python\pythoncore-3.14-64\python.exe -m waitress --port=4455 kindergarden.wsgi:application
pause

@echo off
echo ===============================
echo Git Pull
echo ===============================
git pull

echo.
echo ===============================
echo Git Add
echo ===============================
git add .

echo.
set /p commitmsg=Introduce el mensaje del commit: 

echo.
echo ===============================
echo Git Commit
echo ===============================
git commit -m "%commitmsg%"

echo.
echo ===============================
echo Git Push
echo ===============================
git push

echo.
echo Operacion finalizada.
pause

@echo off
REM SMS Spam Detection — Ortam Kurulum Scripti (Windows)
REM Kullanım: setup.bat dosyasına çift tıkla ya da cmd'den çalıştır

SET ENV_NAME=spam_env

REM Python 3.11 var mı kontrol et
python --version 2>NUL | findstr "3.11" >NUL
IF ERRORLEVEL 1 (
    echo Python 3.11 bulunamadi. Lutfen once Python 3.11 kurun:
    echo   https://www.python.org/downloads/release/python-3119/
    echo Kurulumda "Add Python to PATH" secenegini isaretleyin.
    pause
    exit /b 1
)

echo Python surumu:
python --version

REM Sanal ortam oluştur
IF EXIST %ENV_NAME% (
    echo Ortam zaten mevcut: %ENV_NAME%
) ELSE (
    echo Sanal ortam olusturuluyor: %ENV_NAME%
    python -m venv %ENV_NAME%
)

REM Ortamı aktive et ve kütüphaneleri kur
echo Kutuphaneler kuruluyor...
call %ENV_NAME%\Scripts\activate
pip install --upgrade pip -q
pip install -r requirements.txt

echo.
echo Kurulum tamamlandi.
echo.
echo Jupyter baslatmak icin:
echo   %ENV_NAME%\Scripts\activate
echo   jupyter notebook
pause

#!/bin/bash
# SMS Spam Detection — Ortam Kurulum Scripti (Mac / Linux)
# Kullanım: bash setup.sh

set -e

PYTHON="python3.11"
ENV_NAME="spam_env"

# Python 3.11 var mı kontrol et
if ! command -v $PYTHON &> /dev/null; then
    echo "Python 3.11 bulunamadı. Lütfen önce Python 3.11 kurun:"
    echo "  Mac:   brew install python@3.11"
    echo "  Linux: sudo apt install python3.11 python3.11-venv"
    exit 1
fi

echo "Python sürümü: $($PYTHON --version)"

# Sanal ortam oluştur
if [ -d "$ENV_NAME" ]; then
    echo "Ortam zaten mevcut: $ENV_NAME"
else
    echo "Sanal ortam oluşturuluyor: $ENV_NAME"
    $PYTHON -m venv $ENV_NAME
fi

# Ortamı aktive et ve kütüphaneleri kur
echo "Kütüphaneler kuruluyor..."
source $ENV_NAME/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

echo ""
echo "Kurulum tamamlandı."
echo ""
echo "Jupyter başlatmak için:"
echo "  source $ENV_NAME/bin/activate"
echo "  jupyter notebook"

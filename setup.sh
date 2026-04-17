#!/bin/bash

echo "=== Setup do projeto Cantina Escolar ==="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 nao encontrado."
    echo "Instale em https://www.python.org/downloads/"
    exit 1
fi

echo "Python encontrado: $(python3 --version)"
echo ""

echo "Criando ambiente virtual..."
python3 -m venv .venv

echo "Ativando ambiente virtual..."
source .venv/bin/activate

cho "Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "Aplicando migrations..."
python3 manage.py migrate

echo ""
echo "=== Setup concluido! ==="
echo ""
echo "Para rodar o projeto:"
echo "  1. source .venv/bin/activate"
echo "  2. python3 manage.py runserver"
echo "  3. Abra http://127.0.0.1:8000/ no navegador"
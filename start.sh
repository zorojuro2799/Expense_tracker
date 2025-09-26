#!/bin/bash


sudo apt-get update

sudo apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev pkg-config

streamlit run app.py --server.port $PORT --server.enableCORS false

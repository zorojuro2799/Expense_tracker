# Expense_tracker
A lightweight Streamlit app that extracts data from bills using OCR (Tesseract), tracks expenses automatically, and maps restaurant locations.
Coordinates are saved in both decimal and NMEA protocol formats.


✨ Features
📷 Upload bill images → extract text & total via OCR

🏪 Detect restaurant names & geolocate them

🌍 Store coordinates in decimal + NMEA protocol

💰 Automatic expense logging (default: Food)

📝 Add manual expenses from sidebar

📊 View total expenses + interactive map of restaurants


🛠 Tech Stack
Python, Streamlit
Pytesseract, Pillow
Geopy
Folium + streamlit-folium


🚀 Deployment
Hosted on Render
requirements.txt → Python dependencies
apt.txt → installs Tesseract OCR

⚡ For Local Setup
# Clone repo
git clone https://github.com/zorojuro2799/Expense_tracker.git
cd Expense_tracker
# Install dependencies
pip install -r requirements.txt
# Run app
streamlit run app.py


📜 License
MIT License – free to use and modify.


This project demonstrates how to combine OCR, geolocation, expense tracking, and the NMEA protocol into a single Streamlit web application.


# # import pytesseract
# # from PIL import Image
# # import json
# # from geopy.geocoders import Nominatim

# # # Configure path to tesseract executable if needed
# # # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# # def extract_text_from_image(image_path):
# #     image = Image.open(image_path)
# #     text = pytesseract.image_to_string(image)
# #     return text

# # def extract_restaurant_name(text):
# #     lines = text.split('\n')
# #     for line in lines:
# #         if line.strip() != '':
# #             return line.strip()
# #     return "Unknown"

# # def get_geolocation(restaurant_name):
# #     geolocator = Nominatim(user_agent="bill_locator")
# #     location = geolocator.geocode(restaurant_name)
# #     if location:
# #         return {'latitude': location.latitude, 'longitude': location.longitude}
# #     else:
# #         return {'latitude': None, 'longitude': None}

# # def decimal_to_nmea(lat, lon):
# #     """
# #     Convert decimal degrees to NMEA format.
# #     Returns a dict: {'lat_nmea': '...', 'lon_nmea': '...'}
# #     """
# #     def convert(coord, is_lat=True):
# #         direction = ''
# #         if is_lat:
# #             direction = 'N' if coord >= 0 else 'S'
# #         else:
# #             direction = 'E' if coord >= 0 else 'W'
# #         coord = abs(coord)
# #         degrees = int(coord)
# #         minutes = (coord - degrees) * 60
# #         # Format as ddmm.mmmm for lat, dddmm.mmmm for lon
# #         if is_lat:
# #             nmea = f"{degrees:02d}{minutes:07.4f},{direction}"
# #         else:
# #             nmea = f"{degrees:03d}{minutes:07.4f},{direction}"
# #         return nmea

# #     return {
# #         'lat_nmea': convert(lat, is_lat=True),
# #         'lon_nmea': convert(lon, is_lat=False)
# #     }

# # def create_bill_entry(image_path, json_file='bills.json'):
# #     text = extract_text_from_image(image_path)
# #     restaurant_name = extract_restaurant_name(text)
# #     location = get_geolocation(restaurant_name)

# #     # Convert to NMEA
# #     nmea_coords = decimal_to_nmea(location.get('latitude', 0), location.get('longitude', 0))
# #     location.update(nmea_coords)

# #     bill_entry = {
# #         'restaurant': restaurant_name,
# #         'bill_text': text,
# #         'location': location
# #     }

# #     # Append to JSON file
# #     try:
# #         with open(json_file, 'r') as f:
# #             data = json.load(f)
# #     except FileNotFoundError:
# #         data = []

# #     data.append(bill_entry)

# #     with open(json_file, 'w') as f:
# #         json.dump(data, f, indent=4)

# #     print(f"Entry added for {restaurant_name}.")

# #     # Generate map HTML
# #     generate_map_html(restaurant_name, location)

# # def generate_map_html(restaurant_name, location, output_file='map.html'):
# #     lat = location.get('latitude', 0)
# #     lon = location.get('longitude', 0)

# #     html_content = f"""
# #     <!DOCTYPE html>
# #     <html>
# #     <head>
# #         <meta charset="utf-8" />
# #         <title>Restaurant Location Map</title>
# #         <meta name="viewport" content="width=device-width, initial-scale=1.0">
# #         <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
# #         <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
# #         <style>#map {{ height: 500px; width: 100%; }}</style>
# #     </head>
# #     <body>
# #     <h2>{restaurant_name} Location</h2>
# #     <div id="map"></div>
# #     <script>
# #         const latitude = {lat};
# #         const longitude = {lon};

# #         const map = L.map('map').setView([latitude, longitude], 15);

# #         L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
# #             attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
# #         }}).addTo(map);

# #         L.marker([latitude, longitude]).addTo(map)
# #             .bindPopup('<b>{restaurant_name}</b><br>Here is your restaurant.')
# #             .openPopup();
# #     </script>
# #     </body>
# #     </html>
# #     """

# #     with open(output_file, 'w') as f:
# #         f.write(html_content)

# #     print(f"Map HTML generated: {output_file}")


# # # Example usage
# # if __name__ == "__main__":
# #     image_path = "/root/code/create1.png"
# #     create_bill_entry(image_path)
 
# import pytesseract
# from PIL import Image
# import json
# from geopy.geocoders import Nominatim

# # Configure path to tesseract executable if needed
# # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# BILLS_FILE = 'bills.json'
# EXPENSES_FILE = 'expenses.json'

# def extract_text_from_image(image_path):
#     image = Image.open(image_path)
#     text = pytesseract.image_to_string(image)
#     return text

# def extract_restaurant_name(text):
#     lines = text.split('\n')
#     for line in lines:
#         if line.strip() != '':
#             return line.strip()
#     return "Unknown"

# def extract_bill_amount(text):
#     """
#     A simple heuristic to extract bill amount.
#     Finds the last number in the text that looks like a price.
#     """
#     import re
#     matches = re.findall(r'\d+\.\d{2}', text)
#     if matches:
#         return float(matches[-1])
#     return None

# def get_geolocation(restaurant_name):
#     geolocator = Nominatim(user_agent="bill_locator")
#     location = geolocator.geocode(restaurant_name)
#     if location:
#         return {'latitude': location.latitude, 'longitude': location.longitude}
#     else:
#         return {'latitude': None, 'longitude': None}

# def decimal_to_nmea(lat, lon):
#     def convert(coord, is_lat=True):
#         direction = 'N' if (coord >= 0 and is_lat) else ('S' if is_lat else 'E' if coord >=0 else 'W')
#         coord = abs(coord)
#         degrees = int(coord)
#         minutes = (coord - degrees) * 60
#         if is_lat:
#             return f"{degrees:02d}{minutes:07.4f},{direction}"
#         else:
#             return f"{degrees:03d}{minutes:07.4f},{direction}"
#     return {'lat_nmea': convert(lat, True), 'lon_nmea': convert(lon, False)}

# def create_bill_entry(image_path, add_as_expense=True):
#     text = extract_text_from_image(image_path)
#     restaurant_name = extract_restaurant_name(text)
#     location = get_geolocation(restaurant_name)

#     # Convert to NMEA
#     nmea_coords = decimal_to_nmea(location.get('latitude', 0), location.get('longitude', 0))
#     location.update(nmea_coords)

#     # Extract bill amount
#     amount = extract_bill_amount(text)

#     bill_entry = {
#         'restaurant': restaurant_name,
#         'bill_text': text,
#         'location': location,
#         'amount': amount
#     }

#     # Append to bills.json
#     try:
#         with open(BILLS_FILE, 'r') as f:
#             bills = json.load(f)
#     except FileNotFoundError:
#         bills = []

#     bills.append(bill_entry)

#     with open(BILLS_FILE, 'w') as f:
#         json.dump(bills, f, indent=4)

#     print(f"Entry added for {restaurant_name}.")

#     # Add expense if requested
#     if add_as_expense and amount is not None:
#         add_expense(amount, 'Food', f'Bill at {restaurant_name}')

#     # Generate map
#     generate_map_html(restaurant_name, location)

# def generate_map_html(restaurant_name, location, output_file='map.html'):
#     lat = location.get('latitude', 0)
#     lon = location.get('longitude', 0)
#     html_content = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <meta charset="utf-8" />
#         <title>Restaurant Location Map</title>
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
#         <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
#         <style>#map {{ height: 500px; width: 100%; }}</style>
#     </head>
#     <body>
#     <h2>{restaurant_name} Location</h2>
#     <div id="map"></div>
#     <script>
#         const latitude = {lat};
#         const longitude = {lon};

#         const map = L.map('map').setView([latitude, longitude], 15);

#         L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
#             attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
#         }}).addTo(map);

#         L.marker([latitude, longitude]).addTo(map)
#             .bindPopup('<b>{restaurant_name}</b><br>Lat: {location["lat_nmea"]}, Lon: {location["lon_nmea"]}')
#             .openPopup();
#     </script>
#     </body>
#     </html>
#     """
#     with open(output_file, 'w') as f:
#         f.write(html_content)
#     print(f"Map HTML generated: {output_file}")

# # ================== Expenses Functions ==================
# def add_expense(amount, category, description=''):
#     expense_entry = {
#         'amount': amount,
#         'category': category,
#         'description': description
#     }

#     try:
#         with open(EXPENSES_FILE, 'r') as f:
#             expenses = json.load(f)
#     except FileNotFoundError:
#         expenses = []

#     expenses.append(expense_entry)

#     with open(EXPENSES_FILE, 'w') as f:
#         json.dump(expenses, f, indent=4)

#     print(f"Added expense: {amount} in category '{category}'")

# def display_expenses():
#     try:
#         with open(EXPENSES_FILE, 'r') as f:
#             expenses = json.load(f)
#     except FileNotFoundError:
#         print("No expenses recorded yet.")
#         return

#     if not expenses:
#         print("No expenses recorded yet.")
#         return

#     print("All Expenses:")
#     for i, exp in enumerate(expenses, start=1):
#         amount = exp.get('amount', 0)
#         category = exp.get('category', 'Unknown')
#         description = exp.get('description', '')
#         print(f"{i}. {amount} - {category} ({description})")

# # ================== Example Usage ==================
# if __name__ == "__main__":
#     image_path = "/root/code/create1.png"
#     create_bill_entry(image_path)

#     # Optionally, display all expenses
#     display_expenses()

# import streamlit as st
# import os
# import pytesseract
# from PIL import Image
# import json
# from geopy.geocoders import Nominatim
# import folium
# from streamlit_folium import st_folium

# # Configure paths
# BILLS_FILE = 'bills.json'
# EXPENSES_FILE = 'expenses.json'
# UPLOAD_FOLDER = 'uploaded_bills'

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# # ================== Helper Functions ==================
# def extract_text_from_image(image_path):
#     image = Image.open(image_path)
#     text = pytesseract.image_to_string(image)
#     return text

# def extract_restaurant_name(text):
#     lines = text.split('\n')
#     for line in lines:
#         if line.strip() != '':
#             return line.strip()
#     return "Unknown"

# def extract_bill_amount(text):
#     import re
#     matches = re.findall(r'\d+\.\d{2}', text)
#     if matches:
#         return float(matches[-1])
#     return None

# def get_geolocation(restaurant_name):
#     geolocator = Nominatim(user_agent="bill_locator")
#     location = geolocator.geocode(restaurant_name)
#     if location:
#         return {'latitude': location.latitude, 'longitude': location.longitude}
#     else:
#         return {'latitude': None, 'longitude': None}

# def decimal_to_nmea(lat, lon):
#     def convert(coord, is_lat=True):
#         direction = 'N' if (coord >= 0 and is_lat) else ('S' if is_lat else 'E' if coord >=0 else 'W')
#         coord = abs(coord)
#         degrees = int(coord)
#         minutes = (coord - degrees) * 60
#         if is_lat:
#             return f"{degrees:02d}{minutes:07.4f},{direction}"
#         else:
#             return f"{degrees:03d}{minutes:07.4f},{direction}"
#     return {'lat_nmea': convert(lat, True), 'lon_nmea': convert(lon, False)}

# def add_expense(amount, category, description=''):
#     expense_entry = {
#         'amount': amount,
#         'category': category,
#         'description': description
#     }
#     try:
#         with open(EXPENSES_FILE, 'r') as f:
#             expenses = json.load(f)
#     except FileNotFoundError:
#         expenses = []

#     expenses.append(expense_entry)

#     with open(EXPENSES_FILE, 'w') as f:
#         json.dump(expenses, f, indent=4)

# def display_expenses():
#     try:
#         with open(EXPENSES_FILE, 'r') as f:
#             expenses = json.load(f)
#     except FileNotFoundError:
#         return []
#     return expenses

# def calculate_total_expense():
#     expenses = display_expenses()
#     total = sum(exp.get('amount', 0) for exp in expenses)
#     return total


# def create_bill_entry(image_path, add_as_expense=True):
#     text = extract_text_from_image(image_path)
#     restaurant_name = extract_restaurant_name(text)
#     location = get_geolocation(restaurant_name)
#     nmea_coords = decimal_to_nmea(location.get('latitude', 0), location.get('longitude', 0))
#     location.update(nmea_coords)
#     amount = extract_bill_amount(text)

#     bill_entry = {
#         'restaurant': restaurant_name,
#         'bill_text': text,
#         'location': location,
#         'amount': amount,
#         'bill_image': os.path.basename(image_path) 
#     }

   

#     try:
#         with open(BILLS_FILE, 'r') as f:
#             bills = json.load(f)
#     except FileNotFoundError:
#         bills = []

#     bills.append(bill_entry)

#     with open(BILLS_FILE, 'w') as f:
#         json.dump(bills, f, indent=4)

#     if add_as_expense and amount is not None:
#         add_expense(amount, 'Food', f'Bill at {restaurant_name}')

#     return bill_entry

# def load_bills():
#     try:
#         with open(BILLS_FILE, 'r') as f:
#             bills = json.load(f)
#     except FileNotFoundError:
#         bills = []
#     return bills

# # ================== Streamlit App ==================
# st.title("📄 Bill OCR & Expense Tracker with Map")

# # --- Upload Bill Image ---
# st.header("Upload Bill Image")
# uploaded_file = st.file_uploader("Choose a bill image", type=['png', 'jpg', 'jpeg'])
# if uploaded_file is not None:
#     image_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
#     with open(image_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())
    
#     bill_entry = create_bill_entry(image_path)
#     st.success(f"Bill processed for {bill_entry['restaurant']}")
#     st.write("Extracted Text:")
#     st.text(bill_entry['bill_text'])
#     if bill_entry['amount'] is not None:
#         st.write(f"Detected Amount: {bill_entry['amount']}")

# # --- Manual Expense Entry ---
# st.header("Add Manual Expense")
# with st.form("manual_expense"):
#     amount = st.number_input("Amount", min_value=0.0, step=0.01)
#     category = st.text_input("Category")
#     description = st.text_input("Description")
#     submitted = st.form_submit_button("Add Expense")
#     if submitted:
#         add_expense(amount, category, description)
#         st.success(f"Added expense: {amount} ({category})")

# # --- Display Expenses ---
# st.header("All Expenses")
# expenses = display_expenses()
# if not expenses:
#     st.write("No expenses recorded yet.")
# else:
#     total = calculate_total_expense()
#     st.write(f"**Total Expense:** {total}")
#     for i, exp in enumerate(expenses, start=1):
#         st.write(f"{i}. {exp['amount']} - {exp['category']} ({exp['description']})")

# # --- Display Map ---
# # --- Display Map ---
# st.header("Restaurant Locations Map")
# bills = load_bills()
 
# if bills:
#     # Create map centered on the first bill with valid coordinates
#     first_valid = next((b for b in bills if b['location'].get('latitude') and b['location'].get('longitude')), None)
#     if first_valid:
#         m = folium.Map(location=[first_valid['location']['latitude'], first_valid['location']['longitude']], zoom_start=12)
#     else:
#         m = folium.Map(location=[0, 0], zoom_start=2)

#     for bill in bills:
#         loc = bill['location']
#         if loc.get('latitude') is not None and loc.get('longitude') is not None:
#             # Ensure NMEA fields exist
#             if 'lat_nmea' not in loc or 'lon_nmea' not in loc:
#                 nmea_coords = decimal_to_nmea(loc['latitude'], loc['longitude'])
#                 loc.update(nmea_coords)

#             folium.Marker(
#                 location=[loc['latitude'], loc['longitude']],
#                 popup=f"{bill['restaurant']}<br>Lat: {loc['lat_nmea']}<br>Lon: {loc['lon_nmea']}<br>Amount: {bill.get('amount', 'N/A')}"
#             ).add_to(m)
    
#     st_folium(m, width=700, height=500)
# else:
#     st.write("No bills uploaded yet to display on map.")

import streamlit as st
import os
import pytesseract
from PIL import Image
import json
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

# Configure paths
BILLS_FILE = 'bills.json'
EXPENSES_FILE = 'expenses.json'
UPLOAD_FOLDER = 'uploaded_bills'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ================== Helper Functions ==================
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_restaurant_name(text):
    lines = text.split('\n')
    for line in lines:
        if line.strip() != '':
            return line.strip()
    return "Unknown"

def extract_bill_amount(text):
    import re
    matches = re.findall(r'\d+\.\d{2}', text)
    if matches:
        return float(matches[-1])
    return None

def get_geolocation(restaurant_name):
    geolocator = Nominatim(user_agent="bill_locator")
    location = geolocator.geocode(restaurant_name)
    if location:
        return {'latitude': location.latitude, 'longitude': location.longitude}
    else:
        return {'latitude': None, 'longitude': None}

def decimal_to_nmea(lat, lon):
    def convert(coord, is_lat=True):
        direction = 'N' if (coord >= 0 and is_lat) else ('S' if is_lat else 'E' if coord >=0 else 'W')
        coord = abs(coord)
        degrees = int(coord)
        minutes = (coord - degrees) * 60
        if is_lat:
            return f"{degrees:02d}{minutes:07.4f},{direction}"
        else:
            return f"{degrees:03d}{minutes:07.4f},{direction}"
    return {'lat_nmea': convert(lat, True), 'lon_nmea': convert(lon, False)}

def add_expense(amount, category, description=''):
    expense_entry = {
        'amount': amount,
        'category': category,
        'description': description
    }
    try:
        with open(EXPENSES_FILE, 'r') as f:
            expenses = json.load(f)
    except FileNotFoundError:
        expenses = []

    expenses.append(expense_entry)

    with open(EXPENSES_FILE, 'w') as f:
        json.dump(expenses, f, indent=4)

def display_expenses():
    try:
        with open(EXPENSES_FILE, 'r') as f:
            expenses = json.load(f)
    except FileNotFoundError:
        return []
    return expenses

def calculate_total_expense():
    expenses = display_expenses()
    total = sum(exp.get('amount', 0) for exp in expenses)
    return total

def create_bill_entry(image_path, add_as_expense=True):
    text = extract_text_from_image(image_path)
    restaurant_name = extract_restaurant_name(text)
    location = get_geolocation(restaurant_name)
    nmea_coords = decimal_to_nmea(location.get('latitude', 0), location.get('longitude', 0))
    location.update(nmea_coords)
    amount = extract_bill_amount(text)

    bill_entry = {
        'restaurant': restaurant_name,
        'bill_text': text,
        'location': location,
        'amount': amount,
        'bill_image': os.path.basename(image_path) 
    }

    try:
        with open(BILLS_FILE, 'r') as f:
            bills = json.load(f)
    except FileNotFoundError:
        bills = []

    bills.append(bill_entry)

    with open(BILLS_FILE, 'w') as f:
        json.dump(bills, f, indent=4)

    if add_as_expense and amount is not None:
        add_expense(amount, 'Food', f'Bill at {restaurant_name}')

    return bill_entry

def load_bills():
    try:
        with open(BILLS_FILE, 'r') as f:
            bills = json.load(f)
    except FileNotFoundError:
        bills = []
    return bills

# ================== Streamlit App ==================
st.set_page_config(layout="wide")
st.title("📄 Bill OCR & Expense Tracker with Map")

# --- Sidebar: Total Expense and Manual Entry ---
st.sidebar.header("💰 Total Expense")
total = calculate_total_expense()
st.sidebar.metric("Total Expense", f"${total:.2f}")

st.sidebar.header("Add Manual Expense")
with st.sidebar.form("manual_expense_sidebar"):
    amount = st.number_input("Amount", min_value=0.0, step=0.01, key="sidebar_amount")
    category = st.text_input("Category", key="sidebar_category")
    description = st.text_input("Description", key="sidebar_description")
    submitted = st.form_submit_button("Add Expense")
    if submitted:
        add_expense(amount, category, description)
        st.success(f"Added expense: {amount} ({category})")
        total = calculate_total_expense()  # update total

# --- Upload Bill Image ---
st.header("Upload Bill Image")
uploaded_file = st.file_uploader("Choose a bill image", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Reset the processed flag if a new file is uploaded
    if 'last_uploaded_file' not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.bill_processed = False
        st.session_state.last_uploaded_file = uploaded_file.name

    if not st.session_state.get('bill_processed', False):
        image_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        bill_entry = create_bill_entry(image_path)
        st.success(f"Bill processed for {bill_entry['restaurant']}")
        st.write("Extracted Text:")
        st.text(bill_entry['bill_text'])
        if bill_entry['amount'] is not None:
            st.write(f"Detected Amount: {bill_entry['amount']}")

        st.session_state.bill_processed = True
# --- Display Expenses ---
st.header("All Expenses")
expenses = display_expenses()
if not expenses:
    st.write("No expenses recorded yet.")
else:
    st.write(f"**Total Expense:** {calculate_total_expense()}")
    for i, exp in enumerate(expenses, start=1):
        st.write(f"{i}. {exp['amount']} - {exp['category']} ({exp['description']})")

# --- Display Map ---
st.header("Restaurant Locations Map")
bills = load_bills()
if bills:
    first_valid = next((b for b in bills if b['location'].get('latitude') and b['location'].get('longitude')), None)
    if first_valid:
        m = folium.Map(location=[first_valid['location']['latitude'], first_valid['location']['longitude']], zoom_start=12)
    else:
        m = folium.Map(location=[0, 0], zoom_start=2)

    for bill in bills:
        loc = bill['location']
        if loc.get('latitude') is not None and loc.get('longitude') is not None:
            if 'lat_nmea' not in loc or 'lon_nmea' not in loc:
                nmea_coords = decimal_to_nmea(loc['latitude'], loc['longitude'])
                loc.update(nmea_coords)

            folium.Marker(
                location=[loc['latitude'], loc['longitude']],
                popup=f"{bill['restaurant']}<br>Lat: {loc['lat_nmea']}<br>Lon: {loc['lon_nmea']}<br>Amount: {bill.get('amount', 'N/A')}"
            ).add_to(m)
    
    st_folium(m, width=700, height=500)
else:
    st.write("No bills uploaded yet to display on map.")

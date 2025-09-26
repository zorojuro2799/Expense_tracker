import streamlit as st
import os
import pytesseract
from PIL import Image
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import folium
from streamlit_folium import st_folium
import re
import hashlib
from datetime import datetime
import pandas as pd
import plotly.express as px
import calendar

BILLS_FILE = 'data/bills.json'
EXPENSES_FILE = 'data/expenses.json'
USERS_FILE = 'data/users.json'
UPLOAD_FOLDER = 'uploaded_bills'
DATA_FOLDER = 'data'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_files():
    files = {
        BILLS_FILE: [],
        EXPENSES_FILE: [],
        USERS_FILE: {'users': []}
    }
    for file, default in files.items():
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump(default, f, indent=4)

def load_data(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        initialize_files()
        return load_data(filename)

def save_data(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return ""

def extract_restaurant_name(text):
    lines = text.split('\n')
    for line in lines:
        if line.strip() and len(line.strip()) > 3:
            return line.strip()
    return "Unknown"

def extract_bill_amount(text):
    matches = re.findall(r'\d+\.\d{2}\b', text)
    if matches:
        return float(matches[-1])
    return None

def get_geolocation(restaurant_name):
    geolocator = Nominatim(user_agent="bill_locator")
    try:
        location = geolocator.geocode(restaurant_name, timeout=10)
        if location:
            return {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'address': location.address
            }
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        st.warning(f"Geocoding service error: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected geocoding error: {str(e)}")
    return {'latitude': None, 'longitude': None, 'address': None}

def decimal_to_nmea(lat, lon):
    if lat is None or lon is None:
        return {'lat_nmea': 'N/A', 'lon_nmea': 'N/A'}
    def convert(coord, is_lat=True):
        direction = 'N' if (coord >= 0 and is_lat) else ('S' if is_lat else 'E' if coord >=0 else 'W')
        coord = abs(coord)
        degrees = int(coord)
        minutes = (coord - degrees) * 60
        if is_lat:
            return f"{degrees:02d}{minutes:07.4f}{direction}"
        else:
            return f"{degrees:03d}{minutes:07.4f}{direction}"
    return {
        'lat_nmea': convert(lat, True),
        'lon_nmea': convert(lon, False),
        'lat_dir': 'N' if lat >=0 else 'S',
        'lon_dir': 'E' if lon >=0 else 'W'
    }

def add_expense(amount, category, description='', username=None):
    expenses = load_data(EXPENSES_FILE)
    expense_entry = {
        'amount': amount,
        'category': category,
        'description': description,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user': username
    }
    expenses.append(expense_entry)
    save_data(EXPENSES_FILE, expenses)
    st.rerun()

def create_bill_entry(image_path, username=None):
    text = extract_text_from_image(image_path)
    restaurant_name = extract_restaurant_name(text)
    location = get_geolocation(restaurant_name)
    nmea_coords = decimal_to_nmea(location.get('latitude'), location.get('longitude'))
    location.update(nmea_coords)
    amount = extract_bill_amount(text)
    bill_entry = {
        'restaurant': restaurant_name,
        'bill_text': text,
        'location': location,
        'amount': amount,
        'bill_image': os.path.basename(image_path),
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user': username
    }
    bills = load_data(BILLS_FILE)
    bills.append(bill_entry)
    save_data(BILLS_FILE, bills)
    if amount is not None:
        add_expense(amount, 'Food', f'Bill at {restaurant_name}', username)
    return bill_entry

def authenticate(username, password):
    users_data = load_data(USERS_FILE)
    hashed_pw = hash_password(password)
    for user in users_data['users']:
        if user['username'] == username and user['password'] == hashed_pw:
            return True
    return False

def register_user(username, password):
    users_data = load_data(USERS_FILE)
    for user in users_data['users']:
        if user['username'] == username:
            return False, "Username already exists"
    hashed_pw = hash_password(password)
    users_data['users'].append({
        'username': username,
        'password': hashed_pw
    })
    if save_data(USERS_FILE, users_data):
        return True, "Registration successful"
    return False, "Registration failed"

def create_map(bills, username=None):
    if not bills:
        return None
    user_bills = [b for b in bills if username is None or b.get('user') == username]
    first_valid = next((b for b in user_bills if b['location'].get('latitude') is not None), None)
    if first_valid:
        m = folium.Map(
            location=[first_valid['location']['latitude'], 
            first_valid['location']['longitude']],
            zoom_start=12
        )
    else:
        m = folium.Map(location=[0, 0], zoom_start=2)
    for bill in user_bills:
        loc = bill['location']
        if loc.get('latitude') is not None:
            popup_content = f"""
                <b>{bill['restaurant']}</b><br>
                Amount: {bill.get('amount', 'N/A')}<br>
                Date: {bill.get('date', 'Unknown')}<br>
                Decimal: {loc['latitude']:.4f}°{loc['lat_dir']}, {loc['longitude']:.4f}°{loc['lon_dir']}<br>
                NMEA: {loc['lat_nmea']}, {loc['lon_nmea']}
            """
            folium.Marker(
                location=[loc['latitude'], loc['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color='red', icon='cutlery', prefix='fa')
            ).add_to(m)
    return m

def prepare_expense_data(expenses):
    if not expenses:
        return None
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.date
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['month_name'] = df['month'].apply(lambda x: calendar.month_abbr[x])
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    df['amount'] = pd.to_numeric(df['amount'])
    return df

def create_expense_charts(df):
    if df is None or df.empty:
        return None, None, None, None
    daily_df = df.groupby('day')['amount'].sum().reset_index()
    daily_fig = px.line(daily_df, x='day', y='amount', 
                        title='Daily Expenses Trend',
                        labels={'amount': 'Amount ($)', 'day': 'Date'})
    daily_fig.update_traces(line_color='#FF4B4B', line_width=2)
    daily_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    monthly_df = df.groupby(['year_month', 'month_name', 'year'])['amount'].sum().reset_index()
    monthly_fig = px.bar(monthly_df, x='year_month', y='amount', 
                         title='Monthly Expenses',
                         labels={'amount': 'Amount ($)', 'year_month': 'Month'},
                         color='amount',
                         color_continuous_scale='Bluered')
    monthly_fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': monthly_df['year_month']})
    category_df = df.groupby('category')['amount'].sum().reset_index()
    category_fig = px.pie(category_df, values='amount', names='category',
                          title='Expense Distribution by Category',
                          hole=0.3)
    category_fig.update_traces(textposition='inside', textinfo='percent+label')
    yearly_df = df.groupby('year')['amount'].sum().reset_index()
    yearly_fig = px.bar(yearly_df, x='year', y='amount',
                       title='Yearly Expense Breakdown',
                       labels={'amount': 'Amount ($)', 'year': 'Year'},
                       color='amount',
                       color_continuous_scale='tealrose')
    return daily_fig, monthly_fig, category_fig, yearly_fig

def main_app(username):
    st.set_page_config(layout="wide")
    st.title(f"📄 Bill OCR & Expense Tracker - Welcome {username}")
    if 'processed_bills' not in st.session_state:
        st.session_state.processed_bills = []
    st.sidebar.header(f"User: {username}")
    expenses = load_data(EXPENSES_FILE)
    user_expenses = [e for e in expenses if e.get('user') == username]
    total = sum(float(e.get('amount', 0)) for e in user_expenses)
    st.sidebar.metric("Your Total Expense", f"${total:.2f}")
    with st.sidebar.expander("➕ Add Manual Expense"):
        with st.form("manual_expense_form"):
            amount = st.number_input("Amount", min_value=0.0, step=0.01, key="manual_amount")
            category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Shopping", "Other"], key="manual_category")
            description = st.text_input("Description", key="manual_description")
            submitted = st.form_submit_button("Add Expense")
            if submitted:
                if amount > 0:
                    add_expense(amount, category, description, username)
                else:
                    st.error("Amount must be greater than 0")
    tab1, tab2, tab3, tab4 = st.tabs(["Upload Bill", "Your Expenses", "Analytics", "Restaurant Map"])
    with tab1:
        st.header("Upload Bill Image")
        uploaded_file = st.file_uploader("Choose a bill image", type=['png', 'jpg', 'jpeg'], key="bill_uploader")
        if uploaded_file is not None:
            image_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            if st.button("Process Bill", key="process_bill"):
                with st.spinner("Processing bill..."):
                    bill_entry = create_bill_entry(image_path, username)
                    st.session_state.processed_bills.append(bill_entry)
                st.success(f"Bill processed for {bill_entry['restaurant']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.image(image_path, caption="Uploaded Bill", use_column_container=True)
                with col2:
                    st.subheader("Extracted Information")
                    st.write(f"**Restaurant:** {bill_entry['restaurant']}")
                    if bill_entry['amount']:
                        st.write(f"**Amount:** ${bill_entry['amount']:.2f}")
                    else:
                        st.warning("Could not detect amount")
                    if bill_entry['location']['address']:
                        st.write(f"**Address:** {bill_entry['location']['address']}")
                    st.write("**Coordinates:**")
                    st.write(f"Decimal: {bill_entry['location']['latitude']:.4f}°, {bill_entry['location']['longitude']:.4f}°")
                    st.write(f"NMEA: {bill_entry['location']['lat_nmea']}, {bill_entry['location']['lon_nmea']}")
    with tab2:
        st.header("Your Expenses")
        if not user_expenses:
            st.info("No expenses recorded yet.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Expenses", f"${total:.2f}")
            with col2:
                avg_expense = total / len(user_expenses) if user_expenses else 0
                st.metric("Average Expense", f"${avg_expense:.2f}")
            with col3:
                latest_expense = max(user_expenses, key=lambda x: x['date'])
                st.metric("Latest Expense", f"${float(latest_expense['amount']):.2f}")
            st.subheader("Expense History")
            for expense in sorted(user_expenses, key=lambda x: x['date'], reverse=True):
                with st.expander(f"{expense['date']} - {expense['category']} (${float(expense['amount']):.2f})"):
                    st.write(f"**Description:** {expense.get('description', 'No description')}")
                    if 'restaurant' in expense:
                        st.write(f"**Restaurant:** {expense['restaurant']}")
    with tab3:
        st.header("Expense Analytics")
        if not user_expenses:
            st.info("No expenses recorded yet to show analytics.")
        else:
            expense_df = prepare_expense_data(user_expenses)
            if expense_df is not None:
                daily_fig, monthly_fig, category_fig, yearly_fig = create_expense_charts(expense_df)
                if daily_fig:
                    st.plotly_chart(daily_fig, use_container_width=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(monthly_fig, use_container_width=True)
                    with col2:
                        st.plotly_chart(category_fig, use_container_width=True)
                    st.plotly_chart(yearly_fig, use_container_width=True)
                else:
                    st.warning("Could not generate charts from the data")
            else:
                st.error("Failed to prepare data for analytics")
    with tab4:
        st.header("Restaurant Locations")
        bills = load_data(BILLS_FILE)
        user_bills = [b for b in bills if b.get('user') == username]
        if not any(b['location']['latitude'] is not None for b in user_bills):
            st.warning("No geolocation data available for your bills")
        else:
            m = create_map(bills, username)
            if m:
                st_folium(m, width=1200, height=600)
            else:
                st.warning("Could not create map")

def login_page():
    st.title("Bill OCR & Expense Tracker")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if authenticate(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_username) < 3:
                    st.error("Username must be at least 3 characters")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = register_user(new_username, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

initialize_files()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_app(st.session_state.username)
else:
    login_page()

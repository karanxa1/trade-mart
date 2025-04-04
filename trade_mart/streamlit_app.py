import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import base64
from io import BytesIO

# Database setup
def init_db():
    conn = sqlite3.connect('trade_mart.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  email TEXT UNIQUE, user_type TEXT, is_verified BOOLEAN, 
                  identity_verified BOOLEAN, is_suspended BOOLEAN)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY, name TEXT, description TEXT, 
                  price REAL, category_id INTEGER, condition_id INTEGER,
                  seller_id INTEGER, image TEXT, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY, name TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS conditions
                 (id INTEGER PRIMARY KEY, name TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY, buyer_id INTEGER, product_id INTEGER,
                  quantity INTEGER, total_price REAL, status TEXT,
                  created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS offers
                 (id INTEGER PRIMARY KEY, buyer_id INTEGER, product_id INTEGER,
                  amount REAL, status TEXT, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, sender_id INTEGER, receiver_id INTEGER,
                  content TEXT, read BOOLEAN, created_at TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS verification_activities
                 (id INTEGER PRIMARY KEY, seller_id INTEGER, govt_employee_id INTEGER,
                  status TEXT, reason TEXT, created_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('trade_mart.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_user(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                       (username, password)).fetchone()
    conn.close()
    return user

def register_user(username, password, email, user_type):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password, email, user_type, is_verified) VALUES (?, ?, ?, ?, ?)',
                    (username, password, email, user_type, False))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Main app
def main():
    st.set_page_config(
        page_title="Trade Mart",
        page_icon="🛍️",
        layout="wide"
    )
    
    # Initialize database
    init_db()
    
    # Sidebar for navigation
    st.sidebar.title("Trade Mart")
    
    if st.session_state.user_id is None:
        st.sidebar.subheader("Login/Register")
        login_choice = st.sidebar.radio("Choose", ["Login", "Register"])
        
        if login_choice == "Login":
            with st.sidebar.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    user = login_user(username, password)
                    if user:
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.user_type = user['user_type']
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        else:
            with st.sidebar.form("register_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                email = st.text_input("Email")
                user_type = st.selectbox("User Type", ["buyer", "seller", "govt_employee"])
                submit = st.form_submit_button("Register")
                
                if submit:
                    if register_user(username, password, email, user_type):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username or email already exists")
    
    else:
        st.sidebar.write(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.user_type = None
            st.rerun()
        
        # Navigation based on user type
        if st.session_state.user_type == "buyer":
            st.sidebar.subheader("Buyer Options")
            if st.sidebar.button("Browse Products"):
                st.session_state.page = "products"
            if st.sidebar.button("My Orders"):
                st.session_state.page = "orders"
            if st.sidebar.button("My Offers"):
                st.session_state.page = "offers"
            if st.sidebar.button("Messages"):
                st.session_state.page = "messages"
        
        elif st.session_state.user_type == "seller":
            st.sidebar.subheader("Seller Options")
            if st.sidebar.button("My Products"):
                st.session_state.page = "seller_products"
            if st.sidebar.button("Orders"):
                st.session_state.page = "seller_orders"
            if st.sidebar.button("Offers"):
                st.session_state.page = "seller_offers"
            if st.sidebar.button("Messages"):
                st.session_state.page = "messages"
            if st.sidebar.button("Identity Verification"):
                st.session_state.page = "identity_verification"
        
        elif st.session_state.user_type == "govt_employee":
            st.sidebar.subheader("Government Portal")
            if st.sidebar.button("Verify Sellers"):
                st.session_state.page = "verify_sellers"
            if st.sidebar.button("Manage Sellers"):
                st.session_state.page = "manage_sellers"
    
    # Main content area
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    if st.session_state.page == "home":
        st.title("Welcome to Trade Mart")
        st.write("A Government-Approved Marketplace for Safe Buying & Selling")
        
        # Display featured products
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products ORDER BY created_at DESC LIMIT 6').fetchall()
        conn.close()
        
        if products:
            st.subheader("Featured Products")
            cols = st.columns(3)
            for i, product in enumerate(products):
                with cols[i % 3]:
                    st.image(product['image'], use_column_width=True)
                    st.write(f"**{product['name']}**")
                    st.write(f"Price: ₹{product['price']}")
                    if st.button(f"View Details", key=f"view_{product['id']}"):
                        st.session_state.page = "product_detail"
                        st.session_state.product_id = product['id']
                        st.rerun()
    
    # Footer section
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    with footer_col1:
        st.write("")
    with footer_col2:
        st.markdown("<div style='text-align: center;'><p>© 2023 Trade Mart | Developed by Karan</p><p>Contact: abc@abc.com | Phone: 9999999999</p></div>", unsafe_allow_html=True)
    with footer_col3:
        st.write("")

if __name__ == "__main__":
    main()
# Trade Mart - Streamlit Version

A Government-Approved Marketplace for Safe Buying & Selling

## Features

- User Authentication (Buyers, Sellers, Government Employees)
- Product Management
- Order Processing
- Offer System
- Messaging System
- Identity Verification
- Government Portal for Seller Management

## Setup for Streamlit Cloud

1. Fork this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your forked repository
6. Set the main file path as `streamlit_app.py`
7. Click "Deploy"

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Environment Variables

Create a `.streamlit/secrets.toml` file with:
```toml
[general]
debug = false
```

## Database

The application uses SQLite for data storage. The database file (`trade_mart.db`) will be automatically created when you first run the application.

## Contact

Phone: +91 7276640676
Email: support@trademart.com 
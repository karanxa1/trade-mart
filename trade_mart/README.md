# Trade Mart E-commerce Platform

A Flask-based e-commerce web application with features similar to modern online shopping platforms.

## Features

- Responsive design with modern UI
- User authentication (register/login)
- Product browsing by categories
- Product detail pages
- Shopping cart functionality
- Checkout process
- Order confirmation
- Admin capabilities

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/trade_mart.git
cd trade_mart
```

2. Create a virtual environment and activate it:
```
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the application:
```
python app.py
```

5. Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

## Database

The application uses SQLite for development purposes. The database will be automatically created with sample data when you run the application for the first time.

## Project Structure

```
trade_mart/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
├── app.py
├── requirements.txt
└── README.md
```

## License

MIT

## Credits

Developed by [Your Name] 
from trade_mart.app import app, db, User, Category, Condition, BusinessVerification, VerificationActivity, SuspensionActivity, Product, Order, OrderItem, Offer, Message
from datetime import datetime
import os

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all tables")
        
        # Create all tables
        db.create_all()
        print("Created all tables with updated schema")
        
        # Add initial categories
        categories = [
            Category(name='Electronics'),
            Category(name='Fashion'),
            Category(name='Home & Living'),
            Category(name='Books'),
            Category(name='Sports'),
            Category(name='Toys'),
            Category(name='Beauty'),
            Category(name='Other')
        ]
        db.session.add_all(categories)
        
        # Add initial conditions
        conditions = [
            Condition(name='New'),
            Condition(name='Like New'),
            Condition(name='Good'),
            Condition(name='Fair'),
            Condition(name='Poor')
        ]
        db.session.add_all(conditions)
        
        # Commit all changes
        db.session.commit()
        print("Initial categories and conditions added successfully")

if __name__ == '__main__':
    init_db() 
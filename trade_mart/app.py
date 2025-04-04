from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import random
import string
from werkzeug.utils import secure_filename
import time
from sqlalchemy import func
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'trademartkey123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///trademart.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Currency used throughout the application is Indian Rupees (₹)
db = SQLAlchemy(app)

# Register format_date filter
@app.template_filter('format_date')
def format_date_filter(date):
    if not date:
        return ''
        
    # Convert string date to datetime object if needed
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            # If format doesn't match, just return the string
            return date
            
    delta = datetime.now() - date
    if delta.days == 0:
        if delta.seconds < 60:
            return 'Just now'
        elif delta.seconds < 3600:
            return f'{delta.seconds // 60} minutes ago'
        else:
            return f'{delta.seconds // 3600} hours ago'
    elif delta.days == 1:
        return 'Yesterday'
    elif delta.days < 7:
        return f'{delta.days} days ago'
    else:
        return date.strftime('%b %d, %Y')

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    user_type = db.Column(db.String(20), nullable=False)  # 'buyer', 'seller', or 'govt_employee'
    created_at = db.Column(db.String(50), default=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Verification fields
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    verification_code_expires = db.Column(db.DateTime, nullable=True)
    identity_verified = db.Column(db.Boolean, default=False)
    id_document = db.Column(db.String(200), nullable=True)
    selfie_document = db.Column(db.String(200), nullable=True)
    
    # Business verification fields
    business_verification = db.relationship('BusinessVerification', backref='user', lazy=True, uselist=False, foreign_keys='BusinessVerification.user_id')
    
    # Seller ratings
    avg_rating = db.Column(db.Float, default=0.0)
    total_ratings = db.Column(db.Integer, default=0)
    
    # Suspension fields
    is_suspended = db.Column(db.Boolean, default=False)
    suspend_reason = db.Column(db.Text, nullable=True)
    suspended_at = db.Column(db.DateTime, nullable=True)
    suspended_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    products = db.relationship('Product', backref='seller', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    carts = db.relationship('Cart', backref='user', lazy=True)
    
    # Define simple foreign key relationships with Offer model without backrefs
    offers_as_buyer = db.relationship('Offer', 
                               foreign_keys='Offer.buyer_id',
                               backref=db.backref('buyer_user', lazy=True),
                               lazy=True)
    
    offers_as_seller = db.relationship('Offer', 
                               foreign_keys='Offer.seller_id',
                               backref=db.backref('seller_user', lazy=True),
                               lazy=True)
    
    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'user_type': self.user_type,
            'is_verified': self.is_verified,
            'identity_verified': self.identity_verified,
            'avg_rating': self.avg_rating,
            'total_ratings': self.total_ratings,
            'is_suspended': self.is_suspended,
            'created_at': self.created_at
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', backref='condition', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    negotiable = db.Column(db.Boolean, default=True)
    condition_id = db.Column(db.Integer, db.ForeignKey('condition.id'), nullable=False)
    image = db.Column(db.String(100), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='available')  # available, sold, reserved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    offers = db.relationship('Offer', backref='product', lazy=True)
    
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    tracking_status = db.Column(db.String(50), default='order_placed')  # order_placed, processing, shipped, out_for_delivery, delivered
    tracking_id = db.Column(db.String(20), default=lambda: f"TM{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}")
    tracking_updates = db.Column(db.JSON, default=lambda: [{"status": "order_placed", "timestamp": datetime.utcnow().isoformat(), "description": "Order has been placed successfully"}])
    estimated_delivery = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=5))
    delivery_address = db.Column(db.Text, nullable=False)
    payment_method = db.Column(db.String(20), default='cash_on_delivery')
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship('Product')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    offer_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships are handled by backref in the User model

class BusinessVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    business_type = db.Column(db.String(50), nullable=False)
    registration_number = db.Column(db.String(50), nullable=False)
    business_address = db.Column(db.String(200), nullable=False)
    business_document = db.Column(db.String(200), nullable=False)  # Path to business registration document
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    reject_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class VerificationActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    verification_id = db.Column(db.Integer, db.ForeignKey('business_verification.id'), nullable=False)
    govt_employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # approved, rejected
    reason = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add relationships
    verification = db.relationship('BusinessVerification', backref='activities')
    govt_employee = db.relationship('User', backref='verification_activities')
    
    def as_dict(self):
        return {
            'id': self.id,
            'verification_id': self.verification_id,
            'govt_employee': self.govt_employee.username,
            'action': self.action,
            'reason': self.reason,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

class SuspensionActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    govt_employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # suspended, unsuspended
    reason = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Context processors for templates
@app.context_processor
def utility_processor():
    def get_categories():
        return Category.query.all()
    
    def get_category_name(category_id):
        category = Category.query.get(category_id)
        return category.name if category else ''
    
    def get_condition_name(condition_id):
        condition = Condition.query.get(condition_id)
        return condition.name if condition else ''
    
    def get_cart_count():
        if 'user_id' in session:
            return Cart.query.filter_by(user_id=session['user_id']).count()
        return 0
    
    def get_cart_total():
        if 'user_id' not in session:
            return 0.0
        cart_items = db.session.query(Cart, Product).join(
            Product, Cart.product_id == Product.id
        ).filter(Cart.user_id == session['user_id']).all()
        return sum(cart.quantity * product.price for cart, product in cart_items)
    
    def get_unread_messages_count(partner_id=None):
        if 'user_id' not in session:
            return 0
        
        query = Message.query.filter_by(receiver_id=session['user_id'], read=False)
        
        if partner_id:
            query = query.filter_by(sender_id=partner_id)
            
        return query.count()
    
    def get_user_type():
        return session.get('user_type', None)
    
    def get_category_icon(category_name):
        icons = {
            'Electronics': 'laptop',
            'Books': 'book',
            'Furniture': 'couch',
            'Tools': 'tools',
            'Vehicles': 'car',
            'Toys': 'gamepad',
            'Clothing': 'tshirt',
            'Home & Garden': 'home'
        }
        return icons.get(category_name, 'tag')
    
    def get_current_user():
        if 'user_id' in session:
            return User.query.get(session['user_id'])
        return None
    
    def get_pending_offers():
        if 'user_id' not in session or session.get('user_type') != 'seller':
            return 0
        return Offer.query.join(Product).filter(
            Product.seller_id == session['user_id'],
            Offer.status == 'pending'
        ).count()
    
    return dict(
        get_categories=get_categories,
        get_category_name=get_category_name,
        get_condition_name=get_condition_name,
        get_cart_count=get_cart_count,
        get_cart_total=get_cart_total,
        get_unread_messages_count=get_unread_messages_count,
        get_user_type=get_user_type,
        get_category_icon=get_category_icon,
        current_user=get_current_user(),
        pending_offers=get_pending_offers()
    )

@app.route('/')
def index():
    # Get featured products (newest 8 products)
    featured_products = Product.query.filter_by(
        status='available'
    ).order_by(Product.created_at.desc()).limit(8).all()
    
    categories = Category.query.all()
    
    return render_template('index.html', featured_products=featured_products, categories=categories)

@app.route('/products')
def products():
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float, default=0)
    max_price = request.args.get('max_price', type=float)
    condition_id = request.args.get('condition', type=int)
    seller_id = request.args.get('seller', type=int)
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'newest')  # Default sort by newest
    
    # Start with a base query
    query = Product.query.filter_by(status='available')
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if condition_id:
        query = query.filter_by(condition_id=condition_id)
    
    if seller_id:
        query = query.filter_by(seller_id=seller_id)
        
    # Only show listings from verified sellers by default, unless specifically searching for a seller
    if not seller_id:
        # Join with User model to filter by verification
        query = query.join(User, Product.seller_id == User.id).filter(User.is_verified == True)
    
    if search_query:
        search_terms = '%' + search_query + '%'
        query = query.filter(
            db.or_(
                Product.name.ilike(search_terms),
                Product.description.ilike(search_terms)
            )
        )
    
    # Apply sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    # Get all categories and conditions for the filter sidebar
    categories = Category.query.all()
    conditions = Condition.query.all()
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of products per page
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    
    return render_template(
        'products.html',
        products=products,
        pagination=pagination,
        categories=categories,
        conditions=conditions,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        condition_id=condition_id,
        seller_id=seller_id,
        search_query=search_query,
        sort_by=sort_by
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    seller = User.query.get(product.seller_id)
    condition = Condition.query.get(product.condition_id)
    
    # Get similar products (from same category)
    similar_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.status == 'available'
    ).limit(4).all()
    
    # Count reviews for seller
    review_count = Review.query.filter_by(seller_id=seller.id).count()
    
    # Get average rating for seller
    avg_rating = 0
    if review_count > 0:
        avg_rating = db.session.query(db.func.avg(Review.rating)).filter(
            Review.seller_id == seller.id
        ).scalar() or 0
    
    return render_template('product_detail.html', 
                          product=product, 
                          seller=seller,
                          condition=condition,
                          similar_products=similar_products,
                          review_count=review_count,
                          avg_rating=avg_rating)

@app.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id, status='available').all()
    return render_template('category.html', category=category, products=products)

# Buyer Routes
@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please login to view your cart', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'buyer':
        flash('Only buyers can access cart features', 'warning')
        return redirect(url_for('index'))
    
    # Get cart items
    cart_items = db.session.query(Cart, Product, Condition).join(
        Product, Cart.product_id == Product.id
    ).join(
        Condition, Product.condition_id == Condition.id
    ).filter(
        Cart.user_id == session['user_id']
    ).all()
    
    # Calculate total
    total = sum(cart.quantity * product.price for cart, product, _ in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Please login to add items to your cart', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'buyer':
        flash('Only buyers can add items to cart', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
    
    product = Product.query.get_or_404(product_id)
    
    if product.status != 'available':
        flash('This product is no longer available', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
    
    if product.seller_id == session['user_id']:
        flash('You cannot buy your own product', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
        
    quantity = int(request.form.get('quantity', 1))
    
    cart_item = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=session['user_id'], product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Item added to cart successfully!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:cart_id>')
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        flash('Please login to manage your cart', 'warning')
        return redirect(url_for('login'))
    
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != session['user_id']:
        flash('Access denied', 'danger')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    if 'user_id' not in session:
        flash('Please login to manage your cart', 'warning')
        return redirect(url_for('login'))
    
    # Get all cart items for the user
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    
    # Update quantities
    for item in cart_items:
        new_quantity = request.form.get(f'quantity_{item.id}', type=int)
        if new_quantity and new_quantity > 0:
            item.quantity = new_quantity
    
    db.session.commit()
    flash('Cart updated successfully', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please login to checkout', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'buyer':
        flash('Only buyers can checkout', 'warning')
        return redirect(url_for('index'))
    
    # Get cart items
    cart_items = db.session.query(Cart, Product, Condition).join(
        Product, Cart.product_id == Product.id
    ).join(
        Condition, Product.condition_id == Condition.id
    ).filter(
        Cart.user_id == session['user_id']
    ).all()
    
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart'))
    
    # Calculate total
    total = sum(cart.quantity * product.price for cart, product, _ in cart_items)
    
    if request.method == 'POST':
        # Collect all the address information from the form
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        address = request.form.get('address')
        address2 = request.form.get('address2', '')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip')
        
        # Combine the address components
        delivery_address = f"{first_name} {last_name}, {address}"
        if address2:
            delivery_address += f", {address2}"
        delivery_address += f", {city}, {state} {zip_code}"
        
        payment_method = request.form.get('payment_method')
        
        if not address or not city or not state or not zip_code:
            flash('Please provide a complete delivery address', 'warning')
            return render_template('checkout.html', cart_items=cart_items, total=total)
        
        # Create a new order
        new_order = Order(
            user_id=session['user_id'],
            total_amount=total,
            delivery_address=delivery_address,
            payment_method=payment_method,
            status='pending'
        )
        db.session.add(new_order)
        db.session.flush()  # Get the order ID without committing
        
        # Add order items
        for cart, product, _ in cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=cart.quantity,
                price=product.price
            )
            db.session.add(order_item)
            
            # Update product status
            product.status = 'reserved'
        
        # Clear the cart
        for cart, _, _ in cart_items:
            db.session.delete(cart)
        
        db.session.commit()
        
        # For cash on delivery, immediately redirect to confirmation
        if payment_method == 'cash_on_delivery':
            flash('Your order has been placed successfully! You will pay upon delivery.', 'success')
            return redirect(url_for('order_confirmation', order_id=new_order.id))
        
        # For other payment methods, redirect to payment processing (placeholder)
        flash('Your order has been placed! Please complete the payment.', 'info')
        return redirect(url_for('order_confirmation', order_id=new_order.id))
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'user_id' not in session:
        flash('Please login to view order details', 'warning')
        return redirect(url_for('login'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != session['user_id']:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    return render_template('order_confirmation.html', order=order)

@app.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        flash('Please login to view your orders', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'buyer':
        flash('Only buyers can view orders', 'warning')
        return redirect(url_for('index'))
    
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.order_date.desc()).all()
    return render_template('my_orders.html', orders=orders)

@app.route('/make_offer/<int:product_id>', methods=['POST'])
def make_offer(product_id):
    if 'user_id' not in session:
        flash('Please login to make an offer', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'buyer':
        flash('Only buyers can make offers', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
    
    product = Product.query.get_or_404(product_id)
    
    if product.status != 'available':
        flash('This product is no longer available for offers', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
    
    if product.seller_id == session['user_id']:
        flash('You cannot make an offer on your own product', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
    
    if not product.negotiable:
        flash('This product does not accept offers', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
        
    offer_price = float(request.form.get('offer_price', 0))
    
    if offer_price <= 0:
        flash('Please enter a valid offer amount', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
    
    if offer_price >= product.price:
        flash('Your offer must be lower than the listing price', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))
    
    # Check if user already has a pending offer for this product
    existing_offer = Offer.query.filter_by(
        product_id=product_id,
        buyer_id=session['user_id'],
        status='pending'
    ).first()
    
    if existing_offer:
        existing_offer.offer_price = offer_price
        existing_offer.created_at = datetime.utcnow()
        db.session.commit()
        flash('Your existing offer has been updated!', 'success')
    else:
        new_offer = Offer(
            product_id=product_id,
            buyer_id=session['user_id'],
            seller_id=product.seller_id,
            offer_price=offer_price
        )
        db.session.add(new_offer)
        db.session.commit()
        flash('Your offer has been sent to the seller!', 'success')
    
    return redirect(url_for('product_detail', product_id=product_id))

@app.route('/my_offers')
def my_offers():
    if 'user_id' not in session:
        flash('Please login to view your offers', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'buyer':
        flash('Access denied. Buyers only.', 'danger')
        return redirect(url_for('index'))
    
    # Get all offers made by this buyer
    offers = db.session.query(Offer, Product, User).join(
        Product, Offer.product_id == Product.id
    ).join(
        User, Product.seller_id == User.id
    ).filter(
        Offer.buyer_id == session['user_id']
    ).order_by(Offer.created_at.desc()).all()
    
    return render_template('my_offers.html', offers=offers)

@app.route('/messages')
def messages():
    if 'user_id' not in session:
        flash('Please login to view your messages', 'warning')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Get unique conversations
    received_msg_partners = db.session.query(Message.sender_id, User.username).join(User, User.id == Message.sender_id).filter(Message.receiver_id == user_id).group_by(Message.sender_id).all()
    
    sent_msg_partners = db.session.query(Message.receiver_id, User.username).join(User, User.id == Message.receiver_id).filter(Message.sender_id == user_id).group_by(Message.receiver_id).all()
    
    # Combine and remove duplicates
    conversation_partners = {}
    for partner_id, username in received_msg_partners:
        conversation_partners[partner_id] = username
    
    for partner_id, username in sent_msg_partners:
        conversation_partners[partner_id] = username
    
    # Mark messages as read if viewing specific conversation
    partner_id = request.args.get('partner_id', type=int)
    if partner_id:
        unread_messages = Message.query.filter_by(
            sender_id=partner_id,
            receiver_id=user_id,
            read=False
        ).all()
        
        for message in unread_messages:
            message.read = True
        
        db.session.commit()
        
        # Get conversation with this partner
        conversation = Message.query.filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == partner_id)) |
            ((Message.sender_id == partner_id) & (Message.receiver_id == user_id))
        ).order_by(Message.created_at.asc()).all()
        
        partner = User.query.get(partner_id)
        
        return render_template(
            'messages.html', 
            conversation_partners=conversation_partners,
            active_partner=partner,
            conversation=conversation
        )
    
    return render_template(
        'messages.html', 
        conversation_partners=conversation_partners,
        active_partner=None,
        conversation=None
    )

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        flash('Please login to send messages', 'warning')
        return redirect(url_for('login'))
    
    receiver_id = request.form.get('receiver_id', type=int)
    content = request.form.get('content')
    product_id = request.form.get('product_id', type=int)
    
    if not receiver_id or not content:
        flash('Invalid message data', 'danger')
        return redirect(url_for('messages'))
    
    new_message = Message(
        sender_id=session['user_id'],
        receiver_id=receiver_id,
        content=content,
        product_id=product_id
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    if request.form.get('from_product'):
        flash('Message sent to seller!', 'success')
        return redirect(url_for('product_detail', product_id=product_id))
    
    return redirect(url_for('messages', partner_id=receiver_id))

@app.route('/add_review/<int:seller_id>', methods=['POST'])
def add_review(seller_id):
    if 'user_id' not in session:
        flash('Please login to leave a review', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'buyer':
        flash('Only buyers can leave reviews', 'warning')
        return redirect(url_for('index'))
    
    # Check if the buyer has purchased from this seller
    has_purchased = OrderItem.query.join(Order).join(Product).filter(
        Order.user_id == session['user_id'],
        Product.seller_id == seller_id,
        Order.status == 'completed'
    ).first()
    
    if not has_purchased:
        flash('You can only review sellers you have purchased from', 'warning')
        return redirect(url_for('index'))
    
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '')
    
    if rating < 1 or rating > 5:
        flash('Rating must be between 1 and 5', 'warning')
        return redirect(request.referrer or url_for('index'))
    
    # Check if review already exists
    existing_review = Review.query.filter_by(
        reviewer_id=session['user_id'],
        seller_id=seller_id
    ).first()
    
    if existing_review:
        existing_review.rating = rating
        existing_review.comment = comment
        existing_review.created_at = datetime.utcnow()
    else:
        new_review = Review(
            reviewer_id=session['user_id'],
            seller_id=seller_id,
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
    
    db.session.commit()
    flash('Your review has been submitted!', 'success')
    return redirect(request.referrer or url_for('index'))

# Seller Routes
@app.route('/seller/dashboard')
def seller_dashboard():
    if 'user_id' not in session:
        flash('Please login to access seller dashboard', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can access this dashboard', 'warning')
        return redirect(url_for('index'))
    
    # Get seller statistics
    user_id = session['user_id']
    
    # Products statistics
    total_products = Product.query.filter_by(seller_id=user_id).count()
    available_products = Product.query.filter_by(seller_id=user_id, status='available').count()
    sold_products = Product.query.filter_by(seller_id=user_id, status='sold').count()
    
    # Order statistics
    orders = db.session.query(Order).join(OrderItem).join(Product).filter(
        Product.seller_id == user_id
    ).distinct().all()
    
    # Count pending orders (products with 'reserved' status that need approval)
    pending_orders = Product.query.filter_by(seller_id=user_id, status='reserved').count()
    
    # Revenue calculation
    total_revenue = db.session.query(db.func.sum(OrderItem.price * OrderItem.quantity)).join(Product).filter(
        Product.seller_id == user_id,
        Product.status == 'sold'
    ).scalar() or 0
    
    # Pending offers
    pending_offers = Offer.query.join(Product).filter(
        Product.seller_id == user_id,
        Offer.status == 'pending'
    ).count()
    
    # Recent messages
    recent_messages = Message.query.filter_by(
        receiver_id=user_id,
        read=False
    ).count()
    
    # Recent products
    recent_products = Product.query.filter_by(
        seller_id=user_id
    ).order_by(Product.created_at.desc()).limit(5).all()
    
    # Reviews
    reviews = Review.query.filter_by(seller_id=user_id).order_by(Review.created_at.desc()).limit(5).all()
    
    avg_rating = 0
    review_count = 0
    if reviews:
        all_reviews = Review.query.filter_by(seller_id=user_id).all()
        review_count = len(all_reviews)
        avg_rating = sum(review.rating for review in all_reviews) / review_count if review_count > 0 else 0
    
    return render_template(
        'seller/dashboard.html',
        total_products=total_products,
        available_products=available_products,
        sold_products=sold_products,
        orders=orders,
        total_revenue=total_revenue,
        pending_offers=pending_offers,
        pending_orders=pending_orders,
        recent_messages=recent_messages,
        recent_products=recent_products,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=review_count
    )

@app.route('/seller/products')
def seller_products():
    if 'user_id' not in session:
        flash('Please login to view your products', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can access this page', 'warning')
        return redirect(url_for('index'))
    
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    status = request.args.get('status')
    sort = request.args.get('sort', 'newest')
    
    # Build query
    query = Product.query.filter_by(seller_id=session['user_id'])
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Apply sorting
    if sort == 'oldest':
        query = query.order_by(Product.created_at.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'price_low':
        query = query.order_by(Product.price.asc())
    else:  # newest first (default)
        query = query.order_by(Product.created_at.desc())
    
    # Execute query
    products = query.all()
    
    # Add extra data for display
    for product in products:
        # Count offers for this product - use a different attribute name to avoid conflict
        product.offer_count = Offer.query.filter_by(product_id=product.id).count()
        
        # Count messages related to this product
        product.message_count = Message.query.filter_by(product_id=product.id).count()
        
        # In a real app, you would track views in a separate table
        product.view_count = 0  # Placeholder
    
    # Get all categories for the filter dropdown
    categories = Category.query.all()
    
    return render_template('seller/products.html', products=products, categories=categories)

@app.route('/seller/add_product', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        flash('Please login to add a product', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can add products', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        condition_id = request.form.get('condition_id')
        negotiable = True if request.form.get('negotiable') == 'on' else False
        
        # Validate required fields
        if not all([name, description, price, category_id, condition_id]):
            flash('All fields are required except image', 'danger')
            categories = Category.query.all()
            conditions = Condition.query.all()
            return render_template('seller/add_product.html', categories=categories, conditions=conditions)
        
        try:
            price = float(price)
            if price <= 0:
                raise ValueError("Price must be positive")
            
            # Handle image upload
            image_filename = 'default-product.jpg'  # Default image
            if 'image_file' in request.files and request.files['image_file'].filename:
                image_file = request.files['image_file']
                # Ensure the filename is secure
                filename = secure_filename(image_file.filename)
                # Create a unique filename by adding timestamp
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                
                # Save the file to the products directory
                file_path = os.path.join(app.root_path, 'static', 'images', 'products', image_filename)
                # Ensure the directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                image_file.save(file_path)
                
            # Create new product
            new_product = Product(
                name=name,
                description=description,
                price=price,
                category_id=int(category_id),
                condition_id=int(condition_id),
                image=image_filename,
                seller_id=session['user_id'],
                negotiable=negotiable,
                status='available'
            )
            
            db.session.add(new_product)
            db.session.commit()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('seller_products'))
            
        except ValueError as e:
            flash(f'Invalid price: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')
    
    # GET request - show form
    categories = Category.query.all()
    conditions = Condition.query.all()
    return render_template('seller/add_product.html', categories=categories, conditions=conditions)

@app.route('/seller/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'user_id' not in session:
        flash('Please login to edit a product', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can edit products', 'warning')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != session['user_id']:
        flash('You do not have permission to edit this product', 'danger')
        return redirect(url_for('seller_products'))
    
    if product.status != 'available':
        flash('You cannot edit a product that is not available', 'warning')
        return redirect(url_for('seller_products'))
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', 0))
        product.category_id = int(request.form.get('category_id', 0))
        product.condition_id = int(request.form.get('condition_id', 0))
        product.negotiable = True if request.form.get('negotiable') == 'on' else False
        
        # Handle image upload
        if 'image_file' in request.files and request.files['image_file'].filename:
            image_file = request.files['image_file']
            # Ensure the filename is secure
            filename = secure_filename(image_file.filename)
            # Create a unique filename by adding timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            image_filename = f"{timestamp}_{filename}"
            
            # Save the file to the products directory
            file_path = os.path.join(app.root_path, 'static', 'images', 'products', image_filename)
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            image_file.save(file_path)
            
            # Update the product image
            product.image = image_filename
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('seller_products'))
    
    categories = Category.query.all()
    conditions = Condition.query.all()
    return render_template('seller/edit_product.html', product=product, categories=categories, conditions=conditions)

@app.route('/seller/delete_product/<int:product_id>')
def delete_product(product_id):
    if 'user_id' not in session:
        flash('Please login to delete a product', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can delete products', 'warning')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != session['user_id']:
        flash('You do not have permission to delete this product', 'danger')
        return redirect(url_for('seller_products'))
    
    if product.status != 'available':
        flash('You cannot delete a product that is reserved or sold', 'warning')
        return redirect(url_for('seller_products'))
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('seller_products'))

@app.route('/seller/orders')
def seller_orders():
    if 'user_id' not in session:
        flash('Please login to view orders', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can view these orders', 'warning')
        return redirect(url_for('index'))
    
    # Find all orders containing products sold by this seller
    orders = db.session.query(Order, OrderItem, Product).join(
        OrderItem, Order.id == OrderItem.order_id
    ).join(
        Product, OrderItem.product_id == Product.id
    ).filter(
        Product.seller_id == session['user_id']
    ).order_by(Order.order_date.desc()).all()
    
    # Group by order
    grouped_orders = {}
    for order, item, product in orders:
        if order.id not in grouped_orders:
            grouped_orders[order.id] = {
                'order': order,
                'items': [],
                'buyer': User.query.get(order.user_id)
            }
        grouped_orders[order.id]['items'].append((item, product))
    
    return render_template('seller/orders.html', orders=grouped_orders)

@app.route('/seller/update_order_status/<int:order_id>/<int:product_id>', methods=['POST'])
def update_order_status(order_id, product_id):
    if 'user_id' not in session:
        flash('Please login to update order status', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can update order status', 'warning')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(product_id)
    
    if product.seller_id != session['user_id']:
        flash('You do not have permission to update this order status', 'danger')
        return redirect(url_for('seller_orders'))
    
    status = request.form.get('status')
    if status not in ['pending', 'completed', 'cancelled']:
        flash('Invalid status value', 'danger')
        return redirect(url_for('seller_orders'))
    
    # Update the product status
    if status == 'completed':
        product.status = 'sold'
    elif status == 'cancelled':
        product.status = 'available'
    
    # Get the order item
    order_item = OrderItem.query.filter_by(order_id=order_id, product_id=product_id).first()
    
    # Check if all items in order are in the same status
    order = Order.query.get(order_id)
    items = OrderItem.query.filter_by(order_id=order_id).all()
    
    # Count completed and cancelled items
    completed_count = sum(1 for i in items if Product.query.get(i.product_id).status == 'sold')
    cancelled_count = sum(1 for i in items if Product.query.get(i.product_id).status == 'available')
    
    # Update order status if all items have the same status
    if completed_count == len(items):
        order.status = 'completed'
        # Update tracking information
        order.tracking_status = 'shipped'
        
        # Add tracking update
        tracking_updates = order.tracking_updates.copy() if order.tracking_updates else []
        tracking_updates.append({
            "status": "shipped",
            "timestamp": datetime.utcnow().isoformat(),
            "description": "Your order has been shipped and is on the way!"
        })
        order.tracking_updates = tracking_updates
        
    elif cancelled_count == len(items):
        order.status = 'cancelled'
        # Update tracking information
        order.tracking_status = 'cancelled'
        
        # Add tracking update
        tracking_updates = order.tracking_updates.copy() if order.tracking_updates else []
        tracking_updates.append({
            "status": "cancelled",
            "timestamp": datetime.utcnow().isoformat(),
            "description": "Your order has been cancelled."
        })
        order.tracking_updates = tracking_updates
    
    db.session.commit()
    flash('Order status updated successfully!', 'success')
    return redirect(url_for('seller_orders'))

@app.route('/seller/offers')
def seller_offers():
    if 'user_id' not in session:
        flash('Please login to view offers', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Access denied. Sellers only.', 'danger')
        return redirect(url_for('index'))
    
    # Get all offers for the seller's products
    offers = db.session.query(Offer, Product, User).join(
        Product, Offer.product_id == Product.id
    ).join(
        User, Offer.buyer_id == User.id
    ).filter(
        Product.seller_id == session['user_id']
    ).all()
    
    # Group offers by status
    pending_offers = [o for o, p, u in offers if o.status == 'pending']
    accepted_offers = [o for o, p, u in offers if o.status == 'accepted']
    rejected_offers = [o for o, p, u in offers if o.status == 'rejected']
    
    return render_template(
        'seller/offers.html',
        offers=offers,
        pending_offers=pending_offers,
        accepted_offers=accepted_offers,
        rejected_offers=rejected_offers
    )

@app.route('/seller/respond_to_offer/<int:offer_id>', methods=['POST'])
def respond_to_offer(offer_id):
    if 'user_id' not in session:
        flash('Please login to respond to offers', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Access denied. Sellers only.', 'danger')
        return redirect(url_for('index'))
    
    offer = Offer.query.get_or_404(offer_id)
    product = Product.query.get(offer.product_id)
    
    # Verify the product belongs to this seller
    if product.seller_id != session['user_id']:
        flash('You do not have permission to respond to this offer', 'danger')
        return redirect(url_for('seller_offers'))
    
    response = request.form.get('response')
    
    if response not in ['accept', 'reject']:
        flash('Invalid response option', 'danger')
        return redirect(url_for('seller_offers'))
    
    if offer.status != 'pending':
        flash('This offer has already been processed', 'warning')
        return redirect(url_for('seller_offers'))
    
    if response == 'accept':
        offer.status = 'accepted'
        
        # Mark other offers for this product as rejected
        other_offers = Offer.query.filter(
            Offer.product_id == offer.product_id,
            Offer.id != offer.id,
            Offer.status == 'pending'
        ).all()
        
        for other_offer in other_offers:
            other_offer.status = 'rejected'
        
        # Update product price to the accepted offer (optional)
        product.price = offer.offer_price
        flash('Offer accepted! The buyer has been notified.', 'success')
    else:
        offer.status = 'rejected'
        flash('Offer rejected! The buyer has been notified.', 'success')
    
    db.session.commit()
    return redirect(url_for('seller_offers'))

@app.route('/seller/reviews')
def seller_reviews():
    if 'user_id' not in session:
        flash('Please login to view reviews', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can view their reviews', 'warning')
        return redirect(url_for('index'))
    
    reviews = db.session.query(Review, User).join(
        User, Review.reviewer_id == User.id
    ).filter(
        Review.seller_id == session['user_id']
    ).order_by(Review.created_at.desc()).all()
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = sum(review.rating for review, _ in reviews) / len(reviews)
    
    # Group ratings by number of stars
    rating_counts = {i: 0 for i in range(1, 6)}
    for review, _ in reviews:
        rating_counts[review.rating] += 1
    
    return render_template(
        'seller/reviews.html', 
        reviews=reviews, 
        avg_rating=avg_rating, 
        rating_counts=rating_counts,
        review_count=len(reviews)
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type
            
            # Check if user needs verification
            if not user.is_verified:
                flash('Please verify your email address to access all features.', 'warning')
                return redirect(url_for('verify_account'))
            
            # Special warning for sellers without identity verification
            if user.user_type == 'seller' and not user.identity_verified:
                flash('Complete identity verification to increase trust in your listings.', 'warning')
                
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        address = request.form['address']
        user_type = request.form['user_type']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists. Please use a different email or login.', 'danger')
        else:
            new_user = User(
                username=username,
                email=email,
                password=password,
                phone=phone,
                address=address,
                user_type=user_type
            )
            
            # Generate verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            new_user.verification_code = verification_code
            new_user.verification_code_expires = datetime.utcnow() + timedelta(hours=24)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Automatically login the user
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            session['user_type'] = new_user.user_type
            
            flash(f'Account created successfully! Please verify your email. Your verification code is: {verification_code}', 'success')
            return redirect(url_for('verify_account'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_type', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Initialize Database
def init_db():
    # Create tables if they don't exist
    db.create_all()
    
    # Check if we already have data
    if Category.query.count() > 0:
        return
    
    # Add sample categories
    categories = [
        Category(name='Electronics'),
        Category(name='Books'),
        Category(name='Furniture'),
        Category(name='Tools'),
        Category(name='Vehicles'),
        Category(name='Toys'),
        Category(name='Clothing'),
        Category(name='Home & Garden')
    ]
    db.session.add_all(categories)
    
    # Add sample conditions
    conditions = [
        Condition(name='New'),
        Condition(name='Like New'),
        Condition(name='Good'),
        Condition(name='Fair'),
        Condition(name='Poor')
    ]
    db.session.add_all(conditions)
    
    # Add sample users
    users = [
        User(
            username='johndoe',
            email='john@example.com',
            password='password123',
            phone='1234567890',
            address='123 Main St, City',
            user_type='seller',
            is_verified=True
        ),
        User(
            username='janesmith',
            email='jane@example.com',
            password='password123',
            phone='0987654321',
            address='456 Elm St, Town',
            user_type='buyer',
            is_verified=True
        ),
        User(
            username='seller1',
            email='seller1@example.com',
            password='password123',
            phone='1122334455',
            address='789 Oak St, Village',
            user_type='seller',
            is_verified=True
        ),
        User(
            username='buyer1',
            email='buyer1@example.com',
            password='password123',
            phone='5566778899',
            address='101 Pine St, County',
            user_type='buyer',
            is_verified=True
        )
    ]
    db.session.add_all(users)
    
    # Commit the changes
    db.session.commit()
    print("Initial categories, conditions, and users added successfully")

# Order tracking
@app.route('/track-order', methods=['GET', 'POST'])
def track_order():
    form_submitted = False
    order = None
    
    if request.method == 'POST':
        tracking_id = request.form.get('tracking_id', '').strip()
        form_submitted = True
        
        if tracking_id:
            order = Order.query.filter_by(tracking_id=tracking_id).first()
            
            if not order:
                flash('Order not found with the provided tracking ID. Please check and try again.', 'warning')
        else:
            flash('Please enter a valid tracking ID.', 'warning')
            
    return render_template('track_order.html', order=order, form_submitted=form_submitted, Product=Product)

@app.route('/my-orders/<int:order_id>/track')
def track_my_order(order_id):
    if 'user_id' not in session:
        flash('Please login to track your order', 'warning')
        return redirect(url_for('login'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != session['user_id']:
        flash('Access denied. This order does not belong to you.', 'danger')
        return redirect(url_for('my_orders'))
        
    return render_template('track_order.html', order=order, form_submitted=True, Product=Product)

@app.route('/seller/update_tracking/<int:order_id>', methods=['POST'])
def update_tracking(order_id):
    if 'user_id' not in session:
        flash('Please login to update tracking information', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != 'seller':
        flash('Only sellers can update tracking information', 'warning')
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(order_id)
    
    # Check if seller owns at least one product in this order
    order_products = [OrderItem.query.filter_by(order_id=order_id, product_id=item.product_id).first() 
                      for item in order.items]
    seller_products = [Product.query.get(item.product_id) for item in order_products 
                      if Product.query.get(item.product_id).seller_id == session['user_id']]
    
    if not seller_products:
        flash('You do not have permission to update this order tracking', 'danger')
        return redirect(url_for('seller_orders'))
    
    tracking_status = request.form.get('tracking_status')
    description = request.form.get('description', '')
    
    valid_statuses = ['processing', 'shipped', 'out_for_delivery', 'delivered']
    if tracking_status not in valid_statuses:
        flash('Invalid tracking status', 'danger')
        return redirect(url_for('seller_orders'))
    
    # Update order tracking status
    order.tracking_status = tracking_status
    
    # Add tracking update
    tracking_updates = order.tracking_updates.copy() if order.tracking_updates else []
    
    # Default descriptions for each status
    default_descriptions = {
        'processing': 'Your order is being processed and prepared for shipping.',
        'shipped': 'Your order has been shipped and is on the way!',
        'out_for_delivery': 'Your order is out for delivery today!',
        'delivered': 'Your order has been delivered. Thank you for shopping with us!'
    }
    
    # If no description is provided, use the default
    if not description:
        description = default_descriptions.get(tracking_status, '')
    
    tracking_updates.append({
        "status": tracking_status,
        "timestamp": datetime.utcnow().isoformat(),
        "description": description
    })
    
    order.tracking_updates = tracking_updates
    
    # If status is delivered, mark order as completed
    if tracking_status == 'delivered':
        order.status = 'completed'
        
        # Mark all products as sold
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.status = 'sold'
    
    db.session.commit()
    flash('Order tracking information updated successfully!', 'success')
    return redirect(url_for('seller_orders'))

@app.route('/verify-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_code=token).first()
    
    if not user or user.verification_code_expires < datetime.utcnow():
        flash('The verification link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))
    
    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires = None
    db.session.commit()
    
    flash('Your email has been verified! You can now access all features.', 'success')
    return redirect(url_for('login'))

@app.route('/send-verification-code')
def send_verification_code():
    if 'user_id' not in session:
        flash('Please login to verify your account', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user.is_verified:
        flash('Your account is already verified!', 'info')
        return redirect(url_for('index'))
    
    # Generate a random 6-digit code
    verification_code = ''.join(random.choices(string.digits, k=6))
    user.verification_code = verification_code
    user.verification_code_expires = datetime.utcnow() + timedelta(hours=24)
    db.session.commit()
    
    # In a real application, send this via email
    # Here we just display it on the page for demonstration
    flash(f'Your verification code is: {verification_code} (In a real app, this would be sent to your email)', 'info')
    return redirect(url_for('verify_account'))

@app.route('/verify-account', methods=['GET', 'POST'])
def verify_account():
    if 'user_id' not in session:
        flash('Please login to verify your account', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user.is_verified:
        flash('Your account is already verified!', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        code = request.form.get('verification_code', '').strip()
        
        if code and code == user.verification_code and user.verification_code_expires > datetime.utcnow():
            user.is_verified = True
            user.verification_code = None
            user.verification_code_expires = None
            db.session.commit()
            
            flash('Your account has been verified successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid or expired verification code. Please try again.', 'danger')
    
    return render_template('verify_account.html', user=user)

@app.route('/identity-verification', methods=['GET', 'POST'])
def identity_verification():
    if 'user_id' not in session:
        flash('Please login to verify your identity', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if user.identity_verified:
        flash('Your identity is already verified!', 'info')
        return redirect(url_for('index'))
    
    if not user.is_verified:
        flash('Please verify your email before verifying your identity.', 'warning')
        return redirect(url_for('verify_account'))
    
    # Check if user already has a pending verification
    existing_verification = BusinessVerification.query.filter_by(
        user_id=user.id,
        status='pending'
    ).first()
    
    if existing_verification:
        flash('You already have a pending verification request. Please wait for approval.', 'info')
        return render_template('identity_verification.html', user=user, verification=existing_verification)
    
    if request.method == 'POST':
        # Get form data
        business_name = request.form.get('business_name')
        business_type = request.form.get('business_type')
        registration_number = request.form.get('registration_number')
        business_address = request.form.get('business_address')
        
        id_document = request.files.get('id_document')
        selfie_document = request.files.get('selfie_document')
        business_document = request.files.get('business_document')
        
        if not all([business_name, business_type, registration_number, business_address,
                   id_document, selfie_document, business_document]):
            flash('Please fill all fields and upload all required documents', 'danger')
            return render_template('identity_verification.html', user=user)
        
        try:
            # Save ID document
            id_filename = secure_filename(f"id_{user.id}_{int(time.time())}.{id_document.filename.split('.')[-1]}")
            id_path = os.path.join('trade_mart/static/uploads/identity', id_filename)
            
            # Save selfie document
            selfie_filename = secure_filename(f"selfie_{user.id}_{int(time.time())}.{selfie_document.filename.split('.')[-1]}")
            selfie_path = os.path.join('trade_mart/static/uploads/identity', selfie_filename)
            
            # Save business document
            business_doc_filename = secure_filename(f"business_{user.id}_{int(time.time())}.{business_document.filename.split('.')[-1]}")
            business_doc_path = os.path.join('trade_mart/static/uploads/identity', business_doc_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(id_path), exist_ok=True)
            
            # Save all files
            id_document.save(id_path)
            selfie_document.save(selfie_path)
            business_document.save(business_doc_path)
            
            # Update user record
            user.id_document = id_filename
            user.selfie_document = selfie_filename
            
            # Create business verification record
            verification = BusinessVerification(
                user_id=user.id,
                business_name=business_name,
                business_type=business_type,
                registration_number=registration_number,
                business_address=business_address,
                business_document=business_doc_filename
            )
            
            db.session.add(verification)
            db.session.commit()
            
            flash('Your verification documents have been submitted and are pending review.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting verification: {str(e)}', 'danger')
            return render_template('identity_verification.html', user=user)
    
    return render_template('identity_verification.html', user=user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you can add code to handle the contact form submission
        # For example, send an email or save to database
        
        flash('Thank you for your message. We will get back to you soon!', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

# Government Portal Routes
@app.route('/govt/portal')
def govt_portal():
    if 'user_id' not in session or session.get('user_type') != 'govt_employee':
        flash('Access denied. Government employees only.', 'danger')
        return redirect(url_for('index'))
    
    # Get statistics
    pending_count = BusinessVerification.query.filter_by(status='pending').count()
    verified_count = BusinessVerification.query.filter_by(status='approved').count()
    rejected_count = BusinessVerification.query.filter_by(status='rejected').count()
    total_sellers = User.query.filter_by(user_type='seller').count()
    
    # Get pending verifications
    pending_verifications = BusinessVerification.query.filter_by(status='pending').order_by(BusinessVerification.created_at.desc()).all()
    
    # Get recent activities
    recent_activities = VerificationActivity.query.order_by(VerificationActivity.timestamp.desc()).limit(10).all()
    
    return render_template('admin/govt_portal.html',
                         pending_count=pending_count,
                         verified_count=verified_count,
                         rejected_count=rejected_count,
                         total_sellers=total_sellers,
                         pending_verifications=pending_verifications,
                         recent_activities=recent_activities)

@app.route('/govt/verify/<int:verification_id>', methods=['POST'])
def govt_verify_seller(verification_id):
    if 'user_id' not in session or session.get('user_type') != 'govt_employee':
        flash('Access denied. Government employees only.', 'danger')
        return redirect(url_for('index'))
    
    verification = BusinessVerification.query.get_or_404(verification_id)
    action = request.form.get('action')
    
    if action == 'approve':
        verification.status = 'approved'
        verification.verified_at = datetime.utcnow()
        verification.verified_by = session['user_id']
        
        # Update user's identity verification status
        user = User.query.get(verification.user_id)
        user.identity_verified = True
        
        description = f"Approved business verification for {user.username}"
        
    elif action == 'reject':
        verification.status = 'rejected'
        verification.reject_reason = request.form.get('reject_reason')
        
        user = User.query.get(verification.user_id)
        description = f"Rejected business verification for {user.username}"
    else:
        flash('Invalid action', 'danger')
        return redirect(url_for('govt_portal'))
    
    # Record the activity
    activity = VerificationActivity(
        verification_id=verification.id,
        govt_employee_id=session['user_id'],
        action=action,
        reason=description
    )
    
    db.session.add(activity)
    db.session.commit()
    
    flash(f'Successfully {action}ed the verification request', 'success')
    return redirect(url_for('govt_portal'))

@app.route('/govt/manage-sellers')
def manage_sellers():
    if 'user_id' not in session or session.get('user_type') != 'govt_employee':
        flash('Access denied. Government employees only.', 'danger')
        return redirect(url_for('index'))
    
    # Get all statistics
    total_sellers = User.query.filter_by(user_type='seller').count()
    verified_sellers = User.query.filter_by(user_type='seller', identity_verified=True).count()
    pending_verifications = BusinessVerification.query.filter_by(status='pending').count()
    total_buyers = User.query.filter_by(user_type='buyer').count()
    
    # Get platform statistics
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Get all sellers with their statistics
    sellers = User.query.filter_by(user_type='seller').all()
    for seller in sellers:
        # Calculate seller statistics
        seller.total_sales = Order.query.join(OrderItem).join(Product).filter(Product.seller_id == seller.id).count()
        seller.total_revenue = db.session.query(func.sum(Order.total_amount)).join(OrderItem).join(Product).filter(Product.seller_id == seller.id).scalar() or 0
        seller.net_profit = seller.total_revenue * 0.8  # Assuming 20% platform fee
    
    # Get recent activities
    recent_activities = VerificationActivity.query.order_by(VerificationActivity.timestamp.desc()).limit(10).all()
    
    return render_template('admin/manage_sellers.html',
                         total_sellers=total_sellers,
                         verified_sellers=verified_sellers,
                         pending_verifications=pending_verifications,
                         total_buyers=total_buyers,
                         total_products=total_products,
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         avg_order_value=avg_order_value,
                         sellers=sellers,
                         recent_activities=recent_activities)

@app.route('/govt/suspend-seller/<int:seller_id>', methods=['POST'])
def suspend_seller(seller_id):
    if 'user_id' not in session or session.get('user_type') != 'govt_employee':
        flash('Access denied. Government employees only.', 'danger')
        return redirect(url_for('index'))
    
    seller = User.query.get_or_404(seller_id)
    reason = request.form.get('suspend_reason')
    
    if not reason:
        flash('Please provide a reason for suspension', 'danger')
        return redirect(url_for('manage_sellers'))
    
    # Create suspension record
    suspension = SuspensionActivity(
        seller_id=seller.id,
        govt_employee_id=session['user_id'],
        action='suspended',
        reason=reason
    )
    
    # Update seller status
    seller.is_suspended = True
    seller.suspend_reason = reason
    seller.suspended_at = datetime.utcnow()
    seller.suspended_by = session['user_id']
    
    db.session.add(suspension)
    db.session.commit()
    
    flash(f'Successfully suspended seller {seller.username}', 'success')
    return redirect(url_for('manage_sellers'))

@app.route('/check-notifications')
def check_notifications():
    if 'user_id' not in session:
        return jsonify({'new_messages': 0, 'new_offers': 0})
    
    user_id = session['user_id']
    user_type = session.get('user_type')
    
    new_messages = Message.query.filter_by(receiver_id=user_id, read=False).count()
    new_offers = 0
    
    if user_type == 'seller':
        new_offers = Offer.query.join(Product).filter(
            Product.seller_id == user_id,
            Offer.status == 'pending'
        ).count()
    
    return jsonify({
        'new_messages': new_messages,
        'new_offers': new_offers
    })

# Initialize database when imported in a production environment
with app.app_context():
    try:
        db.create_all()
        # Only initialize with sample data if tables are empty
        if Category.query.count() == 0:
            init_db()
    except Exception as e:
        print(f"Error during automatic database initialization: {e}")

if __name__ == '__main__':
    app.run(debug=True)
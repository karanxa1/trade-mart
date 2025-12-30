// Cart Page
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { cartAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import './Cart.css';

const Cart = () => {
  const { user, isBuyer } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (!isBuyer) {
      navigate('/');
      return;
    }
    fetchCart();
  }, [user, isBuyer, navigate]);

  const fetchCart = async () => {
    setLoading(true);
    try {
      const response = await cartAPI.getCart(user.id);
      setCartItems(response.data.items || []);
    } catch (err) {
      console.error('Error fetching cart:', err);
      setError('Failed to load cart items.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateQuantity = async (cartId, currentQty, change) => {
    const newQty = currentQty + change;
    if (newQty < 1) return;

    setUpdating(true);
    try {
      await cartAPI.updateCartItem(cartId, newQty);
      setCartItems(prev => prev.map(item => 
        item.id === cartId ? { ...item, quantity: newQty } : item
      ));
      toast.success('Cart updated');
    } catch (err) {
      console.error('Error updating quantity:', err);
      toast.error('Failed to update quantity');
    } finally {
      setUpdating(false);
    }
  };

  const handleRemoveItem = async (cartId) => {
    if (!window.confirm('Remove this item from cart?')) return;
    
    setUpdating(true);
    try {
      await cartAPI.removeFromCart(cartId);
      setCartItems(prev => prev.filter(item => item.id !== cartId));
      toast.success('Item removed from cart');
    } catch (err) {
      console.error('Error removing item:', err);
      toast.error('Failed to remove item');
    } finally {
      setUpdating(false);
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => total + (item.product.price * item.quantity), 0);
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) return '/images/products/placeholder.jpg';
    if (imagePath.startsWith('http')) return imagePath;
    return `http://localhost:8000/uploads/${imagePath}`;
  };

  if (loading) return <div className="loading">Loading cart...</div>;

  return (
    <div className="cart-page">
      <div className="container">
        <h1>Shopping Cart</h1>
        
        {error && <div className="alert alert-error">{error}</div>}

        {cartItems.length === 0 ? (
          <div className="empty-cart">
            <i className="fas fa-shopping-cart"></i>
            <h2>Your cart is empty</h2>
            <p>Looks like you haven't added any products yet.</p>
            <Link to="/products" className="btn btn-primary">Browse Products</Link>
          </div>
        ) : (
          <div className="cart-layout">
            <div className="cart-items">
              {cartItems.map(item => (
                <div key={item.id} className="cart-item">
                  <div className="item-image">
                    <img 
                      src={getImageUrl(item.product.image)} 
                      alt={item.product.name}
                      onError={(e) => {e.target.src = '/images/products/placeholder.jpg'}}
                    />
                  </div>
                  
                  <div className="item-details">
                    <Link to={`/products/${item.product.id}`} className="item-name">
                      {item.product.name}
                    </Link>
                    <div className="item-meta">
                      <span>Condition: {item.product.condition_name}</span>
                      <span>Seller: {item.product.seller_name || 'Seller'}</span>
                    </div>
                    <div className="item-price">₹{item.product.price.toLocaleString()}</div>
                  </div>

                  <div className="item-actions">
                    <div className="quantity-control">
                      <button 
                        onClick={() => handleUpdateQuantity(item.id, item.quantity, -1)}
                        disabled={updating || item.quantity <= 1}
                      >
                        <i className="fas fa-minus"></i>
                      </button>
                      <span>{item.quantity}</span>
                      <button 
                        onClick={() => handleUpdateQuantity(item.id, item.quantity, 1)}
                        disabled={updating}
                      >
                        <i className="fas fa-plus"></i>
                      </button>
                    </div>
                    <button 
                      className="remove-btn"
                      onClick={() => handleRemoveItem(item.id)}
                      disabled={updating}
                    >
                      <i className="fas fa-trash"></i> Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="cart-summary">
              <h3>Order Summary</h3>
              <div className="summary-row">
                <span>Subtotal ({cartItems.length} items)</span>
                <span>₹{calculateTotal().toLocaleString()}</span>
              </div>
              <div className="summary-row">
                <span>Shipping</span>
                <span>Free</span>
              </div>
              <div className="summary-divider"></div>
              <div className="summary-row total">
                <span>Total</span>
                <span>₹{calculateTotal().toLocaleString()}</span>
              </div>
              
              <Link to="/checkout" className="btn btn-primary btn-block checkout-btn">
                Proceed to Checkout
              </Link>
              <Link to="/products" className="continue-shopping">
                <i className="fas fa-arrow-left"></i> Continue Shopping
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Cart;

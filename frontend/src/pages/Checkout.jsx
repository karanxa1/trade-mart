// Checkout Page
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { cartAPI, ordersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import './Checkout.css';

const Checkout = () => {
  const { user, isBuyer } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    address: '',
    address2: '',
    city: '',
    state: '',
    zip_code: '',
    payment_method: 'cash_on_delivery'
  });

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
    try {
      const response = await cartAPI.getCart(user.id);
      if (!response.data.items || response.data.items.length === 0) {
        toast.warning('Your cart is empty');
        navigate('/cart');
        return;
      }
      setCartItems(response.data.items);
    } catch (err) {
      console.error('Error fetching cart:', err);
      toast.error('Failed to load cart');
    } finally {
      setLoading(false);
    }
  };

  const calculateTotal = () => {
    return cartItems.reduce((total, item) => total + (item.product.price * item.quantity), 0);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const orderData = {
        user_id: user.id,
        first_name: formData.first_name,
        last_name: formData.last_name,
        address: formData.address,
        address2: formData.address2,
        city: formData.city,
        state: formData.state,
        zip_code: formData.zip_code,
        payment_method: formData.payment_method
      };

      await ordersAPI.checkout(orderData);
      
      toast.success('Order placed successfully!');
      navigate('/my-orders');
      
    } catch (err) {
      console.error('Error placing order:', err);
      toast.error('Failed to place order: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Loading checkout...</div>;

  return (
    <div className="checkout-page">
      <div className="container">
        <h1>Checkout</h1>
        
        <div className="checkout-layout">
          <div className="checkout-form-section">
            <form onSubmit={handleSubmit} id="checkout-form">
              <div className="form-section">
                <h3>Shipping Address</h3>
                <div className="form-row">
                  <div className="form-group">
                    <label>First Name</label>
                    <input
                      type="text"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      required
                      placeholder="John"
                    />
                  </div>
                  <div className="form-group">
                    <label>Last Name</label>
                    <input
                      type="text"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      required
                      placeholder="Doe"
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>Street Address</label>
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    required
                    placeholder="123 Main St"
                  />
                </div>
                <div className="form-group">
                  <label>Address Line 2 (Optional)</label>
                  <input
                    type="text"
                    name="address2"
                    value={formData.address2}
                    onChange={handleChange}
                    placeholder="Apt, Suite, etc."
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>City</label>
                    <input
                      type="text"
                      name="city"
                      value={formData.city}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>State</label>
                    <input
                      type="text"
                      name="state"
                      value={formData.state}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>ZIP / Postal Code</label>
                    <input
                      type="text"
                      name="zip_code"
                      value={formData.zip_code}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h3>Payment Method</h3>
                <div className="payment-methods">
                  <div className="payment-option">
                    <input
                      type="radio"
                      name="payment_method"
                      value="credit_card"
                      id="cc"
                      checked={formData.payment_method === 'credit_card'}
                      onChange={handleChange}
                    />
                    <label htmlFor="cc">
                      <i className="fas fa-credit-card"></i> Credit Card
                    </label>
                  </div>
                  <div className="payment-option">
                    <input
                      type="radio"
                      name="payment_method"
                      value="upi"
                      id="upi"
                      checked={formData.payment_method === 'upi'}
                      onChange={handleChange}
                    />
                    <label htmlFor="upi">
                      <i className="fas fa-mobile-alt"></i> UPI
                    </label>
                  </div>
                  <div className="payment-option">
                    <input
                      type="radio"
                      name="payment_method"
                      value="cod"
                      id="cod"
                      checked={formData.payment_method === 'cod'}
                      onChange={handleChange}
                    />
                    <label htmlFor="cod">
                      <i className="fas fa-money-bill-wave"></i> Cash on Delivery
                    </label>
                  </div>
                </div>
              </div>
            </form>
          </div>

          <div className="order-summary-section">
            <div className="cart-summary">
              <h3>Order Summary</h3>
              <div className="summary-items">
                {cartItems.map(item => (
                  <div key={item.id} className="summary-item-row">
                    <div className="summary-item-info">
                      <span>{item.product.name}</span>
                      <small>Qty: {item.quantity}</small>
                    </div>
                    <span>₹{(item.product.price * item.quantity).toLocaleString()}</span>
                  </div>
                ))}
              </div>
              
              <div className="summary-divider"></div>
              
              <div className="summary-row total">
                <span>Total</span>
                <span>₹{calculateTotal().toLocaleString()}</span>
              </div>
              
              <button 
                type="submit" 
                form="checkout-form" 
                className="btn btn-primary btn-block place-order-btn"
                disabled={submitting}
              >
                {submitting ? 'Placing Order...' : 'Place Order'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;

// My Orders Page
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ordersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './MyOrders.css';

const MyOrders = () => {
  const { user, isBuyer } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchOrders();
  }, [user]);

  const fetchOrders = async () => {
    try {
      const response = await ordersAPI.getUserOrders(user.id);
      setOrders(response.data);
    } catch (err) {
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'status-success';
      case 'shipped': return 'status-info';
      case 'processing': return 'status-warning';
      case 'cancelled': return 'status-danger';
      default: return 'status-secondary';
    }
  };

  const formatDate = (dateValue) => {
    if (!dateValue) return 'N/A';
    try {
      // Handle Firestore timestamp or ISO string
      const date = dateValue.toDate ? dateValue.toDate() : new Date(dateValue);
      return date.toLocaleDateString();
    } catch (e) {
      return 'N/A';
    }
  };

  if (loading) return <div className="loading">Loading orders...</div>;

  return (
    <div className="orders-page">
      <div className="container">
        <h1>My Orders</h1>

        {orders.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-box-open"></i>
            <h2>No orders yet</h2>
            <p>Once you place an order, it will appear here.</p>
            <Link to="/products" className="btn btn-primary">Start Shopping</Link>
          </div>
        ) : (
          <div className="orders-list">
            {orders.map(order => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <div className="order-meta">
                    <span className="order-date">Placed on {formatDate(order.order_date)}</span>
                    <span className="order-id">Order #{order.tracking_id || order.id.slice(0, 8)}</span>
                  </div>
                  <div className="order-actions">
                     <span className={`status-badge ${getStatusColor(order.status)}`}>
                       {order.status.toUpperCase()}
                     </span>
                     <Link to={`/track-order?id=${order.id}`} className="btn btn-outline btn-sm">
                       Track Order
                     </Link>
                  </div>
                </div>
                
                <div className="order-items">
                  {order.items.map((item, index) => (
                    <div key={index} className="order-item">
                      <div className="item-info">
                        <Link to={`/products/${item.product_id}`} className="item-title">
                          Product ID: {item.product_id.slice(0,8)}...
                        </Link>
                        <span className="item-qty">Qty: {item.quantity}</span>
                      </div>
                      <span className="item-price">₹{item.price.toLocaleString()}</span>
                    </div>
                  ))}
                </div>

                <div className="order-footer">
                  <span className="total-label">Total Amount:</span>
                  <span className="total-amount">₹{order.total_amount.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyOrders;

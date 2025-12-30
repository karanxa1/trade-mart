// Seller Orders Page (Manage Orders)
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ordersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import './SellerOrders.css';

const SellerOrders = () => {
  const { user, isSeller } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(null);

  useEffect(() => {
    if (!user || !isSeller) {
      navigate('/login');
      return;
    }
    fetchOrders();
  }, [user, isSeller, navigate]);

  const fetchOrders = async () => {
    try {
      const response = await ordersAPI.getSellerOrders(user.id);
      setOrders(response.data || []);
    } catch (err) {
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (orderId, newStatus) => {
    if (!window.confirm(`Update order status to ${newStatus}?`)) return;
    
    setUpdating(orderId);
    try {
      await ordersAPI.updateOrderStatus(orderId, newStatus);
      setOrders(orders.map(o => 
        o.id === orderId ? { ...o, status: newStatus } : o
      ));
      toast.success(`Order marked as ${newStatus}`);
    } catch (err) {
      console.error('Error updating status:', err);
      toast.error('Failed to update order status');
    } finally {
      setUpdating(null);
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

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = dateString.toDate ? dateString.toDate() : new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (e) {
      return 'N/A';
    }
  };

  if (loading) return <div className="loading">Loading orders...</div>;

  return (
    <div className="seller-orders-page">
      <div className="container">
        <h1>Manage Orders</h1>

        {orders.length === 0 ? (
          <div className="empty-state">
            <p>No orders received yet.</p>
          </div>
        ) : (
          <div className="orders-list">
            {orders.map(order => (
              <div key={order.id} className="seller-order-card">
                <div className="order-header">
                  <div>
                    <span className="order-id">Order #{order.tracking_id || order.id.slice(0, 8)}</span>
                    <span className="order-date">{formatDate(order.order_date)}</span>
                  </div>
                  <span className={`status-badge ${getStatusColor(order.status)}`}>
                    {order.status?.toUpperCase() || 'PENDING'}
                  </span>
                </div>
                
                <div className="customer-info">
                  <h4>Customer Details</h4>
                  <p><strong>Buyer:</strong> {order.buyer?.username || 'Unknown'}</p>
                  <p><strong>Delivery Address:</strong> {order.delivery_address || 'N/A'}</p>
                </div>

                <div className="order-items">
                  {order.items && order.items.map((item, index) => (
                    <div key={index} className="order-item">
                      <div className="item-info">
                         <span className="item-name">{item.product?.name || 'Product'}</span>
                         <span className="item-qty">x{item.quantity}</span>
                      </div>
                      <span className="item-price">₹{(item.price * item.quantity).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
                
                <div className="order-total">
                   <span>Total Earnings</span>
                   <span>₹{order.total_amount?.toLocaleString() || '0'}</span>
                </div>

                <div className="order-actions">
                  <div className="status-control">
                    <label>Update Status:</label>
                    <div className="action-buttons">
                      {order.status === 'processing' && (
                        <>
                          <button 
                            className="btn btn-sm btn-info"
                            onClick={() => handleStatusUpdate(order.id, 'shipped')}
                            disabled={updating === order.id}
                          >
                            Mark Shipped
                          </button>
                          <button 
                            className="btn btn-sm btn-danger"
                            onClick={() => handleStatusUpdate(order.id, 'cancelled')}
                            disabled={updating === order.id}
                          >
                            Cancel
                          </button>
                        </>
                      )}
                      
                      {order.status === 'shipped' && (
                        <button 
                          className="btn btn-sm btn-success"
                          onClick={() => handleStatusUpdate(order.id, 'completed')}
                          disabled={updating === order.id}
                        >
                          Mark Delivered
                        </button>
                      )}
                      
                      {(order.status === 'completed' || order.status === 'cancelled') && (
                        <span className="action-note">Order is finalized</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SellerOrders;

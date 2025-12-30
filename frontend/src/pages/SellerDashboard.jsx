// Seller Dashboard
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { productsAPI, ordersAPI, offersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './SellerDashboard.css';

const SellerDashboard = () => {
  const { user, isSeller } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    products: 0,
    orders: 0,
    sales: 0,
    pendingOffers: 0,
    pendingOrders: 0
  });
  const [recentOrders, setRecentOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    if (!isSeller) {
      navigate('/');
      return;
    }
    fetchDashboardData();
  }, [user, isSeller, navigate]);

  const fetchDashboardData = async () => {
    try {
      const [productsRes, ordersRes, offersRes] = await Promise.all([
        productsAPI.getSellerProducts(user.id),
        ordersAPI.getSellerOrders(user.id),
        offersAPI.getPendingCount(user.id)
      ]);

      const products = productsRes.data || [];
      const orders = ordersRes.data || [];
      
      const totalSales = orders
        .filter(o => o.status !== 'cancelled')
        .reduce((sum, o) => sum + o.total_amount, 0);

      const pendingOrdersCount = orders.filter(o => o.status === 'processing').length;

      setStats({
        products: products.length,
        orders: orders.length,
        sales: totalSales,
        pendingOffers: offersRes.data.count,
        pendingOrders: pendingOrdersCount
      });

      setRecentOrders(orders.slice(0, 5));
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
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
      const date = dateValue.toDate ? dateValue.toDate() : new Date(dateValue);
      return date.toLocaleDateString();
    } catch (e) {
      return 'N/A';
    }
  };

  if (loading) return <div className="loading">Loading dashboard...</div>;

  return (
    <div className="seller-dashboard">
      <div className="container">
        <div className="dashboard-header">
          <h1>Seller Dashboard</h1>
          <div className="header-actions">
            <Link to="/seller/products/new" className="btn btn-primary">
              <i className="fas fa-plus"></i> Add Product
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon sales">
              <i className="fas fa-rupee-sign"></i>
            </div>
            <div className="stat-info">
              <h3>Total Sales</h3>
              <p>₹{stats.sales.toLocaleString()}</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon orders">
              <i className="fas fa-shopping-bag"></i>
            </div>
            <div className="stat-info">
              <h3>Total Orders</h3>
              <p>{stats.orders}</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon products">
              <i className="fas fa-box"></i>
            </div>
            <div className="stat-info">
              <h3>Active Products</h3>
              <p>{stats.products}</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon offers">
              <i className="fas fa-tags"></i>
            </div>
            <div className="stat-info">
              <h3>Pending Offers</h3>
              <p>{stats.pendingOffers}</p>
            </div>
          </div>
        </div>

        <div className="dashboard-content">
          {/* Recent Orders */}
          <div className="content-section orders-section">
            <div className="section-header">
              <h2>Recent Orders</h2>
              <Link to="/seller/orders">View All</Link>
            </div>
            {recentOrders.length === 0 ? (
              <p className="no-data">No orders yet.</p>
            ) : (
              <table className="orders-table">
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentOrders.map(order => (
                    <tr key={order.id}>
                      <td>#{order.id.slice(0, 8)}</td>
                      <td>{formatDate(order.order_date)}</td>
                      <td>₹{order.total_amount.toLocaleString()}</td>
                      <td>
                        <span className={`status-badge ${getStatusColor(order.status)}`}>
                          {order.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Quick Actions / Notifications */}
          <div className="content-section actions-section">
            <div className="section-header">
              <h2>Quick Actions</h2>
            </div>
            <div className="quick-actions-list">
              {stats.pendingOrders > 0 && (
                <Link to="/seller/orders" className="action-item warning">
                  <i className="fas fa-exclamation-circle"></i>
                  <span>You have {stats.pendingOrders} orders to process</span>
                  <i className="fas fa-chevron-right arrow"></i>
                </Link>
              )}
              {stats.pendingOffers > 0 && (
                <Link to="/seller/offers" className="action-item info">
                  <i className="fas fa-tag"></i>
                  <span>You have {stats.pendingOffers} new offers</span>
                  <i className="fas fa-chevron-right arrow"></i>
                </Link>
              )}
              <Link to="/seller/products" className="action-item primary">
                <i className="fas fa-box-open"></i>
                <span>Manage your inventory</span>
                <i className="fas fa-chevron-right arrow"></i>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SellerDashboard;

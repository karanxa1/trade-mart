// Government Dashboard - Product Approval System
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../components/Common/Toast';
import { adminAPI } from '../services/api';
import './GovtDashboard.css';

const GovtDashboard = () => {
  const [allProducts, setAllProducts] = useState([]);
  const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [deletionReason, setDeletionReason] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  
  const { user } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    if (!user || user.user_type !== 'government') {
      navigate('/');
      return;
    }
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [productsRes, statsRes] = await Promise.all([
        adminAPI.getPendingProducts(),
        adminAPI.getApprovalStats()
      ]);
      setAllProducts(Array.isArray(productsRes.data) ? productsRes.data : []);
      setStats(statsRes.data || { pending: 0, approved: 0, rejected: 0, total: 0 });
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load data');
      setAllProducts([]);
      setStats({ pending: 0, approved: 0, rejected: 0, total: 0 });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (productId) => {
    try {
      await adminAPI.approveProduct(productId, user.id);
      toast.success('Product approved successfully!');
      fetchData();
    } catch (error) {
      console.error('Error approving product:', error);
      toast.error('Failed to approve product');
    }
  };

  const handleReject = async (product) => {
    setSelectedProduct(product);
    setShowRejectModal(true);
  };

  const confirmReject = async () => {
    if (!rejectionReason.trim()) {
      toast.error('Please provide a rejection reason');
      return;
    }

    try {
      await adminAPI.rejectProduct(selectedProduct.id, user.id, rejectionReason);
      toast.success('Product rejected');
      setShowRejectModal(false);
      setRejectionReason('');
      setSelectedProduct(null);
      fetchData();
    } catch (error) {
      console.error('Error rejecting product:', error);
      toast.error('Failed to reject product');
    }
  };

  const handleDelete = async (product) => {
    setSelectedProduct(product);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!deletionReason.trim()) {
      toast.error('Please provide a deletion reason');
      return;
    }

    try {
      await adminAPI.deleteProduct(selectedProduct.id, user.id, deletionReason);
      toast.success('Product deleted successfully');
      setShowDeleteModal(false);
      setDeletionReason('');
      setSelectedProduct(null);
      fetchData();
    } catch (error) {
      console.error('Error deleting product:', error);
      toast.error('Failed to delete product');
    }
  };

  const renderProductCard = (product) => (
    <div key={product.id} className="product-approval-card">
      <div className="product-image-section">
        {product.image ? (
          <img src={product.image} alt={product.name} />
        ) : (
          <div className="no-image"><i className="fas fa-image"></i></div>
        )}
      </div>
      <div className="product-info-section">
        <h3>{product.name}</h3>
        <p className="product-description">{product.description}</p>
        <div className="product-meta">
          <span className="meta-item">
            <i className="fas fa-tag"></i> {product.category_name}
          </span>
          <span className="meta-item">
            <i className="fas fa-info-circle"></i> {product.condition_name}
          </span>
          <span className="meta-item price">
            <i className="fas fa-rupee-sign"></i> ₹{product.price?.toLocaleString()}
          </span>
          {product.negotiable && (
            <span className="meta-item negotiable">
              <i className="fas fa-handshake"></i> Negotiable
            </span>
          )}
        </div>
        <div className="seller-info">
          <i className="fas fa-user"></i>
          <strong>Seller:</strong> {product.seller?.username || 'Unknown'}
          <span className="seller-email">({product.seller?.email})</span>
        </div>
        {product.approval_status === 'approved' && (
          <div className="approval-badge">
            <span className="badge-approved">
              <i className="fas fa-check-circle"></i> Approved
            </span>
          </div>
        )}
      </div>
      <div className="product-actions-section">
        {product.approval_status === 'pending' && (
          <>
            <button className="btn-approve" onClick={() => handleApprove(product.id)}>
              <i className="fas fa-check"></i> Approve
            </button>
            <button className="btn-reject" onClick={() => handleReject(product)}>
              <i className="fas fa-times"></i> Reject
            </button>
          </>
        )}
        <button className="btn-delete" onClick={() => handleDelete(product)}>
          <i className="fas fa-trash"></i> Delete
        </button>
      </div>
    </div>
  );

  if (loading) {
    return <div className="govt-dashboard"><div className="loading">Loading...</div></div>;
  }

  const pendingProducts = allProducts.filter(p => p.approval_status === 'pending');
  const approvedProducts = allProducts.filter(p => p.approval_status === 'approved');

  return (
    <div className="govt-dashboard">
      <div className="container">
        <div className="dashboard-header">
          <h1>Government Product Approval Dashboard</h1>
          <p>Review and manage all products on the platform</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card pending">
            <div className="stat-icon"><i className="fas fa-clock"></i></div>
            <div className="stat-info">
              <h3>{stats.pending}</h3>
              <p>Pending Approval</p>
            </div>
          </div>
          <div className="stat-card approved">
            <div className="stat-icon"><i className="fas fa-check-circle"></i></div>
            <div className="stat-info">
              <h3>{stats.approved}</h3>
              <p>Approved</p>
            </div>
          </div>
          <div className="stat-card rejected">
            <div className="stat-icon"><i className="fas fa-times-circle"></i></div>
            <div className="stat-info">
              <h3>{stats.rejected}</h3>
              <p>Rejected</p>
            </div>
          </div>
          <div className="stat-card total">
            <div className="stat-icon"><i className="fas fa-box"></i></div>
            <div className="stat-info">
              <h3>{stats.total}</h3>
              <p>Total Products</p>
            </div>
          </div>
        </div>

        {pendingProducts.length === 0 && approvedProducts.length === 0 ? (
          <div className="no-pending">
            <i className="fas fa-check-double"></i>
            <h3>All Clear!</h3>
            <p>No products to manage at the moment.</p>
          </div>
        ) : (
          <>
            {pendingProducts.length > 0 && (
              <div className="pending-products">
                <h2>Products Awaiting Approval ({pendingProducts.length})</h2>
                <div className="products-table">
                  {pendingProducts.map(renderProductCard)}
                </div>
              </div>
            )}

            {approvedProducts.length > 0 && (
              <div className="pending-products">
                <h2>Approved Products ({approvedProducts.length})</h2>
                <div className="products-table">
                  {approvedProducts.map(renderProductCard)}
                </div>
              </div>
            )}
          </>
        )}

        {showRejectModal && (
          <div className="modal-overlay" onClick={() => setShowRejectModal(false)}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
              <h3>Reject Product</h3>
              <p>You are about to reject: <strong>{selectedProduct?.name}</strong></p>
              <div className="form-group">
                <label>Rejection Reason *</label>
                <textarea
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder="Please provide a detailed reason for rejection..."
                  rows="4"
                  required
                ></textarea>
              </div>
              <div className="modal-actions">
                <button className="btn btn-outline" onClick={() => setShowRejectModal(false)}>
                  Cancel
                </button>
                <button className="btn btn-danger" onClick={confirmReject}>
                  Confirm Rejection
                </button>
              </div>
            </div>
          </div>
        )}

        {showDeleteModal && (
          <div className="modal-overlay" onClick={() => setShowDeleteModal(false)}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
              <h3>Delete Product</h3>
              <p>You are about to permanently delete: <strong>{selectedProduct?.name}</strong></p>
              <p className="warning-text">This action cannot be undone. The seller will see this product was removed by government employee.</p>
              <div className="form-group">
                <label>Deletion Reason *</label>
                <textarea
                  value={deletionReason}
                  onChange={(e) => setDeletionReason(e.target.value)}
                  placeholder="Please provide a detailed reason for deletion..."
                  rows="4"
                  required
                ></textarea>
              </div>
              <div className="modal-actions">
                <button className="btn btn-outline" onClick={() => setShowDeleteModal(false)}>
                  Cancel
                </button>
                <button className="btn btn-danger" onClick={confirmDelete}>
                  Confirm Deletion
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GovtDashboard;

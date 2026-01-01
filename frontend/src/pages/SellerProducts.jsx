// Seller Products List
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { productsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import './SellerProducts.css';

const SellerProducts = () => {
  const { user, isSeller } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || !isSeller) {
      navigate('/login');
      return;
    }
    fetchProducts();
  }, [user, isSeller, navigate]);

  const fetchProducts = async () => {
    try {
      const response = await productsAPI.getSellerProducts(user.id);
      setProducts(response.data || []);
    } catch (err) {
      console.error('Error fetching products:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      await productsAPI.deleteProduct(productId);
      setProducts(products.filter(p => p.id !== productId));
      toast.success('Product deleted successfully');
    } catch (err) {
      toast.error('Failed to delete product');
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) return '/images/products/placeholder.jpg';
    if (imagePath.startsWith('http')) return imagePath;
    return `http://localhost:8000/uploads/${imagePath}`;
  };

  if (loading) return <div className="loading">Loading products...</div>;

  return (
    <div className="seller-products-page">
      <div className="container">
        <div className="page-header">
          <h1>My Products</h1>
          <Link to="/seller/products/new" className="btn btn-primary">
            <i className="fas fa-plus"></i> Add New Product
          </Link>
        </div>

        {products.length === 0 ? (
          <div className="empty-state">
            <p>You haven't listed any products yet.</p>
            <Link to="/seller/products/new" className="btn btn-outline">Create your first listing</Link>
          </div>
        ) : (
          <div className="seller-products-grid">
            {products.map(product => (
              <div key={product.id} className="seller-product-card">
                <div className="product-image">
                  <img src={getImageUrl(product.image)} alt={product.name} />
                  <span className={`status-badge ${product.status}`}>
                    {product.status}
                  </span>
                </div>
                <div className="product-details">
                  <h3>{product.name}</h3>
                  <p className="price">₹{product.price.toLocaleString()}</p>
                  <div className="meta">
                    <span>{product.category_name}</span>
                    <span>{product.condition_name}</span>
                  </div>
                  {/* Approval Status */}
                  <div className="approval-status">
                    {product.deleted_by_govt && (
                      <div className="status-tag govt-deleted">
                        <i className="fas fa-ban"></i> Removed by Government
                        {product.deletion_reason && (
                          <span className="deletion-reason">
                            Reason: {product.deletion_reason}
                          </span>
                        )}
                      </div>
                    )}
                    {!product.deleted_by_govt && product.approval_status === 'pending' && (
                      <div className="status-tag pending">
                        <i className="fas fa-clock"></i> Pending Approval
                      </div>
                    )}
                    {!product.deleted_by_govt && product.approval_status === 'approved' && (
                      <div className="status-tag approved">
                        <i className="fas fa-check-circle"></i> Approved
                      </div>
                    )}
                    {!product.deleted_by_govt && product.approval_status === 'rejected' && (
                      <div className="status-tag rejected">
                        <i className="fas fa-times-circle"></i> Rejected
                        {product.rejection_reason && (
                          <span className="rejection-reason">
                            Reason: {product.rejection_reason}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                <div className="product-actions">
                  <Link to={`/seller/products/edit/${product.id}`} className="btn-icon edit">
                    <i className="fas fa-edit"></i>
                  </Link>
                  <button onClick={() => handleDelete(product.id)} className="btn-icon delete">
                    <i className="fas fa-trash"></i>
                  </button>
                  <Link to={`/products/${product.id}`} className="btn-icon view">
                    <i className="fas fa-eye"></i>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SellerProducts;

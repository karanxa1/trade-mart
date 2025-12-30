// Product Card Component
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { cartAPI } from '../../services/api';
import './Product.css';

const ProductCard = ({ product }) => {
  const { user, isBuyer } = useAuth();
  const apiBaseUrl = 'http://localhost:8000';

  const handleAddToCart = async (e) => {
    e.preventDefault();
    if (!user) {
      alert('Please login to add items to cart');
      return;
    }
    try {
      await cartAPI.addToCart(user.id, product.id);
      alert('Added to cart successfully!');
    } catch (error) {
      alert('Error adding to cart: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) return '/images/products/placeholder.jpg';
    // If it's a full URL (e.g. from seed data), use it
    if (imagePath.startsWith('http')) return imagePath;
    // Otherwise serve from backend static files
    return `${apiBaseUrl}/uploads/${imagePath}`;
  };

  return (
    <Link to={`/products/${product.id}`} className="product-card">
      <div className="product-image">
        <img 
          src={getImageUrl(product.image)} 
          alt={product.name} 
          onError={(e) => {e.target.src = '/images/products/placeholder.jpg'}}
        />
        {product.status !== 'available' && (
          <span className="product-badge closed">Sold</span>
        )}
        {product.negotiable && (
          <span className="product-badge negotiable">Negotiable</span>
        )}
      </div>
      <div className="product-details">
        <div className="product-category">{product.category_name}</div>
        <h3 className="product-title">{product.name}</h3>
        <div className="product-meta">
          <span className="product-condition">{product.condition_name}</span>
          <span className="product-seller">
            <i className="fas fa-user-circle"></i> {product.seller?.username || 'Seller'}
          </span>
        </div>
        <div className="product-footer">
          <div className="product-price">₹{product.price?.toLocaleString()}</div>
          {isBuyer && product.status === 'available' && (
            <button className="add-cart-btn" onClick={handleAddToCart}>
              <i className="fas fa-cart-plus"></i>
            </button>
          )}
        </div>
      </div>
    </Link>
  );
};

export default ProductCard;

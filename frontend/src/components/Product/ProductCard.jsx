import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../Common/Toast';
import { cartAPI } from '../../services/api';
import './Product.css';

const ProductCard = ({ product }) => {
  const { user, isBuyer } = useAuth();
  const toast = useToast();
  const apiBaseUrl = 'http://localhost:8000';
  const [imageLoaded, setImageLoaded] = useState(false);
  const [isWideImage, setIsWideImage] = useState(false);

  const handleAddToCart = async (e) => {
    e.preventDefault();
    if (!user) {
      toast.warning('Please login to add items to cart');
      return;
    }
    try {
      await cartAPI.addToCart(user.id, product.id);
      toast.success('Added to cart!');
    } catch (error) {
      toast.error('Error adding to cart: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleImageLoad = (e) => {
    const img = e.target;
    // If image aspect ratio is wide enough (width > 80% of container), use cover
    const aspectRatio = img.naturalWidth / img.naturalHeight;
    setIsWideImage(aspectRatio >= 0.8);
    setImageLoaded(true);
  };

  const getImageUrl = (imagePath) => {
    // If no image, return category specific placeholder if possible, or general placeholder
    if (!imagePath) {
      if (product.category_name === 'Electronics') return '/images/products/electronics.jpg';
      if (product.category_name === 'Furniture') return '/images/products/furniture.jpg';
      if (product.category_name === 'Clothing') return '/images/products/perfume.jpg'; // Using perfume for fashion-ish
      return '/images/products/placeholder.jpg';
    }
    // If it's a full URL (e.g. from seed data), use it
    if (imagePath.startsWith('http')) return imagePath;
    // Otherwise serve from backend static files
    return `${apiBaseUrl}/uploads/${imagePath}`;
  };

  return (
    <Link to={`/products/${product.id}`} className="product-card">
      <div className={`product-image ${isWideImage ? 'cover-fit' : ''}`}>
        <img 
          src={getImageUrl(product.image)} 
          alt={product.name}
          onLoad={handleImageLoad}
          onError={(e) => {
            if (e.target.src.includes('placeholder.jpg')) return;
            e.target.src = '/images/products/placeholder.jpg'
          }}
          style={{ opacity: imageLoaded ? 1 : 0, transition: 'opacity 0.3s ease' }}
        />
        {!imageLoaded && (
          <div className="image-placeholder">
            <i className="fas fa-image"></i>
          </div>
        )}
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

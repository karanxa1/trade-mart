// Product Detail Page
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { productsAPI, cartAPI, offersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import ProductCard from '../components/Product/ProductCard';
import './ProductDetail.css';

const ProductDetail = () => {
  const { id } = useParams();
  const { user, isBuyer } = useAuth();
  const toast = useToast();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [offerPrice, setOfferPrice] = useState('');
  const [offerSubmitLoading, setOfferSubmitLoading] = useState(false);
  const apiBaseUrl = 'http://localhost:8000';

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    setLoading(true);
    try {
      const response = await productsAPI.getProduct(id);
      setProduct(response.data);
    } catch (err) {
      setError('Product not found or failed to load.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!user) return toast.warning('Please login to add items to cart');
    
    try {
      await cartAPI.addToCart(user.id, product.id);
      toast.success('Product added to cart!');
    } catch (err) {
      toast.error('Failed to add to cart: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleMakeOffer = async (e) => {
    e.preventDefault();
    if (!user) return toast.warning('Please login to make an offer');
    if (!offerPrice) return toast.warning('Please enter an offer price');

    setOfferSubmitLoading(true);
    try {
      await offersAPI.createOffer(product.id, user.id, parseFloat(offerPrice));
      toast.success('Offer submitted! Waiting for seller response.');
      setOfferPrice('');
    } catch (err) {
      toast.error('Failed to submit offer: ' + (err.response?.data?.detail || err.message));
    } finally {
      setOfferSubmitLoading(false);
    }
  };

  const getImageUrl = (imagePath) => {
    if (!imagePath) return '/images/products/placeholder.jpg';
    if (imagePath.startsWith('http')) return imagePath;
    return `${apiBaseUrl}/uploads/${imagePath}`;
  };

  if (loading) return <div className="loading">Loading product details...</div>;
  if (error) return <div className="container error-container">{error} <Link to="/products">Back to products</Link></div>;
  if (!product) return null;

  return (
    <div className="product-detail-page">
      <div className="container">
        <div className="product-layout">
          {/* Left Column: Image */}
          <div className="product-gallery">
            <div className="main-image">
              <img 
                src={getImageUrl(product.image)} 
                alt={product.name} 
                onError={(e) => {e.target.src = '/images/products/placeholder.jpg'}}
              />
              {product.status !== 'available' && (
                <span className="status-badge closed">Sold</span>
              )}
            </div>
          </div>

          {/* Right Column: Details */}
          <div className="product-info-section">
            <div className="product-header">
              <h1>{product.name}</h1>
              <div className="product-meta-tags">
                <span className="tag category">{product.category_name}</span>
                <span className="tag condition">{product.condition_name}</span>
              </div>
            </div>

            <div className="product-price-box">
              <div className="price-tag">
                ₹{product.price?.toLocaleString()}
                {product.negotiable && <span className="negotiable-label">Negotiable</span>}
              </div>
              
              <div className="action-buttons">
                {isBuyer && product.status === 'available' && (
                  <>
                    <button onClick={handleAddToCart} className="btn btn-primary btn-lg">
                      <i className="fas fa-shopping-cart"></i> Add to Cart
                    </button>
                    
                    {product.negotiable && (
                      <div className="offer-section">
                        <h4>Make an Offer</h4>
                        <form onSubmit={handleMakeOffer} className="offer-form">
                          <div className="input-group">
                            <span className="currency-symbol">₹</span>
                            <input
                              type="number"
                              value={offerPrice}
                              onChange={(e) => setOfferPrice(e.target.value)}
                              placeholder="Enter amount"
                              min="1"
                            />
                            <button type="submit" disabled={offerSubmitLoading}>
                              {offerSubmitLoading ? 'Sending...' : 'Send Offer'}
                            </button>
                          </div>
                        </form>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            <div className="product-description">
              <h3>Description</h3>
              <p>{product.description}</p>
            </div>

            <div className="seller-box">
              <div className="seller-header">
                <i className="fas fa-user-circle seller-avatar"></i>
                <div className="seller-info">
                  <h4>{product.seller?.username || 'Seller'}</h4>
                  {product.seller?.avg_rating > 0 && (
                     <div className="rating">
                       <i className="fas fa-star"></i>
                       <span>{product.seller.avg_rating.toFixed(1)} / 5.0</span>
                       <span className="count">({product.seller.review_count} reviews)</span>
                     </div>
                  )}
                </div>
              </div>
              <div className="seller-actions">
                {isBuyer && (
                  <Link to={`/messages?user=${product.seller?.id}&product=${product.id}`} className="btn btn-outline btn-sm">
                    <i className="fas fa-comment-alt"></i> Chat with Seller
                  </Link>
                )}
                <Link to={`/products?seller=${product.seller?.id}`} className="btn btn-link btn-sm">
                  View Seller's Other Items
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Similar Products */}
        {product.similar_products && product.similar_products.length > 0 && (
          <div className="similar-products">
            <h3>Similar Items You Might Like</h3>
            <div className="products-grid">
              {product.similar_products.map(p => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductDetail;

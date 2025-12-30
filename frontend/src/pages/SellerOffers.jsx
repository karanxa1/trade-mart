    // Seller Offers Page
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { offersAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import './SellerOffers.css';

const SellerOffers = () => {
  const { user, isSeller } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(null);

  useEffect(() => {
    if (!user || !isSeller) {
      navigate('/login');
      return;
    }
    fetchOffers();
  }, [user, isSeller, navigate]);

  const fetchOffers = async () => {
    try {
      const response = await offersAPI.getSellerOffers(user.id);
      // Transform backend response to match expected format
      // Backend returns: { product: {...}, buyer: {id, username}, offer_price, status, created_at }
      // Frontend expects: { product_name, original_price, offer_amount, buyer_name, status }
      const transformedOffers = (response.data || []).map(offer => ({
        ...offer,
        product_name: offer.product?.name || 'Unknown Product',
        original_price: offer.product?.price || 0,
        offer_amount: offer.offer_price,
        buyer_name: offer.buyer?.username || 'Unknown Buyer'
      }));
      setOffers(transformedOffers);
    } catch (err) {
      console.error('Error fetching offers:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOfferAction = async (offerId, action) => {
    setUpdating(offerId);
    try {
      await offersAPI.respondToOffer(offerId, action);
      const newStatus = action === 'accept' ? 'accepted' : 'rejected';
      setOffers(offers.map(o => 
        o.id === offerId ? { ...o, status: newStatus } : o
      ));
      toast.success(action === 'accept' ? 'Offer accepted!' : 'Offer rejected');
    } catch (err) {
      console.error('Error updating offer:', err);
      toast.error('Failed to update offer');
    } finally {
      setUpdating(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'accepted': return 'status-success';
      case 'rejected': return 'status-danger';
      case 'pending': return 'status-warning';
      default: return 'status-secondary';
    }
  };

  if (loading) return <div className="loading">Loading offers...</div>;

  return (
    <div className="seller-offers-page">
      <div className="container">
        <h1>Received Offers</h1>

        {offers.length === 0 ? (
          <div className="empty-state">
            <p>No offers pending currently.</p>
          </div>
        ) : (
          <div className="offers-list">
            {offers.map(offer => (
              <div key={offer.id} className="offer-card">
                <div className="offer-header">
                  <span className={`status-badge ${getStatusColor(offer.status)}`}>
                    {offer.status.toUpperCase()}
                  </span>
                  <span className="offer-date">{new Date(offer.created_at).toLocaleDateString()}</span>
                </div>
                
                <div className="offer-content">
                  <div className="product-info">
                    <h4>{offer.product_name}</h4>
                    <p className="original-price">Listed Price: ₹{offer.original_price.toLocaleString()}</p>
                  </div>
                  
                  <div className="offer-details">
                    <div className="offer-amount">
                      <label>Offered Price</label>
                      <span>₹{offer.offer_amount.toLocaleString()}</span>
                    </div>
                    <div className="buyer-info">
                       <label>From</label>
                       <span>{offer.buyer_name}</span>
                    </div>
                  </div>
                  
                  {offer.message && (
                    <div className="offer-message">
                      <p>"{offer.message}"</p>
                    </div>
                  )}
                </div>

                {offer.status === 'pending' && (
                  <div className="offer-actions">
                    <button 
                      className="btn btn-success"
                      onClick={() => handleOfferAction(offer.id, 'accept')}
                      disabled={updating === offer.id}
                    >
                      <i className="fas fa-check"></i> Accept
                    </button>
                    <button 
                      className="btn btn-danger"
                      onClick={() => handleOfferAction(offer.id, 'reject')}
                      disabled={updating === offer.id}
                    >
                      <i className="fas fa-times"></i> Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SellerOffers;

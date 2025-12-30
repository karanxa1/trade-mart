// Track Order Page
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ordersAPI } from '../services/api';
import './TrackOrder.css';

const TrackOrder = () => {
  const [searchParams] = useSearchParams();
  const [trackingId, setTrackingId] = useState(searchParams.get('id') || '');
  const [orderData, setOrderData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Auto-search if ID provided in URL
  useEffect(() => {
    const idFromUrl = searchParams.get('id');
    if (idFromUrl) {
      setTrackingId(idFromUrl); // Sync state with URL
      handleTrack(idFromUrl);
    }
  }, [searchParams]);

  const handleTrack = async (idToTrack) => {
    const id = idToTrack || trackingId;
    if (!id.trim()) return;

    setLoading(true);
    setError('');
    setOrderData(null);

    try {
      // API expects tracking ID (e.g., from shipping provider) or Internal Order ID?
      // Frontend link sends Order ID usually. Let's assume we search by Order ID for now if tracking_id not distinct
      // But API says `track_order` takes `tracking_id`. Backend `orders.py` -> `get_by_tracking_id`.
      // Let's assume Order ID works as a fallback or user enters Tracking ID provided in email
      // For simplicity in this demo, let's try fetching by Order ID directly if Track fails, OR 
      // check if the ID passed is order ID. MyOrders page links to `/track-order?id=ORDER_ID`
      // backend request `ordersAPI.getOrder(id)` might be better for "My Orders" link context
      // But "Track Order" usually implies public tracking. 
      // Let's try `ordersAPI.getOrder(id)` first as that's what we have ID for.
      
      // If we want "Public Tracking" we use tracking ID. 
      // Let's support both logic: try getOrder (authenticated usually, but maybe public?)
      // Actually `ordersAPI.getOrder` is likely authenticated.
      // `ordersAPI.trackOrder` is `/orders/track/{tracking_id}`.
      
      // If we are coming from MyOrders, we have Order ID. 
      // We should probably redirect to Order Details or have a dedicated verify.
      // Let's try to fetch order details.
      
      let response;
      try {
        // Try as Order ID first (authenticated user flow)
        response = await ordersAPI.getOrder(id);
      } catch (e) {
        // If 404 or 403, try as tracking ID
        response = await ordersAPI.trackOrder(id);
      }
      
      setOrderData(response.data);
    } catch (err) {
      console.error('Tracking Error:', err);
      setError('Order not found. Please check your ID and try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusStep = (status) => {
    switch (status) {
      case 'processing': return 1;
      case 'shipped': return 2;
      case 'completed': return 3;
      default: return 0;
    }
  };

  return (
    <div className="track-order-page">
      <div className="container">
        <h1>Track Your Order</h1>
        
        <div className="tracking-search">
           <input
             type="text"
             placeholder="Enter Order ID or Tracking Number"
             value={trackingId}
             onChange={(e) => setTrackingId(e.target.value)}
           />
           <button onClick={() => handleTrack()} className="btn btn-primary" disabled={loading}>
             {loading ? 'Tracking...' : 'Track'}
           </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {orderData && (
          <div className="tracking-result">
            <div className="order-summary-card">
              <div className="result-header">
                <h3>Order Status</h3>
                <span className="order-ref">Ref: {orderData.id}</span>
              </div>
              
              <div className="progress-track">
                {['Processing', 'Shipped', 'Delivered'].map((step, index) => {
                  const currentStep = getStatusStep(orderData.status);
                  const stepNum = index + 1;
                  let className = 'step';
                  if (currentStep >= stepNum) className += ' active';
                  if (currentStep === stepNum) className += ' current';
                  
                  return (
                    <div key={step} className={className}>
                      <div className="step-icon">
                        {index === 0 && <i className="fas fa-box-open"></i>}
                        {index === 1 && <i className="fas fa-shipping-fast"></i>}
                        {index === 2 && <i className="fas fa-check-circle"></i>}
                      </div>
                      <span className="step-label">{step}</span>
                    </div>
                  );
                })}
              </div>
              
              <div className="order-details-mini">
                 <p><strong>Estimated Delivery:</strong> {orderData.status === 'completed' ? 'Delivered' : '3-5 Business Days'}</p>
                 <p><strong>Shipping To:</strong> {orderData.delivery_address}</p>
              </div>
              
              <div className="tracking-items">
                <h4>Items in Shipment</h4>
                <ul>
                  {orderData.items && orderData.items.map((item, idx) => (
                    <li key={idx}>
                      <span>{item.quantity}x Product ID: {item.product_id.slice(0,8)}...</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrackOrder;

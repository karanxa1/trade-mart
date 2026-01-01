// API Service
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  googleLogin: (idToken, userType) => api.post('/auth/google-login', { id_token: idToken, user_type: userType }),
  verify: (userId, code) => api.post('/auth/verify', { user_id: userId, verification_code: code }),
  getUser: (userId) => api.get(`/auth/user/${userId}`),
};

export const productsAPI = {
  getProducts: (params) => {
    // Clean up empty parameters to avoid 422 errors on backend
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
    );
    return api.get('/products', { params: cleanParams });
  },
  getFeatured: (limit = 8) => api.get('/products/featured', { params: { limit } }),
  getProduct: (id) => api.get(`/products/${id}`),
  getCategories: () => api.get('/products/categories'),
  getConditions: () => api.get('/products/conditions'),
  createProduct: (formData) => api.post('/products', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  updateProduct: (id, data) => api.put(`/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/products/${id}`),
  getSellerProducts: (sellerId) => api.get(`/products/seller/${sellerId}`),
};

export const cartAPI = {
  getCart: (userId) => api.get(`/cart/${userId}`),
  addToCart: (userId, productId, quantity = 1) => 
    api.post('/cart/add', { user_id: userId, product_id: productId, quantity }),
  updateCartItem: (cartId, quantity) => api.put(`/cart/${cartId}`, { quantity }),
  removeFromCart: (cartId) => api.delete(`/cart/${cartId}`),
  clearCart: (userId) => api.delete(`/cart/clear/${userId}`),
};

export const ordersAPI = {
  getUserOrders: (userId) => api.get(`/orders/user/${userId}`),
  getOrder: (orderId) => api.get(`/orders/${orderId}`),
  trackOrder: (trackingId) => api.get(`/orders/track/${trackingId}`),
  checkout: (data) => api.post('/orders/checkout', data),
  getSellerOrders: (sellerId) => api.get(`/orders/seller/${sellerId}`),
  updateOrderStatus: (orderId, status) => api.put(`/orders/${orderId}/status`, { status }),
};

export const messagesAPI = {
  getConversations: (userId) => api.get(`/messages/conversations/${userId}`),
  getConversation: (userId, partnerId) => api.get(`/messages/conversation/${userId}/${partnerId}`),
  sendMessage: (senderId, receiverId, content, productId) => 
    api.post('/messages/send', { sender_id: senderId, receiver_id: receiverId, content, product_id: productId }),
  getUnreadCount: (userId) => api.get(`/messages/unread/${userId}`),
};

export const offersAPI = {
  getBuyerOffers: (buyerId) => api.get(`/offers/buyer/${buyerId}`),
  getSellerOffers: (sellerId) => api.get(`/offers/seller/${sellerId}`),
  getPendingCount: (sellerId) => api.get(`/offers/seller/${sellerId}/pending-count`),
  createOffer: (productId, buyerId, offerPrice) => 
    api.post('/offers', { product_id: productId, buyer_id: buyerId, offer_price: offerPrice }),
  respondToOffer: (offerId, action) => api.post(`/offers/${offerId}/respond`, { action }),
}

export const adminAPI = {
  getPendingProducts: () => api.get('/admin/pending-products'),
  getApprovalStats: () => api.get('/admin/product-approval-stats'),
  approveProduct: (productId, govEmployeeId) => 
    api.post(`/admin/product/${productId}/approve`, { gov_employee_id: govEmployeeId }),
  rejectProduct: (productId, govEmployeeId, reason) => 
    api.post(`/admin/product/${productId}/reject`, { gov_employee_id: govEmployeeId, reason }),
  deleteProduct: (productId, govEmployeeId, reason) =>
    api.post(`/admin/product/${productId}/delete`, { gov_employee_id: govEmployeeId, reason }),
};

export default api;

// Main App Component with Routes
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/Common/Toast';
import Navbar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Messages from './pages/Messages';
import SellerDashboard from './pages/SellerDashboard';
import SellerProducts from './pages/SellerProducts';
import SellerProductForm from './pages/SellerProductForm';
import SellerOrders from './pages/SellerOrders';
import SellerOffers from './pages/SellerOffers';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import MyOrders from './pages/MyOrders';
import TrackOrder from './pages/TrackOrder';

import './App.css';

// Placeholder components for routes not yet implemented
const Placeholder = ({ title }) => (
  <div className="container" style={{ padding: '4rem 0', textAlign: 'center' }}>
    <h2>{title}</h2>
    <p>Coming Soon</p>
  </div>
);

function App() {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/products" element={<Products />} />
              
              {/* Routes to be implemented in next phase */}
              <Route path="/products/:id" element={<ProductDetail />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/track-order" element={<TrackOrder />} />
              <Route path="/my-orders" element={<MyOrders />} />
              <Route path="/messages" element={<Messages />} />
              
              {/* Seller Routes */}
              <Route path="/seller/dashboard" element={<SellerDashboard />} />
              <Route path="/seller/products" element={<SellerProducts />} />
              <Route path="/seller/products/new" element={<SellerProductForm />} />
              <Route path="/seller/products/edit/:id" element={<SellerProductForm />} />
              <Route path="/seller/orders" element={<SellerOrders />} />
              <Route path="/seller/offers" element={<SellerOffers />} />
              
              {/* Admin Routes Removed */}
              
              <Route path="*" element={<Placeholder title="404 - Page Not Found" />} />
            </Routes>
          </main>
          <Footer />
        </div>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;

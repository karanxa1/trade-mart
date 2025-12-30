// Navbar Component
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { cartAPI, messagesAPI, offersAPI } from '../../services/api';
import './Navbar.css';

const Navbar = () => {
  const { user, logout, isBuyer, isSeller, isGovt } = useAuth();
  const navigate = useNavigate();
  const [cartCount, setCartCount] = useState(0);
  const [unreadMessages, setUnreadMessages] = useState(0);
  const [pendingOffers, setPendingOffers] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    if (user) {
      fetchCounts();
    }
  }, [user]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownOpen && !event.target.closest('.user-dropdown')) {
        setDropdownOpen(false);
      }
    };

    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dropdownOpen]);

  const fetchCounts = async () => {
    try {
      if (isBuyer) {
        const cartRes = await cartAPI.getCart(user.id);
        setCartCount(cartRes.data.count);
      }
      const msgRes = await messagesAPI.getUnreadCount(user.id);
      setUnreadMessages(msgRes.data.unread_count);
      if (isSeller) {
        const offersRes = await offersAPI.getPendingCount(user.id);
        setPendingOffers(offersRes.data.count);
      }
    } catch (error) {
      console.error('Error fetching counts:', error);
    }
  };

  const handleLogout = () => {
    setDropdownOpen(false);
    logout();
    navigate('/');
  };

  const handleLinkClick = () => {
    setDropdownOpen(false);
  };

  return (
    <nav className="navbar glass-nav">
      <div className="container">
        <Link to="/" className="navbar-brand">
          <span className="brand-text">Trade Mart</span>
        </Link>

        <button className="mobile-toggle" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          <i className={`fas ${mobileMenuOpen ? 'fa-times' : 'fa-bars'}`}></i>
        </button>

        <div className={`navbar-menu ${mobileMenuOpen ? 'active' : ''}`}>
          <ul className="nav-links">
            {isSeller ? (
              <>
                <li><Link to="/seller/dashboard">Dashboard</Link></li>
                <li><Link to="/seller/products">My Products</Link></li>
                <li><Link to="/seller/orders">Orders</Link></li>
                <li>
                  <Link to="/seller/offers" className="badge-link">
                    Offers
                    {pendingOffers > 0 && <span className="badge">{pendingOffers}</span>}
                  </Link>
                </li>
                <li>
                  <Link to="/messages" className="badge-link">
                    Messages
                    {unreadMessages > 0 && <span className="badge">{unreadMessages}</span>}
                  </Link>
                </li>
              </>
            ) : (
              <>
                <li><Link to="/">Home</Link></li>
                <li><Link to="/products">Products</Link></li>
                <li><Link to="/track-order">Track Order</Link></li>
              </>
            )}
          </ul>

          <div className="nav-actions">
            {isBuyer && (
              <Link to="/cart" className="cart-btn">
                <i className="fas fa-shopping-cart"></i>
                {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
              </Link>
            )}

            {user ? (
              <div className="user-dropdown">
                <button className="dropdown-toggle" onClick={() => setDropdownOpen(!dropdownOpen)}>
                  <i className="fas fa-user"></i> {user.username}
                </button>
                {dropdownOpen && (
                  <div className="dropdown-menu">
                    {!isSeller && (
                      <>
                        <Link to="/my-orders" onClick={handleLinkClick}>My Orders</Link>
                        <Link to="/my-offers" onClick={handleLinkClick}>My Offers</Link>
                        <Link to="/messages" onClick={handleLinkClick}>Messages</Link>
                      </>
                    )}
                    {isSeller && (
                      <>
                        <Link to="/seller/dashboard" onClick={handleLinkClick}>Seller Dashboard</Link>
                        <Link to="/seller/products" onClick={handleLinkClick}>My Products</Link>
                      </>
                    )}
                    <hr />
                    <button onClick={handleLogout}>Logout</button>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline">Login</Link>
                <Link to="/register" className="btn btn-primary">Register</Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

// Footer Component
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-section">
            <h5>Trade Mart</h5>
            <p>Trade Mart – A Government-Approved Marketplace for Safe Buying & Selling</p>
          </div>

          <div className="footer-section">
            <h5>Quick Links</h5>
            <ul>
              <li><Link to="/">Home</Link></li>
              <li><Link to="/products">Products</Link></li>
              <li><Link to="/about">About Us</Link></li>
              <li><Link to="/contact">Contact</Link></li>
            </ul>
          </div>

          <div className="footer-section">
            <h5>Categories</h5>
            <ul>
              <li><Link to="/products?category=1">Electronics</Link></li>
              <li><Link to="/products?category=2">Books</Link></li>
              <li><Link to="/products?category=3">Furniture</Link></li>
              <li><Link to="/products?category=4">Tools</Link></li>
            </ul>
          </div>

          <div className="footer-section">
            <h5>Contact Info</h5>
            <ul className="contact-info">
              <li><i className="fas fa-map-marker-alt"></i> 123 Trade Street, Market City</li>
              <li><i className="fas fa-phone"></i> +91 7276640676</li>
              <li><i className="fas fa-envelope"></i> support@trademart.com</li>
            </ul>
            <div className="social-icons">
              <a href="#"><i className="fab fa-facebook-f"></i></a>
              <a href="#"><i className="fab fa-twitter"></i></a>
              <a href="#"><i className="fab fa-instagram"></i></a>
              <a href="#"><i className="fab fa-pinterest"></i></a>
            </div>
          </div>
        </div>

        <hr />
        <div className="footer-bottom">
          <p>© 2024 Trade Mart. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

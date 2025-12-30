// Home Page
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productsAPI } from '../services/api';
import ProductCard from '../components/Product/ProductCard';
import './Home.css';

const Home = () => {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [productsRes, categoriesRes] = await Promise.all([
        productsAPI.getFeatured(8),
        productsAPI.getCategories()
      ]);
      setFeaturedProducts(productsRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const categoryIcons = {
    'Electronics': 'fa-laptop',
    'Books': 'fa-book',
    'Furniture': 'fa-couch',
    'Tools': 'fa-tools',
    'Vehicles': 'fa-car',
    'Toys': 'fa-gamepad',
    'Clothing': 'fa-tshirt',
    'Home & Garden': 'fa-home'
  };

  return (
    <div className="home">
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <h1>Find Great Deals on Used Items</h1>
              <p>Buy and sell second-hand products directly from other users. From electronics to furniture, find everything you need at affordable prices.</p>
              <div className="hero-buttons">
                <Link to="/products" className="btn btn-primary btn-lg">Browse Products</Link>
                <Link to="/register" className="btn btn-outline btn-lg">Register Now</Link>
              </div>
            </div>
            <div className="hero-image">
              <div className="logo-container">
                <img src="/images/trademart-logo.jpg" alt="Trade Mart" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="featured-products">
        <div className="container">
          <div className="section-header">
            <h2>Featured Products</h2>
            <Link to="/products" className="btn btn-outline">View All</Link>
          </div>
          {loading ? (
            <div className="loading">Loading...</div>
          ) : (
            <div className="products-grid">
              {featuredProducts.map(product => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="categories">
        <div className="container">
          <h2>Shop by Category</h2>
          <div className="categories-grid">
            {categories.map(category => (
              <Link to={`/products?category=${category.id}`} key={category.id} className="category-card">
                <i className={`fas ${categoryIcons[category.name] || 'fa-tag'}`}></i>
                <span>{category.name}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <div className="container">
          <h2>How Trade Mart Works</h2>
          <div className="steps-grid">
            <div className="step-card">
              <div className="step-icon">
                <i className="fas fa-sign-in-alt"></i>
              </div>
              <h4>Create an Account</h4>
              <p>Sign up as a buyer or seller to start your second-hand trading journey.</p>
            </div>
            <div className="step-card">
              <div className="step-icon">
                <i className="fas fa-search"></i>
              </div>
              <h4>Find or List Items</h4>
              <p>Browse items to buy or list your own products for sale at your preferred price.</p>
            </div>
            <div className="step-card">
              <div className="step-icon">
                <i className="fas fa-handshake"></i>
              </div>
              <h4>Make Deals</h4>
              <p>Negotiate prices, communicate with other users, and complete your transaction.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="testimonials">
        <div className="container">
          <h2>What Our Users Say</h2>
          <div className="testimonial-card">
            <i className="fas fa-quote-left"></i>
            <p>"I sold my old laptop within days of listing it! The negotiation feature made it easy to agree on a fair price with the buyer."</p>
            <div className="testimonial-author">
              <h5>David Wilson</h5>
              <div className="stars">
                <i className="fas fa-star"></i>
                <i className="fas fa-star"></i>
                <i className="fas fa-star"></i>
                <i className="fas fa-star"></i>
                <i className="fas fa-star"></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container">
          <div className="cta-card">
            <h2>Ready to Start Trading?</h2>
            <p>Join thousands of users buying and selling second-hand items on Trade Mart today!</p>
            <div className="cta-buttons">
              <Link to="/register?user_type=seller" className="btn btn-light btn-lg">Become a Seller</Link>
              <Link to="/register?user_type=buyer" className="btn btn-outline-light btn-lg">Join as Buyer</Link>
            </div>
          </div>
        </div>
      </section>

      <section className="govt-approval">
        <div className="container">
          <h2>Trade Mart – A Government-Approved Marketplace for Safe Buying & Selling</h2>
          <p>Trade Mart is a secure, government-approved online platform where users can buy and sell products with confidence. Whether you're looking to sell pre-owned items, shop for great deals, or connect with genuine buyers and sellers, Trade Mart provides a seamless and trustworthy experience. With strict verification processes and advanced security measures, we ensure a safe and hassle-free marketplace for everyone. Trade smart, trade safe – only on Trade Mart!</p>
        </div>
      </section>
    </div>
  );
};

export default Home;

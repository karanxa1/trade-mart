// Register Page
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import './Auth.css';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    address: '',
    user_type: 'buyer'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleModalOpen, setGoogleModalOpen] = useState(false);
  
  const { register, googleLogin } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      toast.error('Passwords do not match');
      return;
    }
    
    setError('');
    setLoading(true);
    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        phone: formData.phone,
        address: formData.address,
        user_type: formData.user_type
      });
      toast.success('Account created successfully!');
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to register. Please try again.');
      toast.error('Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async (type) => {
    try {
      setGoogleModalOpen(false);
      await googleLogin(type);
      toast.success('Account created successfully!');
      navigate('/');
    } catch (err) {
      setError('Google registration failed. Please try again.');
      toast.error('Google registration failed');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Create Account</h2>
          <p>Join Trade Mart today</p>
        </div>
        
        {error && <div className="alert alert-danger">{error}</div>}
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>I want to:</label>
            <select 
              name="user_type" 
              value={formData.user_type} 
              onChange={handleChange}
              className="form-control"
            >
              <option value="buyer">Buy Items (Buyer)</option>
              <option value="seller">Sell Items (Seller)</option>
            </select>
          </div>

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Choose a username"
            />
          </div>

          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Create a password"
            />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              placeholder="Confirm your password"
            />
          </div>

          <div className="form-group">
            <label>Phone Number</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              placeholder="Enter your phone number"
            />
          </div>

          <div className="form-group">
            <label>Address</label>
            <textarea
              name="address"
              value={formData.address}
              onChange={handleChange}
              required
              placeholder="Enter your full address"
              rows="2"
            ></textarea>
          </div>
          
          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <div className="auth-divider">
          <span>OR</span>
        </div>

        <button onClick={() => setGoogleModalOpen(true)} className="btn btn-google btn-block">
          <img src="/images/google-icon.png" alt="Google" onError={(e) => {e.target.style.display='none'}} /> 
          <i className="fab fa-google" style={{marginRight: '8px'}}></i> Continue with Google
        </button>

        <div className="auth-footer">
          <p>Already have an account? <Link to="/login">Login here</Link></p>
        </div>
      </div>

      {googleModalOpen && (
        <div className="modal-overlay" onClick={() => setGoogleModalOpen(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h3>Select Account Type</h3>
            <div className="modal-actions">
              <button onClick={() => handleGoogleLogin('buyer')} className="btn btn-primary btn-block">
                Continue as Buyer
              </button>
              <button onClick={() => handleGoogleLogin('seller')} className="btn btn-outline btn-block">
                Continue as Seller
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Register;

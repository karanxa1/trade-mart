// Seller Product Form (Add/Edit)
import { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { productsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../components/Common/Toast';
import './SellerProductForm.css';

const SellerProductForm = () => {
  const { user, isSeller } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const { id } = useParams(); // If ID exists, we are in edit mode
  const isEditMode = !!id;

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category_id: '',
    condition_id: '',
    negotiable: false
  });
  const [imageFile, setImageFile] = useState(null);
  const [currentImage, setCurrentImage] = useState(null);
  const [categories, setCategories] = useState([]);
  const [conditions, setConditions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  useEffect(() => {
    if (!user || !isSeller) {
      navigate('/login');
      return;
    }
    fetchInitialData();
  }, [user, isSeller, navigate, id]);

  const fetchInitialData = async () => {
    try {
      const [catRes, condRes] = await Promise.all([
        productsAPI.getCategories(),
        productsAPI.getConditions()
      ]);
      setCategories(catRes.data);
      setConditions(condRes.data);

      if (isEditMode) {
        const productRes = await productsAPI.getProduct(id);
        const product = productRes.data;
        if (product.seller_id !== user.id) {
          toast.error("You don't have permission to edit this product");
          navigate('/seller/products');
          return;
        }
        setFormData({
          name: product.name,
          description: product.description,
          price: product.price,
          category_id: product.category_id,
          condition_id: product.condition_id,
          negotiable: product.negotiable
        });
        setCurrentImage(product.image);
      }
    } catch (err) {
      console.error('Error fetching initial data:', err);
      toast.error('Failed to load form data');
    } finally {
      setInitialLoading(false);
    }
  };

  const handleChange = (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setFormData({
      ...formData,
      [e.target.name]: value
    });
  };

  const handleImageChange = (e) => {
    if (e.target.files[0]) {
      setImageFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isEditMode) {
        const updateData = { ...formData };
        await productsAPI.updateProduct(id, updateData);
        toast.success('Product updated successfully!');
      } else {
        const data = new FormData();
        data.append('name', formData.name);
        data.append('description', formData.description);
        data.append('price', formData.price);
        data.append('category_id', formData.category_id);
        data.append('condition_id', formData.condition_id);
        data.append('negotiable', formData.negotiable);
        data.append('seller_id', user.id);
        if (imageFile) {
          data.append('image', imageFile);
        }

        await productsAPI.createProduct(data);
        toast.success('Product created successfully!');
      }
      navigate('/seller/products');
    } catch (err) {
      console.error('Error saving product:', err);
      toast.error('Failed to save product: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) return <div className="loading">Loading form...</div>;

  return (
    <div className="product-form-page">
      <div className="container">
        <h1>{isEditMode ? 'Edit Product' : 'Add New Product'}</h1>
        
        <form onSubmit={handleSubmit} className="product-form">
          <div className="form-group">
            <label>Product Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="e.g. iPhone 12 Pro Max"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Category</label>
              <select name="category_id" value={formData.category_id} onChange={handleChange} required>
                <option value="">Select Category</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label>Condition</label>
              <select name="condition_id" value={formData.condition_id} onChange={handleChange} required>
                <option value="">Select Condition</option>
                {conditions.map(cond => (
                  <option key={cond.id} value={cond.id}>{cond.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Price (₹)</label>
              <input
                type="number"
                name="price"
                value={formData.price}
                onChange={handleChange}
                required
                min="0"
              />
            </div>
            
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="negotiable"
                  checked={formData.negotiable}
                  onChange={handleChange}
                />
                Open to Negotiation
              </label>
            </div>
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="5"
              required
              placeholder="Describe your product..."
            ></textarea>
          </div>

          {!isEditMode && (
             <div className="form-group">
               <label>Product Image</label>
               <input
                 type="file"
                 accept="image/*"
                 onChange={handleImageChange}
                 required
               />
               <small>Upload a clear image of your product.</small>
             </div>
          )}
          
          {isEditMode && currentImage && (
             <div className="form-group">
               <label>Current Image</label>
               <div className="current-image-preview">
                 <img src={currentImage.startsWith('http') ? currentImage : `http://localhost:8000/uploads/${currentImage}`} alt="Current" />
                 <p className="note">Image updates are not supported in edit mode currently.</p>
               </div>
             </div>
          )}

          <div className="form-actions">
            <Link to="/seller/products" className="btn btn-outline">Cancel</Link>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Saving...' : (isEditMode ? 'Update Product' : 'Create Product')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SellerProductForm;

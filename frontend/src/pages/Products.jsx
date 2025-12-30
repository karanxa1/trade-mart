// Products Page
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { productsAPI } from '../services/api';
import ProductCard from '../components/Product/ProductCard';
import './Products.css';

const Products = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [conditions, setConditions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: searchParams.get('category') || '',
    condition: '',
    min_price: '',
    max_price: '',
    sort: 'newest',
    q: searchParams.get('q') || ''
  });

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    fetchProducts();
    // Update URL params
    const params = {};
    if (filters.category) params.category = filters.category;
    if (filters.q) params.q = filters.q;
    setSearchParams(params);
  }, [filters]);

  const fetchInitialData = async () => {
    try {
      const [catRes, condRes] = await Promise.all([
        productsAPI.getCategories(),
        productsAPI.getConditions()
      ]);
      setCategories(catRes.data);
      setConditions(condRes.data);
    } catch (error) {
      console.error('Error fetching filters:', error);
    }
  };

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await productsAPI.getProducts(filters);
      setProducts(response.data.products);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchProducts();
  };

  const clearFilters = () => {
    setFilters({
      category: '',
      condition: '',
      min_price: '',
      max_price: '',
      sort: 'newest',
      q: ''
    });
  };

  return (
    <div className="products-page">
      <div className="container">
        <div className="products-layout">
          <aside className="filters-sidebar">
            <div className="sidebar-header">
              <h3>Filters</h3>
              <button onClick={clearFilters} className="clear-btn">Clear All</button>
            </div>

            <div className="filter-group">
              <label>Search</label>
              <form onSubmit={handleSearch}>
                <input
                  type="text"
                  name="q"
                  value={filters.q}
                  onChange={handleFilterChange}
                  placeholder="Search products..."
                  className="search-input"
                />
              </form>
            </div>

            <div className="filter-group">
              <label>Category</label>
              <select name="category" value={filters.category} onChange={handleFilterChange}>
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>Price Range</label>
              <div className="price-inputs">
                <input
                  type="number"
                  name="min_price"
                  value={filters.min_price}
                  onChange={handleFilterChange}
                  placeholder="Min"
                />
                <span>-</span>
                <input
                  type="number"
                  name="max_price"
                  value={filters.max_price}
                  onChange={handleFilterChange}
                  placeholder="Max"
                />
              </div>
            </div>

            <div className="filter-group">
              <label>Condition</label>
              {conditions.map(cond => (
                <div key={cond.id} className="checkbox-item">
                  <input
                    type="radio"
                    name="condition"
                    value={cond.id}
                    checked={filters.condition === cond.id}
                    onChange={handleFilterChange}
                    id={`cond-${cond.id}`}
                  />
                  <label htmlFor={`cond-${cond.id}`}>{cond.name}</label>
                </div>
              ))}
            </div>
          </aside>

          <main className="products-content">
            <div className="products-header">
              <h2>All Products</h2>
              <div className="sort-control">
                <label>Sort by:</label>
                <select name="sort" value={filters.sort} onChange={handleFilterChange}>
                  <option value="newest">Newest First</option>
                  <option value="price_low">Price: Low to High</option>
                  <option value="price_high">Price: High to Low</option>
                </select>
              </div>
            </div>

            {loading ? (
              <div className="loading">Loading products...</div>
            ) : products.length > 0 ? (
              <div className="products-grid">
                {products.map(product => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            ) : (
              <div className="no-results">
                <i className="fas fa-search"></i>
                <p>No products found matching your criteria.</p>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default Products;

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, SlidersHorizontal, Home } from 'lucide-react';
import { propertiesAPI } from '../services/api';
import PropertyCard from '../components/PropertyCard';
import { useAuth } from '../contexts/AuthContext';

export default function PropertiesPage() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    property_type: '',
    city: '',
    min_price: '',
    max_price: '',
    bedrooms: '',
  });
  const [showFilters, setShowFilters] = useState(false);

  const { user, logout } = useAuth();

  useEffect(() => {
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    setLoading(true);
    setError('');

    try {
      const params = {};
      
      if (searchTerm) params.search = searchTerm;
      if (filters.property_type) params.property_type = filters.property_type;
      if (filters.city) params.city = filters.city;
      if (filters.min_price) params.min_price = filters.min_price;
      if (filters.max_price) params.max_price = filters.max_price;
      if (filters.bedrooms) params.bedrooms = filters.bedrooms;

      const response = await propertiesAPI.list(params);
      setProperties(response.data);
    } catch (err) {
      setError('Failed to load properties. Please try again.');
      console.error('Error fetching properties:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchProperties();
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  const clearFilters = () => {
    setFilters({
      property_type: '',
      city: '',
      min_price: '',
      max_price: '',
      bedrooms: '',
    });
    setSearchTerm('');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <Home className="w-8 h-8 text-primary-600" />
              <span className="text-2xl font-bold text-primary-600">SmartSquare</span>
            </Link>

            <div className="flex items-center gap-4">
              {user ? (
                <>
                  <Link to="/dashboard" className="btn-secondary">
                    Dashboard
                  </Link>
                  <button onClick={() => logout()} className="text-gray-600 hover:text-gray-900">
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="text-gray-600 hover:text-gray-900">
                    Login
                  </Link>
                  <Link to="/register" className="btn-primary">
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Header */}
      <div className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4">Find Your Perfect Home</h1>
          <p className="text-primary-100 mb-8">
            Browse {properties.length} verified properties in Ghana
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by location, title..."
                className="w-full pl-12 pr-4 py-3 rounded-lg text-gray-900 focus:ring-2 focus:ring-primary-300 outline-none"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button type="submit" className="bg-white text-primary-600 px-6 py-3 rounded-lg font-medium hover:bg-primary-50 transition-colors">
              Search
            </button>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="bg-white/10 backdrop-blur-sm text-white px-4 py-3 rounded-lg hover:bg-white/20 transition-colors"
            >
              <SlidersHorizontal className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <select
                name="property_type"
                className="input-field"
                value={filters.property_type}
                onChange={handleFilterChange}
              >
                <option value="">All Types</option>
                <option value="APARTMENT">Apartment</option>
                <option value="HOUSE">House</option>
                <option value="STUDIO">Studio</option>
                <option value="ROOM">Room</option>
              </select>

              <input
                type="text"
                name="city"
                placeholder="City"
                className="input-field"
                value={filters.city}
                onChange={handleFilterChange}
              />

              <input
                type="number"
                name="min_price"
                placeholder="Min Price"
                className="input-field"
                value={filters.min_price}
                onChange={handleFilterChange}
              />

              <input
                type="number"
                name="max_price"
                placeholder="Max Price"
                className="input-field"
                value={filters.max_price}
                onChange={handleFilterChange}
              />

              <select
                name="bedrooms"
                className="input-field"
                value={filters.bedrooms}
                onChange={handleFilterChange}
              >
                <option value="">Any Bedrooms</option>
                <option value="1">1 Bedroom</option>
                <option value="2">2 Bedrooms</option>
                <option value="3">3 Bedrooms</option>
                <option value="4">4+ Bedrooms</option>
              </select>
            </div>

            <div className="flex gap-2 mt-4">
              <button onClick={fetchProperties} className="btn-primary">
                Apply Filters
              </button>
              <button onClick={clearFilters} className="btn-secondary">
                Clear All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Properties Grid */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="text-gray-600 mt-4">Loading properties...</p>
          </div>
        ) : error ? (
          <div className="card text-center py-12">
            <p className="text-red-600 mb-4">{error}</p>
            <button onClick={fetchProperties} className="btn-primary">
              Try Again
            </button>
          </div>
        ) : properties.length === 0 ? (
          <div className="card text-center py-12">
            <Home className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No properties found
            </h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your search or filters
            </p>
            <button onClick={clearFilters} className="btn-primary">
              Clear Filters
            </button>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <p className="text-gray-600">
                Showing {properties.length} {properties.length === 1 ? 'property' : 'properties'}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {properties.map((property) => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
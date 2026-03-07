import { Link } from 'react-router-dom';
import { MapPin, Bed, Bath, Home } from 'lucide-react';

export default function PropertyCard({ property }) {
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-GH', {
      style: 'currency',
      currency: property.currency || 'GHS',
    }).format(price);
  };

  return (
    <Link 
      to={`/properties/${property.id}`}
      className="card hover:shadow-xl transition-shadow duration-300 overflow-hidden group"
    >
      {/* Property Image */}
      <div className="relative h-48 bg-gray-200 overflow-hidden">
        {property.primary_image ? (
          <img
            src={property.primary_image}
            alt={property.title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-100 to-primary-200">
            <Home className="w-16 h-16 text-primary-400" />
          </div>
        )}
        
        {/* Property Type Badge */}
        <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium text-gray-700">
          {property.property_type}
        </div>

        {/* Verified Badge */}
        {property.is_verified && (
          <div className="absolute top-3 left-3 bg-green-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1">
            ✓ Verified
          </div>
        )}
      </div>

      {/* Property Details */}
      <div className="p-5">
        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-1 group-hover:text-primary-600 transition-colors">
          {property.title}
        </h3>

        {/* Location */}
        <div className="flex items-center gap-1 text-gray-600 mb-3">
          <MapPin className="w-4 h-4" />
          <span className="text-sm">{property.city}, {property.state}</span>
        </div>

        {/* Features */}
        <div className="flex items-center gap-4 mb-4 text-gray-600">
          <div className="flex items-center gap-1">
            <Bed className="w-4 h-4" />
            <span className="text-sm">{property.bedrooms} Bed</span>
          </div>
          <div className="flex items-center gap-1">
            <Bath className="w-4 h-4" />
            <span className="text-sm">{property.bathrooms} Bath</span>
          </div>
          {property.is_furnished && (
            <span className="text-xs bg-gray-100 px-2 py-1 rounded">Furnished</span>
          )}
        </div>

        {/* Price */}
        <div className="flex items-center justify-between">
          <div>
            <span className="text-2xl font-bold text-primary-600">
              {formatPrice(property.price_per_month)}
            </span>
            <span className="text-gray-500 text-sm">/month</span>
          </div>
          <span className="text-xs text-gray-500">
            {property.view_count || 0} views
          </span>
        </div>
      </div>
    </Link>
  );
}
import {
  Star,
  ShoppingBag,
  User,
  Tag,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useState } from "react";

interface ProductMetadata {
  product_title?: string;
  price?: string;
  average_rating?: number;
  total_reviews?: number;
  shop_name?: string;
  image_url?: string;
  description?: string;
  category?: string;
}

interface ProductMetadataCardProps {
  metadata: ProductMetadata;
}

const ProductMetadataCard = ({ metadata }: ProductMetadataCardProps) => {
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);

  if (!metadata || !metadata.product_title) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
        Product Information
      </h2>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Product Image */}
        {metadata.image_url && (
          <div className="flex-shrink-0">
            <img
              src={metadata.image_url}
              alt={metadata.product_title}
              className="w-full lg:w-48 h-48 object-cover rounded-lg border border-gray-200 dark:border-gray-600"
            />
          </div>
        )}

        {/* Product Details */}
        <div className="flex-1 space-y-4">
          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {metadata.product_title}
          </h3>

          {/* Price */}
          {metadata.price && (
            <div className="flex items-center gap-2">
              <ShoppingBag size={16} className="text-green-600" />
              <span className="text-lg font-bold text-green-600">
                {metadata.price}
              </span>
            </div>
          )}

          {/* Rating and Reviews */}
          <div className="flex items-center gap-4">
            {metadata.average_rating && (
              <div className="flex items-center gap-1">
                <Star size={16} className="text-yellow-500 fill-current" />
                <span className="font-medium text-gray-900 dark:text-white">
                  {metadata.average_rating.toFixed(1)}
                </span>
              </div>
            )}

            {metadata.total_reviews && (
              <span className="text-gray-600 dark:text-gray-400">
                ({metadata.total_reviews.toLocaleString()} reviews)
              </span>
            )}
          </div>

          {/* Shop Name */}
          {metadata.shop_name && (
            <div className="flex items-center gap-2">
              <User size={16} className="text-blue-600" />
              <span className="text-gray-700 dark:text-gray-300">
                {metadata.shop_name}
              </span>
            </div>
          )}

          {/* Category */}
          {metadata.category && (
            <div className="flex items-center gap-2">
              <Tag size={16} className="text-purple-600" />
              <span className="text-gray-700 dark:text-gray-300">
                {metadata.category}
              </span>
            </div>
          )}

          {/* Description */}
          {metadata.description && (
            <div className="mt-4">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                Description
              </h4>
              <div className="text-gray-600 dark:text-gray-400 text-sm">
                <p className={isDescriptionExpanded ? "" : "line-clamp-3"}>
                  {metadata.description}
                </p>
                {metadata.description.length > 200 && (
                  <button
                    onClick={() =>
                      setIsDescriptionExpanded(!isDescriptionExpanded)
                    }
                    className="mt-2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm flex items-center gap-1 transition-colors"
                  >
                    {isDescriptionExpanded ? (
                      <>
                        <ChevronUp className="h-4 w-4" />
                        Show Less
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4" />
                        Show More
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductMetadataCard;

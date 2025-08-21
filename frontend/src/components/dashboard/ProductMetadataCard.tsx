import {
  Package,
  Star,
  DollarSign,
  Tag,
  MessageSquare,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import Card from "../ui/Card";
import { useState } from "react";

interface ProductMetadataCardProps {
  metadata: {
    title: string;
    description: string;
    price: string;
    category: string;
    total_reviews: number;
    average_rating: number;
  };
}

const ProductMetadataCard = ({ metadata }: ProductMetadataCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return "text-green-400";
    if (rating >= 3) return "text-yellow-400";
    return "text-red-400";
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M";
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K";
    }
    return num.toString();
  };

  return (
    <Card className="p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="h-10 w-10 bg-primary-500/10 rounded-lg flex items-center justify-center">
          <Package className="h-5 w-5 text-primary-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Product Overview</h3>
          <p className="text-sm text-gray-400">Basic product information</p>
        </div>
      </div>

      {/* Product Title */}
      <div className="mb-4">
        <h2 className="text-xl font-bold text-white mb-2 line-clamp-2">
          {metadata.title}
        </h2>
        {metadata.description && (
          <div className="text-gray-400 text-sm">
            <p className={isExpanded ? "" : "line-clamp-3"}>
              {metadata.description}
            </p>
            {metadata.description.length > 200 && (
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="mt-2 text-primary-400 hover:text-primary-300 text-xs flex items-center gap-1 transition-colors"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="h-3 w-3" />
                    Show Less
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-3 w-3" />
                    Show More
                  </>
                )}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Price */}
        <div className="bg-gray-800/50 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <DollarSign className="h-4 w-4 text-green-400" />
            <span className="text-xs text-gray-400">Price</span>
          </div>
          <div className="text-lg font-bold text-white">
            {metadata.price || "N/A"}
          </div>
        </div>

        {/* Category */}
        <div className="bg-gray-800/50 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <Tag className="h-4 w-4 text-blue-400" />
            <span className="text-xs text-gray-400">Category</span>
          </div>
          <div className="text-sm font-medium text-white truncate">
            {metadata.category || "N/A"}
          </div>
        </div>

        {/* Rating */}
        <div className="bg-gray-800/50 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <Star className="h-4 w-4 text-yellow-400" />
            <span className="text-xs text-gray-400">Rating</span>
          </div>
          <div
            className={`text-lg font-bold ${getRatingColor(
              metadata.average_rating
            )}`}
          >
            {metadata.average_rating
              ? metadata.average_rating.toFixed(1)
              : "N/A"}
          </div>
        </div>

        {/* Reviews */}
        <div className="bg-gray-800/50 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-1">
            <MessageSquare className="h-4 w-4 text-purple-400" />
            <span className="text-xs text-gray-400">Reviews</span>
          </div>
          <div className="text-lg font-bold text-white">
            {metadata.total_reviews
              ? formatNumber(metadata.total_reviews)
              : "N/A"}
          </div>
        </div>
      </div>

      {/* Performance Indicators */}
      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Performance Score</span>
          <div className="flex items-center space-x-2">
            <div className="w-20 bg-gray-800 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  metadata.average_rating >= 4
                    ? "bg-green-500"
                    : metadata.average_rating >= 3
                    ? "bg-yellow-500"
                    : "bg-red-500"
                }`}
                style={{ width: `${(metadata.average_rating / 5) * 100}%` }}
              />
            </div>
            <span
              className={`font-medium ${getRatingColor(
                metadata.average_rating
              )}`}
            >
              {metadata.average_rating
                ? Math.round((metadata.average_rating / 5) * 100)
                : 0}
              %
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ProductMetadataCard;

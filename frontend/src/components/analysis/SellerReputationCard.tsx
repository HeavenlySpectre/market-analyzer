import {
  Shield,
  Star,
  Users,
  Package,
  Clock,
  TrendingUp,
  Award,
} from "lucide-react";

interface SellerReputation {
  seller_name?: string;
  badges: string[];
  store_rating?: number;
  followers?: number;
  product_count?: number;
  chat_performance?: number;
  on_time_shipping?: number;
  cancellation_rate?: number;
  join_date?: string;
  location?: string;
  processing_time?: string;
  reliability_score: number;
  confidence_score?: number;
  components: Record<string, any>;
  coverage_info?: Record<string, any>;
  score_explanation: string;
  notes: string[];
}

interface SellerReputationCardProps {
  reputation: SellerReputation;
}

const SellerReputationCard = ({ reputation }: SellerReputationCardProps) => {
  if (!reputation) {
    return null;
  }

  // Show card even with minimal data
  const sellerName = reputation.seller_name || "Unknown Seller";

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-500 bg-green-50 dark:bg-green-900/20";
    if (score >= 60)
      return "text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20";
    return "text-red-500 bg-red-50 dark:bg-red-900/20";
  };

  const getBadgeDisplay = (badge: string) => {
    switch (badge) {
      case "OFFICIAL_STORE":
        return {
          text: "Official Store",
          color:
            "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
        };
      case "POWER_MERCHANT_PRO":
        return {
          text: "Power Merchant PRO",
          color:
            "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
        };
      case "POWER_MERCHANT":
        return {
          text: "Power Merchant",
          color:
            "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
        };
      default:
        return {
          text: badge,
          color:
            "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
        };
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
    return num.toString();
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <div className="h-10 w-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
          <Shield className="h-5 w-5 text-blue-500" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Seller Reputation
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Reliability analysis
          </p>
        </div>
      </div>

      {/* Seller Name and Badges */}
      <div className="mb-4">
        <div className="flex items-center gap-3 mb-2">
          <h4 className="text-lg font-medium text-gray-900 dark:text-white">
            {sellerName}
          </h4>
          {reputation.badges.map((badge, index) => {
            const badgeInfo = getBadgeDisplay(badge);
            return (
              <span
                key={index}
                className={`px-2 py-1 text-xs font-medium rounded-full ${badgeInfo.color}`}
              >
                {badgeInfo.text}
              </span>
            );
          })}
        </div>
      </div>

      {/* Reliability Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Reliability Score
          </span>
          <div
            className={`px-3 py-1 rounded-full text-lg font-bold ${getScoreColor(
              reputation.reliability_score
            )}`}
          >
            {reputation.reliability_score}/100
          </div>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              reputation.reliability_score >= 80
                ? "bg-green-500"
                : reputation.reliability_score >= 60
                ? "bg-yellow-500"
                : "bg-red-500"
            }`}
            style={{ width: `${reputation.reliability_score}%` }}
          />
        </div>
        {reputation.score_explanation && (
          <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
            {reputation.score_explanation}
          </p>
        )}
      </div>

      {/* Confidence Score */}
      {reputation.confidence_score !== undefined && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Data Confidence
            </span>
            <div
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                reputation.confidence_score >= 80
                  ? "text-green-600 bg-green-50 dark:bg-green-900/20"
                  : reputation.confidence_score >= 60
                  ? "text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20"
                  : "text-red-600 bg-red-50 dark:bg-red-900/20"
              }`}
            >
              {reputation.confidence_score.toFixed(0)}%
            </div>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
            <div
              className={`h-1.5 rounded-full transition-all duration-300 ${
                reputation.confidence_score >= 80
                  ? "bg-green-500"
                  : reputation.confidence_score >= 60
                  ? "bg-yellow-500"
                  : "bg-red-500"
              }`}
              style={{ width: `${reputation.confidence_score}%` }}
            />
          </div>
          {reputation.coverage_info?.cap_applied && (
            <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
              Score capped due to{" "}
              {reputation.coverage_info.cap_applied.toLowerCase()}
            </p>
          )}
        </div>
      )}

      {/* Key Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-4">
        {reputation.store_rating && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <Star className="h-4 w-4 text-yellow-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                Rating
              </span>
            </div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {reputation.store_rating.toFixed(1)}/5
            </div>
          </div>
        )}

        {reputation.followers && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <Users className="h-4 w-4 text-blue-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                Reviews
              </span>
            </div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {formatNumber(reputation.followers)}
            </div>
          </div>
        )}

        {reputation.product_count && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <Package className="h-4 w-4 text-green-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                Products
              </span>
            </div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {formatNumber(reputation.product_count)}
            </div>
          </div>
        )}

        {reputation.processing_time && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <Clock className="h-4 w-4 text-purple-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                Processing
              </span>
            </div>
            <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {reputation.processing_time}
            </div>
          </div>
        )}

        {reputation.chat_performance && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <TrendingUp className="h-4 w-4 text-indigo-500" />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                Chat Perf
              </span>
            </div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {reputation.chat_performance}%
            </div>
          </div>
        )}

        {reputation.on_time_shipping && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <Award className="h-4 w-4 text-green-600" />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                On-time
              </span>
            </div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {reputation.on_time_shipping}%
            </div>
          </div>
        )}

        {reputation.location && (
          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3">
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-xs text-gray-600 dark:text-gray-400">
                Location
              </span>
            </div>
            <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {reputation.location}
            </div>
          </div>
        )}
      </div>

      {/* Notes */}
      {reputation.notes && reputation.notes.length > 0 && (
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Note: {reputation.notes.join(", ")}
          </p>
        </div>
      )}

      {/* Disclaimer */}
      <div className="pt-4 border-t border-gray-200 dark:border-gray-700 mt-4">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Metrics depend on what Tokopedia displays publicly and may be
          incomplete.
        </p>
      </div>
    </div>
  );
};

export default SellerReputationCard;

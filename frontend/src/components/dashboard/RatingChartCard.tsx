import { TrendingUp, Star } from "lucide-react";
import Card from "../ui/Card";

interface RatingChartCardProps {
  sentimentAnalysis: {
    positive: number;
    negative: number;
    neutral: number;
  };
  overallRating: number;
}

const RatingChartCard = ({
  sentimentAnalysis,
  overallRating,
}: RatingChartCardProps) => {
  const { positive, negative, neutral } = sentimentAnalysis;
  const total = positive + negative + neutral;

  const getPercentage = (value: number) => {
    return total > 0 ? Math.round((value / total) * 100) : 0;
  };

  const sentimentData = [
    {
      label: "Positive",
      value: positive,
      percentage: getPercentage(positive),
      color: "bg-green-500",
      lightColor: "bg-green-500/20",
    },
    {
      label: "Neutral",
      value: neutral,
      percentage: getPercentage(neutral),
      color: "bg-yellow-500",
      lightColor: "bg-yellow-500/20",
    },
    {
      label: "Negative",
      value: negative,
      percentage: getPercentage(negative),
      color: "bg-red-500",
      lightColor: "bg-red-500/20",
    },
  ];

  const getRatingColor = (rating: number) => {
    if (rating >= 4) return "text-green-400";
    if (rating >= 3) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <Card className="p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="h-10 w-10 bg-primary-500/10 rounded-lg flex items-center justify-center">
          <TrendingUp className="h-5 w-5 text-primary-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">
            Sentiment Analysis
          </h3>
          <p className="text-sm text-gray-400">Customer sentiment breakdown</p>
        </div>
      </div>

      {/* Overall Rating */}
      <div className="mb-6 p-4 bg-gray-800/50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-gray-300">Overall Rating</span>
          <div className="flex items-center space-x-2">
            <Star className={`h-5 w-5 ${getRatingColor(overallRating)}`} />
            <span
              className={`text-xl font-bold ${getRatingColor(overallRating)}`}
            >
              {overallRating.toFixed(1)}
            </span>
          </div>
        </div>
      </div>

      {/* Sentiment Bars */}
      <div className="space-y-4">
        {sentimentData.map((item, index) => (
          <div key={index} className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-300">{item.label}</span>
              <div className="flex items-center space-x-2">
                <span className="text-gray-400">{item.value}</span>
                <span className="text-white font-medium">
                  {item.percentage}%
                </span>
              </div>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div
                className={`${item.color} h-2 rounded-full transition-all duration-500`}
                style={{ width: `${item.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-4 border-t border-gray-800">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-white">{total}</div>
            <div className="text-xs text-gray-400">Total Reviews</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">
              {getPercentage(positive)}%
            </div>
            <div className="text-xs text-gray-400">Satisfaction</div>
          </div>
          <div>
            <div
              className={`text-2xl font-bold ${getRatingColor(overallRating)}`}
            >
              {overallRating.toFixed(1)}
            </div>
            <div className="text-xs text-gray-400">Avg Rating</div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default RatingChartCard;

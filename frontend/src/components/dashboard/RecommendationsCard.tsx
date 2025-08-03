import { Lightbulb, CheckCircle } from "lucide-react";
import Card from "../ui/Card";

interface RecommendationsCardProps {
  recommendations: string[];
}

const RecommendationsCard = ({ recommendations }: RecommendationsCardProps) => {
  return (
    <Card className="p-6">
      <div className="flex items-center space-x-3 mb-4">
        <div className="h-10 w-10 bg-primary-500/10 rounded-lg flex items-center justify-center">
          <Lightbulb className="h-5 w-5 text-primary-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Recommendations</h3>
          <p className="text-sm text-gray-400">
            AI-generated improvement suggestions
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {recommendations.map((recommendation, index) => (
          <div
            key={index}
            className="flex items-start space-x-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700/50 hover:border-primary-500/30 transition-colors"
          >
            <CheckCircle className="h-5 w-5 text-green-400 mt-0.5 flex-shrink-0" />
            <p className="text-gray-300 text-sm leading-relaxed">
              {recommendation}
            </p>
          </div>
        ))}
      </div>

      {recommendations.length === 0 && (
        <div className="text-center py-8">
          <Lightbulb className="h-12 w-12 text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400">No recommendations available</p>
        </div>
      )}

      {recommendations.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-800">
          <p className="text-xs text-gray-500 text-center">
            {recommendations.length} improvement suggestions generated
          </p>
        </div>
      )}
    </Card>
  );
};

export default RecommendationsCard;

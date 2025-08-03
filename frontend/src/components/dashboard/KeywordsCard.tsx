import { Tag } from "lucide-react";
import Card from "../ui/Card";

interface KeywordsCardProps {
  keywords: string[];
}

const KeywordsCard = ({ keywords }: KeywordsCardProps) => {
  const getKeywordColor = (index: number) => {
    const colors = [
      "bg-primary-500/10 text-primary-400 border-primary-500/20",
      "bg-purple-500/10 text-purple-400 border-purple-500/20",
      "bg-green-500/10 text-green-400 border-green-500/20",
      "bg-orange-500/10 text-orange-400 border-orange-500/20",
      "bg-pink-500/10 text-pink-400 border-pink-500/20",
      "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    ];
    return colors[index % colors.length];
  };

  return (
    <Card className="p-6">
      <div className="flex items-center space-x-3 mb-4">
        <div className="h-10 w-10 bg-primary-500/10 rounded-lg flex items-center justify-center">
          <Tag className="h-5 w-5 text-primary-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Key Topics</h3>
          <p className="text-sm text-gray-400">
            Most mentioned themes in reviews
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {keywords.map((keyword, index) => (
          <span
            key={index}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border ${getKeywordColor(
              index
            )} transition-all hover:scale-105`}
          >
            {keyword}
          </span>
        ))}
      </div>

      {keywords.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-400">No keywords extracted</p>
        </div>
      )}
    </Card>
  );
};

export default KeywordsCard;

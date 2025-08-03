import { FileText } from "lucide-react";
import Card from "../ui/Card";

interface SummaryCardProps {
  summary: string;
}

const SummaryCard = ({ summary }: SummaryCardProps) => {
  return (
    <Card className="p-6">
      <div className="flex items-center space-x-3 mb-4">
        <div className="h-10 w-10 bg-primary-500/10 rounded-lg flex items-center justify-center">
          <FileText className="h-5 w-5 text-primary-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">
            Executive Summary
          </h3>
          <p className="text-sm text-gray-400">AI-generated product overview</p>
        </div>
      </div>

      <div className="prose prose-invert max-w-none">
        <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
          {summary}
        </p>
      </div>
    </Card>
  );
};

export default SummaryCard;

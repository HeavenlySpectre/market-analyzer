import { motion } from "framer-motion";
import SummaryCard from "./SummaryCard";
import KeywordsCard from "./KeywordsCard";
import RatingChartCard from "./RatingChartCard";
import RecommendationsCard from "./RecommendationsCard";
import ProductMetadataCard from "./ProductMetadataCard";

interface AnalysisResult {
  summary: string;
  keywords: string[];
  rating: number;
  sentiment_analysis: {
    positive: number;
    negative: number;
    neutral: number;
  };
  recommendations: string[];
  metadata: {
    title: string;
    description: string;
    price: string;
    category: string;
    total_reviews: number;
    average_rating: number;
  };
}

interface AnalysisDashboardProps {
  result: AnalysisResult;
}

const AnalysisDashboard = ({ result }: AnalysisDashboardProps) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Analysis Results</h1>
        <p className="text-gray-400">
          Comprehensive insights from AI-powered marketplace analysis
        </p>
      </motion.div>

      {/* Product Metadata */}
      <motion.div variants={itemVariants}>
        <ProductMetadataCard metadata={result.metadata} />
      </motion.div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-6">
          <motion.div variants={itemVariants}>
            <SummaryCard summary={result.summary} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <KeywordsCard keywords={result.keywords} />
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <motion.div variants={itemVariants}>
            <RatingChartCard
              sentimentAnalysis={result.sentiment_analysis}
              overallRating={result.rating}
            />
          </motion.div>

          <motion.div variants={itemVariants}>
            <RecommendationsCard recommendations={result.recommendations} />
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default AnalysisDashboard;

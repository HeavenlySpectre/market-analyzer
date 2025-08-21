import { useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import AnalysisForm from "../components/analysis/AnalysisForm";
import LoadingIndicator from "../components/analysis/LoadingIndicator";
import ProductMetadataCard from "../components/analysis/ProductMetadataCard";
import SellerReputationCard from "../components/analysis/SellerReputationCard";
import Chat from "../components/Chat";
import ReactMarkdown from "react-markdown";

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
  components: Record<string, any>;
  score_explanation: string;
  notes: string[];
}

interface AnalysisResult {
  message: string;
  summary: string;
  product_metadata?: ProductMetadata;
  seller_reputation?: SellerReputation;
  chart_data: {
    rating_distribution: Array<{ [key: string]: number }>;
    positive_keywords: Array<{ [key: string]: any }>;
    negative_keywords: Array<{ [key: string]: any }>;
  };
}

const DashboardPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [chatMessages, setChatMessages] = useState<
    Array<{ role: "user" | "assistant"; content: string }>
  >([]);

  const handleAnalysisSubmit = async (submittedUrl: string) => {
    setIsLoading(true);
    setAnalysisResult(null);
    setChatMessages([]);

    try {
      const apiBaseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${apiBaseUrl}/api/v1/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: submittedUrl }),
      });

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      const result = await response.json();
      setAnalysisResult(result);
    } catch (error) {
      console.error("Analysis error:", error);
      // Handle error - you might want to show an error message to the user
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!analysisResult) return;

    const newMessages = [
      ...chatMessages,
      { role: "user" as const, content: message },
    ];
    setChatMessages(newMessages);

    try {
      const apiBaseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${apiBaseUrl}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: message, // Changed from 'message' to 'query' to match backend
          product_metadata: analysisResult.product_metadata, // Include product metadata
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const result = await response.json();
      setChatMessages([
        ...newMessages,
        { role: "assistant", content: result.answer }, // Changed from 'response' to 'answer'
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      // Handle error
    }
  };

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 flex overflow-hidden">
        {/* Main Content Area */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
            {!analysisResult && !isLoading && (
              <AnalysisForm onSubmit={handleAnalysisSubmit} />
            )}

            {isLoading && <LoadingIndicator />}

            {analysisResult && !isLoading && (
              <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div className="mb-8">
                  <h1 className="text-3xl font-bold text-white mb-2">
                    Analysis Complete
                  </h1>
                  <p className="text-green-400 text-sm">
                    {analysisResult.message}
                  </p>
                </div>

                {/* Product Metadata Card */}
                {analysisResult.product_metadata && (
                  <ProductMetadataCard
                    metadata={analysisResult.product_metadata}
                  />
                )}

                {/* Seller Reputation Card */}
                {analysisResult.seller_reputation && (
                  <SellerReputationCard
                    reputation={analysisResult.seller_reputation}
                  />
                )}

                {/* Main Grid Layout */}
                <div className="grid lg:grid-cols-3 gap-6">
                  {/* Left Column - Summary (2/3 width) */}
                  <div className="lg:col-span-2 space-y-6">
                    {/* Summary Card */}
                    <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
                      <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
                        <svg
                          className="w-5 h-5 text-blue-400 mr-2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                        Executive Summary
                      </h2>
                      <div className="prose prose-invert prose-sm max-w-none text-gray-100">
                        <ReactMarkdown
                          components={{
                            p: ({ children }) => (
                              <p className="text-gray-100 mb-4 leading-relaxed">
                                {children}
                              </p>
                            ),
                            h1: ({ children }) => (
                              <h1 className="text-white text-xl font-bold mb-3">
                                {children}
                              </h1>
                            ),
                            h2: ({ children }) => (
                              <h2 className="text-white text-lg font-semibold mb-2">
                                {children}
                              </h2>
                            ),
                            h3: ({ children }) => (
                              <h3 className="text-white text-base font-medium mb-2">
                                {children}
                              </h3>
                            ),
                            strong: ({ children }) => (
                              <strong className="text-white font-semibold">
                                {children}
                              </strong>
                            ),
                            ul: ({ children }) => (
                              <ul className="text-gray-100 list-disc list-inside mb-4 space-y-1">
                                {children}
                              </ul>
                            ),
                            li: ({ children }) => (
                              <li className="text-gray-100">{children}</li>
                            ),
                          }}
                        >
                          {analysisResult.summary}
                        </ReactMarkdown>
                      </div>
                    </div>

                    {/* Rating Distribution */}
                    <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
                      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                        <svg
                          className="w-5 h-5 text-yellow-400 mr-2"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                        Rating Distribution
                      </h3>
                      <div className="space-y-3">
                        {analysisResult.chart_data.rating_distribution.map(
                          (item, index) => (
                            <div
                              key={index}
                              className="flex items-center space-x-3"
                            >
                              <span className="text-sm text-gray-300 w-12">
                                {item.stars} ⭐
                              </span>
                              <div className="flex-1 bg-gray-800 rounded-full h-3">
                                <div
                                  className="bg-gradient-to-r from-yellow-500 to-orange-500 h-3 rounded-full transition-all duration-500"
                                  style={{
                                    width: `${
                                      (item.count /
                                        Math.max(
                                          ...analysisResult.chart_data.rating_distribution.map(
                                            (r) => r.count
                                          )
                                        )) *
                                      100
                                    }%`,
                                  }}
                                />
                              </div>
                              <span className="text-sm text-white font-medium w-8">
                                {item.count}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column - Keywords (1/3 width) */}
                  <div className="space-y-6">
                    {/* Positive Keywords */}
                    <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
                      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                        <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                        Positive Keywords
                      </h3>
                      <div className="space-y-2">
                        {analysisResult.chart_data.positive_keywords
                          .slice(0, 5)
                          .map((keyword, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
                            >
                              <span className="text-sm text-gray-300">
                                {keyword.text}
                              </span>
                              <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded-full">
                                {keyword.value}
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>

                    {/* Key Mentions */}
                    <div className="bg-gray-900 rounded-lg border border-gray-800 p-6">
                      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                        <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                        Key Mentions
                      </h3>
                      <div className="space-y-2">
                        {analysisResult.chart_data.negative_keywords
                          .slice(0, 5)
                          .map((keyword, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
                            >
                              <span className="text-sm text-gray-300">
                                {keyword.text}
                              </span>
                              <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full">
                                {keyword.value}
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Chat Sidebar - Only show when analysis exists */}
        {analysisResult && (
          <div className="w-80 border-l border-gray-800 flex-shrink-0">
            <Chat
              messages={chatMessages}
              onSendMessage={handleSendMessage}
              disabled={isLoading}
            />
          </div>
        )}
      </main>
    </div>
  );
};

export default DashboardPage;

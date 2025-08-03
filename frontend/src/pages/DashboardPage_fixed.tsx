import { useState } from "react";
import Sidebar from "../components/layout/Sidebar";
import AnalysisForm from "../components/analysis/AnalysisForm";
import LoadingIndicator from "../components/analysis/LoadingIndicator";
import AnalysisDashboard from "../components/dashboard/AnalysisDashboard";
import Chat from "../components/Chat";

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

const DashboardPage = () => {
  const [url, setUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [chatMessages, setChatMessages] = useState<
    Array<{ role: "user" | "assistant"; content: string }>
  >([]);

  const handleAnalysisSubmit = async (submittedUrl: string) => {
    setUrl(submittedUrl);
    setIsLoading(true);
    setAnalysisResult(null);
    setChatMessages([]);

    try {
      const response = await fetch("http://localhost:8000/api/v1/analyze", {
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
      const response = await fetch("http://localhost:8000/api/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          analysis_result: analysisResult,
          chat_history: newMessages,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const result = await response.json();
      setChatMessages([
        ...newMessages,
        { role: "assistant", content: result.response },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      // Handle error
    }
  };

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 flex">
          {/* Main Content Area */}
          <div className="flex-1 overflow-y-auto">
            <div className="p-6">
              {!analysisResult && !isLoading && (
                <AnalysisForm onSubmit={handleAnalysisSubmit} />
              )}

              {isLoading && <LoadingIndicator />}

              {analysisResult && !isLoading && (
                <AnalysisDashboard result={analysisResult} />
              )}
            </div>
          </div>

          {/* Chat Sidebar */}
          {analysisResult && (
            <div className="w-80 border-l border-gray-800">
              <Chat
                messages={chatMessages}
                onSendMessage={handleSendMessage}
                disabled={isLoading}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;

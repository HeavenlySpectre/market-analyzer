import { useState } from "react";
import { Search, ExternalLink } from "lucide-react";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Card from "../ui/Card";

interface AnalysisFormProps {
  onSubmit: (url: string) => void;
}

const AnalysisForm = ({ onSubmit }: AnalysisFormProps) => {
  const [url, setUrl] = useState("");
  const [isValidUrl, setIsValidUrl] = useState(true);

  const validateUrl = (urlString: string) => {
    try {
      new URL(urlString);
      return true;
    } catch {
      return false;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim()) {
      setIsValidUrl(false);
      return;
    }

    const isValid = validateUrl(url);
    setIsValidUrl(isValid);

    if (isValid) {
      onSubmit(url);
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
    if (!isValidUrl) {
      setIsValidUrl(true);
    }
  };

  const exampleUrls = [
    "https://www.tokopedia.com/velixirparfums/velixir-adonis-eau-de-parfum-for-unisex-1730882164656997590",
    "https://www.tokopedia.com/xiaomi-indonesia/xiaomi-redmi-note-13-8-256gb-midnight-black",
    "https://www.tokopedia.com/unilever/dove-beauty-bar-pink-100gr-4pcs",
  ];

  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-white mb-4 text-balance">
          Marketplace Analytics Pro
        </h1>
        <p className="text-xl text-gray-300 mb-8 text-balance">
          Get deep insights from any marketplace product URL. Analyze reviews,
          sentiment, pricing, and more with AI-powered analytics.
        </p>
      </div>

      {/* Main Form Card */}
      <Card className="p-8 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="url"
              className="block text-sm font-medium text-gray-200 mb-2"
            >
              Product URL
            </label>
            <div className="relative">
              <Input
                id="url"
                type="url"
                placeholder="https://www.tokopedia.com/..."
                value={url}
                onChange={handleUrlChange}
                className={`pl-10 ${
                  !isValidUrl
                    ? "border-red-500 focus:border-red-500 focus:ring-red-500"
                    : ""
                }`}
              />
              <ExternalLink className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            </div>
            {!isValidUrl && (
              <p className="mt-2 text-sm text-red-400">
                Please enter a valid URL
              </p>
            )}
          </div>

          <Button
            type="submit"
            size="lg"
            className="w-full"
            disabled={!url.trim()}
          >
            <Search className="mr-2 h-4 w-4" />
            Analyze Product
          </Button>
        </form>
      </Card>

      {/* Example URLs */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Try these example URLs:
        </h3>
        <div className="space-y-2">
          {exampleUrls.map((exampleUrl, index) => (
            <button
              key={index}
              onClick={() => setUrl(exampleUrl)}
              className="block w-full text-left p-3 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              {exampleUrl}
            </button>
          ))}
        </div>
      </Card>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-6 mt-8">
        <Card className="p-6 text-center">
          <div className="h-12 w-12 bg-primary-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
            <Search className="h-6 w-6 text-primary-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">
            Smart Analysis
          </h3>
          <p className="text-gray-400 text-sm">
            AI-powered analysis of product reviews, ratings, and market
            positioning
          </p>
        </Card>

        <Card className="p-6 text-center">
          <div className="h-12 w-12 bg-primary-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
            <div className="h-6 w-6 rounded-full bg-gradient-to-r from-green-400 to-primary-400"></div>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">
            Sentiment Insights
          </h3>
          <p className="text-gray-400 text-sm">
            Understand customer sentiment with detailed positive, negative, and
            neutral analysis
          </p>
        </Card>

        <Card className="p-6 text-center">
          <div className="h-12 w-12 bg-primary-500/10 rounded-lg flex items-center justify-center mx-auto mb-4">
            <div className="h-6 w-6 bg-gradient-to-r from-primary-400 to-purple-400 rounded"></div>
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">
            Actionable Recommendations
          </h3>
          <p className="text-gray-400 text-sm">
            Get specific recommendations to improve product performance and
            customer satisfaction
          </p>
        </Card>
      </div>
    </div>
  );
};

export default AnalysisForm;

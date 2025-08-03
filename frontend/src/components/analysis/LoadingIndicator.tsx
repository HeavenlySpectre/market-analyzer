import { motion } from "framer-motion";
import { Loader2, BarChart3, Search, Zap } from "lucide-react";
import Card from "../ui/Card";

const LoadingIndicator = () => {
  const loadingSteps = [
    { label: "Fetching product data", icon: Search, delay: 0 },
    { label: "Analyzing reviews", icon: BarChart3, delay: 0.2 },
    { label: "Processing sentiment", icon: Zap, delay: 0.4 },
    { label: "Generating insights", icon: Loader2, delay: 0.6 },
  ];

  return (
    <div className="max-w-2xl mx-auto">
      <Card className="p-8">
        <div className="text-center mb-8">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="h-16 w-16 mx-auto mb-4"
          >
            <div className="h-16 w-16 border-4 border-primary-500/20 border-t-primary-500 rounded-full"></div>
          </motion.div>

          <h2 className="text-2xl font-bold text-white mb-2">
            Analyzing Product
          </h2>
          <p className="text-gray-400">
            Our AI is processing the product data and reviews...
          </p>
        </div>

        <div className="space-y-4">
          {loadingSteps.map((step, index) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: step.delay, duration: 0.5 }}
                className="flex items-center space-x-3 p-3 rounded-lg bg-gray-800/50"
              >
                <div className="flex-shrink-0">
                  {step.icon === Loader2 ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{
                        duration: 1,
                        repeat: Infinity,
                        ease: "linear",
                      }}
                    >
                      <Icon className="h-5 w-5 text-primary-400" />
                    </motion.div>
                  ) : (
                    <Icon className="h-5 w-5 text-primary-400" />
                  )}
                </div>
                <span className="text-gray-300">{step.label}</span>
                <div className="flex-1 flex justify-end">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: step.delay + 0.3, duration: 0.3 }}
                    className="h-2 w-2 bg-green-400 rounded-full"
                  />
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Progress</span>
            <span>Processing...</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: "100%" }}
              transition={{ duration: 3, ease: "easeInOut" }}
              className="bg-gradient-to-r from-primary-500 to-primary-400 h-2 rounded-full"
            />
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-xs text-gray-500">
            This usually takes 15-30 seconds depending on the product complexity
          </p>
        </div>
      </Card>
    </div>
  );
};

export default LoadingIndicator;

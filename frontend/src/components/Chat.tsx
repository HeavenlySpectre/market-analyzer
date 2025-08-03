import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";
import Button from "./ui/Button";
import Input from "./ui/Input";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const Chat = ({ messages, onSendMessage, disabled = false }: ChatProps) => {
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Simulate typing indicator
    if (messages.length > 0 && messages[messages.length - 1].role === "user") {
      setIsTyping(true);
      const timer = setTimeout(() => setIsTyping(false), 1500);
      return () => clearTimeout(timer);
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;

    onSendMessage(input.trim());
    setInput("");
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-900 border-l border-gray-800">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-primary-500/10 rounded-full flex items-center justify-center">
            <Bot className="h-4 w-4 text-primary-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">AI Assistant</h3>
            <p className="text-xs text-gray-400">
              Ask questions about the analysis
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="h-12 w-12 text-gray-600 mx-auto mb-3" />
            <p className="text-gray-400 text-sm">
              Ask me anything about the product analysis!
            </p>
            <div className="mt-4 space-y-2">
              <button
                onClick={() =>
                  onSendMessage("What are the main strengths of this product?")
                }
                className="block w-full text-left p-2 text-xs text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
                disabled={disabled}
              >
                💪 What are the main strengths?
              </button>
              <button
                onClick={() =>
                  onSendMessage("What do customers complain about most?")
                }
                className="block w-full text-left p-2 text-xs text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
                disabled={disabled}
              >
                ⚠️ What are the main complaints?
              </button>
              <button
                onClick={() =>
                  onSendMessage("How can this product be improved?")
                }
                className="block w-full text-left p-2 text-xs text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
                disabled={disabled}
              >
                💡 How can it be improved?
              </button>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex space-x-3 ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {message.role === "assistant" && (
              <div className="h-6 w-6 bg-primary-500/10 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <Bot className="h-3 w-3 text-primary-400" />
              </div>
            )}

            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.role === "user"
                  ? "bg-primary-500 text-white"
                  : "bg-gray-800 text-gray-200"
              }`}
            >
              {message.role === "assistant" ? (
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => (
                        <p className="text-gray-200 mb-2 leading-relaxed text-sm">
                          {children}
                        </p>
                      ),
                      h1: ({ children }) => (
                        <h1 className="text-white text-base font-bold mb-2">
                          {children}
                        </h1>
                      ),
                      h2: ({ children }) => (
                        <h2 className="text-white text-sm font-semibold mb-2">
                          {children}
                        </h2>
                      ),
                      h3: ({ children }) => (
                        <h3 className="text-white text-sm font-medium mb-1">
                          {children}
                        </h3>
                      ),
                      strong: ({ children }) => (
                        <strong className="text-white font-semibold">
                          {children}
                        </strong>
                      ),
                      ul: ({ children }) => (
                        <ul className="text-gray-200 list-disc list-inside mb-2 space-y-1">
                          {children}
                        </ul>
                      ),
                      li: ({ children }) => (
                        <li className="text-gray-200 text-sm">{children}</li>
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {message.content}
                </p>
              )}
            </div>

            {message.role === "user" && (
              <div className="h-6 w-6 bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                <User className="h-3 w-3 text-gray-300" />
              </div>
            )}
          </div>
        ))}

        {isTyping && (
          <div className="flex space-x-3 justify-start">
            <div className="h-6 w-6 bg-primary-500/10 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
              <Bot className="h-3 w-3 text-primary-400" />
            </div>
            <div className="bg-gray-800 p-3 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                />
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-800">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about the analysis..."
            disabled={disabled}
            className="flex-1"
          />
          <Button
            type="submit"
            size="sm"
            disabled={!input.trim() || disabled}
            className="px-3"
          >
            {disabled ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
      </div>
    </div>
  );
};

export default Chat;

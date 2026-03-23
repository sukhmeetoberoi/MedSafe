import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Trash2, Info, ExternalLink } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const ChatBox = ({ reportIds }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "bot",
      text: "Hello! I've analyzed your medical reports. You can ask me any specific questions about them, such as your lab results, blood sugar levels, or medications. I'll provide answers based strictly on your reports and WHO guidelines.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading || reportIds.length === 0) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      text: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // Build query string for multiple report IDs
      const queryParams = new URLSearchParams();
      queryParams.append("question", userMessage.text);
      reportIds.forEach((id) => queryParams.append("report_ids", id));

      const response = await fetch(`${API_BASE}/api/chat/qa?${queryParams.toString()}`);
      
      if (!response.ok) {
        throw new Error("Failed to get answer from AI.");
      }

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        type: "bot",
        text: data.answer || "I''m sorry, I couldn't find an answer in your reports.",
        disclaimer: data.disclaimer
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          type: "bot",
          text: "I encountered an error while trying to answer your question. Please try again later.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([messages[0]]);
  };

  if (reportIds.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-2xl p-8 text-center">
        <Bot className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-700">Medical Report Chat</h3>
        <p className="text-gray-500">Upload reports above to start a conversation with MedSafe AI.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[600px] bg-white border border-gray-200 rounded-2xl shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-medical-blue p-4 flex items-center justify-between text-white">
        <div className="flex items-center space-x-3">
          <div className="bg-white/20 p-2 rounded-lg">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold">MedSafe AI Assistant</h3>
            <p className="text-xs text-blue-100">{reportIds.length} Reports Loaded</p>
          </div>
        </div>
        <button 
          onClick={clearChat}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          title="Clear Chat"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`flex max-w-[85%] space-x-2 ${msg.type === "user" ? "flex-row-reverse space-x-reverse" : "flex-row"}`}>
              <div className={`p-2 rounded-full h-8 w-8 flex-shrink-0 flex items-center justify-center ${
                msg.type === "user" ? "bg-teal-accent text-white" : "bg-medical-blue text-white"
              }`}>
                {msg.type === "user" ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`p-4 rounded-2xl ${
                msg.type === "user" 
                  ? "bg-medical-blue text-white rounded-tr-none" 
                  : "bg-gray-100 text-gray-800 rounded-tl-none"
              }`}>
                <p className="text-sm whitespace-pre-line leading-relaxed">
                  {msg.text}
                </p>
                {msg.disclaimer && (
                  <div className="mt-3 pt-3 border-t border-gray-200 text-[10px] text-gray-500 italic flex items-start space-x-1">
                    <Info size={12} className="mt-0.5 flex-shrink-0" />
                    <span>{msg.disclaimer}</span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="flex space-x-2">
              <div className="p-2 rounded-full h-8 w-8 bg-medical-blue text-white flex items-center justify-center">
                <Bot size={16} />
              </div>
              <div className="bg-gray-100 p-4 rounded-2xl rounded-tl-none">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Footer / Input */}
      <form onSubmit={handleSend} className="p-4 border-t border-gray-100 bg-gray-50">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your results, e.g., 'What is my glucose level?'"
            className="w-full p-4 pr-12 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-medical-blue bg-white text-sm"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-colors ${
              input.trim() && !loading 
                ? "bg-medical-blue text-white hover:bg-dark-blue-gray" 
                : "bg-gray-100 text-gray-400 cursor-not-allowed"
            }`}
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-[10px] text-gray-400 mt-2 text-center uppercase tracking-wider font-semibold">
          AI generated answers strictly based on your clinical records
        </p>
      </form>
    </div>
  );
};

export default ChatBox;

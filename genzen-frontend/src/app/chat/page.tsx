'use client';
import { useState } from 'react';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    { text: 'How are you feeling today?', sender: 'bot' }
  ]);
  const [inputText, setInputText] = useState('');

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { text: inputText, sender: 'user' }]);
    setInputText('');

    // Simulate bot response (this will be replaced with actual API call)
    setTimeout(() => {
      setMessages(prev => [...prev, {
        text: "I'm here to listen and help. Can you tell me more about what's on your mind?",
        sender: 'bot'
      }]);
    }, 1000);
  };

  return (
    <>
      <h1 className="text-2xl font-semibold mb-6 text-gray-800">Chat</h1>
      
      {/* Messages Container */}
      <div className="bg-white/80 rounded-lg p-4 mb-4 min-h-[500px] shadow-lg">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                  message.sender === 'user'
                    ? 'bg-white text-gray-800 ml-4'
                    : 'bg-gray-100 text-gray-800 mr-4'
                }`}
              >
                {message.sender === 'bot' && (
                  <div className="text-sm text-gray-500 mb-1">GenZen bot</div>
                )}
                <p>{message.text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="flex gap-2">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="How may we help today?"
          className="flex-1 rounded-full px-4 py-2 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-300"
        />
        <button
          type="submit"
          className="bg-white text-gray-800 px-6 py-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-purple-300"
        >
          Send
        </button>
      </form>
    </>
  );
} 
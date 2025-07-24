import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, PanelLeftClose, PanelLeftOpen, History } from "lucide-react";

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const mockMessages: Message[] = [
  {
    id: '1',
    content: 'Hello! I\'m your AI coding assistant. How can I help you build your application today?',
    sender: 'ai',
    timestamp: new Date()
  },
  {
    id: '2',
    content: 'I want to create a beautiful landing page for my startup',
    sender: 'user',
    timestamp: new Date()
  },
  {
    id: '3',
    content: 'Great! I\'ll help you create a modern landing page. Let me start by building a hero section with a clean design and call-to-action buttons. I\'ll use a professional color scheme with gradients.',
    sender: 'ai',
    timestamp: new Date()
  }
];

interface ChatInterfaceProps {
  initialPrompt?: string;
  onCollapse?: () => void;
}

export const ChatInterface = ({ initialPrompt, onCollapse }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [inputValue, setInputValue] = useState('');
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    if (initialPrompt) {
      const userMessage: Message = {
        id: Date.now().toString(),
        content: initialPrompt,
        sender: 'user',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // Simulate AI response to the initial prompt
      setTimeout(() => {
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          content: `Great idea! I'll help you build "${initialPrompt}". Let me start by creating the basic structure and components for your application.`,
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiResponse]);
      }, 1500);
    }
  }, [initialPrompt]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: 'I understand what you need. Let me implement that for you right away!',
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full bg-chat-bg">
      {/* Chat Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-primary rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h3 className="font-medium text-foreground">AI Assistant</h3>
              <p className="text-xs text-muted-foreground">Ready to code</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-1">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setShowHistory(!showHistory)}
              className="w-8 h-8 p-0"
            >
              <History className="w-4 h-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onCollapse}
              className="w-8 h-8 p-0"
            >
              <PanelLeftClose className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Messages */}
      {showHistory && (
        <div className="p-4 border-b border-border bg-muted/20">
          <h4 className="text-sm font-medium text-foreground mb-2">Recent Conversations</h4>
          <div className="space-y-2">
            <Button variant="ghost" size="sm" className="w-full justify-start text-xs">
              Landing page design
            </Button>
            <Button variant="ghost" size="sm" className="w-full justify-start text-xs">
              E-commerce dashboard
            </Button>
            <Button variant="ghost" size="sm" className="w-full justify-start text-xs">
              Portfolio website
            </Button>
          </div>
        </div>
      )}
      
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-[85%] ${
                message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.sender === 'user' 
                    ? 'bg-message-user' 
                    : 'bg-message-ai border border-border'
                }`}>
                  {message.sender === 'user' ? (
                    <User className="w-4 h-4 text-primary-foreground" />
                  ) : (
                    <Bot className="w-4 h-4 text-foreground" />
                  )}
                </div>
                
                <div className={`rounded-lg p-3 ${
                  message.sender === 'user'
                    ? 'bg-message-user text-primary-foreground'
                    : 'bg-message-ai text-foreground border border-border'
                }`}>
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  <p className={`text-xs mt-2 ${
                    message.sender === 'user' 
                      ? 'text-primary-foreground/70' 
                      : 'text-muted-foreground'
                  }`}>
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t border-border">
        <div className="flex space-x-2">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Describe what you want to build..."
            className="flex-1 bg-input border-border"
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <Button 
            onClick={handleSendMessage}
            className="bg-gradient-primary hover:opacity-90 transition-opacity"
            size="sm"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};
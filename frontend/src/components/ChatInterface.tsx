import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, PanelLeftClose, History } from "lucide-react";

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface ChatInterfaceProps {
  initialPrompt?: string;
  chat_id?: string;
  onCollapse?: () => void;
  chatTitle?: string;
}

export const ChatInterface = ({ initialPrompt, chat_id, onCollapse, chatTitle }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentChatTitle, setCurrentChatTitle] = useState<string>(chatTitle || 'New Chat');
  
  // Set default title for new chats
  useEffect(() => {
    if (!chat_id) {
      setCurrentChatTitle('New Chat');
    }
  }, [chat_id]);

      // Fetch chat title and history
    useEffect(() => {
      if (!chat_id) return;
      setLoading(true);
      setError(null);
      
      console.log('Fetching chat data for chat_id:', chat_id);
      
      // Fetch chat history (includes title)
      fetch(`http://127.0.0.1:8000/chat/${chat_id}`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to load');
          return res.json();
        })
        .then(data => {
          console.log('Chat data received:', data);
          // Update chat title from response
          if (data.title) {
            console.log('Setting chat title to:', data.title);
            setCurrentChatTitle(data.title);
          } else {
            console.log('No title in response, using default');
            setCurrentChatTitle('Untitled Chat');
          }
          
          setMessages(
            data.messages.map((msg: any, idx: number) => ({
              id: idx + '',
              content: msg.content,
              sender: msg.role,
              timestamp: new Date()
            }))
          );
          setLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching chat data:', error);
          setError('Failed to load chat history');
          setLoading(false);
        });
    }, [chat_id]);

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputValue.trim() || !chat_id) return;
    setError(null);
    setLoading(true);
    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    setInputValue('');
    try {
      // 流式处理
      const response = await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id, message: inputValue })
      });
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response');
      let aiMsg = '';
      let aiMsgId = Date.now() + '';
      // 先插入空AI消息
      setMessages(prev => [...prev, {
        id: aiMsgId,
        content: '',
        sender: 'ai',
        timestamp: new Date()
      }]);
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        aiMsg += new TextDecoder().decode(value);
        // 流式渲染：每次更新AI消息内容
        setMessages(prev => prev.map(m => m.id === aiMsgId ? { ...m, content: aiMsg } : m));
      }
      // 发送完消息后自动刷新历史
      fetch(`http://127.0.0.1:8000/chat/${chat_id}`)
        .then(res => res.json())
        .then(data => {
          setMessages(
            data.messages.map((msg: any, idx: number) => ({
              id: idx + '',
              content: msg.content,
              sender: msg.role,
              timestamp: new Date()
            }))
          );
        });
    } catch (e) {
      setError('Failed to send message');
    }
    setLoading(false);
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
              <h3 className="font-medium text-foreground">{currentChatTitle}</h3>
              <p className="text-xs text-muted-foreground">
                {chat_id ? `Chat ID: ${chat_id.slice(0, 8)}...` : 'Starting new conversation...'}
              </p>
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
        {loading && <div className="text-muted-foreground text-center py-4">Loading...</div>}
        {error && <div className="text-red-500 text-center py-2">{error}</div>}
        <div className="space-y-4">
          {messages.length === 0 && !loading && !error && (
            <div className="text-muted-foreground text-center py-8">No messages yet. Start the conversation!</div>
          )}
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
            onKeyPress={(e) => e.key === 'Enter' && !loading && handleSendMessage()}
          />
          <Button 
            onClick={handleSendMessage}
            className="bg-gradient-primary hover:opacity-90 transition-opacity"
            size="sm"
            disabled={loading}
          >
            {loading ? '...' : <Send className="w-4 h-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
};
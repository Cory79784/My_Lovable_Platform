import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, 
  MessageSquare, 
  Clock, 
  Trash2, 
  Edit3, 
  Search,
  FolderOpen,
  Code
} from 'lucide-react';

interface ChatSummary {
  chat_id: string;
  title: string;
  last_updated?: string;
  message_count?: number;
  has_project?: boolean;
}

interface WorkspaceManagerProps {
  onSelectChat: (chatId: string) => void;
  onCreateNewChat: () => void;
  className?: string;
}

export const WorkspaceManager: React.FC<WorkspaceManagerProps> = ({
  onSelectChat,
  onCreateNewChat,
  className = ''
}) => {
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [lastChatId, setLastChatId] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch all chats
  const fetchChats = async () => {
    try {
      console.log('Fetching chats...');
      const response = await fetch('http://127.0.0.1:8000/chat/chats');
      if (response.ok) {
        const chatList = await response.json();
        console.log('Received chats:', chatList);
        setChats(chatList);
        
        // Sort chats by last updated time (most recent first)
        const sortedChats = chatList.sort((a, b) => {
          const dateA = new Date(a.last_updated || 0);
          const dateB = new Date(b.last_updated || 0);
          return dateB.getTime() - dateA.getTime();
        });
        setChats(sortedChats);
        console.log('Sorted chats:', sortedChats);
        
        // Set the last chat ID (most recent one)
        if (sortedChats.length > 0) {
          setLastChatId(sortedChats[0].chat_id);
        }
      } else {
        console.error('Failed to fetch chats:', response.status);
      }
    } catch (error) {
      console.error('Error fetching chats:', error);
    } finally {
      setLoading(false);
    }
  };

  // Delete a chat
  const deleteChat = async (chatId: string) => {
    try {
              const response = await fetch(`http://127.0.0.1:8000/chat/${chatId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        setChats(chats.filter(chat => chat.chat_id !== chatId));
      }
    } catch (error) {
      console.error('Error deleting chat:', error);
    }
  };

  // Rename a chat
  const renameChat = async (chatId: string, newTitle: string) => {
    try {
      console.log(`Renaming chat ${chatId} to "${newTitle}"`);
      console.log('Available chats:', chats.map(c => ({ id: c.chat_id, title: c.title })));
              const response = await fetch(`http://127.0.0.1:8000/chat/${chatId}/rename`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Rename successful:', result);
        // Update local state
        setChats(chats.map(chat => 
          chat.chat_id === chatId 
            ? { ...chat, title: newTitle }
            : chat
        ));
        setEditingChatId(null);
        setEditingTitle('');
        
        // Refresh the chat list to ensure consistency
        setTimeout(() => {
          fetchChats();
        }, 100);
      } else {
        const errorData = await response.json();
        console.error('Rename failed:', errorData);
        if (response.status === 404) {
          alert(`Chat not found. The chat may have been deleted or doesn't exist.`);
        } else {
          alert(`Failed to rename chat: ${errorData.detail || 'Unknown error'}`);
        }
      }
    } catch (error) {
      console.error('Error renaming chat:', error);
      alert('Failed to rename chat. Please try again.');
    }
  };

  // Start editing a chat title
  const startEditing = (chat: ChatSummary) => {
    setEditingChatId(chat.chat_id);
    setEditingTitle(chat.title);
  };

  // Save the edited title
  const saveEdit = () => {
    if (editingChatId && editingTitle.trim()) {
      renameChat(editingChatId, editingTitle.trim());
    }
  };

  // Cancel editing
  const cancelEdit = () => {
    setEditingChatId(null);
    setEditingTitle('');
  };

  // Filter chats based on search term
  const filteredChats = chats.filter(chat =>
    chat.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  useEffect(() => {
    fetchChats();
  }, []);

  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">My Lovable Workspace</h1>
          <p className="text-muted-foreground">Manage your chat sessions and projects</p>
        </div>
        <Button onClick={onCreateNewChat} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
        <Input
          placeholder="Search chats..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Chats Grid */}
      {filteredChats.length === 0 ? (
        <div className="text-center py-12">
          <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-foreground mb-2">
            {searchTerm ? 'No chats found' : 'No chats yet'}
          </h3>
          <p className="text-muted-foreground mb-4">
            {searchTerm 
              ? 'Try adjusting your search terms'
              : 'Start your first conversation to see it here'
            }
          </p>
          {!searchTerm && (
            <Button onClick={onCreateNewChat} className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Create Your First Chat
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredChats.map((chat) => (
            <Card 
              key={chat.chat_id} 
              className="hover:shadow-md transition-shadow cursor-pointer group"
              onClick={() => onSelectChat(chat.chat_id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {editingChatId === chat.chat_id ? (
                      <div className="flex items-center gap-2">
                        <Input
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') saveEdit();
                            if (e.key === 'Escape') cancelEdit();
                          }}
                          className="h-8 text-sm"
                          autoFocus
                        />
                        <Button size="sm" onClick={saveEdit} className="h-8 px-2">
                          ✓
                        </Button>
                        <Button size="sm" variant="outline" onClick={cancelEdit} className="h-8 px-2">
                          ✕
                        </Button>
                      </div>
                    ) : (
                      <CardTitle className="text-base truncate">{chat.title}</CardTitle>
                    )}
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        startEditing(chat);
                      }}
                      className="h-6 w-6 p-0"
                    >
                      <Edit3 className="h-3 w-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteChat(chat.chat_id);
                      }}
                      className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="pt-0">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <MessageSquare className="h-3 w-3" />
                    <span>{chat.message_count || 0} messages</span>
                  </div>
                  {chat.has_project && (
                    <Badge variant="secondary" className="text-xs">
                      <Code className="h-3 w-3 mr-1" />
                      Project
                    </Badge>
                  )}
                </div>
                
                {chat.last_updated && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground mt-2">
                    <Clock className="h-3 w-3" />
                    <span>{new Date(chat.last_updated).toLocaleDateString()}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Button 
            variant="outline" 
            className="flex items-center gap-2 h-auto p-4"
            onClick={() => {
              if (lastChatId) {
                navigate('/workspace', { 
                  state: { 
                    chat_id: lastChatId,
                    isExistingChat: true
                  } 
                });
              } else {
                navigate('/workspace');
              }
            }}
            disabled={!lastChatId}
          >
            <FolderOpen className="h-5 w-5" />
            <div className="text-left">
              <div className="font-medium">Open Workspace</div>
              <div className="text-xs text-muted-foreground">
                {lastChatId ? 'Continue your latest work' : 'No chats available'}
              </div>
            </div>
          </Button>
          

          
          <Button 
            variant="outline" 
            className="flex items-center gap-2 h-auto p-4"
            onClick={onCreateNewChat}
          >
            <Plus className="h-5 w-5" />
            <div className="text-left">
              <div className="font-medium">New Project</div>
              <div className="text-xs text-muted-foreground">Start building something new</div>
            </div>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default WorkspaceManager; 
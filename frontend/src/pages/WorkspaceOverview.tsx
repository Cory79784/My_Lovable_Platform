import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WorkspaceManager } from '@/components/WorkspaceManager';
import { Header } from '@/components/Header';

const WorkspaceOverview = () => {
  const navigate = useNavigate();

  const handleSelectChat = (chatId: string) => {
    // Navigate to workspace with the selected chat
    navigate('/workspace', { 
      state: { 
        chat_id: chatId,
        isExistingChat: true
      } 
    });
  };

  const handleCreateNewChat = async () => {
    try {
      // Create new chat via API
      const response = await fetch('http://127.0.0.1:8001/chat/new_chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Created new chat:', data);
        
        // Navigate to workspace with the new chat
        navigate('/workspace', { 
          state: { 
            chat_id: data.chat_id,
            isExistingChat: false,
            isNewChat: true
          } 
        });
      } else {
        console.error('Failed to create new chat');
        alert('Failed to create new chat. Please try again.');
      }
    } catch (error) {
      console.error('Error creating new chat:', error);
      alert('Error creating new chat. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header 
        isChatCollapsed={false}
        onToggleChat={() => {}}
      />
      
      <div className="container mx-auto px-4 py-8">
        <WorkspaceManager
          onSelectChat={handleSelectChat}
          onCreateNewChat={handleCreateNewChat}
        />
      </div>
    </div>
  );
};

export default WorkspaceOverview; 
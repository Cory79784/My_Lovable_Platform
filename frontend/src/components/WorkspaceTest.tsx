import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface TestResult {
  name: string;
  status: 'pending' | 'pass' | 'fail';
  message: string;
}

export const WorkspaceTest: React.FC = () => {
  const [results, setResults] = useState<TestResult[]>([]);
  const [running, setRunning] = useState(false);

  const runTests = async () => {
    setRunning(true);
    setResults([
      { name: 'Backend Connection', status: 'pending', message: 'Testing...' },
      { name: 'Chat Creation', status: 'pending', message: 'Testing...' },
      { name: 'Chat Isolation', status: 'pending', message: 'Testing...' },
      { name: 'Chat Listing', status: 'pending', message: 'Testing...' },
      { name: 'Chat Rename', status: 'pending', message: 'Testing...' },
      { name: 'Chat Deletion', status: 'pending', message: 'Testing...' }
    ]);

    try {
      // Test 1: Backend Connection
      setResults(prev => prev.map(r => 
        r.name === 'Backend Connection' 
          ? { ...r, status: 'pending', message: 'Connecting to backend...' }
          : r
      ));

      const healthCheck = await fetch('http://127.0.0.1:8000/chat/chats');
      if (healthCheck.ok) {
        setResults(prev => prev.map(r => 
          r.name === 'Backend Connection' 
            ? { ...r, status: 'pass', message: 'Backend is running' }
            : r
        ));
      } else {
        throw new Error('Backend not responding');
      }

      // Test 2: Chat Creation
      setResults(prev => prev.map(r => 
        r.name === 'Chat Creation' 
          ? { ...r, status: 'pending', message: 'Creating new chat...' }
          : r
      ));

      const createResponse = await fetch('http://127.0.0.1:8000/chat/new_chat', {
        method: 'POST'
      });
      
      if (createResponse.ok) {
        const createData = await createResponse.json();
        setResults(prev => prev.map(r => 
          r.name === 'Chat Creation' 
            ? { ...r, status: 'pass', message: `Created chat: ${createData.chat_id}` }
            : r
        ));
        
        // Test 3: Chat Isolation (send message to specific chat)
        setResults(prev => prev.map(r => 
          r.name === 'Chat Isolation' 
            ? { ...r, status: 'pending', message: 'Testing chat isolation...' }
            : r
        ));

        const messageResponse = await fetch('http://127.0.0.1:8000/chat/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            chat_id: createData.chat_id, 
            message: 'Test message for isolation' 
          })
        });

        if (messageResponse.ok) {
          setResults(prev => prev.map(r => 
            r.name === 'Chat Isolation' 
              ? { ...r, status: 'pass', message: 'Chat isolation working' }
              : r
          ));
        } else {
          throw new Error('Failed to send message');
        }

        // Test 4: Chat Listing
        setResults(prev => prev.map(r => 
          r.name === 'Chat Listing' 
            ? { ...r, status: 'pending', message: 'Fetching chat list...' }
            : r
        ));

        const listResponse = await fetch('http://127.0.0.1:8000/chat/chats');
        if (listResponse.ok) {
          const chatList = await listResponse.json();
          setResults(prev => prev.map(r => 
            r.name === 'Chat Listing' 
              ? { ...r, status: 'pass', message: `Found ${chatList.length} chats` }
              : r
          ));
        } else {
          throw new Error('Failed to list chats');
        }

        // Test 5: Chat Rename
        setResults(prev => prev.map(r => 
          r.name === 'Chat Rename' 
            ? { ...r, status: 'pending', message: 'Testing rename...' }
            : r
        ));

        const renameResponse = await fetch(`http://127.0.0.1:8000/chat/${createData.chat_id}/rename`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: 'Test Renamed Chat' })
        });

        if (renameResponse.ok) {
          setResults(prev => prev.map(r => 
            r.name === 'Chat Rename' 
              ? { ...r, status: 'pass', message: 'Chat renamed successfully' }
              : r
          ));
        } else {
          throw new Error('Failed to rename chat');
        }

        // Test 6: Chat Deletion
        setResults(prev => prev.map(r => 
          r.name === 'Chat Deletion' 
            ? { ...r, status: 'pending', message: 'Testing deletion...' }
            : r
        ));

        const deleteResponse = await fetch(`http://127.0.0.1:8000/chat/${createData.chat_id}`, {
          method: 'DELETE'
        });

        if (deleteResponse.ok) {
          setResults(prev => prev.map(r => 
            r.name === 'Chat Deletion' 
              ? { ...r, status: 'pass', message: 'Chat deleted successfully' }
              : r
          ));
        } else {
          throw new Error('Failed to delete chat');
        }

      } else {
        throw new Error('Failed to create chat');
      }

    } catch (error) {
      console.error('Test error:', error);
      setResults(prev => prev.map(r => 
        r.status === 'pending' 
          ? { ...r, status: 'fail', message: `Error: ${error}` }
          : r
      ));
    }

    setRunning(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'fail':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pass':
        return <Badge variant="default" className="bg-green-500">PASS</Badge>;
      case 'fail':
        return <Badge variant="destructive">FAIL</Badge>;
      default:
        return <Badge variant="secondary">PENDING</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Workspace Separation Test</h2>
        <Button 
          onClick={runTests} 
          disabled={running}
          className="flex items-center gap-2"
        >
          {running ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          {running ? 'Running Tests...' : 'Run Tests'}
        </Button>
      </div>

      <div className="grid gap-4">
        {results.map((result, index) => (
          <Card key={index}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getStatusIcon(result.status)}
                  <CardTitle className="text-base">{result.name}</CardTitle>
                </div>
                {getStatusBadge(result.status)}
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{result.message}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {results.length > 0 && (
        <div className="border-t pt-4">
          <div className="flex items-center gap-4 text-sm">
            <span>Summary:</span>
            <span className="text-green-500">
              {results.filter(r => r.status === 'pass').length} passed
            </span>
            <span className="text-red-500">
              {results.filter(r => r.status === 'fail').length} failed
            </span>
            <span className="text-blue-500">
              {results.filter(r => r.status === 'pending').length} pending
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkspaceTest; 
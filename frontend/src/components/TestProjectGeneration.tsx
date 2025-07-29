import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Play, CheckCircle, XCircle } from 'lucide-react';

interface TestResult {
  test: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  message?: string;
}

const TestProjectGeneration: React.FC = () => {
  const [prompt, setPrompt] = useState('Create a simple HTML page with a header and navigation');
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<TestResult[]>([
    { test: 'Backend API Connection', status: 'pending' },
    { test: 'Project Generation', status: 'pending' },
    { test: 'Iframe Preview', status: 'pending' },
    { test: 'File Serving', status: 'pending' }
  ]);

  const runTests = async () => {
    setIsRunning(true);
    const newResults = [...results];

    try {
      // Test 1: Backend API Connection
      newResults[0] = { test: 'Backend API Connection', status: 'running' };
      setResults([...newResults]);

      const healthCheck = await fetch('http://127.0.0.1:8000/chat/chats');
      if (healthCheck.ok) {
        newResults[0] = { test: 'Backend API Connection', status: 'passed', message: 'Backend is reachable' };
      } else {
        throw new Error('Backend not responding');
      }

      // Test 2: Project Generation
      newResults[1] = { test: 'Project Generation', status: 'running' };
      setResults([...newResults]);

      const projectName = `test_project_${Date.now()}`;
      const generateRes = await fetch('http://127.0.0.1:8000/chat/generate-project', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_name: projectName, prompt })
      });

      if (generateRes.ok) {
        newResults[1] = { test: 'Project Generation', status: 'passed', message: `Project ${projectName} created` };
      } else {
        throw new Error('Project generation failed');
      }

      // Test 3: Iframe Preview
      newResults[2] = { test: 'Iframe Preview', status: 'running' };
      setResults([...newResults]);

      const previewRes = await fetch(`http://127.0.0.1:8000/api/projects/${projectName}/preview`);
      if (previewRes.ok) {
        newResults[2] = { test: 'Iframe Preview', status: 'passed', message: 'Preview endpoint working' };
      } else {
        throw new Error('Preview endpoint failed');
      }

      // Test 4: File Serving
      newResults[3] = { test: 'File Serving', status: 'running' };
      setResults([...newResults]);

      const filesRes = await fetch(`http://127.0.0.1:8000/api/projects/${projectName}/files`);
      if (filesRes.ok) {
        const filesData = await filesRes.json();
        newResults[3] = { test: 'File Serving', status: 'passed', message: `${filesData.files?.length || 0} files available` };
      } else {
        throw new Error('File serving failed');
      }

    } catch (error) {
      const failedIndex = newResults.findIndex(r => r.status === 'running');
      if (failedIndex !== -1) {
        newResults[failedIndex] = { 
          test: newResults[failedIndex].test, 
          status: 'failed', 
          message: error instanceof Error ? error.message : 'Unknown error' 
        };
      }
    }

    setResults([...newResults]);
    setIsRunning(false);
  };

  const resetTests = () => {
    setResults(results.map(r => ({ ...r, status: 'pending' as const })));
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return <div className="w-4 h-4 rounded-full bg-gray-300" />;
      case 'running':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case 'passed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return 'text-gray-500';
      case 'running':
        return 'text-blue-500';
      case 'passed':
        return 'text-green-500';
      case 'failed':
        return 'text-red-500';
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Play className="w-5 h-5" />
          Project Generation Test Suite
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Test Prompt:</label>
          <Textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter a test prompt..."
            className="mb-4"
          />
        </div>

        <div className="flex gap-2">
          <Button 
            onClick={runTests} 
            disabled={isRunning}
            className="flex-1"
          >
            {isRunning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Running Tests...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Run Tests
              </>
            )}
          </Button>
          <Button 
            variant="outline" 
            onClick={resetTests}
            disabled={isRunning}
          >
            Reset
          </Button>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium">Test Results:</h4>
          {results.map((result, index) => (
            <div key={index} className="flex items-center gap-3 p-2 rounded border">
              {getStatusIcon(result.status)}
              <div className="flex-1">
                <div className={`font-medium ${getStatusColor(result.status)}`}>
                  {result.test}
                </div>
                {result.message && (
                  <div className="text-sm text-muted-foreground">
                    {result.message}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="text-sm text-muted-foreground">
          <p>This test suite verifies:</p>
          <ul className="list-disc list-inside mt-1 space-y-1">
            <li>Backend API connectivity</li>
            <li>Project generation functionality</li>
            <li>Iframe preview system</li>
            <li>File serving capabilities</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default TestProjectGeneration; 
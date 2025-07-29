import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowRight, Sparkles, Play, CheckCircle, Loader2 } from 'lucide-react';
import TestProjectGeneration from '@/components/TestProjectGeneration';
import { WorkspaceTest } from '@/components/WorkspaceTest';

const Demo: React.FC = () => {
  const [prompt, setPrompt] = useState('Create a personal portfolio website with dark mode');
  const [isGenerating, setIsGenerating] = useState(false);
  const [projectName, setProjectName] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleStartBuilding = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    try {
      // 1. 创建新会话
      const res = await fetch("http://127.0.0.1:8000/chat/new_chat", { method: "POST" });
      const data = await res.json();
      const chat_id = data.chat_id;
      
      // 2. 生成项目名称
      const newProjectName = `demo_project_${Date.now()}`;
      setProjectName(newProjectName);
      
      // 3. 使用流式生成项目
      const streamRes = await fetch("http://127.0.0.1:8000/chat/generate-project/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          project_name: newProjectName, 
          prompt: prompt.trim() 
        })
      });
      
      if (streamRes.ok) {
        // 4. 跳转到工作区
        navigate("/workspace", { 
          state: { 
            chat_id, 
            initialPrompt: prompt.trim(),
            projectName: newProjectName,
            isGenerating: true
          } 
        });
      } else {
        throw new Error("Failed to start project generation");
      }
    } catch (e) {
      console.error("Project generation error:", e);
      alert("Failed to start building. Please try again.");
    }
    setIsGenerating(false);
  };

  const examplePrompts = [
    "Create a personal portfolio website with dark mode and smooth animations",
    "Build a React todo app with drag and drop functionality",
    "Create a weather dashboard with real-time data and charts",
    "Build an expense tracker with categories and monthly reports"
  ];

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-6xl mx-auto px-4 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-2 text-3xl font-bold">
            <Sparkles className="h-8 w-8 text-primary" />
            <span className="bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
              BuildSpace Demo
            </span>
          </div>
          <p className="text-muted-foreground text-lg">
            Experience the complete "Start Building" functionality with iframe preview
          </p>
        </div>

        {/* Main Demo Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Input Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="w-5 h-5" />
                Start Building
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">What would you like to build?</label>
                <Textarea
                  placeholder="A personal portfolio website"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="min-h-[120px] text-base resize-none"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                      e.preventDefault();
                      handleStartBuilding();
                    }
                  }}
                />
              </div>
              
              <Button
                onClick={handleStartBuilding}
                disabled={!prompt.trim() || isGenerating}
                size="lg"
                className="w-full bg-primary hover:bg-primary/90"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    Start Building
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
              
              <p className="text-sm text-muted-foreground">
                Press Cmd+Enter to start building
              </p>

              {/* Examples */}
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Try these examples:</p>
                <div className="grid gap-2">
                  {examplePrompts.map((example, index) => (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      onClick={() => setPrompt(example)}
                      className="text-left justify-start h-auto p-3"
                    >
                      <div className="text-left">
                        <div className="font-medium">{example.split(' ').slice(0, 4).join(' ')}...</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {example.length > 60 ? example.substring(0, 60) + '...' : example}
                        </div>
                      </div>
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Right: Features Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                Features Overview
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Streaming Project Generation</h4>
                    <p className="text-sm text-muted-foreground">
                      Real-time output streaming from gpt-engineer to frontend
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Iframe Preview</h4>
                    <p className="text-sm text-muted-foreground">
                      Automatic display and refresh of generated projects
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">File Browser</h4>
                    <p className="text-sm text-muted-foreground">
                      Display generated files with main file detection
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Error Handling</h4>
                    <p className="text-sm text-muted-foreground">
                      Graceful error handling and retry mechanisms
                    </p>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <h4 className="font-medium mb-2">How it works:</h4>
                <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                  <li>Enter your project description</li>
                  <li>Click "Start Building" or press Cmd+Enter</li>
                  <li>System creates new chat session</li>
                  <li>gpt-engineer generates project files</li>
                  <li>Iframe automatically displays the result</li>
                  <li>Real-time updates during generation</li>
                </ol>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Test Suite */}
        <Card>
          <CardHeader>
            <CardTitle>Test Suite</CardTitle>
          </CardHeader>
          <CardContent>
            <TestProjectGeneration />
          </CardContent>
        </Card>

        {/* Workspace Separation Test */}
        <Card>
          <CardHeader>
            <CardTitle>Workspace Separation Test</CardTitle>
          </CardHeader>
          <CardContent>
            <WorkspaceTest />
          </CardContent>
        </Card>

        {/* API Endpoints */}
        <Card>
          <CardHeader>
            <CardTitle>API Endpoints</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <h4 className="font-medium">Chat & Generation</h4>
                <div className="text-sm space-y-1">
                  <div><code className="bg-muted px-2 py-1 rounded">POST /chat/new_chat</code></div>
                  <div><code className="bg-muted px-2 py-1 rounded">POST /chat/generate-project/stream</code></div>
                  <div><code className="bg-muted px-2 py-1 rounded">GET /chat/chats</code></div>
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium">Project Preview</h4>
                <div className="text-sm space-y-1">
                  <div><code className="bg-muted px-2 py-1 rounded">GET /api/projects</code></div>
                  <div><code className="bg-muted px-2 py-1 rounded">GET /api/projects/{'{name}'}/preview</code></div>
                  <div><code className="bg-muted px-2 py-1 rounded">GET /api/projects/{'{name}'}/files</code></div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Demo; 
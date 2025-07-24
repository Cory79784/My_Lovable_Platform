import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Eye, 
  Code, 
  Smartphone, 
  Monitor, 
  Tablet,
  RotateCcw,
  ExternalLink
} from "lucide-react";

export const CodePreview = () => {
  const [activeView, setActiveView] = useState<'preview' | 'code'>('preview');
  const [deviceSize, setDeviceSize] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');

  const mockCode = `import React from 'react';
import './App.css';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center text-white">
          <h1 className="text-5xl font-bold mb-6">
            Welcome to the Future
          </h1>
          <p className="text-xl mb-8 text-purple-100">
            Build amazing applications with AI assistance
          </p>
          <div className="space-x-4">
            <button className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-colors">
              Get Started
            </button>
            <button className="border border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-600 transition-colors">
              Learn More
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;`;

  const getDeviceClass = () => {
    switch (deviceSize) {
      case 'mobile':
        return 'max-w-sm mx-auto';
      case 'tablet':
        return 'max-w-2xl mx-auto';
      default:
        return 'w-full';
    }
  };

  return (
    <div className="flex flex-col h-full bg-editor-bg">
      {/* Preview Header */}
      <div className="p-3 border-b border-border flex items-center justify-between">
        <Tabs value={activeView} onValueChange={(value) => setActiveView(value as 'preview' | 'code')}>
          <TabsList className="bg-secondary">
            <TabsTrigger value="preview" className="text-xs">
              <Eye className="w-4 h-4 mr-1" />
              Preview
            </TabsTrigger>
            <TabsTrigger value="code" className="text-xs">
              <Code className="w-4 h-4 mr-1" />
              Code
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="flex items-center space-x-2">
          {activeView === 'preview' && (
            <>
              <div className="flex items-center space-x-1 bg-secondary rounded-md p-1">
                <Button
                  variant={deviceSize === 'mobile' ? 'default' : 'ghost'}
                  size="sm"
                  className="w-8 h-8 p-0"
                  onClick={() => setDeviceSize('mobile')}
                >
                  <Smartphone className="w-4 h-4" />
                </Button>
                <Button
                  variant={deviceSize === 'tablet' ? 'default' : 'ghost'}
                  size="sm"
                  className="w-8 h-8 p-0"
                  onClick={() => setDeviceSize('tablet')}
                >
                  <Tablet className="w-4 h-4" />
                </Button>
                <Button
                  variant={deviceSize === 'desktop' ? 'default' : 'ghost'}
                  size="sm"
                  className="w-8 h-8 p-0"
                  onClick={() => setDeviceSize('desktop')}
                >
                  <Monitor className="w-4 h-4" />
                </Button>
              </div>
              
              <Button variant="ghost" size="sm" className="w-8 h-8 p-0">
                <RotateCcw className="w-4 h-4" />
              </Button>
            </>
          )}
          
          <Button variant="ghost" size="sm" className="w-8 h-8 p-0">
            <ExternalLink className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {activeView === 'preview' ? (
          <div className="h-full p-4 bg-muted/20">
            <div className={`h-full bg-white rounded-lg shadow-elevated overflow-hidden ${getDeviceClass()}`}>
              {/* Mock Preview Content */}
              <div className="h-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                <div className="text-center text-white p-8">
                  <h1 className="text-4xl md:text-5xl font-bold mb-6">
                    Welcome to the Future
                  </h1>
                  <p className="text-lg md:text-xl mb-8 text-purple-100">
                    Build amazing applications with AI assistance
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-colors">
                      Get Started
                    </button>
                    <button className="border border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-purple-600 transition-colors">
                      Learn More
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full">
            <pre className="h-full p-4 text-sm text-foreground font-mono overflow-auto bg-editor-bg">
              <code>{mockCode}</code>
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
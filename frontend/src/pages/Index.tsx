import { Header } from "@/components/Header";
import { FileExplorer } from "@/components/FileExplorer";
import { ChatInterface } from "@/components/ChatInterface";
import { CodePreview } from "@/components/CodePreview";

const Index = () => {
  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <Header />
      
      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* File Explorer */}
        <FileExplorer />
        
        {/* Split Panel */}
        <div className="flex flex-1">
          {/* Chat Interface */}
          <div className="w-1/2 border-r border-border">
            <ChatInterface />
          </div>
          
          {/* Code Preview */}
          <div className="w-1/2">
            <CodePreview />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;

import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { Header } from "@/components/Header";
import { ChatInterface } from "@/components/ChatInterface";
import { CodePreview } from "@/components/CodePreview";

const Workspace = () => {
  const location = useLocation();
  const initialPrompt = location.state?.initialPrompt;
  const chat_id = location.state?.chat_id;
  const [showCodeViewer, setShowCodeViewer] = useState(false);
  const [isChatCollapsed, setIsChatCollapsed] = useState(false);

  useEffect(() => {
    // Here you could use the initialPrompt to populate the chat or trigger an initial message
    if (initialPrompt) {
      console.log("Initial prompt:", initialPrompt);
      // You could dispatch this to a context or pass it to ChatInterface
    }
  }, [initialPrompt]);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <Header 
        showCodeViewer={showCodeViewer} 
        onToggleCodeViewer={() => setShowCodeViewer(!showCodeViewer)}
        isChatCollapsed={isChatCollapsed}
        onToggleChat={() => setIsChatCollapsed(!isChatCollapsed)}
      />
      
      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        <PanelGroup direction="horizontal">
          {/* Chat Interface - Only render when not collapsed */}
          {!isChatCollapsed && (
            <>
              <Panel defaultSize={showCodeViewer ? 33.33 : 50} minSize={25}>
                <ChatInterface 
                  initialPrompt={initialPrompt} 
                  chat_id={chat_id}
                  onCollapse={() => setIsChatCollapsed(true)}
                />
              </Panel>
              
              <PanelResizeHandle className="w-1 bg-border hover:bg-border/80 transition-colors" />
            </>
          )}
          
          {/* Code Viewer (conditional) */}
          {showCodeViewer && !isChatCollapsed && (
            <>
              <Panel defaultSize={33.33} minSize={20}>
                <div className="h-full bg-editor-bg">
                  <div className="p-3 border-b border-border">
                    <h3 className="text-sm font-medium text-foreground">Current Code</h3>
                  </div>
                  <div className="h-full p-4">
                    <pre className="text-sm text-muted-foreground font-mono">
                      <code>{`// Your code will appear here as you build...
// Start by describing what you want to create!`}</code>
                    </pre>
                  </div>
                </div>
              </Panel>
              
              <PanelResizeHandle className="w-1 bg-border hover:bg-border/80 transition-colors" />
            </>
          )}
          
          {/* Code Viewer when chat is collapsed */}
          {showCodeViewer && isChatCollapsed && (
            <>
              <Panel defaultSize={50} minSize={25}>
                <div className="h-full bg-editor-bg">
                  <div className="p-3 border-b border-border">
                    <h3 className="text-sm font-medium text-foreground">Current Code</h3>
                  </div>
                  <div className="h-full p-4">
                    <pre className="text-sm text-muted-foreground font-mono">
                      <code>{`// Your code will appear here as you build...
// Start by describing what you want to create!`}</code>
                    </pre>
                  </div>
                </div>
              </Panel>
              
              <PanelResizeHandle className="w-1 bg-border hover:bg-border/80 transition-colors" />
            </>
          )}
          
          {/* Preview - Takes full width when chat is collapsed */}
          <Panel defaultSize={isChatCollapsed ? 100 : (showCodeViewer ? 33.33 : 50)} minSize={25}>
            <CodePreview />
          </Panel>
        </PanelGroup>
      </div>
    </div>
  );
};

export default Workspace;
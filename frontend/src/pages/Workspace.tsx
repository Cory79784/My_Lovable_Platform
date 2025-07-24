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
  const [projectTree, setProjectTree] = useState([]);
  const [loadingProject, setLoadingProject] = useState(false);

  // 生成项目
  const generateProject = async (prompt: string) => {
    setLoadingProject(true);
    setProjectTree([]);
    try {
      const project_name = `project_${Date.now()}`;
      const res = await fetch("http://127.0.0.1:8000/chat/generate-project", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, project_name })
      });
      const data = await res.json();
      if (data.tree) setProjectTree(data.tree);
    } catch (e) {
      // 可加错误提示
    }
    setLoadingProject(false);
  };

  useEffect(() => {
    if (initialPrompt) {
      generateProject(initialPrompt);
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
                <CodePreview tree={projectTree} loading={loadingProject} />
              </Panel>
              <PanelResizeHandle className="w-1 bg-border hover:bg-border/80 transition-colors" />
            </>
          )}
          {/* Code Viewer when chat is collapsed */}
          {showCodeViewer && isChatCollapsed && (
            <>
              <Panel defaultSize={50} minSize={25}>
                <CodePreview tree={projectTree} loading={loadingProject} />
              </Panel>
              <PanelResizeHandle className="w-1 bg-border hover:bg-border/80 transition-colors" />
            </>
          )}
          {/* Preview - Takes full width when chat is collapsed */}
          <Panel defaultSize={isChatCollapsed ? 100 : (showCodeViewer ? 33.33 : 50)} minSize={25}>
            {/* 这里可以放其他内容 */}
          </Panel>
        </PanelGroup>
      </div>
    </div>
  );
};

export default Workspace;
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { Header } from "@/components/Header";
import { ChatInterface } from "@/components/ChatInterface";
import ProjectTabs from "@/components/ProjectTabs";

const Workspace = () => {
  const location = useLocation();
  const initialPrompt = location.state?.initialPrompt;
  const chat_id = location.state?.chat_id;
  const projectName = location.state?.projectName;
  const isGenerating = location.state?.isGenerating || false;
  const isExistingChat = location.state?.isExistingChat || false;
  const createNewChat = location.state?.createNewChat || false;
  
  const [isChatCollapsed, setIsChatCollapsed] = useState(false);
  const [currentProjectName, setCurrentProjectName] = useState<string | null>(projectName);
  const [generating, setGenerating] = useState(isGenerating);
  const [remixedProjectPath, setRemixedProjectPath] = useState<string | null>(null);

  // 流式生成项目
  const generateProjectStream = async (prompt: string) => {
    setGenerating(true);
    try {
      const project_name = `project_${Date.now()}`;
      setCurrentProjectName(project_name);
      
      const res = await fetch("http://127.0.0.1:8000/chat/generate-project/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, project_name })
      });
      
      if (res.ok) {
        const reader = res.body?.getReader();
        if (reader) {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            // Handle streaming output if needed
            console.log("Generation output:", new TextDecoder().decode(value));
          }
        }
      }
    } catch (e) {
      console.error("Streaming project generation error:", e);
    }
    setGenerating(false);
  };

  useEffect(() => {
    if (initialPrompt) {
      // Use streaming generation for better UX
      generateProjectStream(initialPrompt);
    }
  }, [initialPrompt]);

  // Handle remix functionality
  useEffect(() => {
    if (location.state?.remixedProject) {
      const { projectPath, projectName } = location.state.remixedProject;
      setRemixedProjectPath(projectPath);
      console.log(`Remixed project: ${projectPath} - ${projectName}`);
    }
  }, [location.state]);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <Header 
        isChatCollapsed={isChatCollapsed}
        onToggleChat={() => setIsChatCollapsed(!isChatCollapsed)}
      />
      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        <PanelGroup direction="horizontal">
          {/* Chat Interface - Left side */}
          {!isChatCollapsed && (
            <>
              <Panel defaultSize={40} minSize={25}>
                <ChatInterface 
                  initialPrompt={initialPrompt} 
                  chat_id={chat_id}
                  onCollapse={() => setIsChatCollapsed(true)}
                />
              </Panel>
              <PanelResizeHandle className="w-1 bg-border hover:bg-border/80 transition-colors" />
            </>
          )}
          
          {/* Project Tabs - Right side */}
          <Panel defaultSize={isChatCollapsed ? 100 : 60} minSize={25}>
            <ProjectTabs 
              projectPath={remixedProjectPath || currentProjectName}
              projectName={remixedProjectPath || currentProjectName}
              className="h-full"
            />
          </Panel>
        </PanelGroup>
      </div>
    </div>
  );
};

export default Workspace;
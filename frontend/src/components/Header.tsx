import { Button } from "@/components/ui/button";
import { Code2, Settings, User, FileText, Play, Code, Github, PanelLeftOpen, Bot, FolderOpen } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface HeaderProps {
  isChatCollapsed?: boolean;
  onToggleChat?: () => void;
}

export const Header = ({ 
  isChatCollapsed = false,
  onToggleChat 
}: HeaderProps) => {
  const navigate = useNavigate();
  
  return (
    <header className="h-12 bg-sidebar-bg border-b border-border flex items-center justify-between px-4">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
            <Code2 className="w-5 h-5 text-primary-foreground" />
          </div>
          <h1 className="text-lg font-semibold text-foreground">Lovable</h1>
        </div>
        
        <div className="flex items-center space-x-1">
          {isChatCollapsed && (
            <Button 
              variant="ghost" 
              size="sm"
              onClick={onToggleChat}
              className="text-xs"
            >
              <PanelLeftOpen className="w-4 h-4 mr-1" />
              <Bot className="w-4 h-4" />
            </Button>
          )}
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-xs"
            onClick={() => navigate('/workspace-overview')}
          >
            <FolderOpen className="w-4 h-4 mr-1" />
            Workspace
          </Button>
          <Button variant="ghost" size="sm" className="text-xs">
            <FileText className="w-4 h-4 mr-1" />
            main.tsx
          </Button>
          <Button variant="ghost" size="sm">
            <Play className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <Button variant="ghost" size="sm" className="bg-green-600 hover:bg-green-700 text-white">
          <span className="w-4 h-4 mr-1 text-white">⚡</span>
          Supabase
        </Button>
        <Button variant="ghost" size="sm">
          <Github className="w-4 h-4 mr-1" />
          GitHub
        </Button>
        <Button variant="ghost" size="sm">
          <Settings className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="sm">
          <User className="w-4 h-4" />
        </Button>
      </div>
    </header>
  );
};
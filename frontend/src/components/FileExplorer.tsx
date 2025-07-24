import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Folder, 
  FolderOpen, 
  FileText, 
  ChevronRight, 
  ChevronDown,
  Plus,
  Search
} from "lucide-react";

interface FileItem {
  name: string;
  type: 'file' | 'folder';
  children?: FileItem[];
  isOpen?: boolean;
}

const mockFiles: FileItem[] = [
  {
    name: 'src',
    type: 'folder',
    isOpen: true,
    children: [
      {
        name: 'components',
        type: 'folder',
        isOpen: false,
        children: [
          { name: 'Header.tsx', type: 'file' },
          { name: 'ChatInterface.tsx', type: 'file' },
          { name: 'CodePreview.tsx', type: 'file' }
        ]
      },
      { name: 'pages', type: 'folder', isOpen: false, children: [] },
      { name: 'App.tsx', type: 'file' },
      { name: 'main.tsx', type: 'file' },
      { name: 'index.css', type: 'file' }
    ]
  },
  { name: 'package.json', type: 'file' },
  { name: 'tailwind.config.ts', type: 'file' },
  { name: 'README.md', type: 'file' }
];

export const FileExplorer = () => {
  const [files, setFiles] = useState<FileItem[]>(mockFiles);

  const toggleFolder = (path: number[]) => {
    setFiles(prev => {
      const newFiles = [...prev];
      let current = newFiles;
      
      for (let i = 0; i < path.length - 1; i++) {
        current = current[path[i]].children!;
      }
      
      current[path[path.length - 1]].isOpen = !current[path[path.length - 1]].isOpen;
      return newFiles;
    });
  };

  const renderFileTree = (items: FileItem[], path: number[] = []) => {
    return items.map((item, index) => (
      <div key={`${path.join('-')}-${index}`} className="select-none">
        <div 
          className="flex items-center space-x-2 py-1 px-2 hover:bg-secondary/50 cursor-pointer rounded-sm group"
          onClick={() => item.type === 'folder' && toggleFolder([...path, index])}
        >
          {item.type === 'folder' && (
            <div className="w-4 h-4 flex items-center justify-center">
              {item.isOpen ? (
                <ChevronDown className="w-3 h-3 text-muted-foreground" />
              ) : (
                <ChevronRight className="w-3 h-3 text-muted-foreground" />
              )}
            </div>
          )}
          
          <div className="w-4 h-4 flex items-center justify-center">
            {item.type === 'folder' ? (
              item.isOpen ? (
                <FolderOpen className="w-4 h-4 text-blue-400" />
              ) : (
                <Folder className="w-4 h-4 text-blue-400" />
              )
            ) : (
              <FileText className="w-4 h-4 text-muted-foreground" />
            )}
          </div>
          
          <span className="text-sm text-foreground group-hover:text-primary transition-colors">
            {item.name}
          </span>
        </div>
        
        {item.type === 'folder' && item.isOpen && item.children && (
          <div className="ml-4 border-l border-border/30">
            {renderFileTree(item.children, [...path, index])}
          </div>
        )}
      </div>
    ));
  };

  return (
    <div className="w-64 bg-sidebar-bg border-r border-border flex flex-col h-full">
      <div className="p-3 border-b border-border">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-medium text-foreground">Explorer</h2>
          <div className="flex space-x-1">
            <Button variant="ghost" size="sm" className="w-6 h-6 p-0">
              <Plus className="w-3 h-3" />
            </Button>
            <Button variant="ghost" size="sm" className="w-6 h-6 p-0">
              <Search className="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>
      
      <ScrollArea className="flex-1 p-2">
        {renderFileTree(files)}
      </ScrollArea>
    </div>
  );
};
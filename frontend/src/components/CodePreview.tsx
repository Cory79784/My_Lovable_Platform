import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Eye, Code, Smartphone, Monitor, Tablet, RotateCcw, ExternalLink, Folder, FileText } from "lucide-react";
import React from "react"; // Added missing import for React

// 递归渲染文件树
function FileTree({ tree, onSelect, selectedPath, parentPath = "" }) {
  return (
    <ul className="pl-2">
      {tree.map((item) => {
        const fullPath = parentPath + "/" + item.name;
        if (item.type === "folder") {
          return (
            <li key={fullPath} className="mb-1">
              <div className="flex items-center text-primary font-semibold"><Folder className="w-4 h-4 mr-1" />{item.name}</div>
              <FileTree tree={item.children} onSelect={onSelect} selectedPath={selectedPath} parentPath={fullPath} />
            </li>
          );
        } else {
          return (
            <li key={fullPath}>
              <button
                className={`flex items-center w-full text-left px-2 py-1 rounded hover:bg-secondary ${selectedPath === fullPath ? "bg-secondary font-bold" : ""}`}
                onClick={() => onSelect(fullPath, item.content)}
              >
                <FileText className="w-4 h-4 mr-1" />{item.name}
              </button>
            </li>
          );
        }
      })}
    </ul>
  );
}

export const CodePreview = ({ tree = [], loading = false }) => {
  const [activeView, setActiveView] = useState<'preview' | 'code'>('code');
  const [deviceSize, setDeviceSize] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');
  const [selectedFile, setSelectedFile] = useState<{ path: string; content: string } | null>(null);

  // 默认选中第一个文件
  const handleSelect = (path: string, content: string) => {
    setSelectedFile({ path, content });
  };
  // 自动选中第一个文件
  React.useEffect(() => {
    function findFirstFile(tree, parentPath = "") {
      for (const item of tree) {
        const fullPath = parentPath + "/" + item.name;
        if (item.type === "file") return { path: fullPath, content: item.content };
        if (item.type === "folder") {
          const found = findFirstFile(item.children, fullPath);
          if (found) return found;
        }
      }
      return null;
    }
    if (tree && tree.length > 0) {
      const first = findFirstFile(tree);
      if (first) setSelectedFile(first);
    }
  }, [tree]);

  return (
    <div className="flex flex-col h-full bg-editor-bg">
      {/* Preview Header */}
      <div className="p-3 border-b border-border flex items-center justify-between">
        <Tabs value={activeView} onValueChange={(value) => setActiveView(value as 'preview' | 'code')}>
          <TabsList className="bg-secondary">
            <TabsTrigger value="preview" className="text-xs">
              <Eye className="w-4 h-4 mr-1" />Preview
            </TabsTrigger>
            <TabsTrigger value="code" className="text-xs">
              <Code className="w-4 h-4 mr-1" />Code
            </TabsTrigger>
          </TabsList>
        </Tabs>
        <div className="flex items-center space-x-2">
          {activeView === 'preview' && (
            <>
              <div className="flex items-center space-x-1 bg-secondary rounded-md p-1">
                <Button variant={deviceSize === 'mobile' ? 'default' : 'ghost'} size="sm" className="w-8 h-8 p-0" onClick={() => setDeviceSize('mobile')}><Smartphone className="w-4 h-4" /></Button>
                <Button variant={deviceSize === 'tablet' ? 'default' : 'ghost'} size="sm" className="w-8 h-8 p-0" onClick={() => setDeviceSize('tablet')}><Tablet className="w-4 h-4" /></Button>
                <Button variant={deviceSize === 'desktop' ? 'default' : 'ghost'} size="sm" className="w-8 h-8 p-0" onClick={() => setDeviceSize('desktop')}><Monitor className="w-4 h-4" /></Button>
              </div>
              <Button variant="ghost" size="sm" className="w-8 h-8 p-0"><RotateCcw className="w-4 h-4" /></Button>
            </>
          )}
          <Button variant="ghost" size="sm" className="w-8 h-8 p-0"><ExternalLink className="w-4 h-4" /></Button>
        </div>
      </div>
      {/* Content Area */}
      <div className="flex-1 overflow-hidden flex">
        {activeView === 'code' ? (
          loading ? (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">Generating project...</div>
          ) : (
            <>
              <div className="w-64 h-full border-r border-border bg-muted/30 overflow-auto">
                <FileTree tree={tree} onSelect={handleSelect} selectedPath={selectedFile?.path} />
              </div>
              <div className="flex-1 h-full overflow-auto">
                {selectedFile ? (
                  <pre className="h-full p-4 text-sm text-foreground font-mono overflow-auto bg-editor-bg">
                    <code>{selectedFile.content}</code>
                  </pre>
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground">Select a file to view its content</div>
                )}
              </div>
            </>
          )
        ) : (
          <div className="h-full flex-1 flex items-center justify-center text-muted-foreground">Preview not implemented</div>
        )}
      </div>
    </div>
  );
};
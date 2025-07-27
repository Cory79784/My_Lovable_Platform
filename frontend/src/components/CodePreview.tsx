import * as React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Eye,
  Code,
  Smartphone,
  Monitor,
  Tablet,
  RotateCcw,
  ExternalLink,
  Folder,
  FileText,
} from "lucide-react";
import Editor from "@monaco-editor/react";

interface FileItem {
  name: string;
  type: "folder" | "file";
  content?: string;
  children?: FileItem[];
}

interface FileTreeProps {
  tree: FileItem[];
  onSelect: (path: string, content: string) => void;
  selectedPath: string | null;
  parentPath?: string;
}

function FileTree({ tree, onSelect, selectedPath, parentPath = "" }: FileTreeProps) {
  return (
    <ul className="pl-2">
      {tree.map((item) => {
        const fullPath = `${parentPath}/${item.name}`;
        if (item.type === "folder" && item.children) {
          return (
            <li key={fullPath} className="mb-1">
              <div className="flex items-center text-primary font-semibold">
                <Folder className="w-4 h-4 mr-1" />
                {item.name}
              </div>
              <FileTree
                tree={item.children}
                onSelect={onSelect}
                selectedPath={selectedPath}
                parentPath={fullPath}
              />
            </li>
          );
        }
        return (
          <li key={fullPath}>
            <button
              className={`flex items-center w-full text-left px-2 py-1 rounded hover:bg-secondary ${
                selectedPath === fullPath ? "bg-secondary font-bold" : ""
              }`}
              onClick={() => onSelect(fullPath, item.content || "")}
            >
              <FileText className="w-4 h-4 mr-1" />
              {item.name}
            </button>
          </li>
        );
      })}
    </ul>
  );
}

function getLanguageFromFileName(fileName: string): string {
  const ext = fileName.split(".").pop()?.toLowerCase();
  const languageMap: Record<string, string> = {
    js: "javascript",
    jsx: "javascript",
    ts: "typescript",
    tsx: "typescript",
    html: "html",
    css: "css",
    scss: "scss",
    sass: "sass",
    json: "json",
    py: "python",
    java: "java",
    cpp: "cpp",
    c: "c",
    php: "php",
    rb: "ruby",
    go: "go",
    rs: "rust",
    sql: "sql",
    md: "markdown",
    txt: "plaintext",
    xml: "xml",
    yaml: "yaml",
    yml: "yaml",
    toml: "toml",
    ini: "ini",
    sh: "shell",
    bash: "shell",
    zsh: "shell",
    ps1: "powershell",
    bat: "batch",
    cmd: "batch",
  };
  return languageMap[ext || ""] || "plaintext";
}

export const CodePreview: React.FC<{ tree: FileItem[]; loading?: boolean }> = ({
  tree = [],
  loading = false,
}) => {
  const [activeView, setActiveView] = useState<"preview" | "code">("code");
  const [deviceSize, setDeviceSize] = useState<"mobile" | "tablet" | "desktop">("desktop");
  const [selectedFile, setSelectedFile] = useState<{ path: string; content: string } | null>(null);

  const handleSelect = (path: string, content: string) => {
    setSelectedFile({ path, content });
  };

  React.useEffect(() => {
    function findFirstFile(
      tree: FileItem[],
      parentPath = ""
    ): { path: string; content: string } | null {
      for (const item of tree) {
        const fullPath = `${parentPath}/${item.name}`;
        if (item.type === "file" && item.content) return { path: fullPath, content: item.content };
        if (item.type === "folder" && item.children) {
          const found = findFirstFile(item.children, fullPath);
          if (found) return found;
        }
      }
      return null;
    }
    const first = findFirstFile(tree);
    if (first) setSelectedFile(first);
  }, [tree]);

  return (
    <div className="flex flex-col h-full bg-editor-bg">
      {/* Header */}
      <div className="p-3 border-b border-border flex items-center justify-between">
        <Tabs value={activeView} onValueChange={(v: string) => setActiveView(v as "preview" | "code")}>
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
          {activeView === "preview" && (
            <>
              <div className="flex items-center space-x-1 bg-secondary rounded-md p-1">
                <Button
                  variant={deviceSize === "mobile" ? "default" : "ghost"}
                  size="sm"
                  className="w-8 h-8 p-0"
                  onClick={() => setDeviceSize("mobile")}
                >
                  <Smartphone className="w-4 h-4" />
                </Button>
                <Button
                  variant={deviceSize === "tablet" ? "default" : "ghost"}
                  size="sm"
                  className="w-8 h-8 p-0"
                  onClick={() => setDeviceSize("tablet")}
                >
                  <Tablet className="w-4 h-4" />
                </Button>
                <Button
                  variant={deviceSize === "desktop" ? "default" : "ghost"}
                  size="sm"
                  className="w-8 h-8 p-0"
                  onClick={() => setDeviceSize("desktop")}
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

      {/* Main Content */}
      <div className="flex-1 overflow-hidden flex">
        {activeView === "code" ? (
          loading ? (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              Generating project...
            </div>
          ) : (
            <>
              <div className="w-64 h-full border-r border-border bg-muted/30 overflow-auto">
                <FileTree tree={tree} onSelect={handleSelect} selectedPath={selectedFile?.path || null} />
              </div>
              <div className="flex-1 h-full overflow-hidden">
                {selectedFile ? (
                  <Editor
                    height="100%"
                    defaultLanguage={getLanguageFromFileName(selectedFile.path)}
                    value={selectedFile.content}
                    theme="vs-dark"
                    options={{
                      readOnly: true,
                      minimap: { enabled: true },
                      fontSize: 14,
                      lineNumbers: "on",
                      wordWrap: "on",
                      folding: true,
                      foldingStrategy: "indentation",
                      showFoldingControls: "always",
                      scrollBeyondLastLine: false,
                      automaticLayout: true,
                      tabSize: 2,
                      insertSpaces: true,
                      detectIndentation: true,
                      trimAutoWhitespace: true,
                    }}
                  />
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    Select a file to view its content
                  </div>
                )}
              </div>
            </>
          )
        ) : (
          <div className="h-full flex-1 flex items-center justify-center text-muted-foreground">
            Preview not implemented
          </div>
        )}
      </div>
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { FileText, Folder, Code, File, ChevronRight, ChevronDown, Search, Eye, Code as CodeIcon, Download } from 'lucide-react';
import Prism from 'prismjs';
import './CodeTheme.css';

interface ProjectFile {
  name: string;
  type: 'file' | 'folder';
  content?: string;
  children?: ProjectFile[];
}

interface ProjectTabsProps {
  projectPath?: string;
  projectName?: string;
  className?: string;
}

const ProjectTabs: React.FC<ProjectTabsProps> = ({ projectPath, projectName, className }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [files, setFiles] = useState<ProjectFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isFileTreeCollapsed, setIsFileTreeCollapsed] = useState(false);

  useEffect(() => {
    if (projectPath) {
      fetchProjectFiles(projectPath);
    }
  }, [projectPath]);

  useEffect(() => {
    if (fileContent && selectedFile) {
      // Re-highlight the code when content changes
      Prism.highlightAll();
    }
  }, [fileContent, selectedFile]);

  const fetchProjectFiles = async (projectPath: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/projects/${projectPath}/files`);
      if (response.ok) {
        const data = await response.json();
        const fileTree = buildFileTree(data.files);
        setFiles(fileTree);
      } else {
        console.error('Failed to fetch project files');
        setFiles([]);
      }
    } catch (error) {
      console.error('Error fetching project files:', error);
      setFiles([]);
    }
    setLoading(false);
  };

  const buildFileTree = (fileList: string[]): ProjectFile[] => {
    const tree: ProjectFile[] = [];
    const fileMap = new Map<string, ProjectFile>();

    // Filter out node_modules and other build artifacts
    const filteredFiles = fileList.filter(filePath => {
      const parts = filePath.split('/');
      return !parts.some(part => 
        part === 'node_modules' || 
        part === 'dist' || 
        part === '.next' || 
        part === 'build' ||
        part === '.git' ||
        part.startsWith('.')
      );
    });

    // Organize files into logical folders
    const organizedFiles = organizeFilesIntoFolders(filteredFiles);

    // Sort files to put main_prompt first if it exists
    const sortedFiles = [...organizedFiles].sort((a, b) => {
      if (a === 'main_prompt') return -1;
      if (b === 'main_prompt') return 1;
      return a.localeCompare(b);
    });

    sortedFiles.forEach(filePath => {
      const parts = filePath.split('/');
      let currentPath = '';
      
      parts.forEach((part, index) => {
        const isLast = index === parts.length - 1;
        const fullPath = currentPath ? `${currentPath}/${part}` : part;
        
        if (!fileMap.has(fullPath)) {
          const file: ProjectFile = {
            name: part,
            type: isLast ? 'file' : 'folder',
            children: isLast ? undefined : []
          };
          fileMap.set(fullPath, file);
          
          if (currentPath && fileMap.has(currentPath)) {
            fileMap.get(currentPath)!.children!.push(file);
          } else if (!currentPath) {
            tree.push(file);
          }
        }
        
        currentPath = fullPath;
      });
    });

    return tree;
  };

  const organizeFilesIntoFolders = (files: string[]): string[] => {
    const organized: string[] = [];
    
    files.forEach(file => {
      const ext = file.split('.').pop()?.toLowerCase();
      
      if (file === 'main_prompt' || file === 'package.json' || file === 'README.md') {
        // Keep root files as is
        organized.push(file);
      } else if (ext === 'tsx' || ext === 'ts' || ext === 'jsx' || ext === 'js') {
        // React/TypeScript files go in src/
        if (!file.startsWith('src/')) {
          organized.push(`src/${file}`);
        } else {
          organized.push(file);
        }
      } else if (ext === 'css' || ext === 'scss' || ext === 'sass') {
        // CSS files go in styles/
        if (!file.startsWith('styles/') && !file.startsWith('src/')) {
          organized.push(`styles/${file}`);
        } else {
          organized.push(file);
        }
      } else if (ext === 'json' || ext === 'config') {
        // Config files stay in root
        organized.push(file);
      } else if (ext === 'html') {
        // HTML files stay in root
        organized.push(file);
      } else {
        // Other files go in misc/
        if (!file.includes('/')) {
          organized.push(`misc/${file}`);
        } else {
          organized.push(file);
        }
      }
    });
    
    return organized;
  };

  const fetchFileContent = async (projectPath: string, filePath: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/projects/${projectPath}/files/${filePath}`);
      if (response.ok) {
        const content = await response.text();
        setFileContent(content);
      } else {
        setFileContent('Error loading file content');
      }
    } catch (error) {
      console.error('Error fetching file content:', error);
      setFileContent('Error loading file content');
    }
  };

  const toggleFolder = (folderPath: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderPath)) {
      newExpanded.delete(folderPath);
    } else {
      newExpanded.add(folderPath);
    }
    setExpandedFolders(newExpanded);
  };

  const handleFileClick = (projectPath: string, filePath: string) => {
    setSelectedFile(filePath);
    fetchFileContent(projectPath, filePath);
  };

  const getFileIcon = (fileName: string) => {
    // Special handling for main_prompt
    if (fileName === 'main_prompt') {
      return <FileText className="h-4 w-4 text-purple-500" />;
    }
    
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'html':
      case 'htm':
        return <FileText className="h-4 w-4 text-orange-500" />;
      case 'css':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'js':
      case 'ts':
      case 'jsx':
      case 'tsx':
        return <Code className="h-4 w-4 text-yellow-500" />;
      case 'json':
        return <FileText className="h-4 w-4 text-green-500" />;
      default:
        return <File className="h-4 w-4 text-gray-500" />;
    }
  };

  const getLanguageFromFileName = (fileName: string): string => {
    // Special case for main_prompt
    if (fileName === 'main_prompt') {
      return 'text';
    }
    
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'js':
        return 'javascript';
      case 'jsx':
        return 'jsx';
      case 'ts':
        return 'typescript';
      case 'tsx':
        return 'tsx';
      case 'html':
      case 'htm':
        return 'html';
      case 'css':
      case 'scss':
      case 'sass':
        return 'css';
      case 'json':
        return 'json';
      case 'py':
        return 'python';
      case 'md':
        return 'markdown';
      case 'txt':
        return 'text';
      case 'yml':
      case 'yaml':
        return 'yaml';
      case 'sh':
      case 'bash':
        return 'bash';
      default:
        return 'text';
    }
  };

  const renderFileTree = (fileList: ProjectFile[], level = 0, path = '') => {
    return fileList.map((file) => {
      const fullPath = path ? `${path}/${file.name}` : file.name;
      const isExpanded = expandedFolders.has(fullPath);
      const isSelected = selectedFile === fullPath;

      return (
        <div key={fullPath} style={{ marginLeft: `${level * 16}px` }}>
          <div
            className={`flex items-center gap-2 p-1 rounded cursor-pointer hover:bg-muted ${
              isSelected ? 'bg-muted' : ''
            }`}
            onClick={() => {
              if (file.type === 'folder') {
                toggleFolder(fullPath);
              } else if (projectPath) {
                handleFileClick(projectPath, fullPath);
              }
            }}
          >
            {file.type === 'folder' ? (
              <>
                {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                <Folder className="h-4 w-4 text-blue-500" />
              </>
            ) : (
              getFileIcon(file.name)
            )}
            <span className="text-sm">{file.name}</span>
          </div>
          
          {file.type === 'folder' && isExpanded && file.children && (
            <div>{renderFileTree(file.children, level + 1, fullPath)}</div>
          )}
        </div>
      );
    });
  };

  const filteredFiles = files.filter(file => 
    file.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={`h-full flex flex-col ${className}`}>
      {/* Tab Headers */}
      <div className="flex border-b bg-background justify-between">
        <div className="flex">
          <Button
            variant={activeTab === 'preview' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('preview')}
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
          >
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </Button>
          <Button
            variant={activeTab === 'code' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('code')}
            className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
          >
            <CodeIcon className="h-4 w-4 mr-2" />
            Code
          </Button>
        </div>
        
        {/* Download Button */}
        {projectPath && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.open(`http://127.0.0.1:8000/api/projects/${projectPath}/download`, '_blank')}
            className="mr-2"
          >
            <Download className="h-4 w-4 mr-2" />
            Download ZIP
          </Button>
        )}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'preview' ? (
          // Preview Tab
          <div className="h-full">
            {projectPath ? (
              <iframe
                src={`http://127.0.0.1:8000/api/projects/${projectPath}/preview`}
                className="w-full h-full border-0"
                title={projectName || 'Project Preview'}
                sandbox="allow-scripts allow-same-origin"
              />
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <div className="text-center">
                  <Eye className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No project selected</p>
                  <p className="text-sm mt-2">Select a project to view its preview</p>
                </div>
              </div>
            )}
          </div>
        ) : (
          // Code Tab
          <div className="h-full">
            {projectPath ? (
              <PanelGroup direction="horizontal">
                {/* File Tree Panel */}
                <Panel defaultSize={isFileTreeCollapsed ? 10 : 30} minSize={10} maxSize={50}>
                  <div className="h-full flex flex-col">
                    {/* Search Bar */}
                    <div className="p-3 border-b">
                      <div className="relative">
                        <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input
                          placeholder="Search files..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="pl-8"
                        />
                      </div>
                    </div>
                    
                    {/* File Tree */}
                    <ScrollArea className="flex-1">
                      <div className="p-2">
                        {loading ? (
                          <div className="text-center py-4">
                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
                            <p className="text-sm text-muted-foreground mt-2">Loading files...</p>
                          </div>
                        ) : (
                          <div className="space-y-1">
                            {renderFileTree(filteredFiles)}
                          </div>
                        )}
                      </div>
                    </ScrollArea>
                  </div>
                </Panel>
                
                <PanelResizeHandle className="w-1 bg-border hover:bg-border/80 transition-colors" />
                
                {/* Code Content Panel */}
                <Panel defaultSize={70} minSize={30}>
                  <div className="h-full flex flex-col">
                    {selectedFile ? (
                      <>
                        <div className="p-3 border-b bg-muted/50">
                          <h3 className="text-sm font-medium">{selectedFile}</h3>
                        </div>
                        <ScrollArea className="flex-1">
                          <div className="p-4">
                            <pre className="text-xs bg-muted rounded-lg overflow-auto">
                              <code 
                                className={`language-${getLanguageFromFileName(selectedFile)}`}
                                dangerouslySetInnerHTML={{
                                  __html: Prism.highlight(
                                    fileContent,
                                    Prism.languages.text,
                                    getLanguageFromFileName(selectedFile)
                                  )
                                }}
                              />
                            </pre>
                          </div>
                        </ScrollArea>
                      </>
                    ) : (
                      <div className="flex items-center justify-center h-full text-muted-foreground">
                        <div className="text-center">
                          <CodeIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                          <p>No file selected</p>
                          <p className="text-sm mt-2">Select a file from the tree to view its code</p>
                        </div>
                      </div>
                    )}
                  </div>
                </Panel>
              </PanelGroup>
            ) : (
              <div className="flex items-center justify-center h-full text-muted-foreground">
                <div className="text-center">
                  <CodeIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No project selected</p>
                  <p className="text-sm mt-2">Select a project to view its code</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectTabs; 
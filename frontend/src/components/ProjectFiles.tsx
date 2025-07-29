import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { FileText, Folder, Code, File, ChevronRight, ChevronDown } from 'lucide-react';

interface ProjectFile {
  name: string;
  type: 'file' | 'folder';
  content?: string;
  children?: ProjectFile[];
}

interface ProjectFilesProps {
  projectPath?: string;
  chatId?: string;
}

const ProjectFiles: React.FC<ProjectFilesProps> = ({ projectPath, chatId }) => {
  const [files, setFiles] = useState<ProjectFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');

  useEffect(() => {
    if (projectPath) {
      fetchProjectFiles(projectPath);
    }
  }, [projectPath]);

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

    // Sort files to put main_prompt first if it exists
    const sortedFiles = [...fileList].sort((a, b) => {
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

  if (!projectPath) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-lg">Project Files</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No project selected</p>
            <p className="text-sm">Select a project to view its files</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-lg">Project Files</CardTitle>
        <p className="text-sm text-muted-foreground">{projectPath}</p>
      </CardHeader>
      <CardContent className="p-0">
        <div className="grid grid-cols-2 h-full">
          {/* File Tree */}
          <div className="border-r">
            <div className="p-4">
              <h3 className="font-medium mb-2">File Structure</h3>
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto"></div>
                  <p className="text-sm text-muted-foreground mt-2">Loading files...</p>
                </div>
              ) : (
                <ScrollArea className="h-64">
                  <div className="space-y-1">
                    {renderFileTree(files)}
                  </div>
                </ScrollArea>
              )}
            </div>
          </div>

          {/* File Content */}
          <div className="p-4">
            <h3 className="font-medium mb-2">File Content</h3>
            {selectedFile ? (
              <ScrollArea className="h-64">
                <pre className="text-xs bg-muted p-3 rounded overflow-auto">
                  <code>{fileContent}</code>
                </pre>
              </ScrollArea>
            ) : (
              <div className="text-center text-muted-foreground py-8">
                <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Select a file to view its content</p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProjectFiles; 
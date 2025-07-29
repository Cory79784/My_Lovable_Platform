import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RefreshCw, ExternalLink, FileText, Play, Square } from 'lucide-react';

interface ProjectPreviewProps {
  projectName: string;
  isGenerating?: boolean;
  onRefresh?: () => void;
  className?: string;
}

interface ProjectInfo {
  project_name: string;
  status: string;
  files: string[];
  main_file?: string;
}

export const ProjectPreview: React.FC<ProjectPreviewProps> = ({
  projectName,
  isGenerating = false,
  onRefresh,
  className = ''
}) => {
  const [projectInfo, setProjectInfo] = useState<ProjectInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch project information
  const fetchProjectInfo = async () => {
    if (!projectName) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/projects/${projectName}`);
      if (!response.ok) {
        throw new Error(`Project not found: ${projectName}`);
      }
      
      const data = await response.json();
      setProjectInfo(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch project info');
    } finally {
      setIsLoading(false);
    }
  };

  // Refresh iframe content
  const refreshIframe = () => {
    if (iframeRef.current) {
      // Force iframe refresh by changing src
      const currentSrc = iframeRef.current.src;
      iframeRef.current.src = '';
      setTimeout(() => {
        if (iframeRef.current) {
          iframeRef.current.src = currentSrc;
        }
      }, 100);
    }
  };

  // Auto-refresh when generation is complete
  useEffect(() => {
    if (isGenerating) {
      // Poll for project updates during generation
      refreshIntervalRef.current = setInterval(() => {
        fetchProjectInfo();
      }, 2000); // Check every 2 seconds
    } else {
      // Clear interval when not generating
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
        
        // Refresh iframe after generation completes
        setTimeout(() => {
          fetchProjectInfo();
          refreshIframe();
        }, 1000);
      }
    }

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [isGenerating, projectName]);

  // Initial fetch
  useEffect(() => {
    fetchProjectInfo();
  }, [projectName]);

  // Handle manual refresh
  const handleRefresh = () => {
    fetchProjectInfo();
    refreshIframe();
    onRefresh?.();
  };

  // Handle external link
  const handleExternalLink = () => {
    if (projectInfo) {
      window.open(`http://127.0.0.1:8000/api/projects/${projectName}/preview`, '_blank');
    }
  };

  if (error) {
    return (
      <Card className={`h-full ${className}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Project Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            <div className="text-center">
              <p className="text-red-500 mb-2">{error}</p>
              <Button onClick={handleRefresh} variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className={`h-full ${className}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Project Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-muted-foreground" />
              <p className="text-muted-foreground">Loading project...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!projectInfo) {
    return (
      <Card className={`h-full ${className}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Project Preview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            <p>No project information available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const previewUrl = `http://127.0.0.1:8000/api/projects/${projectName}/preview`;

  return (
    <Card className={`h-full ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            {projectInfo.project_name}
          </CardTitle>
          <div className="flex items-center gap-2">
            {isGenerating && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <RefreshCw className="w-4 h-4 animate-spin" />
                Generating...
              </div>
            )}
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Button onClick={handleExternalLink} variant="outline" size="sm">
              <ExternalLink className="w-4 h-4" />
            </Button>
          </div>
        </div>
        {projectInfo.main_file && (
          <p className="text-sm text-muted-foreground">
            Main file: {projectInfo.main_file}
          </p>
        )}
      </CardHeader>
      <CardContent className="p-0">
        <div className="relative h-96">
          {projectInfo.files.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No files generated yet</p>
                {isGenerating && (
                  <p className="text-sm mt-2">Generation in progress...</p>
                )}
              </div>
            </div>
          ) : (
            <iframe
              ref={iframeRef}
              src={previewUrl}
              className="w-full h-full border-0 rounded-b-lg"
              title={`Preview of ${projectInfo.project_name}`}
              sandbox="allow-scripts allow-same-origin allow-forms"
            />
          )}
        </div>
        
        {/* Project files list */}
        {projectInfo.files.length > 0 && (
          <div className="p-4 border-t">
            <h4 className="text-sm font-medium mb-2">Generated Files:</h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {projectInfo.files.slice(0, 6).map((file, index) => (
                <div key={index} className="flex items-center gap-1 text-muted-foreground">
                  <FileText className="w-3 h-3" />
                  <span className="truncate">{file}</span>
                </div>
              ))}
              {projectInfo.files.length > 6 && (
                <div className="text-muted-foreground">
                  +{projectInfo.files.length - 6} more files
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ProjectPreview; 
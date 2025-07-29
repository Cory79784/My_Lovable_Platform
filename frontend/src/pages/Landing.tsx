import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Dialog as ConfirmDialog } from "@/components/ui/dialog";
import { ArrowRight, Sparkles, Search, ExternalLink, Copy, Loader2, FolderOpen, Download } from "lucide-react";

const Landing = () => {
  const [prompt, setPrompt] = useState("");
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<any>(null);
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  // 获取真实项目列表
  const fetchProjects = async () => {
    setLoadingProjects(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/chat/chats");
      const data = await res.json();
      setProjects(data);
    } catch (e) {
      setProjects([]);
    }
    setLoadingProjects(false);
  };
  useEffect(() => {
    fetchProjects();
  }, []);

  // 新建项目 - 使用流式生成
  const handleStartBuilding = async () => {
    if (!prompt.trim()) return;
    setCreating(true);
    try {
      // 1. 创建新会话
      const res = await fetch("http://127.0.0.1:8000/chat/new_chat", { method: "POST" });
      const data = await res.json();
      const chat_id = data.chat_id;
      
      // 2. 生成项目名称
      const project_name = `project_${Date.now()}`;
      
      // 3. 使用流式生成项目
              const streamRes = await fetch("http://127.0.0.1:8000/chat/generate-project/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          project_name, 
          prompt: prompt.trim() 
        })
      });
      
      if (streamRes.ok) {
        // 4. 跳转并传递chat_id和项目信息
        navigate("/workspace", { 
          state: { 
            chat_id, 
            initialPrompt: prompt.trim(),
            projectName: project_name,
            isGenerating: true
          } 
        });
        
        // 5. 自动刷新项目列表
        setTimeout(() => {
          fetchProjects();
        }, 2000);
      } else {
        throw new Error("Failed to start project generation");
      }
    } catch (e) {
      console.error("Project generation error:", e);
      alert("Failed to start building. Please try again.");
    }
    setCreating(false);
  };

  // 点击已有项目卡片
  const handleProjectClick = (project: any) => {
    navigate("/workspace", { 
      state: { 
        chat_id: project.chat_id, 
        initialPrompt: undefined,
        projectName: `project_${project.chat_id}`,
        isGenerating: false
      } 
    });
  };

  // 删除项目
  const handleDeleteProject = async (project: any) => {
    setDeleting(true);
    try {
              await fetch(`http://127.0.0.1:8000/chat/${project.chat_id}`, { method: "DELETE" });
      setDeleteTarget(null);
      fetchProjects();
    } catch (e) {
      alert("Failed to delete project");
    }
    setDeleting(false);
  };

  // 重混项目
  const handleRemixProject = async (project: any) => {
    setCreating(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/chat/remix-project", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_name: project.name,
          project_description: project.description,
          original_author: project.author
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log("Remix successful:", data);
        
        // Navigate to workspace with remix project information
        navigate("/workspace", {
          state: {
            chat_id: data.chat_id,
            initialPrompt: `I want to remix the '${project.name}' project by ${project.author}. ${project.description}`,
            isExistingChat: false,
            createNewChat: false,
            remixedProject: {
              projectPath: project.project_path,
              projectName: project.name
            }
          }
        });
        
        // 关闭模态框
        setSelectedProject(null);
        
        // 刷新项目列表
        setTimeout(() => {
          fetchProjects();
        }, 1000);
      } else {
        throw new Error("Failed to remix project");
      }
    } catch (e) {
      console.error("Remix error:", e);
      alert("Failed to remix project. Please try again.");
    }
    setCreating(false);
  };

  // 示例项目
  const examplePrompts = [
    "A personal portfolio website with dark mode and smooth animations",
    "A simple todo list app with drag and drop functionality", 
    "A weather dashboard with real-time data and beautiful charts",
    "An expense tracker with categories and monthly reports"
  ];

  const [communityProjects, setCommunityProjects] = useState<any[]>([]);
  const [loadingCommunityProjects, setLoadingCommunityProjects] = useState(false);

  // Fetch community projects from backend
  const fetchCommunityProjects = async () => {
    setLoadingCommunityProjects(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/community-projects");
      if (response.ok) {
        const projects = await response.json();
        console.log("Fetched community projects:", projects);
        setCommunityProjects(projects);
      } else {
        console.error("Failed to fetch community projects");
        setCommunityProjects([]);
      }
    } catch (error) {
      console.error("Error fetching community projects:", error);
      setCommunityProjects([]);
    }
    setLoadingCommunityProjects(false);
  };

  useEffect(() => {
    fetchCommunityProjects();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="py-20">
        <div className="max-w-4xl mx-auto px-4 text-center space-y-8">
          {/* Logo/Brand */}
          <div className="space-y-2">
            <div className="flex items-center justify-center gap-2 text-3xl font-bold">
              <Sparkles className="h-8 w-8 text-primary" />
              <span className="bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
                BuildSpace
              </span>
            </div>
            <p className="text-muted-foreground text-lg">
              Build beautiful web applications with AI assistance
            </p>
            
            {/* Workspace Overview Button */}
            <div className="flex justify-center mt-4">
              <Button
                variant="outline"
                onClick={() => navigate('/workspace-overview')}
                className="flex items-center gap-2"
              >
                <FolderOpen className="h-4 w-4" />
                My Workspace
              </Button>
            </div>
          </div>

          {/* Main Input Area */}
          <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">
              What would you like to build?
            </h1>
            <p className="text-xl text-muted-foreground">
              Describe your idea and we'll help you bring it to life
            </p>
          </div>

          {/* Prompt Input */}
          <div className="space-y-4 max-w-2xl mx-auto">
            <Textarea
              placeholder="A personal portfolio website"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[120px] text-base resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  handleStartBuilding();
                }
              }}
            />
            
            <Button
              onClick={handleStartBuilding}
              disabled={!prompt.trim() || creating}
              size="lg"
              className="w-full sm:w-auto bg-primary hover:bg-primary/90"
            >
              {creating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  Start Building
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
            
            <p className="text-sm text-muted-foreground">
              Press Cmd+Enter to start building
            </p>
          </div>

          {/* Examples */}
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">Or try one of these examples:</p>
            <div className="grid gap-2 sm:grid-cols-2 max-w-2xl mx-auto">
              {examplePrompts.map((example) => (
                <Button
                  key={example}
                  variant="outline"
                  size="sm"
                  onClick={() => setPrompt(example)}
                  className="text-left justify-start h-auto p-3"
                >
                  <div className="text-left">
                    <div className="font-medium">{example.split(' ').slice(0, 3).join(' ')}...</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {example.length > 50 ? example.substring(0, 50) + '...' : example}
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* My Lovable's Workspace Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold">My Lovable's Workspace</h2>
          <Button variant="ghost" onClick={fetchProjects} disabled={loadingProjects}>
            {loadingProjects ? <Loader2 className="h-4 w-4 animate-spin" /> : "Refresh"}
          </Button>
        </div>
        
        <div className="flex gap-4 mb-6">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <input
              placeholder="Search projects..."
              className="w-full pl-10 pr-4 py-2 border border-input rounded-md bg-background"
              disabled
            />
          </div>
          <select className="px-4 py-2 border border-input rounded-md bg-background" disabled>
            <option>Last edited</option>
            <option>Name</option>
            <option>Created</option>
          </select>
          <select className="px-4 py-2 border border-input rounded-md bg-background" disabled>
            <option>All creators</option>
            <option>Me</option>
            <option>Others</option>
          </select>
        </div>
        {loadingProjects ? (
          <div className="text-muted-foreground py-8 text-center">
            <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
            Loading projects...
          </div>
        ) : projects.length === 0 ? (
          <div className="text-muted-foreground py-8 text-center">
            <div className="text-4xl mb-4">🚀</div>
            <p className="text-lg font-medium mb-2">No projects yet</p>
            <p className="text-sm">Start building your first project above!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Card key={project.chat_id} className="relative cursor-pointer hover:shadow-lg transition-shadow group" onClick={() => handleProjectClick(project)}>
                <CardContent className="p-0">
                  <div className="h-24 bg-muted rounded-t-lg flex items-center justify-center">
                    <span className="text-2xl font-bold text-primary">{project.title?.slice(0, 2) || "P"}</span>
                  </div>
                  <div className="p-4">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-semibold">
                        {project.title?.charAt(0).toUpperCase() || "P"}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium">{project.title || "Untitled"}</h3>
                        <p className="text-sm text-muted-foreground">ID: {project.chat_id}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-60 hover:opacity-100 transition-opacity z-10"
                        onClick={e => { e.stopPropagation(); setDeleteTarget(project); }}
                        title="Delete"
                      >
                        <span className="text-lg">🗑️</span>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
        {/* 删除确认弹窗 */}
        <ConfirmDialog open={!!deleteTarget} onOpenChange={open => !open && setDeleteTarget(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Project</DialogTitle>
            </DialogHeader>
            <div className="py-4 text-center text-lg">Are you sure you want to delete this project?</div>
            <div className="flex justify-end gap-2 mt-4">
              <Button variant="outline" onClick={() => setDeleteTarget(null)} disabled={deleting}>Cancel</Button>
              <Button variant="destructive" onClick={() => handleDeleteProject(deleteTarget)} disabled={deleting}>
                {deleting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                {deleting ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </DialogContent>
        </ConfirmDialog>
      </div>

      {/* From the Community Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-3xl font-bold">From the Community</h2>
          <Button variant="ghost">View All</Button>
        </div>

        <div className="flex gap-4 mb-6">
          <select className="px-4 py-2 border border-input rounded-md bg-background">
            <option>Popular</option>
            <option>Recent</option>
            <option>Most Remixed</option>
          </select>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">Discover</Button>
            <Button variant="outline" size="sm">Internal Tools</Button>
            <Button variant="outline" size="sm">Website</Button>
            <Button variant="outline" size="sm">Personal</Button>
            <Button variant="outline" size="sm">Consumer App</Button>
            <Button variant="outline" size="sm">B2B App</Button>
            <Button variant="outline" size="sm">Prototype</Button>
          </div>
        </div>

        {loadingCommunityProjects ? (
          <div className="text-muted-foreground py-8 text-center">
            <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
            Loading community projects...
          </div>
        ) : communityProjects.length === 0 ? (
          <div className="text-muted-foreground py-8 text-center">
            <div className="text-4xl mb-4">🌍</div>
            <p className="text-lg font-medium mb-2">No community projects yet</p>
            <p className="text-sm">Projects will appear here as they're created</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {communityProjects.map((project) => (
              <Card 
                key={project.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => setSelectedProject(project)}
              >
                <CardContent className="p-0">
                  <div className="h-48 bg-muted rounded-t-lg flex items-center justify-center relative overflow-hidden">
                    {project.has_web_files ? (
                      <div className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <div className="text-center text-white">
                          <div className="text-4xl mb-2">🌐</div>
                          <div className="text-sm font-medium">{project.name}</div>
                          <div className="text-xs opacity-80">Click to preview</div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center text-muted-foreground">
                        <div className="text-center">
                          <div className="text-4xl mb-2">📁</div>
                          <div className="text-sm">{project.name}</div>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-semibold">
                        {project.author.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-sm">{project.name}</h3>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                          <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full text-xs font-medium">{project.category}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-muted-foreground">{project.remixes}</p>
                      {project.has_web_files && (
                        <div className="flex items-center gap-1 text-xs text-green-600">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span>Live Preview</span>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Project Modal */}
      <Dialog open={!!selectedProject} onOpenChange={() => setSelectedProject(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
          {selectedProject && (
            <>
              <DialogHeader className="flex flex-row items-center justify-between pb-4">
                <div>
                  <DialogTitle className="text-2xl font-bold">
                    {selectedProject.name}
                  </DialogTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    by {selectedProject.author} • {selectedProject.remixes}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button 
                    variant="outline"
                    onClick={() => window.open(`http://127.0.0.1:8000/api/projects/${selectedProject.project_path}/download`, '_blank')}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download ZIP
                  </Button>
                  <Button variant="outline">
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Open Project
                  </Button>
                  <Button 
                    onClick={() => handleRemixProject(selectedProject)}
                    disabled={creating}
                  >
                    {creating ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Copy className="mr-2 h-4 w-4" />
                    )}
                    {creating ? "Remixing..." : "Remix Project"}
                  </Button>
                </div>
              </DialogHeader>
              
              <div className="space-y-6">
                <div className="h-[500px] bg-muted rounded-lg flex items-center justify-center overflow-hidden">
                  {selectedProject.has_web_files ? (
                    <iframe 
                      src={`http://127.0.0.1:8000/api/projects/${selectedProject.project_path}/preview`}
                      className="w-full h-full border-0 rounded-lg"
                      title={selectedProject.name}
                      sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals"
                      allow="fullscreen"
                    />
                  ) : (
                    <div className="flex items-center justify-center text-muted-foreground">
                      <div className="text-center">
                        <div className="text-6xl mb-4">📁</div>
                        <div className="text-lg font-medium">{selectedProject.name}</div>
                        <div className="text-sm mt-2">No preview available</div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="bg-muted/50 rounded-lg p-4">
                  <h4 className="font-semibold mb-2">About this project</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">{selectedProject.description}</p>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Landing;
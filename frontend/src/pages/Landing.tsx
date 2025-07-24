import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Dialog as ConfirmDialog } from "@/components/ui/dialog";
import { ArrowRight, Sparkles, Search, ExternalLink, Copy } from "lucide-react";

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

  // 新建项目
  const handleStartBuilding = async () => {
    if (!prompt.trim()) return;
    setCreating(true);
    try {
      // 1. 创建新会话
      const res = await fetch("http://127.0.0.1:8000/chat/new_chat", { method: "POST" });
      const data = await res.json();
      const chat_id = data.chat_id;
      // 2. 发送初始prompt
      await fetch("http://127.0.0.1:8000/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id, message: prompt })
      });
      // 3. 跳转并传递chat_id
      navigate("/workspace", { state: { chat_id, initialPrompt: prompt } });
      // 4. 自动刷新项目列表
      fetchProjects();
    } catch (e) {
      alert("新建项目失败");
    }
    setCreating(false);
  };

  // 点击已有项目卡片
  const handleProjectClick = (project: any) => {
    navigate("/workspace", { state: { chat_id: project.chat_id, initialPrompt: undefined } });
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

  const communityProjects = [
    {
      id: 1,
      name: "pulse-robot-template",
      description: "Interactive robot animation template",
      category: "Website",
      remixes: "17448 Remixes",
      thumbnail: "/placeholder.svg",
      author: "creator1"
    },
    {
      id: 2,
      name: "cryptocurrency-trading-dashboard",
      description: "Real-time crypto trading interface",
      category: "Website", 
      remixes: "11302 Remixes",
      thumbnail: "/placeholder.svg",
      author: "henriksd@gmail.com"
    },
    {
      id: 3,
      name: "wrlds-ai-integration",
      description: "AI-powered world building tool",
      category: "Website",
      remixes: "6903 Remixes", 
      thumbnail: "/placeholder.svg",
      author: "creator3"
    },
    {
      id: 4,
      name: "crypto-trade-template",
      description: "Secure crypto trading platform",
      category: "Website",
      remixes: "6112 Remixes",
      thumbnail: "/placeholder.svg",
      author: "creator4"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="py-20">
        {/* 去除原有的bg-gradient-to-br from-background to-muted，保持内容层透明 */}
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
              placeholder="e.g., Create a task management app with drag and drop functionality..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="min-h-[120px] text-base resize-none"
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  handleStartBuilding();
                }
              }}
            />
            
            <Button
              onClick={handleStartBuilding}
              disabled={!prompt.trim() || creating}
              size="lg"
              className="w-full sm:w-auto"
            >
              {creating ? "Creating..." : "Start Building"}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
            
            <p className="text-sm text-muted-foreground">
              Press Cmd+Enter to start building
            </p>
          </div>

          {/* Examples */}
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">Or try one of these examples:</p>
            <div className="grid gap-2 sm:grid-cols-2 max-w-2xl mx-auto">
              {[
                "A personal portfolio website",
                "A simple todo list app", 
                "A weather dashboard",
                "An expense tracker"
              ].map((example) => (
                <Button
                  key={example}
                  variant="outline"
                  size="sm"
                  onClick={() => setPrompt(example)}
                  className="text-left justify-start"
                >
                  {example}
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
          <Button variant="ghost" onClick={fetchProjects} disabled={loadingProjects}>刷新</Button>
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
          <div className="text-muted-foreground py-8 text-center">加载中...</div>
        ) : projects.length === 0 ? (
          <div className="text-muted-foreground py-8 text-center">暂无项目</div>
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
              <Button variant="destructive" onClick={() => handleDeleteProject(deleteTarget)} disabled={deleting}>{deleting ? 'Deleting...' : 'Delete'}</Button>
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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {communityProjects.map((project) => (
            <Card 
              key={project.id} 
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => setSelectedProject(project)}
            >
              <CardContent className="p-0">
                <div className="h-48 bg-muted rounded-t-lg flex items-center justify-center">
                  <img 
                    src={project.thumbnail} 
                    alt={project.name}
                    className="w-full h-full object-cover rounded-t-lg"
                  />
                </div>
                <div className="p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-semibold">
                      {project.author.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-sm">{project.name}</h3>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">{project.category}</span>
                      </div>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">{project.remixes}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Project Modal */}
      <Dialog open={!!selectedProject} onOpenChange={() => setSelectedProject(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
          {selectedProject && (
            <>
              <DialogHeader className="flex flex-row items-center justify-between">
                <DialogTitle className="text-2xl font-bold">
                  {selectedProject.name}
                </DialogTitle>
                <div className="flex gap-2">
                  <Button>
                    <ExternalLink className="mr-2 h-4 w-4" />
                    Open Project
                  </Button>
                  <Button variant="outline">
                    <Copy className="mr-2 h-4 w-4" />
                    Remix
                  </Button>
                </div>
              </DialogHeader>
              
              <div className="space-y-4">
                <div className="h-96 bg-muted rounded-lg flex items-center justify-center">
                  <img 
                    src={selectedProject.thumbnail} 
                    alt={selectedProject.name}
                    className="w-full h-full object-cover rounded-lg"
                  />
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-semibold">
                    {selectedProject.author.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold">{selectedProject.name}</h3>
                    <p className="text-muted-foreground">by {selectedProject.author}</p>
                  </div>
                  <div className="ml-auto">
                    <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded text-sm">{selectedProject.category}</span>
                  </div>
                </div>
                
                <p className="text-muted-foreground">{selectedProject.description}</p>
                <p className="text-sm text-muted-foreground">{selectedProject.remixes}</p>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Landing;
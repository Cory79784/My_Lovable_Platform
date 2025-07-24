import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowRight, Sparkles } from "lucide-react";

const Landing = () => {
  const [prompt, setPrompt] = useState("");
  const navigate = useNavigate();

  const handleStartBuilding = () => {
    if (prompt.trim()) {
      // Navigate to workspace with the prompt
      navigate("/workspace", { state: { initialPrompt: prompt } });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted flex items-center justify-center p-4">
      <div className="max-w-2xl w-full space-y-8 text-center">
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
        <div className="space-y-4">
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
            disabled={!prompt.trim()}
            size="lg"
            className="w-full sm:w-auto"
          >
            Start Building
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
          
          <p className="text-sm text-muted-foreground">
            Press Cmd+Enter to start building
          </p>
        </div>

        {/* Examples */}
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">Or try one of these examples:</p>
          <div className="grid gap-2 sm:grid-cols-2">
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
  );
};

export default Landing;
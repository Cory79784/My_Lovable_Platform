import * as React from "react"
import { 
  Card as BaseCard,
  CardHeader as BaseCardHeader,
  CardTitle as BaseCardTitle,
  CardDescription as BaseCardDescription,
  CardContent as BaseCardContent,
  CardFooter as BaseCardFooter,
  CardProps as BaseCardProps
} from "@/components/ui/card"
import { cn } from "@/lib/utils"

// Semantic card variants
export interface SemanticCardProps extends BaseCardProps {
  variant?: "default" | "elevated" | "outlined" | "filled" | "interactive"
  padding?: "none" | "sm" | "md" | "lg"
  hover?: boolean
  selected?: boolean
  loading?: boolean
}

const Card = React.forwardRef<HTMLDivElement, SemanticCardProps>(
  ({ 
    className, 
    variant = "default", 
    padding = "md", 
    hover = false, 
    selected = false,
    loading = false,
    children,
    ...props 
  }, ref) => {
    // Get semantic-specific styles
    const getSemanticStyles = (semanticVariant: string) => {
      switch (semanticVariant) {
        case "elevated":
          return "shadow-lg hover:shadow-xl transition-shadow"
        case "outlined":
          return "border-2 border-border"
        case "filled":
          return "bg-muted/50"
        case "interactive":
          return "cursor-pointer hover:shadow-md transition-all hover:scale-[1.02] active:scale-[0.98]"
        default:
          return ""
      }
    }

    const semanticStyles = getSemanticStyles(variant)
    const paddingStyles = {
      none: "",
      sm: "p-3",
      md: "p-4",
      lg: "p-6"
    }

    return (
      <BaseCard
        ref={ref}
        className={cn(
          semanticStyles,
          hover && "hover:shadow-md transition-shadow",
          selected && "ring-2 ring-primary ring-offset-2",
          loading && "opacity-70 pointer-events-none",
          paddingStyles[padding],
          className
        )}
        {...props}
      >
        {loading && (
          <div className="absolute inset-0 bg-background/50 flex items-center justify-center rounded-lg">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        )}
        {children}
      </BaseCard>
    )
  }
)

Card.displayName = "SemanticCard"

// Semantic Card Header
export interface SemanticCardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  subtitle?: string
  avatar?: React.ReactNode
  actions?: React.ReactNode
}

const CardHeader = React.forwardRef<HTMLDivElement, SemanticCardHeaderProps>(
  ({ className, title, subtitle, avatar, actions, children, ...props }, ref) => {
    return (
      <BaseCardHeader
        ref={ref}
        className={cn("flex flex-row items-start justify-between", className)}
        {...props}
      >
        <div className="flex items-start space-x-3">
          {avatar && <div className="flex-shrink-0">{avatar}</div>}
          <div className="flex-1 min-w-0">
            {title && <BaseCardTitle className="text-lg font-semibold">{title}</BaseCardTitle>}
            {subtitle && <BaseCardDescription className="mt-1">{subtitle}</BaseCardDescription>}
            {children}
          </div>
        </div>
        {actions && <div className="flex-shrink-0">{actions}</div>}
      </BaseCardHeader>
    )
  }
)

CardHeader.displayName = "SemanticCardHeader"

// Semantic Card Content
const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <BaseCardContent
        ref={ref}
        className={cn("flex-1", className)}
        {...props}
      />
    )
  }
)

CardContent.displayName = "SemanticCardContent"

// Semantic Card Footer
const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <BaseCardFooter
        ref={ref}
        className={cn("flex items-center justify-between", className)}
        {...props}
      />
    )
  }
)

CardFooter.displayName = "SemanticCardFooter"

export { Card, CardHeader, CardContent, CardFooter }
export type { SemanticCardProps, SemanticCardHeaderProps }
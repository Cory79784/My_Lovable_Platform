import * as React from "react"
import { Button as BaseButton, ButtonProps as BaseButtonProps } from "@/components/ui/button"
import { cn } from "@/lib/utils"

// Semantic button variants
export interface SemanticButtonProps extends Omit<BaseButtonProps, 'size' | 'variant'> {
  variant?: "primary" | "secondary" | "success" | "warning" | "danger" | "ghost" | "outline"
  size?: "sm" | "md" | "lg" | "xl"
  loading?: boolean
  icon?: React.ReactNode
  iconPosition?: "left" | "right"
}

const Button = React.forwardRef<HTMLButtonElement, SemanticButtonProps>(
  ({ 
    className, 
    variant = "primary", 
    size = "md", 
    loading = false, 
    icon, 
    iconPosition = "left",
    children,
    disabled,
    ...props 
  }, ref) => {
    // Map semantic variants to shadcn variants
    const getShadcnVariant = (semanticVariant: string): BaseButtonProps["variant"] => {
      switch (semanticVariant) {
        case "primary":
          return "default"
        case "secondary":
          return "secondary"
        case "success":
          return "default"
        case "warning":
          return "default"
        case "danger":
          return "destructive"
        case "ghost":
          return "ghost"
        case "outline":
          return "outline"
        default:
          return "default"
      }
    }

    // Map semantic sizes to shadcn sizes
    const getShadcnSize = (semanticSize: string): BaseButtonProps["size"] => {
      switch (semanticSize) {
        case "sm":
          return "sm"
        case "md":
          return "default"
        case "lg":
          return "lg"
        case "xl":
          return "lg"
        default:
          return "default"
      }
    }

    // Get semantic-specific styles
    const getSemanticStyles = (semanticVariant: string) => {
      switch (semanticVariant) {
        case "success":
          return "bg-green-600 hover:bg-green-700 text-white"
        case "warning":
          return "bg-yellow-600 hover:bg-yellow-700 text-white"
        case "danger":
          return "bg-red-600 hover:bg-red-700 text-white"
        default:
          return ""
      }
    }

    const isSemanticVariant = ["success", "warning"].includes(variant)
    const shadcnVariant = isSemanticVariant ? "default" : getShadcnVariant(variant)
    const shadcnSize = getShadcnSize(size)
    const semanticStyles = getSemanticStyles(variant)

    return (
      <BaseButton
        ref={ref}
        variant={shadcnVariant}
        size={shadcnSize}
        disabled={disabled || loading}
        className={cn(
          isSemanticVariant && semanticStyles,
          loading && "opacity-70 cursor-not-allowed",
          className
        )}
        {...props}
      >
        {loading && (
          <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {icon && iconPosition === "left" && !loading && (
          <span className="mr-2">{icon}</span>
        )}
        {children}
        {icon && iconPosition === "right" && !loading && (
          <span className="ml-2">{icon}</span>
        )}
      </BaseButton>
    )
  }
)

Button.displayName = "SemanticButton"

export { Button }
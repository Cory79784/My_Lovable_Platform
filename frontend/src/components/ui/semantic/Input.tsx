import * as React from "react"
import { Input as BaseInput, InputProps as BaseInputProps } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

// Semantic input variants
export interface SemanticInputProps extends BaseInputProps {
  variant?: "default" | "filled" | "outlined" | "minimal"
  size?: "sm" | "md" | "lg"
  label?: string
  error?: string
  helperText?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  loading?: boolean
  required?: boolean
}

const Input = React.forwardRef<HTMLInputElement, SemanticInputProps>(
  ({ 
    className, 
    variant = "default", 
    size = "md", 
    label,
    error,
    helperText,
    leftIcon,
    rightIcon,
    loading = false,
    required = false,
    disabled,
    id,
    ...props 
  }, ref) => {
    const inputId = id || React.useId()

    // Get semantic-specific styles
    const getSemanticStyles = (semanticVariant: string) => {
      switch (semanticVariant) {
        case "filled":
          return "bg-muted/50 border-0 focus:bg-background"
        case "outlined":
          return "border-2 focus:border-primary"
        case "minimal":
          return "border-0 border-b-2 rounded-none focus:border-primary bg-transparent"
        default:
          return ""
      }
    }

    // Get size-specific styles
    const getSizeStyles = (semanticSize: string) => {
      switch (semanticSize) {
        case "sm":
          return "h-8 text-sm px-2"
        case "md":
          return "h-10 text-sm px-3"
        case "lg":
          return "h-12 text-base px-4"
        default:
          return "h-10 text-sm px-3"
      }
    }

    const semanticStyles = getSemanticStyles(variant)
    const sizeStyles = getSizeStyles(size)

    return (
      <div className="w-full space-y-2">
        {label && (
          <Label 
            htmlFor={inputId}
            className={cn(
              "text-sm font-medium",
              error && "text-destructive"
            )}
          >
            {label}
            {required && <span className="text-destructive ml-1">*</span>}
          </Label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {leftIcon}
            </div>
          )}
          
          <BaseInput
            ref={ref}
            id={inputId}
            disabled={disabled || loading}
            className={cn(
              semanticStyles,
              sizeStyles,
              leftIcon && "pl-10",
              rightIcon && "pr-10",
              error && "border-destructive focus:border-destructive",
              loading && "opacity-70",
              className
            )}
            {...props}
          />
          
          {rightIcon && !loading && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {rightIcon}
            </div>
          )}
          
          {loading && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            </div>
          )}
        </div>
        
        {(error || helperText) && (
          <div className="text-xs">
            {error && (
              <p className="text-destructive">{error}</p>
            )}
            {helperText && !error && (
              <p className="text-muted-foreground">{helperText}</p>
            )}
          </div>
        )}
      </div>
    )
  }
)

Input.displayName = "SemanticInput"

export { Input }
export type { SemanticInputProps }
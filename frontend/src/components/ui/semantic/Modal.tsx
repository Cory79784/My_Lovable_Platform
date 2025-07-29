import * as React from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

// Semantic modal variants
export interface SemanticModalProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  trigger?: React.ReactNode
  title?: string
  description?: string
  children?: React.ReactNode
  variant?: "default" | "alert" | "confirm" | "form"
  size?: "sm" | "md" | "lg" | "xl" | "full"
  loading?: boolean
  className?: string
}

// Modal actions
export interface ModalActions {
  primary?: {
    label: string
    onClick: () => void
    loading?: boolean
    disabled?: boolean
    variant?: "primary" | "secondary" | "success" | "warning" | "danger"
  }
  secondary?: {
    label: string
    onClick: () => void
    loading?: boolean
    disabled?: boolean
    variant?: "primary" | "secondary" | "ghost" | "outline"
  }
  cancel?: {
    label?: string
    onClick?: () => void
  }
}

const Modal = React.forwardRef<HTMLDivElement, SemanticModalProps>(
  ({ 
    open,
    onOpenChange,
    trigger,
    title,
    description,
    children,
    variant = "default",
    size = "md",
    loading = false,
    className,
    ...props 
  }, ref) => {
    // Get size-specific styles
    const getSizeStyles = (modalSize: string) => {
      switch (modalSize) {
        case "sm":
          return "max-w-sm"
        case "md":
          return "max-w-md"
        case "lg":
          return "max-w-lg"
        case "xl":
          return "max-w-xl"
        case "full":
          return "max-w-[95vw] max-h-[95vh]"
        default:
          return "max-w-md"
      }
    }

    const sizeStyles = getSizeStyles(size)

    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
        <DialogContent
          ref={ref}
          className={cn(
            sizeStyles,
            loading && "pointer-events-none",
            className
          )}
          {...props}
        >
          {loading && (
            <div className="absolute inset-0 bg-background/50 flex items-center justify-center rounded-lg z-50">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          )}
          
          {(title || description) && (
            <DialogHeader>
              {title && <DialogTitle>{title}</DialogTitle>}
              {description && <DialogDescription>{description}</DialogDescription>}
            </DialogHeader>
          )}
          
          <div className="flex-1">
            {children}
          </div>
        </DialogContent>
      </Dialog>
    )
  }
)

Modal.displayName = "SemanticModal"

// Modal with actions
export interface ModalWithActionsProps extends SemanticModalProps {
  actions?: ModalActions
  onConfirm?: () => void
  onCancel?: () => void
  confirmLabel?: string
  cancelLabel?: string
  confirmLoading?: boolean
  cancelLoading?: boolean
  confirmDisabled?: boolean
  cancelDisabled?: boolean
  confirmVariant?: "primary" | "secondary" | "success" | "warning" | "danger"
  cancelVariant?: "primary" | "secondary" | "ghost" | "outline"
}

const ModalWithActions = React.forwardRef<HTMLDivElement, ModalWithActionsProps>(
  ({ 
    actions,
    onConfirm,
    onCancel,
    confirmLabel = "Confirm",
    cancelLabel = "Cancel",
    confirmLoading = false,
    cancelLoading = false,
    confirmDisabled = false,
    cancelDisabled = false,
    confirmVariant = "primary",
    cancelVariant = "outline",
    ...props 
  }, ref) => {
    const handleConfirm = () => {
      if (onConfirm) {
        onConfirm()
      } else if (actions?.primary?.onClick) {
        actions.primary.onClick()
      }
    }

    const handleCancel = () => {
      if (onCancel) {
        onCancel()
      } else if (actions?.cancel?.onClick) {
        actions.cancel.onClick()
      } else if (actions?.secondary?.onClick) {
        actions.secondary.onClick()
      }
    }

    const primaryAction = actions?.primary || {
      label: confirmLabel,
      onClick: handleConfirm,
      loading: confirmLoading,
      disabled: confirmDisabled,
      variant: confirmVariant
    }

    const secondaryAction = actions?.secondary || actions?.cancel || {
      label: cancelLabel,
      onClick: handleCancel,
      loading: cancelLoading,
      disabled: cancelDisabled,
      variant: cancelVariant
    }

    return (
      <Modal ref={ref} {...props}>
        <DialogFooter className="flex gap-2">
          {secondaryAction && (
            <Button
              variant={secondaryAction.variant || "outline"}
              onClick={secondaryAction.onClick}
              disabled={secondaryAction.disabled || secondaryAction.loading}
              loading={secondaryAction.loading}
            >
              {secondaryAction.label}
            </Button>
          )}
          
          {primaryAction && (
            <Button
              variant={primaryAction.variant || "default"}
              onClick={primaryAction.onClick}
              disabled={primaryAction.disabled || primaryAction.loading}
              loading={primaryAction.loading}
            >
              {primaryAction.label}
            </Button>
          )}
        </DialogFooter>
      </Modal>
    )
  }
)

ModalWithActions.displayName = "SemanticModalWithActions"

export { Modal, ModalWithActions }
export type { SemanticModalProps, ModalWithActionsProps, ModalActions }
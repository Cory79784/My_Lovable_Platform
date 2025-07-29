# Semantic UI Components

基于 shadcn/ui 的语义化组件封装，提供更直观的 API 和业务语义。

## 组件列表

### Button 语义化按钮

```tsx
import { Button } from "@/components/ui/semantic"

// 基础用法
<Button variant="primary">Primary Button</Button>
<Button variant="success">Success Button</Button>
<Button variant="warning">Warning Button</Button>
<Button variant="danger">Danger Button</Button>

// 带图标
<Button icon={<PlusIcon />} iconPosition="left">
  Add Item
</Button>

// 加载状态
<Button loading>Loading...</Button>
```

**Props:**
- `variant`: "primary" | "secondary" | "success" | "warning" | "danger" | "ghost" | "outline"
- `size`: "sm" | "md" | "lg" | "xl"
- `loading`: boolean
- `icon`: React.ReactNode
- `iconPosition`: "left" | "right"

### Card 语义化卡片

```tsx
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/semantic"

// 基础用法
<Card variant="elevated">
  <CardHeader title="Card Title" subtitle="Card description" />
  <CardContent>Card content goes here</CardContent>
  <CardFooter>Card footer</CardFooter>
</Card>

// 交互式卡片
<Card variant="interactive" hover>
  <CardHeader 
    title="Interactive Card" 
    avatar={<Avatar />}
    actions={<Button>Action</Button>}
  />
</Card>
```

**Props:**
- `variant`: "default" | "elevated" | "outlined" | "filled" | "interactive"
- `padding`: "none" | "sm" | "md" | "lg"
- `hover`: boolean
- `selected`: boolean
- `loading`: boolean

### Input 语义化输入框

```tsx
import { Input } from "@/components/ui/semantic"

// 基础用法
<Input 
  label="Email"
  placeholder="Enter your email"
  required
/>

// 带图标
<Input 
  label="Search"
  leftIcon={<SearchIcon />}
  rightIcon={<ClearIcon />}
/>

// 错误状态
<Input 
  label="Password"
  type="password"
  error="Password is required"
/>
```

**Props:**
- `variant`: "default" | "filled" | "outlined" | "minimal"
- `size`: "sm" | "md" | "lg"
- `label`: string
- `error`: string
- `helperText`: string
- `leftIcon`: React.ReactNode
- `rightIcon`: React.ReactNode
- `loading`: boolean
- `required`: boolean

### Modal 语义化模态框

```tsx
import { Modal, ModalWithActions } from "@/components/ui/semantic"

// 基础模态框
<Modal 
  title="Confirm Action"
  description="Are you sure you want to proceed?"
  trigger={<Button>Open Modal</Button>}
>
  <p>Modal content goes here</p>
</Modal>

// 带操作的模态框
<ModalWithActions
  title="Delete Item"
  description="This action cannot be undone."
  confirmLabel="Delete"
  cancelLabel="Cancel"
  onConfirm={handleDelete}
  onCancel={handleCancel}
  confirmVariant="danger"
>
  <p>Are you sure you want to delete this item?</p>
</ModalWithActions>
```

**Props:**
- `variant`: "default" | "alert" | "confirm" | "form"
- `size`: "sm" | "md" | "lg" | "xl" | "full"
- `loading`: boolean
- `actions`: ModalActions
- `onConfirm`: () => void
- `onCancel`: () => void

## 使用示例

### 表单卡片
```tsx
import { Card, CardHeader, CardContent, Input, Button } from "@/components/ui/semantic"

<Card variant="elevated">
  <CardHeader title="User Profile" subtitle="Update your information" />
  <CardContent className="space-y-4">
    <Input label="Name" placeholder="Enter your name" required />
    <Input label="Email" type="email" placeholder="Enter your email" required />
    <Input label="Phone" placeholder="Enter your phone number" />
  </CardContent>
  <CardFooter>
    <Button variant="secondary">Cancel</Button>
    <Button variant="primary">Save Changes</Button>
  </CardFooter>
</Card>
```

### 确认对话框
```tsx
import { ModalWithActions } from "@/components/ui/semantic"

<ModalWithActions
  title="Delete Project"
  description="This will permanently delete the project and all its files."
  confirmLabel="Delete Project"
  cancelLabel="Cancel"
  confirmVariant="danger"
  onConfirm={handleDeleteProject}
  onCancel={handleCancel}
>
  <div className="space-y-2">
    <p>Project: My Awesome Project</p>
    <p className="text-sm text-muted-foreground">
      This action cannot be undone. All project files will be permanently deleted.
    </p>
  </div>
</ModalWithActions>
```

## 设计原则

1. **语义化**: 组件 API 使用业务语义而非技术语义
2. **一致性**: 所有组件遵循统一的设计模式
3. **可扩展**: 基于 shadcn/ui，保持底层组件的灵活性
4. **易用性**: 提供合理的默认值和简化的 API
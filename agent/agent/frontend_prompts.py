"""
Frontend-specific prompt management for the ReAct agent.

This module manages prompts specifically designed for frontend development tasks,
integrating with the prompt files created earlier.
"""

from pathlib import Path
from typing import Dict, Optional, Any
import logging


class FrontendPromptManager:
    """
    Manages frontend-specific prompts and templates for the ReAct agent.
    """

    def __init__(self, prompts_path: Optional[Path] = None):
        """Initialize the frontend prompt manager."""
        if prompts_path is None:
            prompts_path = Path(__file__).parent.parent / "prompts"
        
        self.prompts_path = Path(prompts_path)
        self.logger = logging.getLogger("frontend_prompt_manager")
        self._prompts_cache: Dict[str, str] = {}
        
        # Load all prompts
        self._load_prompts()

    def _load_prompts(self):
        """Load all prompt files into cache."""
        if not self.prompts_path.exists():
            self.logger.warning(f"Prompts directory not found: {self.prompts_path}")
            return

        prompt_files = [
            "design_system",
            "component_structure", 
            "styling_approach",
            "interaction_patterns",
            "responsive_design"
        ]

        for prompt_name in prompt_files:
            prompt_file = self.prompts_path / prompt_name
            if prompt_file.exists():
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        self._prompts_cache[prompt_name] = f.read()
                    self.logger.debug(f"Loaded prompt: {prompt_name}")
                except Exception as e:
                    self.logger.error(f"Error loading prompt {prompt_name}: {e}")
            else:
                self.logger.warning(f"Prompt file not found: {prompt_file}")

    def get_prompt(self, prompt_name: str) -> Optional[str]:
        """Get a specific prompt by name."""
        return self._prompts_cache.get(prompt_name)

    def get_design_system_prompt(self) -> str:
        """Get the design system prompt."""
        return self.get_prompt("design_system") or self._get_default_design_system_prompt()

    def get_component_structure_prompt(self) -> str:
        """Get the component structure prompt."""
        return self.get_prompt("component_structure") or self._get_default_component_prompt()

    def get_styling_approach_prompt(self) -> str:
        """Get the styling approach prompt."""
        return self.get_prompt("styling_approach") or self._get_default_styling_prompt()

    def get_interaction_patterns_prompt(self) -> str:
        """Get the interaction patterns prompt."""
        return self.get_prompt("interaction_patterns") or self._get_default_interaction_prompt()

    def get_responsive_design_prompt(self) -> str:
        """Get the responsive design prompt."""
        return self.get_prompt("responsive_design") or self._get_default_responsive_prompt()

    def get_task_specific_prompt(self, task_type: str, context: Dict[str, Any] = None) -> str:
        """
        Get a task-specific prompt based on the type of frontend development task.
        
        Args:
            task_type: Type of task (e.g., 'create_component', 'responsive_layout', etc.)
            context: Additional context for the task
        """
        context = context or {}
        
        task_prompts = {
            "create_component": self._build_component_creation_prompt(context),
            "responsive_layout": self._build_responsive_layout_prompt(context),
            "styling_task": self._build_styling_task_prompt(context),
            "interaction_task": self._build_interaction_task_prompt(context),
            "performance_optimization": self._build_performance_optimization_prompt(context),
            "accessibility_audit": self._build_accessibility_audit_prompt(context),
            "cross_browser_testing": self._build_cross_browser_testing_prompt(context)
        }
        
        return task_prompts.get(task_type, self._build_generic_frontend_prompt(context))

    def _build_component_creation_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for component creation tasks."""
        component_type = context.get("component_type", "UI component")
        framework = context.get("framework", "vanilla JavaScript")
        
        base_prompt = self.get_component_structure_prompt()
        
        specific_guidance = f"""
## Component Creation Task

You are creating a {component_type} using {framework}.

### Specific Requirements:
- Follow component-based architecture principles
- Ensure proper prop validation and type checking
- Implement proper state management
- Include accessibility features (ARIA labels, keyboard navigation)
- Write clean, maintainable code
- Follow naming conventions for the chosen framework
- Include error handling and edge cases
- Consider performance implications

### Deliverables:
1. Component code with proper structure
2. Styling (CSS/SCSS/styled-components as appropriate)
3. Usage examples
4. Props/API documentation
5. Unit tests (if applicable)

{base_prompt}
"""
        return specific_guidance

    def _build_responsive_layout_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for responsive layout tasks."""
        breakpoints = context.get("breakpoints", ["mobile", "tablet", "desktop"])
        approach = context.get("approach", "mobile-first")
        
        base_prompt = self.get_responsive_design_prompt()
        
        specific_guidance = f"""
## Responsive Layout Task

Create a responsive layout using a {approach} approach for these breakpoints: {', '.join(breakpoints)}.

### Key Considerations:
- Use CSS Grid and Flexbox appropriately
- Implement fluid typography with clamp() or viewport units
- Ensure touch-friendly interface on mobile devices
- Optimize images for different screen densities
- Test layout at various viewport sizes
- Consider container queries for component-level responsiveness
- Maintain visual hierarchy across all breakpoints

### Tools and Techniques:
- CSS Grid for 2D layouts
- Flexbox for 1D layouts and alignment
- CSS Custom Properties for theme consistency
- Media queries with logical breakpoints
- Relative units (rem, em, %, vw, vh)
- Modern CSS features (aspect-ratio, gap, etc.)

{base_prompt}
"""
        return specific_guidance

    def _build_styling_task_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for styling-related tasks."""
        methodology = context.get("methodology", "BEM")
        preprocessor = context.get("preprocessor", "CSS")
        
        base_prompt = self.get_styling_approach_prompt()
        
        specific_guidance = f"""
## Styling Task

Implement styling using {methodology} methodology with {preprocessor}.

### Styling Goals:
- Create maintainable and scalable CSS architecture
- Follow {methodology} naming conventions
- Implement consistent visual design system
- Ensure cross-browser compatibility
- Optimize for performance (minimize reflows/repaints)
- Use modern CSS features appropriately
- Consider dark mode and theming support

### Best Practices:
- Avoid deep nesting (max 3 levels)
- Use semantic class names
- Group related styles logically
- Implement efficient selectors
- Use CSS custom properties for theming
- Consider cascade and specificity carefully

{base_prompt}
"""
        return specific_guidance

    def _build_interaction_task_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for interaction-related tasks."""
        interaction_type = context.get("interaction_type", "general")
        
        base_prompt = self.get_interaction_patterns_prompt()
        
        specific_guidance = f"""
## User Interaction Task

Implement {interaction_type} interactions with focus on usability and accessibility.

### Interaction Requirements:
- Provide immediate feedback for user actions
- Implement proper loading states
- Handle error states gracefully
- Ensure keyboard accessibility
- Support touch and mouse interactions
- Follow WCAG guidelines for accessibility
- Implement proper focus management
- Consider gesture support for mobile devices

### Technical Implementation:
- Use event delegation for dynamic content
- Implement debouncing for performance
- Handle async operations properly
- Provide clear visual feedback
- Test across different input methods
- Consider offline scenarios

{base_prompt}
"""
        return specific_guidance

    def _build_performance_optimization_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for performance optimization tasks."""
        target_metrics = context.get("target_metrics", ["LCP", "FID", "CLS"])
        
        return f"""
## Performance Optimization Task

Optimize frontend performance focusing on: {', '.join(target_metrics)}.

### Performance Strategies:
1. **Critical Resource Optimization**
   - Minimize critical render path
   - Inline critical CSS
   - Preload important resources
   - Use resource hints (prefetch, preconnect)

2. **JavaScript Optimization**
   - Code splitting and lazy loading
   - Tree shaking unused code
   - Minimize and compress bundles
   - Use service workers for caching

3. **Image Optimization**
   - Use modern formats (WebP, AVIF)
   - Implement responsive images
   - Lazy load off-screen images
   - Optimize image compression

4. **CSS Optimization**
   - Remove unused CSS
   - Use CSS containment
   - Optimize animations (prefer transform/opacity)
   - Minimize reflows and repaints

5. **Network Optimization**
   - Enable compression (gzip/brotli)
   - Use CDN for static assets
   - Implement proper caching strategies
   - Minimize HTTP requests

### Measurement Tools:
- Lighthouse audits
- WebPageTest
- Chrome DevTools Performance panel
- Real User Monitoring (RUM)
"""

    def _build_accessibility_audit_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for accessibility audit tasks."""
        return """
## Accessibility Audit Task

Conduct a comprehensive accessibility audit following WCAG 2.1 AA guidelines.

### Audit Areas:
1. **Semantic HTML**
   - Proper heading hierarchy (h1-h6)
   - Semantic elements (nav, main, section, article)
   - Form labels and fieldsets
   - Lists for grouped content

2. **Keyboard Navigation**
   - All interactive elements focusable
   - Logical tab order
   - Visible focus indicators
   - Skip links for navigation

3. **Screen Reader Support**
   - ARIA labels and descriptions
   - Live regions for dynamic content
   - Proper roles and states
   - Alternative text for images

4. **Visual Design**
   - Color contrast ratios (4.5:1 for normal text)
   - Text scalability up to 200%
   - No information conveyed by color alone
   - Motion preferences respected

5. **User Control**
   - Auto-playing content can be paused
   - Time limits can be extended
   - Flashing content avoided
   - User preferences respected

### Testing Methods:
- Automated testing (axe, WAVE)
- Manual keyboard navigation
- Screen reader testing
- User testing with disabilities
"""

    def _build_cross_browser_testing_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for cross-browser testing tasks."""
        target_browsers = context.get("browsers", ["Chrome", "Firefox", "Safari", "Edge"])
        
        return f"""
## Cross-Browser Testing Task

Test compatibility across: {', '.join(target_browsers)}.

### Testing Strategy:
1. **Feature Detection**
   - Use @supports for CSS features
   - Feature detection in JavaScript
   - Progressive enhancement approach
   - Graceful degradation for older browsers

2. **Browser-Specific Issues**
   - CSS vendor prefixes
   - JavaScript API differences
   - Layout engine quirks
   - Performance variations

3. **Testing Areas**
   - Visual consistency
   - Functionality across browsers
   - Performance benchmarks
   - Responsive behavior
   - Form validation
   - JavaScript interactions

4. **Tools and Techniques**
   - BrowserStack or Sauce Labs
   - Local browser testing
   - Automated cross-browser testing
   - CSS and JS linting
   - Polyfills for missing features

### Common Issues to Check:
- CSS Grid and Flexbox support
- JavaScript ES6+ features
- Form input types and validation
- CSS custom properties
- Intersection Observer API
- Service Worker support
"""

    def _build_generic_frontend_prompt(self, context: Dict[str, Any]) -> str:
        """Build a generic frontend development prompt."""
        return """
## Frontend Development Task

Apply frontend development best practices to complete this task.

### General Guidelines:
- Write semantic, accessible HTML
- Use modern CSS techniques (Grid, Flexbox, Custom Properties)
- Implement responsive design principles
- Follow progressive enhancement
- Optimize for performance
- Ensure cross-browser compatibility
- Test thoroughly across devices
- Write maintainable, documented code

### Quality Checklist:
- [ ] Semantic HTML structure
- [ ] Responsive design implementation
- [ ] Accessibility compliance
- [ ] Performance optimization
- [ ] Cross-browser testing
- [ ] Code documentation
- [ ] Error handling
- [ ] User experience considerations
"""

    # Default prompts (fallbacks if files are not available)
    def _get_default_design_system_prompt(self) -> str:
        """Get default design system prompt."""
        return """
Follow modern design system principles:
- Consistent typography and spacing
- Accessible color contrasts
- Reusable component patterns
- Responsive design approach
"""

    def _get_default_component_prompt(self) -> str:
        """Get default component structure prompt."""
        return """
Create well-structured components:
- Single responsibility principle
- Proper prop interfaces
- Accessibility considerations
- Performance optimization
"""

    def _get_default_styling_prompt(self) -> str:
        """Get default styling approach prompt."""
        return """
Use modern CSS techniques:
- CSS Grid and Flexbox for layouts
- Custom properties for theming
- Mobile-first responsive design
- BEM methodology for naming
"""

    def _get_default_interaction_prompt(self) -> str:
        """Get default interaction patterns prompt."""
        return """
Implement accessible interactions:
- Keyboard navigation support
- Touch-friendly interfaces
- Clear feedback for user actions
- Error handling and validation
"""

    def _get_default_responsive_prompt(self) -> str:
        """Get default responsive design prompt."""
        return """
Create responsive layouts:
- Mobile-first approach
- Flexible grid systems
- Fluid typography
- Optimized images for different screens
"""

    def list_available_prompts(self) -> Dict[str, str]:
        """List all available prompts with descriptions."""
        return {
            "design_system": "Guidelines for creating consistent design systems",
            "component_structure": "Best practices for component architecture",
            "styling_approach": "Modern CSS methodologies and techniques",
            "interaction_patterns": "User interaction and accessibility patterns",
            "responsive_design": "Mobile-first responsive design principles"
        }

    def reload_prompts(self):
        """Reload all prompts from files."""
        self._prompts_cache.clear()
        self._load_prompts()
        self.logger.info("Reloaded all frontend prompts")
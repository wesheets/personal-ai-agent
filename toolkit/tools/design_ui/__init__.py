"""
Design & UI Tools

This module provides tools for design and UI-related tasks including logo generation,
color palette suggestions, CSS styling, UI component scaffolding, and responsive layouts.
"""

import base64
import json
import random
from typing import Dict, List, Any, Optional
import colorsys

# Import the registry for tool registration
from ...registry import register_tool


def logo_generate(name: str, style: str = "minimal", format: str = "svg") -> Dict[str, Any]:
    """
    Generate a logo based on the provided name and style.
    
    Args:
        name: The name to use in the logo
        style: The style of the logo (minimal, modern, vintage, etc.)
        format: The format of the logo (svg, png)
        
    Returns:
        A dictionary containing the logo data and metadata
    """
    # In a real implementation, this would call a design API or ML model
    # For now, we'll return a placeholder with metadata
    
    # Generate a simple SVG as a placeholder
    svg_content = f"""<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect width="200" height="100" fill="#f0f0f0" />
        <text x="50%" y="50%" font-family="Arial" font-size="24" text-anchor="middle" dominant-baseline="middle" fill="#333">{name}</text>
        <style>text {{ font-weight: bold; }}</style>
    </svg>"""
    
    # Encode as base64
    base64_data = base64.b64encode(svg_content.encode()).decode()
    
    return {
        "logo_data": base64_data,
        "format": format,
        "style": style,
        "name": name,
        "data_url": f"data:image/svg+xml;base64,{base64_data}"
    }


def brand_palette_suggest(base_color: Optional[str] = None, palette_type: str = "complementary") -> Dict[str, Any]:
    """
    Suggest a color palette based on a base color and palette type.
    
    Args:
        base_color: The base color in HEX format (e.g., "#FF5733")
        palette_type: The type of palette to generate (complementary, analogous, triadic, etc.)
        
    Returns:
        A dictionary containing the color palette and metadata
    """
    # Generate a base color if none provided
    if not base_color:
        r, g, b = random.random(), random.random(), random.random()
        base_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    else:
        # Parse the hex color
        base_color = base_color.lstrip('#')
        r, g, b = int(base_color[0:2], 16) / 255, int(base_color[2:4], 16) / 255, int(base_color[4:6], 16) / 255
    
    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Generate palette based on type
    colors = []
    if palette_type == "complementary":
        # Base color
        colors.append((r, g, b))
        # Complementary color (opposite on the color wheel)
        h_comp = (h + 0.5) % 1.0
        r_comp, g_comp, b_comp = colorsys.hsv_to_rgb(h_comp, s, v)
        colors.append((r_comp, g_comp, b_comp))
        # Add some neutrals
        colors.append((0.9, 0.9, 0.9))  # Light gray
        colors.append((0.2, 0.2, 0.2))  # Dark gray
        colors.append((0.98, 0.98, 0.98))  # Off-white
    elif palette_type == "analogous":
        # Base color and analogous colors (adjacent on the color wheel)
        for i in range(-2, 3):
            h_analog = (h + 0.1 * i) % 1.0
            r_analog, g_analog, b_analog = colorsys.hsv_to_rgb(h_analog, s, v)
            colors.append((r_analog, g_analog, b_analog))
    elif palette_type == "triadic":
        # Three colors evenly spaced on the color wheel
        for i in range(3):
            h_triad = (h + i/3) % 1.0
            r_triad, g_triad, b_triad = colorsys.hsv_to_rgb(h_triad, s, v)
            colors.append((r_triad, g_triad, b_triad))
        # Add some neutrals
        colors.append((0.9, 0.9, 0.9))  # Light gray
        colors.append((0.2, 0.2, 0.2))  # Dark gray
    else:
        # Default to monochromatic
        for i in range(5):
            # Vary the saturation and value
            s_mono = max(0, min(1, s - 0.15 + i * 0.1))
            v_mono = max(0, min(1, v - 0.3 + i * 0.15))
            r_mono, g_mono, b_mono = colorsys.hsv_to_rgb(h, s_mono, v_mono)
            colors.append((r_mono, g_mono, b_mono))
    
    # Convert colors to hex
    hex_colors = [f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}" for r, g, b in colors]
    
    return {
        "base_color": f"#{int(colors[0][0]*255):02x}{int(colors[0][1]*255):02x}{int(colors[0][2]*255):02x}",
        "palette_type": palette_type,
        "colors": hex_colors,
        "color_names": [f"Color {i+1}" for i in range(len(hex_colors))],
        "rgb_values": [{"r": int(r*255), "g": int(g*255), "b": int(b*255)} for r, g, b in colors]
    }


def css_style_generate(element_type: str, style: str = "modern", color_palette: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate CSS styles for a specific element type.
    
    Args:
        element_type: The type of element to style (button, card, header, etc.)
        style: The style to apply (modern, minimal, retro, etc.)
        color_palette: Optional list of colors to use in the styles
        
    Returns:
        A dictionary containing the CSS styles and metadata
    """
    # Generate a color palette if none provided
    if not color_palette:
        palette_result = brand_palette_suggest(palette_type="complementary")
        color_palette = palette_result["colors"]
    
    # Define style templates for different element types
    css_templates = {
        "button": {
            "modern": """
.button {
    background-color: {{primary_color}};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 10px 20px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.3s ease;
}
.button:hover {
    background-color: {{secondary_color}};
}
""",
            "minimal": """
.button {
    background-color: transparent;
    color: {{primary_color}};
    border: 1px solid {{primary_color}};
    border-radius: 4px;
    padding: 8px 16px;
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    cursor: pointer;
    transition: all 0.2s ease;
}
.button:hover {
    background-color: {{primary_color}};
    color: white;
}
"""
        },
        "card": {
            "modern": """
.card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
}
.card-title {
    color: {{primary_color}};
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 10px;
}
.card-content {
    color: #333;
    font-size: 14px;
    line-height: 1.5;
}
""",
            "minimal": """
.card {
    background-color: {{neutral_color}};
    border: 1px solid #eaeaea;
    border-radius: 4px;
    padding: 16px;
    margin-bottom: 16px;
}
.card-title {
    color: #333;
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 8px;
}
.card-content {
    color: #666;
    font-size: 14px;
    line-height: 1.4;
}
"""
        }
    }
    
    # Get the template for the requested element and style
    template = css_templates.get(element_type, {}).get(style, """
/* Default style */
.{{element_type}} {
    color: {{primary_color}};
    padding: 10px;
    margin: 10px 0;
}
""")
    
    # Replace placeholders with actual values
    css = template.replace("{{element_type}}", element_type)
    css = css.replace("{{primary_color}}", color_palette[0])
    css = css.replace("{{secondary_color}}", color_palette[1] if len(color_palette) > 1 else color_palette[0])
    css = css.replace("{{neutral_color}}", color_palette[2] if len(color_palette) > 2 else "#f5f5f5")
    
    # Generate Tailwind equivalent
    tailwind_classes = ""
    if element_type == "button":
        if style == "modern":
            tailwind_classes = f"bg-[{color_palette[0]}] text-white py-2 px-4 rounded font-medium hover:bg-[{color_palette[1]}] transition-colors"
        else:
            tailwind_classes = f"bg-transparent text-[{color_palette[0]}] border border-[{color_palette[0]}] py-2 px-4 rounded hover:bg-[{color_palette[0]}] hover:text-white transition-all"
    elif element_type == "card":
        if style == "modern":
            tailwind_classes = f"bg-white rounded-lg shadow-md p-5 mb-5"
        else:
            tailwind_classes = f"bg-[{color_palette[2] if len(color_palette) > 2 else '#f5f5f5'}] border border-gray-200 rounded p-4 mb-4"
    
    return {
        "element_type": element_type,
        "style": style,
        "css": css.strip(),
        "tailwind": tailwind_classes,
        "color_palette": color_palette
    }


def ui_component_scaffold(component_type: str, framework: str = "react", props: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate a UI component scaffold for a specific framework.
    
    Args:
        component_type: The type of component to generate (button, card, form, etc.)
        framework: The framework to use (react, vue, angular, etc.)
        props: Optional properties to include in the component
        
    Returns:
        A dictionary containing the component code and metadata
    """
    # Default props if none provided
    if not props:
        props = {
            "button": {"text": "Click me", "onClick": "handleClick", "variant": "primary"},
            "card": {"title": "Card Title", "content": "Card content goes here", "footer": "Card Footer"},
            "form": {"fields": ["name", "email", "message"], "onSubmit": "handleSubmit"}
        }.get(component_type, {})
    
    # Component templates for different frameworks
    templates = {
        "react": {
            "button": """
import React from 'react';
import './Button.css';

interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
  text, 
  onClick, 
  variant = 'primary', 
  disabled = false 
}) => {
  return (
    <button 
      className={`button ${variant}`} 
      onClick={onClick}
      disabled={disabled}
    >
      {text}
    </button>
  );
};

export default Button;
""",
            "card": """
import React from 'react';
import './Card.css';

interface CardProps {
  title: string;
  content: React.ReactNode;
  footer?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, content, footer }) => {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="card-content">{content}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
};

export default Card;
"""
        },
        "vue": {
            "button": """
<template>
  <button 
    :class="['button', variant]" 
    @click="onClick"
    :disabled="disabled"
  >
    {{ text }}
  </button>
</template>

<script>
export default {
  name: 'Button',
  props: {
    text: {
      type: String,
      required: true
    },
    onClick: {
      type: Function,
      required: true
    },
    variant: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'outline'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.button {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}
.primary {
  background-color: #3498db;
  color: white;
  border: none;
}
.secondary {
  background-color: #2ecc71;
  color: white;
  border: none;
}
.outline {
  background-color: transparent;
  color: #3498db;
  border: 1px solid #3498db;
}
.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
""",
            "card": """
<template>
  <div class="card">
    <div class="card-title">{{ title }}</div>
    <div class="card-content">{{ content }}</div>
    <div v-if="footer" class="card-footer">{{ footer }}</div>
  </div>
</template>

<script>
export default {
  name: 'Card',
  props: {
    title: {
      type: String,
      required: true
    },
    content: {
      type: String,
      required: true
    },
    footer: {
      type: String,
      default: null
    }
  }
}
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}
.card-content {
  font-size: 14px;
  line-height: 1.5;
  color: #666;
}
.card-footer {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  font-size: 14px;
  color: #888;
}
</style>
"""
        }
    }
    
    # Get the template for the requested component and framework
    template = templates.get(framework, {}).get(component_type, f"""
// Default {framework} {component_type} component
// This is a placeholder for a {component_type} component
""")
    
    # For HTML/CSS only
    if framework == "html":
        if component_type == "button":
            template = """
<button class="button">Click me</button>

<style>
.button {
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  font-family: 'Arial', sans-serif;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.button:hover {
  background-color: #2980b9;
}
</style>
"""
        elif component_type == "card":
            template = """
<div class="card">
  <div class="card-title">Card Title</div>
  <div class="card-content">Card content goes here</div>
  <div class="card-footer">Card Footer</div>
</div>

<style>
.card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
  max-width: 400px;
}
.card-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}
.card-content {
  font-size: 14px;
  line-height: 1.5;
  color: #666;
  margin-bottom: 15px;
}
.card-footer {
  padding-top: 15px;
  border-top: 1px solid #eee;
  font-size: 14px;
  color: #888;
}
</style>
"""
    
    return {
        "component_type": component_type,
        "framework": framework,
        "props": props,
        "code": template.strip(),
        "file_extension": ".tsx" if framework == "react" else ".vue" if framework == "vue" else ".html"
    }


def responsive_layout_create(layout_type: str, columns: int = 12, breakpoints: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate a responsive layout structure.
    
    Args:
        layout_type: The type of layout to generate (grid, flexbox)
        columns: The number of columns in the grid
        breakpoints: Optional list of breakpoints to use
        
    Returns:
        A dictionary containing the layout code and metadata
    """
    # Default breakpoints if none provided
    if not breakpoints:
        breakpoints = ["sm", "md", "lg", "xl"]
    
    # Define breakpoint values
    breakpoint_values = {
        "xs": "0px",
        "sm": "576px",
        "md": "768px",
        "lg": "992px",
        "xl": "1200px",
        "2xl": "1400px"
    }
    
    # Generate CSS for the layout
    css = ""
    html = ""
    
    if layout_type == "grid":
        css = """
.container {
  width: 100%;
  padding-right: 15px;
  padding-left: 15px;
  margin-right: auto;
  margin-left: auto;
}

.row {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 20px;
}

/* Default column styles */
.col {
  grid-column: span 12;
}

"""
        # Add breakpoint-specific styles
        for bp in breakpoints:
            if bp in breakpoint_values:
                css += f"""
@media (min-width: {breakpoint_values[bp]}) {{
  .col-{bp}-1 {{ grid-column: span 1; }}
  .col-{bp}-2 {{ grid-column: span 2; }}
  .col-{bp}-3 {{ grid-column: span 3; }}
  .col-{bp}-4 {{ grid-column: span 4; }}
  .col-{bp}-6 {{ grid-column: span 6; }}
  .col-{bp}-8 {{ grid-column: span 8; }}
  .col-{bp}-12 {{ grid-column: span 12; }}
  
  .container {{
    max-width: {int(int(breakpoint_values[bp].replace('px', '')) * 0.95)}px;
  }}
}}
"""
        
        # Example HTML
        html = """
<div class="container">
  <div class="row">
    <div class="col col-md-6 col-lg-4">Column 1</div>
    <div class="col col-md-6 col-lg-4">Column 2</div>
    <div class="col col-md-12 col-lg-4">Column 3</div>
  </div>
</div>
"""
    
    elif layout_type == "flexbox":
        css = """
.container {
  width: 100%;
  padding-right: 15px;
  padding-left: 15px;
  margin-right: auto;
  margin-left: auto;
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin-right: -15px;
  margin-left: -15px;
}

.col {
  position: relative;
  width: 100%;
  padding-right: 15px;
  padding-left: 15px;
  flex-basis: 0;
  flex-grow: 1;
  max-width: 100%;
}

"""
        # Add breakpoint-specific styles
        for bp in breakpoints:
            if bp in breakpoint_values:
                css += f"""
@media (min-width: {breakpoint_values[bp]}) {{
  .col-{bp}-1 {{ flex: 0 0 8.333333%; max-width: 8.333333%; }}
  .col-{bp}-2 {{ flex: 0 0 16.666667%; max-width: 16.666667%; }}
  .col-{bp}-3 {{ flex: 0 0 25%; max-width: 25%; }}
  .col-{bp}-4 {{ flex: 0 0 33.333333%; max-width: 33.333333%; }}
  .col-{bp}-6 {{ flex: 0 0 50%; max-width: 50%; }}
  .col-{bp}-8 {{ flex: 0 0 66.666667%; max-width: 66.666667%; }}
  .col-{bp}-12 {{ flex: 0 0 100%; max-width: 100%; }}
  
  .container {{
    max-width: {int(int(breakpoint_values[bp].replace('px', '')) * 0.95)}px;
  }}
}}
"""
        
        # Example HTML
        html = """
<div class="container">
  <div class="row">
    <div class="col col-md-6 col-lg-4">Column 1</div>
    <div class="col col-md-6 col-lg-4">Column 2</div>
    <div class="col col-md-12 col-lg-4">Column 3</div>
  </div>
</div>
"""
    
    # Generate Tailwind equivalent
    tailwind_example = ""
    if layout_type == "grid":
        tailwind_example = """
<div class="container mx-auto px-4">
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="p-4 bg-gray-100">Column 1</div>
    <div class="p-4 bg-gray-100">Column 2</div>
    <div class="p-4 bg-gray-100 md:col-span-2 lg:col-span-1">Column 3</div>
  </div>
</div>
"""
    elif layout_type == "flexbox":
        tailwind_example = """
<div class="container mx-auto px-4">
  <div class="flex flex-wrap -mx-4">
    <div class="w-full md:w-1/2 lg:w-1/3 px-4 mb-4">Column 1</div>
    <div class="w-full md:w-1/2 lg:w-1/3 px-4 mb-4">Column 2</div>
    <div class="w-full lg:w-1/3 px-4 mb-4">Column 3</div>
  </div>
</div>
"""
    
    return {
        "layout_type": layout_type,
        "columns": columns,
        "breakpoints": breakpoints,
        "breakpoint_values": {bp: breakpoint_values[bp] for bp in breakpoints if bp in breakpoint_values},
        "css": css.strip(),
        "html_example": html.strip(),
        "tailwind_example": tailwind_example.strip()
    }


# Register all Design & UI tools
register_tool(
    name="logo.generate",
    description="Generate a logo based on the provided name and style",
    category="Design & UI",
    timeout_seconds=60,
    max_retries=2,
    requires_reflection=True,
    handler=logo_generate
)

register_tool(
    name="brand.palette.suggest",
    description="Suggest a color palette based on a base color and palette type",
    category="Design & UI",
    timeout_seconds=30,
    max_retries=3,
    requires_reflection=False,
    handler=brand_palette_suggest
)

register_tool(
    name="css.style.generate",
    description="Generate CSS styles for a specific element type",
    category="Design & UI",
    timeout_seconds=45,
    max_retries=3,
    requires_reflection=False,
    handler=css_style_generate
)

register_tool(
    name="ui.component.scaffold",
    description="Generate a UI component scaffold for a specific framework",
    category="Design & UI",
    timeout_seconds=60,
    max_retries=2,
    requires_reflection=True,
    handler=ui_component_scaffold
)

register_tool(
    name="responsive.layout.create",
    description="Generate a responsive layout structure",
    category="Design & UI",
    timeout_seconds=45,
    max_retries=3,
    requires_reflection=False,
    handler=responsive_layout_create
)

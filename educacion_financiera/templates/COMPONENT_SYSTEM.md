# Component System Documentation

## Overview

The component system provides a powerful and flexible way to create reusable UI components in Django templates, inspired by the allauth element and slot system. It supports both simple components and complex layouts with multiple slots.

## Features

- **Slot-based Architecture**: Define multiple content areas within components
- **Layout Detection**: Automatically adapts components based on current layout
- **Type Safety**: Separate element and layout component types
- **Flexible Attributes**: Pass any attributes to components
- **Nested Components**: Components can contain other components
- **Convenience Tags**: Simple tags for common components

## Directory Structure

```
templates/
└── components/
    ├── elements/          # UI elements (buttons, cards, alerts, etc.)
    │   ├── button.html
    │   ├── card.html
    │   ├── alert.html
    │   └── icon.html
    └── layout/            # Layout components (headers, sidebars, etc.)
        ├── header.html
        └── sidebar.html
```

## Basic Usage

### Loading the Template Tags

```django
{% load component %}
```

### Simple Component with Attributes

```django
{% component "button" text="Click me" variant="primary" size="lg" %}{% endcomponent %}
```

### Component with Slot Content

```django
{% component "button" variant="success" %}
  <i class="bi bi-check"></i> Success!
{% endcomponent %}
```

### Component with Multiple Slots

```django
{% component "card" title="My Card" %}
  {% slot "header" %}
    <div class="d-flex justify-content-between">
      <h5>Custom Header</h5>
      <button class="btn btn-sm btn-outline-secondary">Action</button>
    </div>
  {% endslot %}
  
  {% slot "body" %}
    <p>This is the card body content.</p>
  {% endslot %}
  
  {% slot "footer" %}
    <div class="text-end">
      <button class="btn btn-primary">Save</button>
    </div>
  {% endslot %}
{% endcomponent %}
```

## Layout Components

Layout components are specified by adding `"layout"` as the second argument:

```django
{% component "header" "layout" brand_text="My App" sticky=True %}
  {% slot "navigation" %}
    <ul class="navbar-nav">
      <li class="nav-item">
        <a class="nav-link" href="/">Home</a>
      </li>
    </ul>
  {% endslot %}
  
  {% slot "user_menu" %}
    <div class="dropdown">
      <!-- User menu content -->
    </div>
  {% endslot %}
{% endcomponent %}
```

## Simple Tags (No Slots)

For components that don't need slots, use the `render_component` tag:

```django
{% render_component "button" variant="primary" text="Simple Button" %}
{% render_component "alert" variant="success" message="Operation completed!" %}
```

## Convenience Tags

Some components have dedicated convenience tags:

```django
<!-- Icon tag -->
{% icon "user" size="lg" color="primary" %}

<!-- Button tag -->
{% button "Submit" variant="success" size="lg" %}
```

## Component Template Structure

### Element Component Template

```html
<!-- components/elements/button.html -->
<button 
  type="{{ attrs.type|default:'button' }}"
  class="btn btn-{{ attrs.variant|default:'primary' }} btn-{{ attrs.size|default:'md' }}{% if attrs.css_class %} {{ attrs.css_class }}{% endif %}"
  {% if attrs.id %}id="{{ attrs.id }}"{% endif %}
>
  {% if slots.default %}
    {% for slot_content in slots.default %}{{ slot_content|safe }}{% endfor %}
  {% elif attrs.text %}
    {{ attrs.text }}
  {% endif %}
</button>
```

### Layout Component Template

```html
<!-- components/layout/sidebar.html -->
<aside class="sidebar{% if attrs.css_class %} {{ attrs.css_class }}{% endif %}">
  {% if slots.header %}
    <div class="sidebar-header">
      {% for slot_content in slots.header %}{{ slot_content|safe }}{% endfor %}
    </div>
  {% endif %}

  <div class="sidebar-content">
    {% if slots.default %}
      {% for slot_content in slots.default %}{{ slot_content|safe }}{% endfor %}
    {% endif %}
  </div>
</aside>
```

## Available Context Variables

Component templates have access to:

- `attrs`: Dictionary of all passed attributes
- `slots`: Dictionary of slot content
- `component_name`: Name of the component
- `is_layout`: Boolean indicating if it's a layout component
- `layout`: Current layout name
- `request`: Django request object

## Layout-Specific Templates

Components can have layout-specific variants:

```
components/elements/button.html          # Default button
components/elements/button__admin.html   # Admin layout variant
components/elements/button__mobile.html  # Mobile layout variant
```

The system automatically selects the appropriate template based on the current layout.

## Best Practices

### 1. Component Naming

- Use descriptive, lowercase names with hyphens for multi-word components
- Examples: `button`, `card`, `user-avatar`, `course-progress`

### 2. Attribute Handling

- Always provide sensible defaults for attributes
- Use the `css_class` attribute for additional CSS classes
- Handle boolean attributes properly

```html
{% if attrs.disabled %}disabled{% endif %}
```

### 3. Slot Organization

- Use descriptive slot names: `header`, `body`, `footer`, `navigation`
- Always provide fallback content for optional slots
- Use the `default` slot for main content

### 4. Accessibility

- Include proper ARIA attributes
- Ensure keyboard navigation works
- Provide alt text for images

### 5. Performance

- Keep component templates lightweight
- Avoid complex logic in templates
- Use template fragments for repeated content

## Advanced Features

### Nested Components

Components can contain other components:

```django
{% component "card" %}
  {% slot "body" %}
    {% component "alert" variant="info" message="Nested alert" %}{% endcomponent %}
    {% component "button" text="Action" variant="primary" %}{% endcomponent %}
  {% endslot %}
{% endcomponent %}
```

### Dynamic Attributes

Pass dynamic values from context:

```django
{% component "button" variant=user.preferred_button_style text=button_text %}{% endcomponent %}
```

### Conditional Rendering

```django
{% if user.is_authenticated %}
  {% component "user-menu" user=user %}{% endcomponent %}
{% else %}
  {% component "login-button" %}{% endcomponent %}
{% endif %}
```

## Creating New Components

### 1. Create the Template

Create a new template in the appropriate directory:

```html
<!-- components/elements/progress-bar.html -->
<div class="progress{% if attrs.css_class %} {{ attrs.css_class }}{% endif %}" 
     style="height: {{ attrs.height|default:'1rem' }};">
  <div class="progress-bar bg-{{ attrs.variant|default:'primary' }}" 
       role="progressbar" 
       style="width: {{ attrs.value|default:0 }}%"
       aria-valuenow="{{ attrs.value|default:0 }}" 
       aria-valuemin="0" 
       aria-valuemax="100">
    {% if attrs.show_label %}{{ attrs.value|default:0 }}%{% endif %}
  </div>
</div>
```

### 2. Use the Component

```django
{% component "progress-bar" value=75 variant="success" show_label=True %}{% endcomponent %}
```

### 3. Add Convenience Tag (Optional)

```python
# In templatetags/component.py
@register.inclusion_tag("components/elements/progress-bar.html", takes_context=True)
def progress_bar(context, value=0, variant="primary", **kwargs):
    return {
        "value": value,
        "variant": variant,
        "attrs": kwargs,
        "request": context.get("request"),
    }
```

## Troubleshooting

### Component Not Found

- Check the template path: `components/elements/` or `components/layout/`
- Verify the component name matches the template filename
- Ensure the template file exists

### Slots Not Rendering

- Check slot names match between usage and template
- Verify the slot content is within the component tags
- Use `{% for slot_content in slots.slot_name %}{{ slot_content|safe }}{% endfor %}`

### Attributes Not Working

- Ensure attributes are accessed via `attrs.attribute_name`
- Check for typos in attribute names
- Verify boolean attributes are handled correctly

### Layout Detection Issues

- Set `page_layout` in your view context
- Check that layout templates follow the naming convention
- Verify the extends context is properly set

## Examples

See `templates/examples/component_demo.html` for comprehensive usage examples. 
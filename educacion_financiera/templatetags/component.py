from django import template
from django.template.base import FilterExpression, kwarg_re
from django.template.loader import render_to_string
from django.template.loader_tags import ExtendsNode
from django.utils.safestring import mark_safe


SLOTS_CONTEXT_KEY = "component_slots_context"
LAYOUT_CONTEXT_KEY = "component_layout_context"


def parse_component_tag(token, parser):
    """Parse component tag arguments and keyword arguments."""
    bits = token.split_contents()
    tag_name = bits.pop(0)
    args = []
    kwargs = {}
    for bit in bits:
        # Is this a kwarg or an arg?
        match = kwarg_re.match(bit)
        kwarg_format = match and match.group(1)
        if kwarg_format:
            key, value = match.groups()
            kwargs[key] = FilterExpression(value, parser)
        else:
            args.append(FilterExpression(bit, parser))

    return (tag_name, args, kwargs)


register = template.Library()


@register.tag(name="slot")
def do_component_slot(parser, token):
    """
    Define a slot within a component.
    Usage: {% slot "slot_name" %} content {% endslot %}
    """
    nodelist = parser.parse(("endslot",))
    bits = token.split_contents()
    bits.pop(0)
    slot_name = bits.pop(0) if bits else "default"
    parser.delete_first_token()
    return ComponentSlotNode(slot_name, nodelist)


class ComponentSlotNode(template.Node):
    def __init__(self, name, nodelist):
        self.name = name
        self.nodelist = nodelist

    def render(self, context):
        slots = context.render_context.get(SLOTS_CONTEXT_KEY)
        with context.push():
            if slots is None:
                # If we're not in a component context, check for slots in context
                if "slots" in context and self.name in context["slots"]:
                    return "".join(context["slots"][self.name])
                return self.nodelist.render(context)
            else:
                # We're in a component context, collect the slot content
                result = self.nodelist.render(context)
                slot_list = slots.setdefault(self.name, [])
                slot_list.append(result)
                return ""


@register.tag(name="component")
def do_component(parser, token):
    """
    Render a component with slots.
    Usage: {% component "component_name" argument=value %} slot content {% endcomponent %}

    The component will be searched in:
    1. components/elements/{component_name}__{layout}.html
    2. components/elements/{component_name}.html
    3. components/layout/{component_name}__{layout}.html (if layout type)
    4. components/layout/{component_name}.html (if layout type)
    """
    nodelist = parser.parse(("endcomponent",))
    tag_name, args, kwargs = parse_component_tag(token, parser)
    usage = f'{{% {tag_name} "component_name" argument=value %}} ... {{% end{tag_name} %}}'

    if len(args) < 1:
        raise template.TemplateSyntaxError("Usage: %s" % usage)

    parser.delete_first_token()
    return ComponentNode(nodelist, args[0], args[1:], kwargs)


class ComponentNode(template.Node):
    def __init__(self, nodelist, component_name, args, kwargs):
        self.component_name = component_name
        self.args = args
        self.kwargs = kwargs
        self.nodelist = nodelist

    def render(self, context):
        slots = {}

        # Resolve component name and arguments
        component_name = self.component_name.resolve(context)
        resolved_args = [arg.resolve(context) for arg in self.args]

        # Determine if this is a layout component
        is_layout = resolved_args and resolved_args[0] == "layout"

        # Get current layout context
        extends_context = context.render_context.get(ExtendsNode.context_key)
        layout = None

        if extends_context:
            # Extract layout from the {% extends %} tags
            for ec in extends_context:
                # Check for our custom layout templates
                if "layout/" in ec.template_name:
                    layout_part = ec.template_name.split("layout/")[-1]
                    layout = layout_part.replace(".html", "")
                    break

        if not layout:
            # Fallback to context layout
            layout = context.render_context.get(LAYOUT_CONTEXT_KEY)

        if not layout:
            # Or from page context
            layout = context.get("page_layout", "default")

        # Build template search paths
        template_names = []

        if is_layout:
            # For layout components, search in layout directory
            if layout:
                template_names.append(f"components/layout/{component_name}__{layout}.html")
            template_names.append(f"components/layout/{component_name}.html")
        else:
            # For element components, search in elements directory
            if layout:
                template_names.append(f"components/elements/{component_name}__{layout}.html")
            template_names.append(f"components/elements/{component_name}.html")

        # Render the component with slots context
        with context.render_context.push(
            **{SLOTS_CONTEXT_KEY: slots, LAYOUT_CONTEXT_KEY: layout}
        ):
            # Render the default slot content
            slots["default"] = [self.nodelist.render(context)]

            # Resolve keyword arguments
            attrs = {}
            for k, v in self.kwargs.items():
                attrs[k] = v.resolve(context)

            # Handle special attributes
            tags = attrs.get("tags")
            if tags:
                attrs["tags"] = [tag.strip() for tag in tags.split(",")]

            css_class = attrs.get("class")
            if css_class:
                attrs["css_class"] = css_class

            # Add component metadata
            component_context = {
                "attrs": attrs,
                "slots": slots,
                "component_name": component_name,
                "is_layout": is_layout,
                "layout": layout,
                "args": resolved_args,
            }

            return render_to_string(template_names, component_context, request=context.get("request"))


@register.tag(name="setvar")
def do_setvar(parser, token):
    """
    Set a variable in the template context.
    Usage: {% setvar "variable_name" %} content {% endsetvar %}
    """
    nodelist = parser.parse(("endsetvar",))
    bits = token.split_contents()
    if len(bits) != 2:
        tag_name = bits[0]
        usage = f'{{% {tag_name} "variable_name" %}} ... {{% end{tag_name} %}}'
        raise template.TemplateSyntaxError("Usage: %s" % usage)
    parser.delete_first_token()
    return SetVarNode(nodelist, bits[1])


class SetVarNode(template.Node):
    def __init__(self, nodelist, var):
        self.nodelist = nodelist
        self.var = var

    def render(self, context):
        context[self.var] = mark_safe(self.nodelist.render(context).strip())  # nosec
        return ""


@register.simple_tag(takes_context=True)
def render_component(context, component_name, component_type="element", **kwargs):
    """
    Simple tag version for rendering components without slots.
    Usage: {% render_component "button" class="btn-primary" text="Click me" %}
    Usage: {% render_component "header" "layout" title="Page Title" %}
    """
    # Determine template paths
    layout = context.get("page_layout", "default")

    template_names = []
    if component_type == "layout":
        if layout:
            template_names.append(f"components/layout/{component_name}__{layout}.html")
        template_names.append(f"components/layout/{component_name}.html")
    else:
        if layout:
            template_names.append(f"components/elements/{component_name}__{layout}.html")
        template_names.append(f"components/elements/{component_name}.html")

    # Prepare context
    component_context = {
        "attrs": kwargs,
        "component_name": component_name,
        "is_layout": component_type == "layout",
        "layout": layout,
    }

    return render_to_string(template_names, component_context, request=context.get("request"))


@register.inclusion_tag("components/elements/icon.html", takes_context=True)
def icon(context, name, size="md", color="current", **kwargs):
    """
    Convenience tag for rendering icons.
    Usage: {% icon "user" size="lg" color="primary" %}
    """
    return {
        "name": name,
        "size": size,
        "color": color,
        "attrs": kwargs,
        "request": context.get("request"),
    }


@register.inclusion_tag("components/elements/button.html", takes_context=True)
def button(context, text="", variant="primary", size="md", **kwargs):
    """
    Convenience tag for rendering buttons.
    Usage: {% button "Submit" variant="success" size="lg" %}
    """
    return {
        "text": text,
        "variant": variant,
        "size": size,
        "attrs": kwargs,
        "request": context.get("request"),
    }

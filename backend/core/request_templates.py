def render_payload(template, payload):
    """Replace placeholders inside decoded JSON values, never by interpolating JSON."""
    found = False

    def render(value):
        nonlocal found
        if isinstance(value, str):
            for marker in ("{{PAYLOAD}}", "{payload}"):
                if marker in value:
                    found = True
                    value = value.replace(marker, payload)
            return value
        if isinstance(value, list):
            return [render(item) for item in value]
        if isinstance(value, dict):
            return {key: render(item) for key, item in value.items()}
        return value

    rendered = render(template)
    if not found:
        raise ValueError("Custom request format must contain {{PAYLOAD}} or {payload}")
    return rendered

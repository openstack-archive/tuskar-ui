import re


def deCamelCase(text):
    """Convert CamelCase names to human-readable format."""
    CAMEL_RE = re.compile(r'([a-z]|SSL)([A-Z])')
    return CAMEL_RE.sub(lambda m: m.group(1) + ' ' + m.group(2), text)

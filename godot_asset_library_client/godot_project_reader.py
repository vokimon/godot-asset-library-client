from dataclasses import field
import re
from pathlib import Path

def from_project(field):
    # TODO: This is somewhat fragile
    patterns = dict(
        project_name = r'config/name="([^"]+)"',
        project_version = r'config/version="([^"]+)"',
        description = r'config/description="([^"]+)"',
        godot_version = r'config/features=PackedStringArray[(]"([^"]+)"',
        icon = r'config/icon="res:/([^"]+)"',
    )
    pattern = patterns[field]
    project_content = Path('project.godot').read_text()
    match =  re.search(pattern, project_content)
    if not match:
        return None
    return match.group(1)

def project_field(attribute, *args, **kwds):
    """
    A field that will be read from godot project file
    if not provided in config.
    """
    def factory():
        return from_project(attribute)
    return field(*args, default_factory=factory, **kwds)



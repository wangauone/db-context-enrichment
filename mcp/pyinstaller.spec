# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec for DB Context Enrichment MCP

This spec file is designed to be robust and self-updating.
It dynamically detects project dependencies from `importlib.metadata`
and collects necessary metadata and hooks (e.g. for google-auth).
"""

from PyInstaller.utils.hooks import copy_metadata, collect_all
import importlib.metadata
import re

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_direct_dependencies(package_name='db-context-enrichment'):
    """
    Returns a list of direct dependency package names from project metadata.
    Handles extra markers (e.g., test dependencies) and version specifiers.
    """
    try:
        requires = importlib.metadata.requires(package_name)
        if not requires:
            return []
        
        deps = []
        for req in requires:
            # Skip optional/test dependencies
            if "extra ==" in req:
                continue
            
            # Extract package name (e.g. "fastmcp>=2.0" -> "fastmcp")
            match = re.match(r"^([a-zA-Z0-9\-_]+)", req)
            if match:
                deps.append(match.group(1))
        return deps
    except importlib.metadata.PackageNotFoundError:
        print(f"WARNING: Could not find metadata for {package_name}. Using fallback list.")
        return ['fastmcp', 'mcp', 'google-genai', 'toolbox-core']

def collect_dynamic_resources():
    """
    Collects datas, binaries, and hiddenimports for the project.
    """
    datas = []
    binaries = []
    hiddenimports = []

    # 1. Project Assets
    datas.append(('prompts', 'prompts'))
    datas.append(('README.md', '.'))

    # 2. Dependency Metadata (Recursive)
    # Necessary for packages that use importlib.metadata at runtime (e.g. fastmcp, pydantic)
    dependencies = get_direct_dependencies()
    print(f"DEBUG: Collecting metadata for dependencies: {dependencies}")
    
    for dep in dependencies:
        try:
            # recursive=True ensures we get metadata for sub-dependencies (e.g. pydantic)
            datas += copy_metadata(dep, recursive=True)
        except Exception as e:
            print(f"WARNING: Failed to copy metadata for {dep}: {e}")

    # 3. Special Hook Collections
    # google.auth is needed by google-genai and has complex data/binary requirements
    ga_datas, ga_binaries, ga_hiddenimports = collect_all('google.auth')
    datas += ga_datas
    binaries += ga_binaries
    hiddenimports += ga_hiddenimports

    return datas, binaries, hiddenimports

# -----------------------------------------------------------------------------
# Main Build Configuration
# -----------------------------------------------------------------------------

# Collect all resources
project_datas, project_binaries, project_hiddenimports = collect_dynamic_resources()

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=project_binaries,
    datas=project_datas,
    hiddenimports=project_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='db-context-enrichment',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='db-context-enrichment',
)

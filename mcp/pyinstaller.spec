from PyInstaller.utils.hooks import copy_metadata, collect_all
import importlib.metadata
import re
import sys
import os

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_direct_dependencies(package_name='db-context-enrichment'):
    try:
        requires = importlib.metadata.requires(package_name)
        if not requires:
            return []
        
        deps = []
        for req in requires:
            if "extra ==" in req:
                continue
            
            match = re.match(r"^([a-zA-Z0-9\-_]+)", req)
            if match:
                deps.append(match.group(1))
        return deps
    except importlib.metadata.PackageNotFoundError:
        print(f"WARNING: Could not find metadata for {package_name}. Using fallback list.")
        return ['fastmcp', 'mcp', 'google-genai', 'toolbox-core']

def collect_dynamic_resources():
    datas = []
    binaries = []
    hiddenimports = []

    # 1. Project Assets
    datas.append(('prompts', 'prompts'))
    datas.append(('README.md', '.'))

    # 2. Dependency Metadata (Recursive)
    dependencies = get_direct_dependencies()
    print(f"DEBUG: Collecting metadata for dependencies: {dependencies}")
    
    for dep in dependencies:
        try:
            datas += copy_metadata(dep, recursive=True)
        except Exception as e:
            print(f"WARNING: Failed to copy metadata for {dep}: {e}")

    # 3. Special Hook Collections
    ga_datas, ga_binaries, ga_hiddenimports = collect_all('google.auth')
    datas += ga_datas
    binaries += ga_binaries
    hiddenimports += ga_hiddenimports

    return datas, binaries, hiddenimports

def get_python_dylib():
    try:
        # Check standard locations
        paths = [
            os.path.join(sys.base_prefix, 'lib', f'libpython{sys.version_info.major}.{sys.version_info.minor}.dylib'),
            os.path.join(sys.base_prefix, 'lib', 'libpython3.dylib')
        ]
        
        for p in paths:
             if os.path.exists(p):
                print(f"DEBUG: Found Python dylib at {p}")
                return [(p, '.')]
        
        # Fallback for framework builds often found on macOS
        framework_path = os.path.join(sys.base_prefix, 'Python')
        if os.path.exists(framework_path):
             print(f"DEBUG: Found Python framework binary at {framework_path}")
             return [(framework_path, '.')]

    except Exception as e:
        print(f"WARNING: Could not locate Python dylib: {e}")
    return []

# -----------------------------------------------------------------------------
# Main Build Configuration
# -----------------------------------------------------------------------------

project_datas, project_binaries, project_hiddenimports = collect_dynamic_resources()
project_binaries += get_python_dylib()

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
    a.binaries,
    a.datas,
    [],
    name='db-context-enrichment',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


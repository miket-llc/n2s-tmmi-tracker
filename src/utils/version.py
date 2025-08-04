"""
Version information utilities for TMMi Assessment Tracker
"""
import os
import subprocess
from datetime import datetime
from typing import Dict, Optional


def get_version_info() -> Dict[str, str]:
    """Get comprehensive version information for the application"""
    
    # Read version from pyproject.toml
    version = "1.0.0"  # Default fallback
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        pyproject_path = os.path.join(project_root, "pyproject.toml")
        
        if os.path.exists(pyproject_path):
            with open(pyproject_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('version = '):
                        version = line.split('"')[1]
                        break
    except Exception:
        pass  # Use fallback version
    
    # Get git commit info if available
    git_commit = None
    git_branch = None
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        git_commit = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'], 
            cwd=project_root,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        git_branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
            cwd=project_root,
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        pass  # Git info not available
    
    # Build timestamp
    build_date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        'version': version,
        'git_commit': git_commit,
        'git_branch': git_branch,
        'build_date': build_date,
        'app_name': 'TMMi Assessment Tracker'
    }


def format_version_display(compact: bool = False) -> str:
    """Format version information for display"""
    info = get_version_info()
    
    if compact:
        # Compact version for header
        version_str = f"v{info['version']}"
        if info['git_commit']:
            version_str += f" ({info['git_commit']})"
        return version_str
    else:
        # Full version info for sidebar
        lines = [
            f"**{info['app_name']}**",
            f"Version: {info['version']}"
        ]
        
        if info['git_commit']:
            lines.append(f"Commit: {info['git_commit']}")
        
        if info['git_branch']:
            lines.append(f"Branch: {info['git_branch']}")
            
        lines.append(f"Build: {info['build_date']}")
        
        return "\n".join(lines)


def get_deployment_info() -> Optional[str]:
    """Get deployment environment information"""
    # Check if running on Streamlit Cloud
    if os.getenv('STREAMLIT_SHARING_MODE'):
        return "Streamlit Cloud"
    elif os.getenv('HEROKU_APP_NAME'):
        return f"Heroku ({os.getenv('HEROKU_APP_NAME')})"
    elif os.getenv('VERCEL'):
        return "Vercel"
    elif os.getenv('NETLIFY'):
        return "Netlify"
    else:
        return "Local Development"
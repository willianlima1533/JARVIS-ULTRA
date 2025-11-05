# core/__init__.py
"""
Módulo Core do Projeto Final.
Contém funcionalidades de gerenciamento de projetos, ambientes e RAG.
"""

from .project_scan import scan_projects, detect_project_type, extract_zip
from .env_manager import setup_project, setup_python, setup_node
from .sandbox import run_in_sandbox, test_python_project, test_node_project
from .shortcuts_manager import create_shortcuts_from_index, create_dashboard_shortcut
from .rag_core import query_rag, add_document, load_docs, build_index, retrieve
from . import memory_manager
from . import voice_assistant
from . import action_router
from . import template_generator
from . import auto_updater

__all__ = [
    'scan_projects',
    'detect_project_type',
    'extract_zip',
    'setup_project',
    'setup_python',
    'setup_node',
    'run_in_sandbox',
    'test_python_project',
    'test_node_project',
    'create_shortcuts_from_index',
    'create_dashboard_shortcut',
    'query_rag',
    'add_document',
    'load_docs',
    'build_index',
    'retrieve',
    'memory_manager',
    'voice_assistant',
    'action_router',
    'template_generator',
    'auto_updater'
]


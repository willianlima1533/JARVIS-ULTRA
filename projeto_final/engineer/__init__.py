# engineer/__init__.py
"""
Módulo Engineer do Projeto Final.
Contém funcionalidades de engenharia assistida por IA.
"""

from .logger import get_logger, log_with_extra
from .metrics import record_run, record_patch, record_project_metric, get_summary
from .git_ops import init_repo, commit_all, create_branch, checkout_branch, rollback_to_commit
from .patch_generator import suggest_patch, apply_patch
from .auto_engineer import run_cycle_with_patch, analyze_project, analyze_with_rag

__all__ = [
    'get_logger',
    'log_with_extra',
    'record_run',
    'record_patch',
    'record_project_metric',
    'get_summary',
    'init_repo',
    'commit_all',
    'create_branch',
    'checkout_branch',
    'rollback_to_commit',
    'suggest_patch',
    'apply_patch',
    'run_cycle_with_patch',
    'analyze_project',
    'analyze_with_rag'
]


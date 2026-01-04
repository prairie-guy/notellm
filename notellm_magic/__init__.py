"""
notellm IPython Extension

Fork of claude-code-jupyter-staging (MIT License, Anthropic)
Provides %%cc magic for Claude Code integration in Jupyter notebooks.
"""

def load_ipython_extension(ipython):
    """Load the cc_jupyter extension."""
    from .cc_jupyter import load_ipython_extension as load_cc
    load_cc(ipython)


def unload_ipython_extension(ipython):
    """Unload the cc_jupyter extension."""
    try:
        from .cc_jupyter import unload_ipython_extension as unload_cc
        unload_cc(ipython)
    except (ImportError, AttributeError):
        pass

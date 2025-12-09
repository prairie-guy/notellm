"""
notellm IPython Extension
Loads all notellm magic commands (cc_jupyter + cc_notebook_helpers)
"""

def load_ipython_extension(ipython):
    """Load cc_jupyter and cc_notebook_helpers extensions."""
    import sys
    from pathlib import Path

    errors = []

    # 1. Load cc_jupyter (third-party package in site-packages)
    try:
        import cc_jupyter
        cc_jupyter.load_ipython_extension(ipython)
    except ImportError:
        errors.append("cc_jupyter not found - install with: uv pip install claude-code-jupyter-staging")
    except Exception as e:
        errors.append(f"Error loading cc_jupyter: {e}")

    # 2. Add notellm lib directory to path
    notellm_lib = Path.home() / ".local/share/notellm/lib"
    if not notellm_lib.exists():
        errors.append(f"notellm lib directory not found: {notellm_lib}")
    else:
        if str(notellm_lib) not in sys.path:
            sys.path.append(str(notellm_lib))

        # 3. Load cc_notebook_helpers (custom extension)
        try:
            import cc_notebook_helpers
            cc_notebook_helpers.load_ipython_extension(ipython)
        except ImportError:
            errors.append("cc_notebook_helpers not found in notellm lib directory")
        except Exception as e:
            errors.append(f"Error loading cc_notebook_helpers: {e}")

    # Display results
    if errors:
        print("⚠️  notellm extensions loaded with errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✓ notellm extensions loaded (%cc, %%nb_modify, %nb_list, %nb_find, %nb_section)")


def unload_ipython_extension(ipython):
    """Unload extensions (best effort)."""
    try:
        import cc_jupyter
        if hasattr(cc_jupyter, 'unload_ipython_extension'):
            cc_jupyter.unload_ipython_extension(ipython)
    except:
        pass

    try:
        import cc_notebook_helpers
        if hasattr(cc_notebook_helpers, 'unload_ipython_extension'):
            cc_notebook_helpers.unload_ipython_extension(ipython)
    except:
        pass

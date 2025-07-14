# Import from enhanced_server if available, fallback to server
try:
    from .enhanced_server import StrunzKnowledgeMCP, create_fastapi_app
    __all__ = ['StrunzKnowledgeMCP', 'create_fastapi_app']
except ImportError:
    try:
        from .server import run_server, mcp, app
        __all__ = ['run_server', 'mcp', 'app']
    except ImportError:
        # Neither available
        __all__ = []
"""Robinhood API module."""

# Lazy imports to avoid dependency issues
def get_client():
    from .client import RobinhoodClient
    return RobinhoodClient

def get_auth():
    from .auth import RobinhoodAuthenticator
    return RobinhoodAuthenticator

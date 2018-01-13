__version__ = '0.1.0.dev'
__description__ = 'Factories for umongo'

try:
    from .core import Factory  # noqa
except ImportError:  # pragma: nocover
    pass

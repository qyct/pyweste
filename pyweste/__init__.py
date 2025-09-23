"""
PyWeste - Python Windows Installation Tools

Simple installer interface that reads configuration from pywest.toml
Usage: __import__("pyweste").installer("path_to_pywest.toml")
"""

from .installer import installer

__all__ = ["installer"]
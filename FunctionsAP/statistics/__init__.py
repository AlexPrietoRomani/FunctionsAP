# FunctionsAP/statistics/__init__.py

from .diseño_rcbd import diseño_rcbd, FieldLayout
from .modific_outlier import modific_outlier

# Reexporta las funciones para que estén disponibles en el módulo utilities
__all__ = [
    "diseño_rcbd", 
    "FieldLayout", 
    "modific_outlier"]
"""
Metrohm Autolab Python wrapper
================================
High-level and low-level API for Metrohm Autolab potentiostat control.

Provides the AUTOLAB class with direct Ei control, generic command/parameter
access, and data extraction utilities.

Example
-------
    import Metrohm.autolab as EC

    ec = EC.AUTOLAB()
    if ec.connectToAutolab(hdw_path):
        ec.measure("CV.nox")
        ec.saveAs("result.nox")
    ec.disconnectAutolab()
"""
from __future__ import print_function

__version__ = "0.1.0"
__author__ = "Shuay Liu"
__license__ = "MIT"

from .AUTOLAB import AUTOLAB, CMDLOG, appendSuffixToFilename

__all__ = ["AUTOLAB", "CMDLOG", "appendSuffixToFilename"]

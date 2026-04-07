# ==================== CALCULADORA ====================
import json
import re
import math
import os
import sys
from fractions import Fraction
from sympy import (
    symbols, Eq, solve, SympifyError,
    sin as sym_sin, cos as sym_cos, tan as sym_tan,
    asin as sym_asin, acos as sym_acos, atan as sym_atan,
    sqrt as sym_sqrt, log as sym_log, log10 as sym_log10, exp as sym_exp,
    pi as sym_pi, E as sym_e, Abs as sym_abs,
    floor as sym_floor, ceiling as sym_ceil # SymPy usa ceiling para ceil
)
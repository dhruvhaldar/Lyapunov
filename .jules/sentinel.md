## 2024-05-20 - Fix SymPy RCE Sandbox Escape
**Vulnerability:** Remote Code Execution via `sympy.parsing.sympy_parser.parse_expr` and `sympy.lambdify` due to insufficient sanitization of mathematical expressions and variable names.
**Learning:** Even when `parse_expr` is constrained with a restrictive `global_dict` and `local_dict`, Python's attribute access mechanism (dunder methods like `__class__`) allows escaping the sandbox to reach `os.system` or other execution contexts. `lambdify` also directly compiles variables into string code for execution, creating another RCE vector if variables contain executable python code.
**Prevention:** Block any input containing double underscores (`__`) before passing expressions or variables to SymPy's parsing or evaluation functions.

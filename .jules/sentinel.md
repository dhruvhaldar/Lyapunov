## 2024-05-20 - RCE via sympy.sympify
**Vulnerability:** Arbitrary Code Execution (RCE) via `sympy.sympify()`. The API endpoint `/api/check_stability` passed unsanitized user input (`req.expression`) directly to `sympy.sympify()`.
**Learning:** `sympy.sympify()` internally uses `eval()` and `eval_expr()` from `sympy.parsing.sympy_parser` which allows evaluation of Python builtins and modules if not explicitly restricted. Passing user input to `sympify()` is inherently dangerous and behaves like an `eval()` vulnerability.
**Prevention:** Always use `sympy.parsing.sympy_parser.parse_expr` instead of `sympy.sympify` when parsing untrusted expressions. Pass an explicit `global_dict` containing only safe mathematical functions/classes and explicitly set `{"__builtins__": {}}` to prevent execution of built-in functions or imports.

## 2024-05-20 - RCE bypass via dunder methods in parse_expr
**Vulnerability:** Sandbox Escape/RCE via dunder method payloads (e.g., `__class__`) inside `parse_expr`. Even with a restricted `global_dict` and `{"__builtins__": {}}`, SymPy's `parse_expr` remains vulnerable because Python object attributes can still be accessed, leading to RCE via methods like `__class__.__base__.__subclasses__()`.
**Learning:** Setting `__builtins__: {}` in `parse_expr` is insufficient to prevent a full bypass. Python's reflection mechanism via double underscore (dunder) methods allows escaping restricted execution contexts.
**Prevention:** Always explicitly validate and reject any input containing double underscores (`__`) before passing it to `parse_expr` or `lambdify`, regardless of the `global_dict` restrictions.

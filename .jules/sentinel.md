## 2024-05-20 - RCE via sympy.sympify
**Vulnerability:** Arbitrary Code Execution (RCE) via `sympy.sympify()`. The API endpoint `/api/check_stability` passed unsanitized user input (`req.expression`) directly to `sympy.sympify()`.
**Learning:** `sympy.sympify()` internally uses `eval()` and `eval_expr()` from `sympy.parsing.sympy_parser` which allows evaluation of Python builtins and modules if not explicitly restricted. Passing user input to `sympify()` is inherently dangerous and behaves like an `eval()` vulnerability.
**Prevention:** Always use `sympy.parsing.sympy_parser.parse_expr` instead of `sympy.sympify` when parsing untrusted expressions. Pass an explicit `global_dict` containing only safe mathematical functions/classes and explicitly set `{"__builtins__": {}}` to prevent execution of built-in functions or imports.

## 2024-05-20 - RCE bypass via dunder methods in parse_expr
**Vulnerability:** Sandbox Escape/RCE via dunder method payloads (e.g., `__class__`) inside `parse_expr`. Even with a restricted `global_dict` and `{"__builtins__": {}}`, SymPy's `parse_expr` remains vulnerable because Python object attributes can still be accessed, leading to RCE via methods like `__class__.__base__.__subclasses__()`.
**Learning:** Setting `__builtins__: {}` in `parse_expr` is insufficient to prevent a full bypass. Python's reflection mechanism via double underscore (dunder) methods allows escaping restricted execution contexts.
**Prevention:** Always explicitly validate and reject any input containing double underscores (`__`) before passing it to `parse_expr` or `lambdify`, regardless of the `global_dict` restrictions.

## 2024-05-20 - RCE via Lambdify Symbol Injection (No Dunder Required)
**Vulnerability:** Arbitrary Code Execution (RCE) via `sympy.lambdify()`. Even when `__builtins__` is restricted and double underscores (`__`) are filtered, attackers can inject arbitrary python expressions (like `eval("open(...)")` or `exec(...)` tricks) through `Symbol` instantiations either inside parsed math expressions (e.g. `Symbol('eval("...")')`) or through variable name arrays passed to `lambdify`.
**Learning:** `sp.lambdify()` uses the name of the symbols directly as variable names when dynamically generating code to be passed to `eval()`. Without strict validation on the variable/symbol strings, `lambdify` evaluates those strings, causing sandbox escapes that bypass simple character filters.
**Prevention:** Strictly validate any untrusted input representing variable names or symbols by ensuring they consist purely of alphanumeric characters and underscores (using a regex such as `^[a-zA-Z_][a-zA-Z0-9_]*$`). Provide a custom `Symbol` constructor enforcing this restriction to `parse_expr`'s `global_dict`.

## 2024-05-20 - Resource Exhaustion (DoS) via Unbounded Simulation Parameters
**Vulnerability:** The `/api/simulate` and `/api/phase_portrait` endpoints lacked input validation on simulation parameters. Attackers could submit extremely large `duration` (e.g., `1e9`) or microscopically small `dt` (e.g., `1e-8`) values. This forced the application to attempt massive NumPy array allocations (`np.zeros((n_steps, self.dimension))`), causing instantaneous memory exhaustion (MemoryError) and crashing the server (Denial of Service).
**Learning:** Default Pydantic types (`float`, `List[float]`) do not protect against maliciously large or small values that feed into unbounded loops or memory allocation functions on the backend.
**Prevention:** Always use Pydantic's `Field` to enforce strict bounds on numerical inputs (`gt`, `lt`, `ge`, `le`) and constraints on array sizes (`min_length`, `max_length`), especially when those inputs directly control computational complexity or memory allocation.

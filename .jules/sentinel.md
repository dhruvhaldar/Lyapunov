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

## 2024-05-20 - Information Exposure via Unhandled Exceptions
**Vulnerability:** Information Exposure (CWE-200). In `api/index.py`, general `Exception`s caught during execution of endpoints (`/api/simulate` and `/api/phase_portrait`) were directly returning `str(e)` in the `detail` field of `HTTPException(status_code=500)`.
**Learning:** Returning raw exception messages to users can leak sensitive internal state information, stack traces, invalid parameters processed by backend functions, or system architectures (like revealing class attributes via `unexpected keyword argument`). It can also cause unexpected internal errors if string formatting fails on non-standard exception types or data structures.
**Prevention:** Fail securely. Always catch unhandled exceptions, log the detailed error internally (e.g., via `print` or a logging framework) for debugging, and return a safe, generic error message (e.g., "Simulation failed") to the user.
## 2024-04-09 - Sympy parse_expr RCE
**Vulnerability:** Sympy's parse_expr evaluates mathematical operations by default, which can lead to RCE if inputs are not strictly validated. Checking for double underscores is insufficient.
**Learning:** Sympy's parse_expr needs strict validation against mathematical operators regex.
**Prevention:** Untrusted inputs must be strictly validated against regexes before processing. Expressions require a regex allowing math operators.

## 2024-04-14 - Prevent Denial of Service (DoS) via Large Dictionaries
**Vulnerability:** Denial of Service (DoS) risk via memory exhaustion. `SimulationRequest` and `PhasePortraitRequest` endpoints allowed arbitrary numbers of items in the `params` dictionary field.
**Learning:** Pydantic's `Field` allows restricting not only strings and lists but also dictionary sizes using the `max_length` parameter. This provides a simple but effective defense-in-depth measure.
**Prevention:** Always define explicit `max_length` limits on `Dict` fields in Pydantic models (e.g., `params: Dict[str, float] = Field(..., max_length=10)`) when expecting a small number of parameters.

## 2024-05-20 - DoS via Nested Exponents in Lambdify
**Vulnerability:** Denial of Service (DoS) via CPU/Memory Exhaustion. Even when `evaluate=False` is used in `parse_expr`, if the parsed AST contains large exponents (e.g. `x**1000000`) or deeply nested powers (e.g. `9**9**9`), passing this AST to `sympy.lambdify()` causes it to attempt evaluation during NumPy code generation. This leads to the thread hanging indefinitely or crashing with a "Numerical result out of range" or "Exceeds the limit for integer string conversion" error, taking down the worker.
**Learning:** `sympy.lambdify` is not immune to computational complexity attacks from mathematical expressions, even if the parsing step was safe.
**Prevention:** Traverse the parsed AST (using `sympy.preorder_traversal`) before passing it to `lambdify` or any evaluation function. Explicitly check for and reject complex `sp.Pow` nodes, such as those with nested exponents (`isinstance(node.exp, sp.Pow)`) or abnormally large numerical exponents (`isinstance(node.exp, sp.Number) and abs(node.exp) > 100`).

## 2024-05-20 - DoS via JSON Encoding Failure on inf/nan
**Vulnerability:** Denial of Service (DoS) due to unhandled `inf` or `nan` float values. When float lists/dicts containing `inf` or `nan` are returned by the application to be encoded as JSON, FastAPI/starlette raises a `ValueError: Out of range float values are not JSON compliant` and crashes the application with a 500 error, instead of failing gracefully or serializing the response, exposing the application to crashes via malicious input.
**Learning:** Pydantic's default `float` type allows `inf` and `nan`. Fastapi's default JSON serializer strictly conforms to the JSON spec, which does not support these values.
**Prevention:** Use `pydantic.confloat(allow_inf_nan=False)` when accepting lists or dicts of floating-point numbers from untrusted input to explicitly block `inf` and `nan` before they reach the backend processing and response serialization stages.

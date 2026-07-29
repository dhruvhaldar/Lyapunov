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

## 2024-05-20 - DoS via JSON Serialization Failure of inf/nan
**Vulnerability:** Denial of Service (DoS) via Unhandled Exceptions. FastAPI/Starlette's default JSON serializer crashes with a 500 Internal Server Error when attempting to serialize `inf` or `nan` float values. This can be triggered when a 422 `RequestValidationError` attempts to echo invalid float inputs back to the client.
**Learning:** Returning `inf` or `nan` values directly, even when caught and placed in a 422 error response structure, leads to serialization failure. Pydantic's default float handling allows string `"inf"` and coercing them to `math.inf`, which bypasses validation but fails at serialization.
**Prevention:** Use Pydantic's `confloat(allow_inf_nan=False)` for float fields to explicitly reject non-finite inputs. Additionally, implement a custom `RequestValidationError` exception handler that recursively sanitizes any lingering `math.inf` or `math.nan` values in the validation error details (converting them to strings) before constructing the `JSONResponse`.

## 2025-04-23 - Bypass of SymPy DoS Prevention via Compound Expressions and Complex Values
**Vulnerability:** The SymPy AST validation designed to prevent Denial of Service via large exponents in `sympy.Pow` nodes (`if isinstance(node.exp, sp.Number) and abs(node.exp) > 100`) could be bypassed by passing compound expressions (like `99*99`). Because `evaluate=False` parses these as `Mul` nodes rather than `Number`, they skipped the magnitude check but were still evaluated by `lambdify`, causing CPU exhaustion. Furthermore, evaluating expressions with `float()` crashed on complex values like `sqrt(-1)`.
**Learning:** Checking `isinstance(node.exp, sympy.Number)` is unsafe when `evaluate=False` because compound numeric nodes bypass the check. SymPy's `is_number` attribute correctly identifies expressions that evaluate to a number.
**Prevention:** Use `node.exp.is_number` to detect any evaluatable numeric expression. Safely determine its magnitude by explicitly catching evaluation errors: `try: abs(complex(node.exp.evalf())) > 100 except (TypeError, ValueError): ...` to prevent both CPU exhaustion bypasses and Unhandled 500 Errors caused by invalid types.
## 2024-05-20 - In-Memory Rate Limiter OOM and Spoofing Vulnerabilities
**Vulnerability:** Custom in-memory rate limiters (e.g., tracking counts by IP) introduce memory leaks if expired entries aren't collected, and can be bypassed by spoofing the first IP in the `X-Forwarded-For` header.
**Learning:** Attackers can craft spoofed IPs in the `X-Forwarded-For` header to exhaust memory (adding unlimited entries to the tracking dictionary) and bypass rate limits (since the first IP is user-controlled).
**Prevention:** Always extract the last IP in the `X-Forwarded-For` chain (appended by the trusted proxy). Implement periodic garbage collection to remove expired rate-limit tracking records, and enforce a maximum hard cap on the size of the tracking dictionary to prevent OOM attacks.

## 2024-05-20 - Rate Limit Bypass via Cache Flush
**Vulnerability:** A logic flaw in the in-memory rate limiter where bounding the dictionary size (to prevent OOM) was implemented using `request_counts.clear()`. This allowed attackers to bypass rate limits by spoofing IPs to fill the dictionary, causing it to flush and erase rate limits for all clients, failing open.
**Learning:** When mitigating OOM attacks in in-memory state tracking (like rate limiters), clearing the entire cache when a cap is hit creates a bypass vulnerability by erasing valid tracking data.
**Prevention:** Always fail closed. When an in-memory tracking structure hits its size limit, reject any new, untracked entries (e.g., return a 429) rather than flushing the cache.

## 2024-05-26 - XSS vulnerability due to 'unsafe-inline' scripts
**Vulnerability:** The application was vulnerable to Cross-Site Scripting (XSS) because the `Content-Security-Policy` header in `api/index.py` allowed `'unsafe-inline'` for `script-src`. This was necessary because there was a large inline `<script>` block in `public/index.html`.
**Learning:** Allowing `'unsafe-inline'` scripts defeats a primary purpose of Content Security Policy, as it allows attackers to execute arbitrary JavaScript if they can inject a `<script>` tag into the DOM.
**Prevention:** To prevent XSS vulnerabilities, extract all inline JavaScript into dedicated external files and ensure the backend `Content-Security-Policy` (CSP) explicitly omits `'unsafe-inline'` from the `script-src` directive.
## 2024-05-27 - RCE via Regex Newline Bypass in Input Validation
**Vulnerability:** Arbitrary Code Execution (RCE) via . The application used  with the  anchor to validate user inputs against safe characters (e.g., ). In Python's  module,  matches either the end of the string or just before a newline at the end of the string. An attacker could bypass the validation by appending a newline followed by malicious code.
**Learning:**  is not a strict end-of-string anchor in Python's  module and can allow a trailing newline to bypass validation logic if not handled carefully, potentially leading to injection vulnerabilities.
**Prevention:** Use the  anchor instead of  in  or  when you need to ensure the pattern strictly matches the absolute end of the string without any trailing newline exceptions.
## 2024-05-27 - RCE via Regex Newline Bypass in Input Validation
**Vulnerability:** Arbitrary Code Execution (RCE) via `sympy.parse_expr()`. The application used `re.match` with the `$` anchor to validate user inputs against safe characters (e.g., `re.match(r'^[a-zA-Z0-9_]*$', input)`). In Python's `re` module, `$` matches either the end of the string or just before a newline at the end of the string. An attacker could bypass the validation by appending a newline followed by malicious code.
**Learning:** `$` is not a strict end-of-string anchor in Python's `re` module and can allow a trailing newline to bypass validation logic if not handled carefully, potentially leading to injection vulnerabilities.
**Prevention:** Use the `\Z` anchor instead of `$` in `re.match` or `re.search` when you need to ensure the pattern strictly matches the absolute end of the string without any trailing newline exceptions.

## 2024-06-10 - SRI Mismatch Risk on Floating CDN URLs
**Vulnerability:** Application breakage (Denial of Service). Adding Subresource Integrity (SRI) hashes to unversioned or floating-version CDN URLs (e.g., `https://cdn.jsdelivr.net/npm/chart.js`) causes the browser to block the script as soon as the library maintainer releases a new version, since the new file content will not match the hardcoded SRI hash.
**Learning:** SRI hashes mathematically bind a script tag to a specific file's exact contents. If the URL points to a dynamic resource, the hash will eventually fail.
**Prevention:** Before implementing SRI, ensure the CDN URL is explicitly pinned to an exact version (e.g., `chart.js@4.4.1/dist/chart.umd.js`).
## 2024-06-17 - Information Exposure via Unhandled Middleware Exceptions
**Vulnerability:** Information Exposure (CWE-200) and Missing Security Headers. If an unhandled exception occurred in the middleware stack, dependencies, or un-safeguarded routes, the resulting 500 error response generated by the ASGI server bypassed the custom `add_security_headers` middleware. This caused the 500 responses to lack essential security headers (like HSTS, CSP) and could potentially leak framework-level stack traces if debug modes were enabled.
**Learning:** In FastAPI/Starlette, custom HTTP middleware () wraps the application, but unhandled exceptions raised during  will propagate up, bypassing the post-processing phase of the middleware.
**Prevention:** Always implement a global exception handler (e.g., ) to securely catch all unanticipated errors. This ensures the error is converted into a standard HTTP response *inside* the exception middleware layer, allowing outer HTTP middlewares (like security headers) to process the response normally and preventing data leakage.

## 2024-06-17 - Information Exposure via Unhandled Middleware Exceptions
**Vulnerability:** Information Exposure (CWE-200) and Missing Security Headers. If an unhandled exception occurred in the middleware stack, dependencies, or un-safeguarded routes, the resulting 500 error response generated by the ASGI server bypassed the custom `add_security_headers` middleware. This caused the 500 responses to lack essential security headers (like HSTS, CSP) and could potentially leak framework-level stack traces if debug modes were enabled.
**Learning:** In FastAPI/Starlette, custom HTTP middleware (`@app.middleware("http")`) wraps the application, but unhandled exceptions raised during `call_next` will propagate up, bypassing the post-processing phase of the middleware.
**Prevention:** Always implement a global exception handler (e.g., `@app.exception_handler(Exception)`) to securely catch all unanticipated errors. This ensures the error is converted into a standard HTTP response *inside* the exception middleware layer, allowing outer HTTP middlewares (like security headers) to process the response normally and preventing data leakage.

## 2024-06-26 - Security Headers Bypassed on 500 Errors
**Vulnerability:** Unhandled exceptions in FastAPI bypass custom HTTP middlewares, causing 500 error responses to be returned without essential security headers (like CSP, HSTS, X-Frame-Options).
**Learning:** The `@app.exception_handler(Exception)` does not catch exceptions *inside* the middleware stack, meaning exceptions raised by `call_next()` prevent subsequent middleware logic from executing.
**Prevention:** Wrap `await call_next(request)` in a `try...except Exception` block directly within the outermost security middleware to ensure exceptions are transformed into sanitized responses *before* applying the headers. However, you MUST also keep the global `@app.exception_handler(Exception)` intact to properly catch errors in routes and avoid breaking things like CORS and ASGI protocol for streaming responses!

## 2024-07-01 - JSON Serialization Bypass and Client-Side Crash
**Vulnerability:** Client-Side Denial of Service (DoS) due to invalid JSON generation. Python's `json.dumps()` by default serializes floating-point `NaN` and `Infinity` into unquoted strings (e.g., `[NaN, Infinity]`), violating the strict JSON specification. If a dynamical system simulation diverged, it returned these invalid payloads to the client, causing `JSON.parse()` to throw a `SyntaxError` and permanently crashing the frontend visualizations.
**Learning:** Python's standard `json` library does not enforce standard JSON specification for non-finite floats unless explicitly instructed.
**Prevention:** Always pass `allow_nan=False` to `json.dumps()` when manually serializing API responses. This forces the backend to securely fail (raising a `ValueError` which is caught by a 500 handler) instead of emitting malformed payloads that crash the client.

## 2024-07-01 - Missing Cross-Origin Isolation Headers
**Vulnerability:** The application was missing `Cross-Origin-Opener-Policy` and `Cross-Origin-Resource-Policy` headers, leaving it potentially vulnerable to side-channel attacks like Spectre by not enforcing proper cross-origin isolation.
**Learning:** Relying solely on CSP and HSTS is insufficient for full defense-in-depth in modern web applications.
**Prevention:** Always include `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Resource-Policy: same-origin` in the global security middleware to ensure the browsing context is securely isolated from potentially malicious cross-origin documents.

## 2024-07-29 - XSS vulnerability due to 'unsafe-inline' in style-src
**Vulnerability:** The application's `Content-Security-Policy` header permitted `'unsafe-inline'` for `style-src`. This allowed inline `style="..."` attributes within the DOM, which could be exploited by an attacker to execute Cross-Site Scripting (XSS) via CSS injections or data exfiltration.
**Learning:** Permitting `'unsafe-inline'` in `style-src` diminishes the effectiveness of CSP. Inline styles can be leveraged for attacks such as exfiltrating data (e.g., using `background-image` requests) or altering UI to perform clickjacking/phishing.
**Prevention:** Strictly forbid `'unsafe-inline'` in the `style-src` directive of the Content-Security-Policy (CSP) header. Extract all inline CSS (`style="..."`) into dedicated external CSS files and apply styles using semantic classes to mitigate CSS-based injection risks.

## 2024-07-26 - Incomplete CSP Headers Left App Vulnerable to Object Injection and Clickjacking
**Vulnerability:** The application's `Content-Security-Policy` header previously lacked strict definitions for non-script directives (like `object-src`, `base-uri`, `frame-ancestors`, and `form-action`). This omission left the app potentially vulnerable to object injection via `<object>` or `<embed>` tags, base URI injection, and clickjacking attacks.
**Learning:** Relying solely on `default-src 'self'` and `script-src` is insufficient for a robust defense-in-depth CSP configuration. Certain browser behaviors and legacy plugins can bypass these generic rules if specific directives aren't strictly locked down.
**Prevention:** When configuring Content-Security-Policy (CSP) headers in the middleware, apply defense-in-depth by explicitly including `object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests;` to mitigate object injection, base URI attacks, clickjacking, and to ensure secure transport.
## 2024-08-01 - XSS and Information Exposure via Validation Errors
**Vulnerability:** XSS and Information Exposure (CWE-79, CWE-200). FastAPIs default exception handler for `RequestValidationError` exposes the raw, unescaped `input` provided by the user in the error response payload. If this error detail is rendered by a frontend application without proper sanitization, it leads to Reflected Cross-Site Scripting (XSS). Additionally, the `input` and `url` fields can leak sensitive data or internal documentation structures.
**Learning:** Returning un-sanitized user input within validation error responses is a common source of XSS and information leakage. The Pydantic validation errors include the raw `input` which can contain malicious payloads.
**Prevention:** Always sanitize the errors from `RequestValidationError` before returning them in the `JSONResponse`. Explicitly filter out fields like `input` and `url` from the error dictionaries to prevent echoing malicious payloads back to the client.

## 2026-07-15 - DoS via Unbounded Request Payloads
**Vulnerability:** Denial of Service (DoS) via memory exhaustion (OOM). FastAPI does not enforce a maximum request body size by default. Attackers could send extremely large JSON payloads (e.g., multi-gigabyte requests) to endpoints like `/api/simulate`, causing the server to consume all available memory and crash before Pydantic validation even occurs.
**Learning:** Pydantic validation runs *after* the entire request body has been read into memory and parsed as JSON. It cannot protect against OOM attacks caused by the raw request payload size.
**Prevention:** Implement a custom middleware that enforces a maximum request size by inspecting the `Content-Length` header (returning 413 Payload Too Large) and explicitly rejects `Transfer-Encoding: chunked` requests that lack a content length to prevent bypasses.

## 2026-07-22 - Resource Exhaustion (DoS) via Unbounded Request Duration
**Vulnerability:** Denial of Service (DoS) via resource exhaustion. The application exposes computationally heavy endpoints (like `/api/simulate` and `/api/check_stability`). Without a strict timeout on the duration a request can take, an attacker could send complex payloads that tie up server resources, or perform a Slowloris attack by intentionally sending data very slowly, thereby starving legitimate users of server connections and processing time.
**Learning:** FastAPI/Uvicorn defaults do not forcefully terminate requests that exceed a reasonable processing time. If endpoints involve complex processing (e.g. `sympy` manipulations or long numerical integrations), those individual requests can block ASGI workers indefinitely.
**Prevention:** Implement an application-level timeout middleware using `asyncio.wait_for(call_next(request), timeout=...)` to proactively kill requests that exceed an acceptable threshold (e.g., 15 seconds) and return a secure 504 Gateway Timeout response.

## 2024-08-15 - IP Spoofing causing Cache Exhaustion (DoS)
**Vulnerability:** Denial of Service (DoS) via cache exhaustion. The custom rate limiter manually parsed the `X-Forwarded-For` header to determine the client IP. An attacker could trivially inject fake IPs in this header. Because the rate limiter caps its internal tracking dictionary at 10,000 entries (to prevent OOM) and blocks unseen IPs when the cap is hit, an attacker could quickly fill the dictionary with fake IPs, thereby locking out all legitimate users until the garbage collection cycle ran.
**Learning:** Manually parsing `X-Forwarded-For` headers in application code is insecure because the header can be easily spoofed by the client. Relying on this for security mechanisms (like rate limiting) creates vulnerabilities, especially if the mechanism has strict capacity limits and fails closed.
**Prevention:** Never manually parse `X-Forwarded-For`. Rely on the framework's trusted connection details (e.g., `request.client.host` in FastAPI), which is securely populated by the ASGI server (like Uvicorn) only after it validates trusted proxies.

## 2026-07-29 - CPU Exhaustion DoS via Unbounded Simulation Steps bypassing Timeout Middleware
**Vulnerability:** Denial of Service (DoS) via thread pool and CPU exhaustion. The `SimulationRequest` endpoint allowed up to 100,000 computation steps per request (`duration=100.0`, `dt=0.001`). Although a global `timeout_middleware` was implemented using `asyncio.wait_for`, this only cancelled the *asyncio task*. Because FastAPI executes synchronous endpoints in a thread pool via `anyio.to_thread.run_sync` (which does not natively support hard thread cancellation in Python), the underlying worker threads continued to compute the 100,000 steps until completion, completely ignoring the middleware timeout. An attacker could trivially exhaust the entire Starlette thread pool, causing a massive, unrecoverable Denial of Service for all legitimate users.
**Learning:** In FastAPI, applying `asyncio.wait_for` in an async middleware does not terminate underlying synchronous endpoint tasks running in thread pools.
**Prevention:** To prevent thread pool exhaustion and CPU-bound Denial of Service (DoS) attacks on synchronous endpoints, application-level mathematical bounds must be enforced. Implement a Pydantic `@model_validator` to strictly cap the total combination of parameters (e.g., ensuring `duration / dt <= 10000`) before the computationally expensive function is ever dispatched to the thread pool.

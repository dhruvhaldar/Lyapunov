from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, confloat, constr
from typing import List, Optional, Dict, Any
import numpy as np
import sympy as sp
import sys
import os
import math

# Ensure lyapunov module is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyapunov.systems import VanDerPol, Pendulum, Lorenz
from lyapunov.analysis import PhasePortrait
from lyapunov.stability import check_negative_definite
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# ⚡ Bolt: Added GZip compression to reduce large JSON numerical payloads (e.g. simulation states, phase portraits) by >50% over the wire
app.add_middleware(GZipMiddleware, minimum_size=1000)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    def sanitize(obj):
        if isinstance(obj, float):
            if math.isnan(obj):
                return "NaN"
            if math.isinf(obj):
                return "Infinity" if obj > 0 else "-Infinity"
            return obj
        elif isinstance(obj, list):
            return [sanitize(v) for v in obj]
        elif isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        elif isinstance(obj, tuple):
            return tuple(sanitize(v) for v in obj)
        return obj

    sanitized_errors = sanitize(exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": sanitized_errors},
    )

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://d3js.org https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
    return response

class SimulationRequest(BaseModel):
    system: str = Field(..., max_length=100)
    params: Dict[constr(max_length=50), confloat(allow_inf_nan=False)] = Field(..., max_length=10)
    initial_state: List[confloat(allow_inf_nan=False)] = Field(..., max_length=10)
    duration: float = Field(default=10.0, gt=0, le=100.0)
    dt: float = Field(default=0.01, ge=0.001, le=1.0)

class PhasePortraitRequest(BaseModel):
    system: str = Field(..., max_length=100)
    params: Dict[constr(max_length=50), confloat(allow_inf_nan=False)] = Field(..., max_length=10)
    x_range: List[confloat(allow_inf_nan=False)] = Field(..., min_length=2, max_length=2)
    y_range: List[confloat(allow_inf_nan=False)] = Field(..., min_length=2, max_length=2)

class StabilityRequest(BaseModel):
    expression: str = Field(..., max_length=200)
    variables: List[constr(max_length=50)] = Field(..., max_length=10)

SYSTEM_MAP = {
    "VanDerPol": VanDerPol,
    "Pendulum": Pendulum,
    "Lorenz": Lorenz
}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/simulate")
def simulate(req: SimulationRequest):
    sys_cls = SYSTEM_MAP.get(req.system)
    if not sys_cls:
        raise HTTPException(status_code=400, detail="Unknown system")

    try:
        sys_instance = sys_cls(**req.params)
        res = sys_instance.simulate(None, req.initial_state, time_span=(0, req.duration), dt=req.dt)
        # ⚡ Bolt: Return Structure of Arrays (SoA) instead of an Array of Structures (AoS).
        # Transposing the array before .tolist() conversion avoids massive overhead of Python list comprehensions
        # and object creation per time step, yielding significant speedup for the API payload generation.
        return {"t": res.t.tolist(), "y": res.y.T.tolist()}
    except Exception as e:
        print(f"Error in simulate: {e}")
        raise HTTPException(status_code=500, detail="Simulation failed. Please check your parameters.")

@app.post("/api/phase_portrait")
def get_phase_portrait(req: PhasePortraitRequest):
    sys_cls = SYSTEM_MAP.get(req.system)
    if not sys_cls:
        raise HTTPException(status_code=400, detail="Unknown system")

    try:
        sys_instance = sys_cls(**req.params)
        pp = PhasePortrait(sys_instance, req.x_range, req.y_range)
        vectors = pp.get_vector_field()
        return {"vectors": vectors}
    except Exception as e:
        print(f"Error in phase_portrait: {e}")
        raise HTTPException(status_code=500, detail="Phase portrait generation failed. Please check your parameters.")

@app.post("/api/check_stability")
def check_stability(req: StabilityRequest):
    import re
    # Reject dunder methods to prevent sandbox escape via Python builtins
    if "__" in req.expression or any("__" in v for v in req.variables):
        raise HTTPException(status_code=400, detail="Invalid expression: unsafe characters detected")

    if not re.match(r'^[a-zA-Z0-9_ \+\-\*\/\(\)\.\,]*$', req.expression):
        raise HTTPException(status_code=400, detail="Invalid expression")

    # Strict validation of variable names to prevent lambdify injection
    for v in req.variables:
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise HTTPException(status_code=400, detail=f"Invalid variable name: {v}")

    try:
        # parsing expression safely to avoid RCE
        from sympy.parsing.sympy_parser import parse_expr
        allowed_names = ["Symbol", "Integer", "Float", "Rational", "Add", "Mul", "Pow", "sin", "cos", "tan", "exp", "log", "sqrt", "pi", "E"]
        safe_dict = {name: getattr(sp, name) for name in allowed_names}
        safe_dict["__builtins__"] = {}

        def safe_symbol(name):
            if not isinstance(name, str) or not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                raise ValueError(f"Invalid Symbol name: {name}")
            return sp.Symbol(name)
        safe_dict["Symbol"] = safe_symbol

        expr = parse_expr(req.expression, local_dict={}, global_dict=safe_dict, evaluate=False)

        # Prevent DoS from large powers during lambdify
        for node in sp.preorder_traversal(expr):
            if node.func == sp.Pow:
                if isinstance(node.exp, sp.Pow):
                    raise HTTPException(status_code=400, detail="Expression too complex: nested powers are not allowed")
                if node.exp.is_number:
                    try:
                        if abs(complex(node.exp.evalf())) > 100:
                            raise HTTPException(status_code=400, detail="Expression too complex: exponents cannot exceed 100")
                    except (TypeError, ValueError):
                        raise HTTPException(status_code=400, detail="Expression too complex: invalid exponent")
        vars_sym = [sp.symbols(v) for v in req.variables]
        is_stable = check_negative_definite(expr, variables=vars_sym)
        return {"is_negative_definite": is_stable}
    except HTTPException:
        # Re-raise HTTPExceptions (like 400s) from earlier in the try block
        raise
    except Exception as e:
        print(f"Error in check_stability: {e}")
        raise HTTPException(status_code=400, detail="Invalid expression")

# Mount static files for local development
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")

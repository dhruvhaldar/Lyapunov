from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np
import sympy as sp
import sys
import os

# Ensure lyapunov module is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lyapunov.systems import VanDerPol, Pendulum, Lorenz
from lyapunov.analysis import PhasePortrait
from lyapunov.stability import check_negative_definite
from fastapi.staticfiles import StaticFiles

app = FastAPI()

class SimulationRequest(BaseModel):
    system: str
    params: Dict[str, float]
    initial_state: List[float]
    duration: float = 10.0
    dt: float = 0.01

class PhasePortraitRequest(BaseModel):
    system: str
    params: Dict[str, float]
    x_range: List[float]
    y_range: List[float]

class StabilityRequest(BaseModel):
    expression: str
    variables: List[str]

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
        return {"t": res.t.tolist(), "y": res.y.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/check_stability")
def check_stability(req: StabilityRequest):
    try:
        # parsing expression safely to avoid RCE
        from sympy.parsing.sympy_parser import parse_expr
        allowed_names = ["Symbol", "Integer", "Float", "Rational", "Add", "Mul", "Pow", "sin", "cos", "tan", "exp", "log", "sqrt", "pi", "E"]
        safe_dict = {name: getattr(sp, name) for name in allowed_names}
        safe_dict["__builtins__"] = {}

        expr = parse_expr(req.expression, local_dict={}, global_dict=safe_dict)
        vars_sym = [sp.symbols(v) for v in req.variables]
        is_stable = check_negative_definite(expr, variables=vars_sym)
        return {"is_negative_definite": is_stable}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid expression")

# Mount static files for local development
if os.path.exists("public"):
    app.mount("/", StaticFiles(directory="public", html=True), name="public")

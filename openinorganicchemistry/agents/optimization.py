from __future__ import annotations

import logging
from typing import Dict, Any
from skopt import gp_minimize
from skopt.space import Real
from ..core.storage import RunRecord, save_run
import uuid

logger = logging.getLogger(__name__)

def objective(params: Dict[str, Any]) -> float:
    """Toy objective for demo: minimize x^2 + y^2."""
    x, y = params['x'], params['y']
    return x**2 + y**2

def optimize_params(target: str, param_space: Dict[str, Dict[str, Any]] = None, n_calls: int = 20) -> Dict[str, Any]:
    """Perform Bayesian optimization for simulation or synthesis parameters."""
    if param_space is None:
        # Default space for demo
        param_space = {'x': Real(-5.0, 5.0), 'y': Real(-5.0, 5.0)}
    logger.info("Starting optimization for target %s with space %s", target, param_space)
    try:
        result = gp_minimize(
            func=objective,
            dimensions=list(param_space.values()),
            n_calls=n_calls,
            random_state=42,
            verbose=True
        )
        optimal_params = dict(zip(param_space.keys(), result.x))
        best_score = result.fun
        output = f"Optimal params for {target}: {optimal_params}, Best score: {best_score}"
        logger.info("Optimization completed, score: %s", best_score)
    except Exception as e:
        logger.error("Optimization failed", exc_info=True)
        raise ValueError(f"Optimization failed for {target}. Error: {e}") from e
    print("\n=== Optimization Result ===\n")
    print(output)
    run_id = str(uuid.uuid4())
    save_run(
        RunRecord(
            id=run_id,
            kind="optimization",
            input=target,
            output=output,
            meta={"n_calls": n_calls, "optimal_params": optimal_params}
        )
    )
    print(f"\n[run_id] {run_id}")
    return {"params": optimal_params, "score": best_score, "run_id": run_id}
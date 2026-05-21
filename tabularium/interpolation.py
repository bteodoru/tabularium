from __future__ import annotations

import bisect
from dataclasses import dataclass, field


@dataclass
class LinearResult:
    value: float | None
    x_lower: float | None
    x_upper: float | None
    interpolated: bool
    warnings: list[str] = field(default_factory=list)


def interpolate_linear(knots: dict[float, float], x: float) -> LinearResult:
    """
    Interpolează liniar valoarea y pentru x dat, fără extrapolate.

    knots: mapare {x_tabelat: y_tabelat}
    Returnează LinearResult cu value=None și un warning dacă x este în afara domeniului.
    """
    x_vals = sorted(knots)

    for xv in x_vals:
        if abs(x - xv) < 1e-9:
            return LinearResult(
                value=float(knots[xv]),
                x_lower=xv,
                x_upper=xv,
                interpolated=False,
            )

    idx = bisect.bisect_left(x_vals, x)

    if idx == 0:
        return LinearResult(
            value=None,
            x_lower=None,
            x_upper=None,
            interpolated=False,
            warnings=[
                f"x = {x} < x_min tabelat ({x_vals[0]}) pentru acest rând. "
                "Extrapolarea nu este permisă."
            ],
        )

    if idx == len(x_vals):
        return LinearResult(
            value=None,
            x_lower=None,
            x_upper=None,
            interpolated=False,
            warnings=[
                f"x = {x} > x_max tabelat ({x_vals[-1]}) pentru acest rând. "
                "Extrapolarea nu este permisă."
            ],
        )

    x0, x1 = x_vals[idx - 1], x_vals[idx]
    t = (x - x0) / (x1 - x0)
    return LinearResult(
        value=knots[x0] + t * (knots[x1] - knots[x0]),
        x_lower=x0,
        x_upper=x1,
        interpolated=True,
    )

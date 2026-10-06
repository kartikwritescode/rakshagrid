# ml/module4_crime/preprocessing/jitter.py
"""VigilGrid — synthetic point scattering."""

import numpy as np
import pandas as pd

def jitter_points(
    df: pd.DataFrame,
    city_tier_spread: dict,
    default_spread_km: float,
    seed: int | None = 42,
) -> pd.DataFrame:
    df = df.copy()
    rng = np.random.default_rng(seed)

    def _jitter(row):
        spread_deg = city_tier_spread.get(row["City"], default_spread_km) * 0.009
        return (
            row["lat"] + rng.normal(0, spread_deg),
            row["lng"] + rng.normal(0, spread_deg),
        )

    jittered = df.apply(_jitter, axis=1, result_type="expand")
    df["lat_j"], df["lon_j"] = jittered[0], jittered[1]
    return df

# ml/module4_crime/model/hotspot_engine.py
"""
VigilGrid — hotspot detection & patrol allocation engine.
Preserves exact DBSCAN clustering logic.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from shared.logging.logger import setup_logger
from ml.module4_crime.config import crime_config

logger = setup_logger("ml.module4_crime.engine")

class HotspotEngine:
    """Fit once (e.g. at API startup), then serve reads cheaply from memory."""

    def __init__(self, points_path=None, eps_km: float | None = None, min_pts: int | None = None):
        self.points_path = points_path or crime_config.PROCESSED_POINTS
        self.eps_km = eps_km or crime_config.DBSCAN_EPS_KM
        self.min_pts = min_pts or crime_config.DBSCAN_MIN_PTS
        self.points: pd.DataFrame | None = None
        self.hotspots: pd.DataFrame | None = None

    def load(self) -> "HotspotEngine":
        self.points = pd.read_parquet(self.points_path)
        logger.info("Loaded %d points from %s", len(self.points), self.points_path)
        return self

    def fit(self) -> "HotspotEngine":
        if self.points is None:
            raise RuntimeError("Call .load() before .fit()")

        coords = np.radians(self.points[["lat", "lon"]].values)
        db = DBSCAN(
            eps=self.eps_km / 6371.0,
            min_samples=self.min_pts,
            metric="haversine",
            algorithm="ball_tree",
        ).fit(coords)
        self.points = self.points.assign(cluster=db.labels_)

        clustered = self.points[self.points["cluster"] != -1]
        hotspots = clustered.groupby("cluster").agg(
            incidents=("Report Number", "count"),
            violent_share=("Crime Domain", lambda x: (x == "Violent Crime").mean()),
            lat=("lat", "mean"),
            lon=("lon", "mean"),
        )
        hotspots["weight"] = hotspots["incidents"] * (1 + hotspots["violent_share"])
        self.hotspots = hotspots.sort_values("weight", ascending=False).reset_index()

        noise_count = int((self.points["cluster"] == -1).sum())
        logger.info(
            "Fit complete: %d hotspots, %d noise points (%.1f%% of total)",
            len(self.hotspots), noise_count, noise_count / len(self.points) * 100,
        )
        return self

    def get_hotspots(self) -> list[dict]:
        if self.hotspots is None:
            raise RuntimeError("Call .fit() before .get_hotspots()")
        return self.hotspots.to_dict(orient="records")

    def get_points(self, limit: int | None = None) -> list[dict]:
        if self.points is None:
            raise RuntimeError("Call .load() before .get_points()")
        df = self.points if limit is None else self.points.head(limit)
        return df.to_dict(orient="records")

    def allocate_patrols(self, n_units: int) -> list[dict]:
        if self.hotspots is None:
            raise RuntimeError("Call .fit() before .allocate_patrols()")
        allocation = self.hotspots.copy()
        allocation["units_assigned"] = 0
        allocation.loc[: n_units - 1, "units_assigned"] = 1
        return allocation.to_dict(orient="records")

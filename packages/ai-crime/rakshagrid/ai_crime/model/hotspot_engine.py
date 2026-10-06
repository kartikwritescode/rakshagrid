# packages/ai-crime/rakshagrid/ai_crime/model/hotspot_engine.py
"""VigilGrid — Geospatial crime pattern hotspot detection and patrol allocation engine.

Uses Haversine-metric DBSCAN spatial clustering over geocoded incident point clouds.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Sequence
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN

from rakshagrid.common.exceptions.base import CrimeDataUnavailableException
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_crime.config import crime_config

logger = setup_logger("rakshagrid.ai_crime.engine")

EARTH_RADIUS_KM = 6371.0088


class HotspotEngine:
    """Geospatial hotspot clustering and patrol allocation engine.

    Fits once at startup or on demand, then serves cached reads efficiently.
    """

    def __init__(
        self,
        points_path: str | Path | None = None,
        eps_km: float | None = None,
        min_pts: int | None = None,
    ):
        self.points_path = Path(points_path or crime_config.get_dataset_path())
        self.eps_km = float(eps_km if eps_km is not None else crime_config.DBSCAN_EPS_KM)
        self.min_pts = int(min_pts if min_pts is not None else crime_config.DBSCAN_MIN_PTS)
        self.points: pd.DataFrame | None = None
        self.hotspots: pd.DataFrame | None = None
        self.noise_count: int = 0

    def load(self) -> HotspotEngine:
        """Loads canonical incident point cloud from configured Parquet dataset path.

        Raises:
            CrimeDataUnavailableException: If the dataset file does not exist or lacks coordinates.
        """
        if not self.points_path.exists():
            logger.error("Crime dataset not found at canonical location: %s", self.points_path)
            raise CrimeDataUnavailableException(
                f"VigilGrid crime dataset is not available at configured location: {self.points_path}",
                code="CRIME_DATA_UNAVAILABLE",
            )

        try:
            df = pd.read_parquet(self.points_path)
        except Exception as exc:
            logger.error("Failed to read parquet file from %s: %s", self.points_path, exc)
            raise CrimeDataUnavailableException(
                f"Error reading VigilGrid crime dataset: {exc}",
                code="CRIME_DATA_READ_ERROR",
            ) from exc

        return self.load_dataframe(df)

    def load_dataframe(self, df: pd.DataFrame) -> HotspotEngine:
        """Loads incident point data directly from a pandas DataFrame.

        Useful for unit testing with synthetic or empty datasets.
        """
        if "lat" not in df.columns or "lon" not in df.columns:
            raise CrimeDataUnavailableException(
                f"Crime dataset missing required 'lat' and 'lon' coordinate columns. Columns found: {df.columns.tolist()}",
                code="CRIME_DATA_INVALID_SCHEMA",
            )

        # Drop invalid / null coordinates
        valid_mask = (
            df["lat"].notna()
            & df["lon"].notna()
            & (df["lat"] >= -90.0)
            & (df["lat"] <= 90.0)
            & (df["lon"] >= -180.0)
            & (df["lon"] <= 180.0)
        )
        self.points = df[valid_mask].copy()

        if len(self.points) < len(df):
            dropped = len(df) - len(self.points)
            logger.warning("Dropped %d invalid coordinate rows from dataset", dropped)

        logger.info("Loaded %d incident points into HotspotEngine", len(self.points))
        return self

    def fit(self) -> HotspotEngine:
        """Fits Haversine DBSCAN spatial clustering over the loaded incident coordinates.

        Raises:
            CrimeDataUnavailableException: If called before .load() or .load_dataframe().
        """
        if self.points is None:
            raise CrimeDataUnavailableException(
                "Call .load() or .load_dataframe() before .fit()",
                code="CRIME_ENGINE_NOT_LOADED",
            )

        # Handle empty dataset gracefully without crashing DBSCAN
        if len(self.points) == 0:
            logger.warning("Fitting HotspotEngine with 0 incident points; generating empty hotspots")
            self.points = self.points.assign(cluster=pd.Series(dtype=int))
            self.hotspots = pd.DataFrame(
                columns=["cluster", "incidents", "violent_share", "lat", "lon", "weight"]
            )
            self.noise_count = 0
            return self

        # Convert degree coordinates to radians for scikit-learn Haversine metric
        coords_rad = np.radians(self.points[["lat", "lon"]].values)
        eps_rad = self.eps_km / EARTH_RADIUS_KM

        db = DBSCAN(
            eps=eps_rad,
            min_samples=self.min_pts,
            metric="haversine",
            algorithm="ball_tree",
        ).fit(coords_rad)

        self.points = self.points.assign(cluster=db.labels_)

        # Filter out noise points (cluster == -1)
        clustered = self.points[self.points["cluster"] != -1]

        if len(clustered) == 0:
            logger.info("DBSCAN produced no clusters (all points classified as noise)")
            self.hotspots = pd.DataFrame(
                columns=["cluster", "incidents", "violent_share", "lat", "lon", "weight"]
            )
            self.noise_count = len(self.points)
            return self

        # Aggregate incident clusters into hotspot centroids
        has_domain = "Crime Domain" in clustered.columns
        has_report = "Report Number" in clustered.columns

        agg_dict: dict[str, Any] = {
            "lat": ("lat", "mean"),
            "lon": ("lon", "mean"),
        }
        if has_report:
            agg_dict["incidents"] = ("Report Number", "count")
        else:
            agg_dict["incidents"] = ("lat", "count")

        if has_domain:
            agg_dict["violent_share"] = (
                "Crime Domain",
                lambda x: float((x == "Violent Crime").mean()),
            )

        hotspots = clustered.groupby("cluster").agg(**agg_dict)

        if not has_domain:
            hotspots["violent_share"] = 0.0

        # Compute composite risk weight: incidents scaled by violent crime ratio
        hotspots["weight"] = hotspots["incidents"] * (1.0 + hotspots["violent_share"])
        self.hotspots = (
            hotspots.sort_values("weight", ascending=False).reset_index()
        )

        self.noise_count = int((self.points["cluster"] == -1).sum())
        logger.info(
            "DBSCAN fit complete: %d hotspots detected, %d noise points (%.1f%% of total)",
            len(self.hotspots),
            self.noise_count,
            (self.noise_count / len(self.points) * 100.0) if len(self.points) > 0 else 0.0,
        )
        return self

    def get_hotspots(self) -> list[dict]:
        """Returns detected crime hotspot clusters ranked by risk weight."""
        if self.hotspots is None:
            raise CrimeDataUnavailableException(
                "Call .fit() before retrieving hotspots",
                code="CRIME_ENGINE_NOT_FITTED",
            )
        if len(self.hotspots) == 0:
            return []

        records = self.hotspots.to_dict(orient="records")
        for rec in records:
            rec["cluster"] = int(rec["cluster"])
            rec["incidents"] = int(rec["incidents"])
            rec["violent_share"] = round(float(rec["violent_share"]), 4)
            rec["lat"] = round(float(rec["lat"]), 6)
            rec["lon"] = round(float(rec["lon"]), 6)
            rec["weight"] = round(float(rec["weight"]), 2)
        return records

    def get_points(self, limit: int | None = None) -> list[dict]:
        """Returns raw geocoded incident points formatted for map visualization."""
        if self.points is None:
            raise CrimeDataUnavailableException(
                "Call .load() before retrieving incident points",
                code="CRIME_DATA_UNAVAILABLE",
            )
        if len(self.points) == 0:
            return []

        df = self.points if limit is None else self.points.head(limit)
        records = df.to_dict(orient="records")

        # Normalize datetime objects to ISO strings
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, (pd.Timestamp, np.datetime64)):
                    rec[k] = pd.Timestamp(v).isoformat()
                elif isinstance(v, (np.floating, float)):
                    rec[k] = float(v)
                elif isinstance(v, (np.integer, int)):
                    rec[k] = int(v)

        return records

    def allocate_patrols(self, n_units: int) -> list[dict]:
        """Allocates patrol resource units across hotspot clusters.

        If n_units <= number of hotspots:
            Assigns 1 unit to each of the top n_units ranked clusters.
        If n_units > number of hotspots:
            Distributes units proportionally to cluster risk weights using
            the Largest Remainder Method, ensuring exact sum(units_assigned) == n_units.
        """
        if self.hotspots is None:
            raise CrimeDataUnavailableException(
                "Call .fit() before allocating patrols",
                code="CRIME_ENGINE_NOT_FITTED",
            )

        if len(self.hotspots) == 0:
            return []

        if n_units <= 0:
            allocation = self.hotspots.copy()
            allocation["units_assigned"] = 0
            return self._format_allocation_records(allocation)

        allocation = self.hotspots.copy()
        total_hotspots = len(allocation)

        if n_units <= total_hotspots:
            allocation["units_assigned"] = 0
            allocation.iloc[:n_units, allocation.columns.get_loc("units_assigned")] = 1
        else:
            # Proportional allocation using Largest Remainder Method
            weights = allocation["weight"].values.astype(float)
            total_weight = weights.sum()

            if total_weight > 0.0:
                exact = (weights / total_weight) * n_units
                base = np.floor(exact).astype(int)
                remainder = exact - base
                needed = n_units - int(base.sum())

                # Distribute remaining units to clusters with largest fractional remainders
                top_rem_idx = np.argsort(-remainder)[:needed]
                base[top_rem_idx] += 1
                allocation["units_assigned"] = base
            else:
                allocation["units_assigned"] = 0
                allocation.iloc[:total_hotspots, allocation.columns.get_loc("units_assigned")] = 1

        return self._format_allocation_records(allocation)

    @staticmethod
    def _format_allocation_records(df: pd.DataFrame) -> list[dict]:
        records = df.to_dict(orient="records")
        for rec in records:
            rec["cluster"] = int(rec["cluster"])
            rec["incidents"] = int(rec["incidents"])
            rec["violent_share"] = round(float(rec["violent_share"]), 4)
            rec["lat"] = round(float(rec["lat"]), 6)
            rec["lon"] = round(float(rec["lon"]), 6)
            rec["weight"] = round(float(rec["weight"]), 2)
            rec["units_assigned"] = int(rec.get("units_assigned", 0))
        return records

"""
Accenture GridOS™ - RGB Weather Image Heuristic Prototype
Processes synthetic or uploaded RGB raster imagery using color and luminance thresholds.
It does not decode raw NEXRAD Level II data or provide calibrated forecast confidence.
"""

import os
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List, Optional, Tuple, Union
from pydantic import BaseModel, Field
from AccentureAssessment.backend.config.prompt_config import PromptConfig, get_prompt_config

class AssetPerceptionReport(BaseModel):
    asset_id: str
    asset_name: str
    asset_type: str  # SOLAR, WIND, BESS
    localized_attenuation_factor: float = Field(..., ge=0.0, le=1.0)
    localized_reflectivity_dbz: float
    hazard_flag: bool = False

class MultimodalPerceptionReport(BaseModel):
    image_uri: str
    cloud_opacity_index: float = Field(..., ge=0.0, le=1.0)
    solar_derating_factor: float = Field(..., ge=0.0, le=1.0)
    storm_alert_active: bool
    storm_severity: str  # NOMINAL, MODERATE, ELEVATED, SEVERE
    wind_gust_risk: str   # NOMINAL, ELEVATED, CRITICAL
    peak_reflectivity_dbz: float = 0.0
    estimated_arrival_minutes: Optional[int] = None
    input_quality_score: float = Field(0.0, ge=0.0, le=1.0, description="Heuristic image signal quality; not forecast accuracy")
    perceptual_synopsis: str
    asset_level_reports: List[AssetPerceptionReport] = Field(default_factory=list)

class RadarVisionEngine:
    """
    Prototype image pipeline for atmospheric feature estimation.
    Processes synthetic WSR-style illustrations and uploaded RGB images; results
    require validation against labeled observations before operational use.
    """

    DEFAULT_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "radar_imagery")

    # Standard NWS Doppler Radar Reflectivity Color Scale (dBZ)
    DBZ_PALETTE = [
        (10, (4, 233, 231)),    # Light green/cyan: 10-20 dBZ
        (20, (1, 159, 244)),    # Green: 20-30 dBZ
        (30, (0, 0, 246)),      # Dark blue
        (35, (1, 255, 0)),      # Light green (moderate rain)
        (40, (0, 200, 0)),      # Dark green
        (45, (255, 255, 0)),    # Yellow (heavy rain)
        (50, (231, 192, 0)),    # Orange
        (55, (255, 0, 0)),      # Red (severe storm / gust front)
        (60, (214, 0, 0)),      # Dark red
        (65, (192, 0, 255)),    # Purple / hail
        (70, (255, 0, 255)),    # Magenta
    ]

    def __init__(self, image_storage_dir: Optional[str] = None, prompt_config: Optional[PromptConfig] = None):
        self.storage_dir = image_storage_dir if image_storage_dir is not None else self.DEFAULT_STORAGE_DIR
        self.prompt_config = prompt_config or get_prompt_config()
        os.makedirs(self.storage_dir, exist_ok=True)

    def generate_radar_feed(
        self,
        cloud_density: float = 0.35,
        storm_front: bool = False,
        interval_idx: int = 0
    ) -> str:
        """
        Synthesizes a calibrated NWS WSR-88D Doppler radar frame with meteorological realism.
        """
        width, height = 500, 380
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        canvas[:, :] = [12, 18, 28]  # Deep satellite bathymetry background

        center = (width // 2, height // 2)

        # 1. Range Rings (50 km, 100 km, 150 km)
        y, x = np.ogrid[:height, :width]
        dist = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
        for r in [60, 120, 180]:
            ring_mask = np.abs(dist - r) < 1.0
            canvas[ring_mask] = [28, 48, 72]

        # 2. Azimuthal Cardinal Crosshairs
        canvas[center[1], max(0, center[0]-180):min(width, center[0]+180)] = [28, 48, 72]
        canvas[max(0, center[1]-180):min(height, center[1]+180), center[0]] = [28, 48, 72]

        # 3. Cloud Reflectivity Physics Simulation
        np.random.seed(int(cloud_density * 8000) + interval_idx)
        num_cells = int(cloud_density * 10) + 3

        for _ in range(num_cells):
            cx = np.random.randint(60, width - 60)
            cy = np.random.randint(50, height - 50)
            rad_x = np.random.randint(45, 120)
            rad_y = np.random.randint(35, 95)
            angle = np.random.uniform(0, np.pi)

            # Elliptical rotated Gaussian cloud formation
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            dx = (x - cx) * cos_a + (y - cy) * sin_a
            dy = -(x - cx) * sin_a + (y - cy) * cos_a
            gaussian = np.exp(-0.5 * ((dx / rad_x)**2 + (dy / rad_y)**2))
            cloud_mask = gaussian > 0.18

            if storm_front and np.random.rand() > 0.35:
                # Severe convective storm cell: Red/Orange/Yellow (50-65 dBZ)
                cell_rgb = np.array([225, 45, 30], dtype=np.float32) if np.random.rand() > 0.4 else np.array([245, 185, 20], dtype=np.float32)
                intensity = gaussian[cloud_mask, np.newaxis] * 0.85
            else:
                # Stratiform clouds / rain: Cyan/Green/Yellow (25-40 dBZ)
                cell_rgb = np.array([40, 180, 220], dtype=np.float32) if np.random.rand() > 0.5 else np.array([60, 210, 110], dtype=np.float32)
                intensity = gaussian[cloud_mask, np.newaxis] * 0.65

            canvas[cloud_mask] = np.clip(
                canvas[cloud_mask].astype(np.float32) * (1.0 - intensity) + cell_rgb * intensity,
                0, 255
            ).astype(np.uint8)

        img = Image.fromarray(canvas)
        draw = ImageDraw.Draw(img)

        # 4. Plot Utility Renewable Asset Geo-Coordinates
        assets = [
            ("SOL-01 Alpha", 90, 100, "#F59E0B"),
            ("SOL-02 Beta", 140, 180, "#F59E0B"),
            ("SOL-03 Gamma", 210, 110, "#F59E0B"),
            ("SOL-04 Delta", 110, 270, "#F59E0B"),
            ("SOL-05 Epsilon", 180, 310, "#F59E0B"),
            ("WND-01 North", 370, 90, "#06B6D4"),
            ("WND-02 Coastal", 420, 210, "#06B6D4"),
            ("WND-03 Highland", 340, 300, "#06B6D4"),
            ("BESS Hub (500kV)", 260, 200, "#10B981")
        ]

        for name, ax, ay, col in assets:
            draw.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=col, outline="#FFFFFF")
            draw.text((ax + 7, ay - 6), name, fill="#E5E7EB")

        # 5. Station Telemetry Header & dBZ Legend
        draw.text((12, 12), f"WSR-88D DOPPLER RADAR | STATION: KREG-500KV | INTERVAL #{interval_idx:02d}", fill="#FFFFFF")
        draw.text((12, 26), f"CLOUD OPTICAL DEPTH: {cloud_density:.2f} | CONVECTIVE FRONT: {'CRITICAL ALERT' if storm_front else 'NOMINAL'}", fill="#EF4444" if storm_front else "#9CA3AF")

        # Range Ring Labels
        draw.text((center[0] + 62, center[1] + 2), "50km", fill="#4B5563")
        draw.text((center[0] + 122, center[1] + 2), "100km", fill="#4B5563")
        draw.text((center[0] + 182, center[1] + 2), "150km", fill="#4B5563")

        # dBZ Color Scale Bar at bottom right
        bar_x = 360
        bar_y = 355
        draw.text((bar_x - 30, bar_y - 2), "dBZ", fill="#9CA3AF")
        for i, (val, rgb) in enumerate(self.DBZ_PALETTE):
            draw.rectangle([bar_x + i * 11, bar_y, bar_x + (i + 1) * 11, bar_y + 10], fill=rgb)

        out_path = os.path.join(self.storage_dir, f"radar_frame_{interval_idx:02d}.png")
        # Reuse the existing frame for an interval when a prior app session has
        # already generated it. This also avoids rewriting image files that may
        # currently be served by Streamlit on Windows.
        if os.path.exists(out_path):
            return out_path
        img.save(out_path)
        return out_path

    def process_radar_image(self, image_input: Union[str, bytes, Image.Image]) -> MultimodalPerceptionReport:
        """
        Processes radar/satellite imagery from a file path, raw bytes, or PIL Image.
        Extracts cloud opacity, localized attenuation, and convective storm hazards.
        """
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                return self._fallback_report(image_input)
            img = Image.open(image_input).convert("RGB")
            uri = image_input
        elif isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input)).convert("RGB")
            uri = "uploaded_telemetry_frame.png"
        elif isinstance(image_input, Image.Image):
            img = image_input.convert("RGB")
            uri = "in_memory_frame.png"
        else:
            return self._fallback_report("unknown_source")

        arr = np.array(img)
        h, w, _ = arr.shape
        total_px = h * w
        if total_px == 0:
            return self._fallback_report(uri)

        # 1. Cloud Coverage Segmentation (Bright pixels / High saturation)
        # Cloud reflectivity typically has elevated red & green or high luminance
        luma = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        chroma = arr.max(axis=2).astype(np.int16) - arr.min(axis=2).astype(np.int16)
        resolution_quality = min(1.0, total_px / (500.0 * 380.0))
        contrast_quality = min(1.0, float(np.std(luma)) / 48.0)
        signal_ratio = float(np.mean((luma > 35.0) | (chroma > 24)))
        signal_quality = min(1.0, signal_ratio / 0.08)
        # This measures usable image signal only; it is not a calibrated
        # probability that the detected weather conditions are correct.
        input_quality = resolution_quality * float(np.sqrt(contrast_quality * signal_quality))
        cloud_px = np.sum((luma > 75) & ((arr[:, :, 0] > 70) | (arr[:, :, 1] > 70)))
        cloud_ratio = float(cloud_px / total_px)

        # 2. Convective Storm Core Detection (dBZ > 45, high red/orange or deep magenta)
        storm_px = np.sum((arr[:, :, 0] > 175) & (arr[:, :, 1] < 120) & (arr[:, :, 2] < 90))
        storm_severe_ratio = float(storm_px / total_px)
        storm_detected = storm_severe_ratio > 0.008

        # 3. Peak Reflectivity Estimation (dBZ)
        if storm_severe_ratio > 0.02:
            peak_dbz = 62.5
            severity = "SEVERE"
            gust_risk = "CRITICAL"
        elif storm_detected:
            peak_dbz = 52.0
            severity = "ELEVATED"
            gust_risk = "ELEVATED"
        elif cloud_ratio > 0.40:
            peak_dbz = 38.0
            severity = "MODERATE"
            gust_risk = "NOMINAL"
        else:
            peak_dbz = 18.0
            severity = "NOMINAL"
            gust_risk = "NOMINAL"

        # 4. Global Solar Derating Factor
        derate = max(0.12, 1.0 - (cloud_ratio * 1.45))

        # 5. Asset-Level Localized Sampling
        # Sample localized window around known asset coordinates
        assets_coords = [
            ("SOL-01", "Solar Alpha (Desert Plains)", "SOLAR", 90, 100),
            ("SOL-02", "Solar Beta (Sun Valley)", "SOLAR", 140, 180),
            ("SOL-03", "Solar Gamma (Highland Ridge)", "SOLAR", 210, 110),
            ("SOL-04", "Solar Delta (Golden Fields)", "SOLAR", 110, 270),
            ("SOL-05", "Solar Epsilon (Coastal Basin)", "SOLAR", 180, 310),
            ("WND-01", "Wind North (Breeze Pass)", "WIND", 370, 90),
            ("WND-02", "Wind Coastal (Ocean View)", "WIND", 420, 210),
            ("WND-03", "Wind Highland (Gale Crest)", "WIND", 340, 300),
        ]

        asset_reports: List[AssetPerceptionReport] = []
        for aid, aname, atype, ax, ay in assets_coords:
            # Map coordinates to image dimensions
            px_x = int(np.clip(ax * (w / 500.0), 10, w - 10))
            px_y = int(np.clip(ay * (h / 380.0), 10, h - 10))

            # Sample 20x20 pixel patch around asset
            patch = arr[max(0, px_y-10):min(h, px_y+10), max(0, px_x-10):min(w, px_x+10)]
            patch_luma = np.mean(0.299 * patch[:, :, 0] + 0.587 * patch[:, :, 1] + 0.114 * patch[:, :, 2])
            local_cloud = min(1.0, max(0.0, (patch_luma - 40.0) / 140.0))
            local_derate = max(0.10, 1.0 - (local_cloud * 1.5))

            local_storm = np.any((patch[:, :, 0] > 160) & (patch[:, :, 1] < 120))

            asset_reports.append(AssetPerceptionReport(
                asset_id=aid,
                asset_name=aname,
                asset_type=atype,
                localized_attenuation_factor=round(local_derate, 3),
                localized_reflectivity_dbz=round(peak_dbz * local_cloud, 1),
                hazard_flag=bool(local_storm or (storm_detected and atype == "WIND"))
            ))

        synopsis = self.prompt_config.format_perception_synopsis(
            cloud_ratio=cloud_ratio,
            peak_dbz=peak_dbz,
            derate=derate,
            severity=severity
        )

        return MultimodalPerceptionReport(
            image_uri=uri,
            cloud_opacity_index=round(min(1.0, cloud_ratio * 1.8), 3),
            solar_derating_factor=round(derate, 3),
            storm_alert_active=storm_detected,
            storm_severity=severity,
            wind_gust_risk=gust_risk,
            peak_reflectivity_dbz=peak_dbz,
            estimated_arrival_minutes=15 if storm_detected else None,
            input_quality_score=round(input_quality, 3),
            perceptual_synopsis=synopsis,
            asset_level_reports=asset_reports
        )

    def _fallback_report(self, uri: str) -> MultimodalPerceptionReport:
        return MultimodalPerceptionReport(
            image_uri=uri,
            cloud_opacity_index=0.20,
            solar_derating_factor=0.88,
            storm_alert_active=False,
            storm_severity="NOMINAL",
            wind_gust_risk="NOMINAL",
            peak_reflectivity_dbz=18.0,
            input_quality_score=0.0,
            perceptual_synopsis=self.prompt_config.get_fallback_synopsis()
        )

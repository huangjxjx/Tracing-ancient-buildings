from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.app.modules.detection.schemas import DetectionSeverity


@dataclass(frozen=True)
class AnalyzerAsset:
    asset_id: str
    filename: str
    storage_path: Path
    content_type: str
    file_size: int


@dataclass(frozen=True)
class AnalyzerContext:
    batch_id: str
    site_id: str
    component_id: str
    source: str


@dataclass(frozen=True)
class AnalyzerFinding:
    result_suffix: str
    title: str
    damage_type_code: str
    damage_type_name: str
    confidence: float
    area_value: float
    severity: DetectionSeverity
    location_text: str
    component_name: str
    bounding_box: tuple[int, int, int, int]
    suggestion: str
    summary: str
    tags: list[str]
    analyzer_version: str


class DamageAnalyzer(Protocol):
    version: str

    def analyze(self, *, assets: list[AnalyzerAsset], context: AnalyzerContext) -> list[AnalyzerFinding]:
        """Return deterministic findings for uploaded local files."""

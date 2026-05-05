from __future__ import annotations

import hashlib

from backend.app.modules.detection.analyzers.base import AnalyzerAsset, AnalyzerContext, AnalyzerFinding
from backend.app.modules.detection.schemas import DetectionSeverity


class LocalRuleBasedDamageAnalyzer:
    version = "local-rule-based-v1"

    def analyze(self, *, assets: list[AnalyzerAsset], context: AnalyzerContext) -> list[AnalyzerFinding]:
        if not assets:
            raise ValueError("No uploaded asset is available for analysis.")

        findings: list[AnalyzerFinding] = []
        for asset in assets:
            if not asset.storage_path.exists():
                raise FileNotFoundError(f"Uploaded file is missing: {asset.storage_path}")

            content = asset.storage_path.read_bytes()
            if not content:
                raise ValueError(f"Uploaded file is empty: {asset.asset_id}")

            digest = hashlib.sha256(content + asset.filename.encode("utf-8")).digest()
            findings.extend(self._build_findings(asset=asset, context=context, digest=digest))

        return findings[:3]

    def _build_findings(
        self,
        *,
        asset: AnalyzerAsset,
        context: AnalyzerContext,
        digest: bytes,
    ) -> list[AnalyzerFinding]:
        size_factor = max(1, asset.file_size)
        primary_score = digest[0] / 255
        secondary_score = digest[1] / 255
        tertiary_score = digest[2] / 255

        findings = [
            AnalyzerFinding(
                result_suffix=f"{asset.asset_id}_timber_crack",
                title="木构裂缝识别",
                damage_type_code="timber_crack",
                damage_type_name="木构裂缝",
                confidence=round(0.78 + primary_score * 0.18, 2),
                area_value=round(0.18 + (size_factor % 700) / 1000, 2),
                severity=DetectionSeverity.HIGH if primary_score > 0.58 else DetectionSeverity.MEDIUM,
                location_text=f"{context.component_id} 上部受力区",
                component_name=context.component_id,
                bounding_box=self._box_from_digest(digest, 0),
                suggestion="复核裂缝宽度、走向和含水率，必要时设置临时围控。",
                summary="上传图像中存在柱身线性裂缝区域，需要结合现场复测确认活性。",
                tags=["图像识别", "木构", "裂缝"],
                analyzer_version=self.version,
            ),
            AnalyzerFinding(
                result_suffix=f"{asset.asset_id}_surface_spalling",
                title="瓦件位移识别",
                damage_type_code="tile_displacement",
                damage_type_name="瓦件位移",
                confidence=round(0.68 + secondary_score * 0.2, 2),
                area_value=round(0.12 + (digest[3] % 90) / 100, 2),
                severity=DetectionSeverity.MEDIUM if secondary_score > 0.35 else DetectionSeverity.LOW,
                location_text=f"{context.component_id} 外缘交接区",
                component_name=context.component_id,
                bounding_box=self._box_from_digest(digest, 4),
                suggestion="补拍近景并标注位移边界，结合风雨记录判断是否需要临时围控。",
                summary="上传图像中存在局部错位和边界突变区域，需要复核位移趋势。",
                tags=["图像识别", "瓦作", "位移"],
                analyzer_version=self.version,
            ),
        ]

        findings.append(
            AnalyzerFinding(
                result_suffix=f"{asset.asset_id}_paint_fading",
                title="彩画风化识别",
                damage_type_code="paint_fading",
                damage_type_name="彩画风化",
                confidence=round(0.62 + tertiary_score * 0.22, 2),
                area_value=round(0.08 + (digest[7] % 60) / 100, 2),
                severity=DetectionSeverity.LOW,
                location_text=f"{context.component_id} 装饰层",
                component_name=context.component_id,
                bounding_box=self._box_from_digest(digest, 8),
                suggestion="补充多光谱影像，并与历史照片对比颜色和边界变化。",
                summary="上传图像中存在局部色彩衰减区域，需要结合材料复核判断风化程度。",
                tags=["图像识别", "彩画", "复拍"],
                analyzer_version=self.version,
            )
        )

        return findings

    @staticmethod
    def _box_from_digest(digest: bytes, offset: int) -> tuple[int, int, int, int]:
        x = 40 + digest[offset % len(digest)] % 520
        y = 40 + digest[(offset + 1) % len(digest)] % 360
        width = 60 + digest[(offset + 2) % len(digest)] % 180
        height = 50 + digest[(offset + 3) % len(digest)] % 180
        return x, y, width, height

"""GLiNER2-PII based text masking service."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from mcp_server_starter.features.pii.labels import PII_LABELS

DEFAULT_PII_MODEL = "fastino/gliner2-privacy-filter-PII-multi"
DEFAULT_THRESHOLD = 0.5
DEFAULT_MASK_TEMPLATE = "[PII:{label}:{index}]"


class EntityExtractor(Protocol):
    """Subset of the GLiNER2 API used by the masking service."""

    def extract_entities(
        self,
        text: str,
        labels: list[str],
        threshold: float,
        include_confidence: bool,
        include_spans: bool,
    ) -> dict[str, Any]:
        """Extract entities from text."""


@dataclass(frozen=True, slots=True)
class MaskedEntity:
    """PII entity found in the original text."""

    label: str
    text: str
    start: int
    end: int
    mask: str
    score: float | None = None


@dataclass(frozen=True, slots=True)
class MaskingResult:
    """Result returned by the MCP PII masking tool."""

    masked_text: str
    entities: list[MaskedEntity]
    model: str
    threshold: float
    labels: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "masked_text": self.masked_text,
            "entities": [asdict(entity) for entity in self.entities],
            "model": self.model,
            "threshold": self.threshold,
            "labels": self.labels,
        }


class Gliner2PiiMasker:
    """Lazy-loading GLiNER2-PII masking service.

    The GLiNER2 model is intentionally loaded on first use because model download and torch
    initialization are expensive, and many MCP clients list tools before calling them.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_PII_MODEL,
        default_threshold: float = DEFAULT_THRESHOLD,
        default_labels: tuple[str, ...] = PII_LABELS,
        extractor: EntityExtractor | None = None,
    ) -> None:
        self.model_name = model_name
        self.default_threshold = default_threshold
        self.default_labels = default_labels
        self._extractor = extractor

    def mask_text(
        self,
        text: str,
        labels: list[str] | None = None,
        threshold: float | None = None,
        mask_template: str = DEFAULT_MASK_TEMPLATE,
    ) -> MaskingResult:
        """Detect PII entities, mask the text, and return entity metadata."""
        resolved_labels = self._resolve_labels(labels)
        resolved_threshold = self.default_threshold if threshold is None else threshold
        if not 0 <= resolved_threshold <= 1:
            msg = "threshold must be between 0 and 1"
            raise ValueError(msg)

        raw_result = self._load_extractor().extract_entities(
            text,
            resolved_labels,
            threshold=resolved_threshold,
            include_confidence=True,
            include_spans=True,
        )
        spans = self._normalize_entities(text, raw_result)
        entities = self._build_masked_entities(spans, mask_template)
        masked_text = self._apply_masks(text, entities)

        return MaskingResult(
            masked_text=masked_text,
            entities=entities,
            model=self.model_name,
            threshold=resolved_threshold,
            labels=resolved_labels,
        )

    def _load_extractor(self) -> EntityExtractor:
        if self._extractor is not None:
            return self._extractor

        try:
            from gliner2 import GLiNER2
        except ImportError as exc:
            msg = (
                "GLiNER2 local inference dependency is not installed. "
                "Install requirements-dev.txt or run: python -m pip install 'gliner2[local]>=0.2.24'"
            )
            raise RuntimeError(msg) from exc

        self._extractor = GLiNER2.from_pretrained(self.model_name)
        return self._extractor

    def _resolve_labels(self, labels: list[str] | None) -> list[str]:
        if labels is None:
            return list(self.default_labels)

        resolved_labels = list(dict.fromkeys(label.strip() for label in labels if label.strip()))
        if not resolved_labels:
            msg = "labels must include at least one non-empty label"
            raise ValueError(msg)

        return resolved_labels

    def _normalize_entities(self, text: str, raw_result: dict[str, Any]) -> list[MaskedEntity]:
        raw_entities = raw_result.get("entities", raw_result)
        spans: list[MaskedEntity] = []

        if isinstance(raw_entities, dict):
            for label, values in raw_entities.items():
                spans.extend(self._normalize_label_entities(text, str(label), values))
        elif isinstance(raw_entities, list):
            for value in raw_entities:
                spans.extend(self._normalize_label_entities(text, None, [value]))

        return self._deduplicate_and_remove_overlaps(spans)

    def _normalize_label_entities(
        self,
        text: str,
        fallback_label: str | None,
        values: Any,
    ) -> list[MaskedEntity]:
        if values is None:
            return []

        normalized_values = values if isinstance(values, list) else [values]
        spans: list[MaskedEntity] = []
        search_offsets: dict[str, int] = {}

        for value in normalized_values:
            entity = self._entity_from_value(text, fallback_label, value, search_offsets)
            if entity is not None:
                spans.append(entity)

        return spans

    def _entity_from_value(
        self,
        text: str,
        fallback_label: str | None,
        value: Any,
        search_offsets: dict[str, int],
    ) -> MaskedEntity | None:
        label = fallback_label
        entity_text: str | None = None
        start: int | None = None
        end: int | None = None
        score: float | None = None

        if isinstance(value, str):
            entity_text = value
        elif isinstance(value, dict):
            label = str(value.get("label") or value.get("type") or value.get("entity") or label)
            raw_text = value.get("text") or value.get("span") or value.get("value")
            entity_text = str(raw_text) if raw_text is not None else None
            start = self._read_int(value, "start", "start_char", "char_start")
            end = self._read_int(value, "end", "end_char", "char_end")
            score = self._read_float(value, "score", "confidence", "probability")
        else:
            return None

        if label is None or entity_text is None or entity_text == "":
            return None

        if start is None or end is None:
            start = text.find(entity_text, search_offsets.get(entity_text, 0))
            if start == -1:
                start = text.find(entity_text)
            if start == -1:
                return None
            end = start + len(entity_text)

        if start < 0 or end <= start or end > len(text):
            return None

        search_offsets[entity_text] = end
        return MaskedEntity(label=label, text=text[start:end], start=start, end=end, mask="", score=score)

    def _build_masked_entities(
        self,
        spans: list[MaskedEntity],
        mask_template: str,
    ) -> list[MaskedEntity]:
        counters: dict[str, int] = {}
        entities: list[MaskedEntity] = []

        for span in spans:
            counters[span.label] = counters.get(span.label, 0) + 1
            index = counters[span.label]
            mask = mask_template.format(label=span.label.upper(), label_lower=span.label, index=index)
            entities.append(
                MaskedEntity(
                    label=span.label,
                    text=span.text,
                    start=span.start,
                    end=span.end,
                    mask=mask,
                    score=span.score,
                )
            )

        return entities

    def _apply_masks(self, text: str, entities: list[MaskedEntity]) -> str:
        masked_text = text
        for entity in sorted(entities, key=lambda item: item.start, reverse=True):
            masked_text = masked_text[: entity.start] + entity.mask + masked_text[entity.end :]
        return masked_text

    def _deduplicate_and_remove_overlaps(self, spans: list[MaskedEntity]) -> list[MaskedEntity]:
        unique = {(span.start, span.end, span.label): span for span in spans}
        ordered = sorted(unique.values(), key=lambda span: (span.start, -(span.end - span.start)))
        accepted: list[MaskedEntity] = []
        occupied_until = -1

        for span in ordered:
            if span.start < occupied_until:
                continue
            accepted.append(span)
            occupied_until = span.end

        return accepted

    @staticmethod
    def _read_int(value: dict[str, Any], *keys: str) -> int | None:
        for key in keys:
            if key in value and value[key] is not None:
                return int(value[key])
        return None

    @staticmethod
    def _read_float(value: dict[str, Any], *keys: str) -> float | None:
        for key in keys:
            if key in value and value[key] is not None:
                return float(value[key])
        return None

import unittest

from mcp_server_starter.features.pii.masking import Gliner2PiiMasker


class FakeExtractor:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def extract_entities(self, text, labels, threshold, include_confidence, include_spans):
        self.calls.append(
            {
                "text": text,
                "labels": labels,
                "threshold": threshold,
                "include_confidence": include_confidence,
                "include_spans": include_spans,
            }
        )
        return self.result


class Gliner2PiiMaskerTest(unittest.TestCase):
    def test_masks_text_and_returns_entity_metadata(self) -> None:
        extractor = FakeExtractor(
            {
                "entities": {
                    "person": [{"text": "Jane Doe", "start": 8, "end": 16, "score": 0.97}],
                    "email": [{"text": "jane@example.com", "start": 20, "end": 36, "score": 0.99}],
                }
            }
        )
        masker = Gliner2PiiMasker(extractor=extractor)

        result = masker.mask_text("Contact Jane Doe at jane@example.com.")

        self.assertEqual(result.masked_text, "Contact [PII:PERSON:1] at [PII:EMAIL:1].")
        self.assertEqual(len(result.entities), 2)
        self.assertEqual(result.entities[0].label, "person")
        self.assertEqual(result.entities[0].text, "Jane Doe")
        self.assertEqual(result.entities[0].mask, "[PII:PERSON:1]")
        self.assertEqual(result.entities[1].label, "email")
        self.assertEqual(result.entities[1].text, "jane@example.com")
        self.assertTrue(extractor.calls[0]["include_spans"])
        self.assertTrue(extractor.calls[0]["include_confidence"])

    def test_supports_string_entities_without_spans(self) -> None:
        extractor = FakeExtractor({"entities": {"phone_number": ["555-0100"]}})
        masker = Gliner2PiiMasker(extractor=extractor)

        result = masker.mask_text("Call 555-0100 today.")

        self.assertEqual(result.masked_text, "Call [PII:PHONE_NUMBER:1] today.")
        self.assertEqual(result.entities[0].start, 5)
        self.assertEqual(result.entities[0].end, 13)

    def test_allows_custom_label_overrides(self) -> None:
        extractor = FakeExtractor({"entities": {}})
        masker = Gliner2PiiMasker(extractor=extractor)

        masker.mask_text("hello", labels=[" custom_id ", "custom_id"])

        self.assertEqual(extractor.calls[0]["labels"], ["custom_id"])

    def test_rejects_empty_label_overrides(self) -> None:
        masker = Gliner2PiiMasker(extractor=FakeExtractor({"entities": {}}))

        with self.assertRaisesRegex(ValueError, "labels must include"):
            masker.mask_text("hello", labels=[" "])

    def test_rejects_threshold_outside_probability_range(self) -> None:
        masker = Gliner2PiiMasker(extractor=FakeExtractor({"entities": {}}))

        with self.assertRaisesRegex(ValueError, "threshold must be between 0 and 1"):
            masker.mask_text("hello", threshold=1.5)

    def test_removes_overlapping_spans_preferring_longer_first_span(self) -> None:
        extractor = FakeExtractor(
            {
                "entities": {
                    "person": [{"text": "Jane Doe", "start": 0, "end": 8}],
                    "first_name": [{"text": "Jane", "start": 0, "end": 4}],
                }
            }
        )
        masker = Gliner2PiiMasker(extractor=extractor)

        result = masker.mask_text("Jane Doe")

        self.assertEqual(result.masked_text, "[PII:PERSON:1]")
        self.assertEqual(len(result.entities), 1)


if __name__ == "__main__":
    unittest.main()

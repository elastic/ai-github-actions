from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_code_complexity_detector_requires_noop_when_no_findings():
    text = (ROOT / ".github/workflows/gh-aw-code-complexity-detector.md").read_text(encoding="utf-8")
    assert "No-op Guardrail" in text
    assert "call `noop` with a brief reason and stop" in text
    assert "Do not end the run silently" in text


def test_code_duplication_detector_requires_noop_when_no_findings():
    text = (ROOT / ".github/workflows/gh-aw-code-duplication-detector.md").read_text(encoding="utf-8")
    assert "No-op Guardrail" in text
    assert "call `noop` with a brief reason and stop" in text
    assert "Do not end the run silently" in text

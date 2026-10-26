import importlib.util
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from smoke_yolo_real import preflight, run


def test_preflight_reports_missing_video_and_weights(tmp_path):
    issues = preflight(tmp_path / "missing.mp4", tmp_path / "missing.pt")
    assert any("Video inexistente" in item for item in issues)
    assert any("Pesos inexistentes" in item for item in issues)


def test_smoke_blocks_without_video_and_weights(tmp_path):
    result, code = run(tmp_path / "missing.mp4", tmp_path / "missing.pt")
    assert code == 2
    assert result["status"] == "BLOCKED"
    assert result["frames"] == 0


def test_preflight_does_not_require_yolo_import_when_missing_files(tmp_path):
    result, code = run(tmp_path / "a.mp4", tmp_path / "a.pt")
    assert result["detections"] == 0
    assert code != 0

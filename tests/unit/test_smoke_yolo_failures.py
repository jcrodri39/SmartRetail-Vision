import sys
import types
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import smoke_yolo_real as smoke

class Cap:
    def __init__(self, limit=2): self.i = 0; self.released = False; self.limit = limit
    def isOpened(self): return True
    def read(self):
        self.i += 1
        return (True, object()) if self.i <= self.limit else (False, None)
    def release(self): self.released = True

def test_failure_keeps_partial_evidence_and_releases_capture():
    cap = Cap()
    class Model:
        def __init__(self, weights): pass
        def track(self, frame, **kwargs):
            if cap.i == 2: raise RuntimeError("inference failed")
            return [types.SimpleNamespace(boxes=None)]
    with patch.object(smoke, "preflight", return_value=[]), patch.dict(sys.modules, {
        "ultralytics": types.SimpleNamespace(YOLO=Model),
        "cv2": types.SimpleNamespace(VideoCapture=lambda _: cap)}):
        result, code = smoke.run("video.mp4", "weights.pt", max_frames=3)
    assert code == 1 and result["status"] == "FAILED"
    assert result["frames"] == 1 and len(result["per_frame"]) == 1
    assert result["detections"] == result["tracked_boxes"] == 0
    assert cap.released

def test_early_video_end_is_disclosed():
    cap = Cap(limit=1)
    class Model:
        def __init__(self, weights): pass
        def track(self, frame, **kwargs): return [types.SimpleNamespace(boxes=None)]
    with patch.object(smoke, "preflight", return_value=[]), patch.dict(sys.modules, {
        "ultralytics": types.SimpleNamespace(YOLO=Model),
        "cv2": types.SimpleNamespace(VideoCapture=lambda _: cap)}):
        result, code = smoke.run("video.mp4", "weights.pt", max_frames=3)
    assert code == 0 and result["complete_requested_window"] is False
    assert result["requested_frames"] == 3 and result["frames"] == 1
    assert cap.released

import sys
import types
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import smoke_yolo_real as smoke

class Tensor:
    def __init__(self, values): self.values = values
    def int(self): return self
    def cpu(self): return self
    def tolist(self): return self.values

class Cap:
    def __init__(self): self.n = 0; self.released = False
    def isOpened(self): return True
    def read(self):
        self.n += 1
        return (True, object()) if self.n == 1 else (False, None)
    def release(self): self.released = True

def test_detailed_evidence_contains_coordinates_confidence_and_track_ids():
    cap = Cap()
    boxes = types.SimpleNamespace(id=Tensor([12]), xyxy=Tensor([[1, 2, 20, 30]]), conf=Tensor([0.87]))
    # Simula el contenedor de cajas de Ultralytics.
    boxes = type("Boxes", (), {"__len__": lambda self: 1, "id": boxes.id, "xyxy": boxes.xyxy, "conf": boxes.conf})()
    class Model:
        def __init__(self, path): pass
        def track(self, frame, **kwargs): return [types.SimpleNamespace(boxes=boxes)]
    with patch.object(smoke, "preflight", return_value=[]), patch.dict(sys.modules, {
        "ultralytics": types.SimpleNamespace(YOLO=Model),
        "cv2": types.SimpleNamespace(VideoCapture=lambda path: cap)}):
        result, code = smoke.run("video.mp4", "model.pt", max_frames=1, details=True)
    assert code == 0
    assert result["per_frame"][0]["observations"] == [{"bbox_xyxy": [1.0, 2.0, 20.0, 30.0], "confidence": 0.87, "track_id": 12}]
    assert cap.released

def test_rejects_nonpositive_frame_count():
    result, code = smoke.run("video.mp4", "model.pt", max_frames=0)
    assert code == 1 and result["status"] == "FAILED"

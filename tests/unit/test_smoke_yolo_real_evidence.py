import sys
import types
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import smoke_yolo_real as smoke


class FakeIds:
    def __init__(self, values): self.values = values
    def int(self): return self
    def cpu(self): return self
    def tolist(self): return self.values
    def __len__(self): return len(self.values)


class FakeBoxes:
    def __init__(self, ids): self.id = FakeIds(ids)
    def __len__(self): return len(self.id)


class FakeCap:
    def __init__(self): self.index = 0; self.released = False
    def isOpened(self): return True
    def read(self):
        self.index += 1
        return (True, object()) if self.index <= 3 else (False, None)
    def release(self): self.released = True


def test_real_smoke_contract_counts_unique_ids_not_per_frame(tmp_path):
    cap = FakeCap()
    class FakeYOLO:
        def __init__(self, weights): pass
        def track(self, frame, **kwargs):
            ids = [[7, 8], [7], [7, 9]][cap.index - 1]
            return [types.SimpleNamespace(boxes=FakeBoxes(ids))]
    with patch.object(smoke, "preflight", return_value=[]), \
         patch.dict(sys.modules, {"ultralytics": types.SimpleNamespace(YOLO=FakeYOLO),
                                  "cv2": types.SimpleNamespace(VideoCapture=lambda _: cap)}):
        result, code = smoke.run(tmp_path / "video.mp4", tmp_path / "model.pt", max_frames=3)
    assert code == 0
    assert result["frames"] == 3
    assert result["detections"] == 5
    assert result["tracked_boxes"] == 5
    assert result["unique_track_ids"] == 3
    assert len(result["per_frame"]) == 3
    assert cap.released


def test_real_smoke_contract_includes_empty_frames(tmp_path):
    cap = FakeCap()
    class FakeYOLO:
        def __init__(self, weights): pass
        def track(self, frame, **kwargs): return [types.SimpleNamespace(boxes=None)]
    with patch.object(smoke, "preflight", return_value=[]), \
         patch.dict(sys.modules, {"ultralytics": types.SimpleNamespace(YOLO=FakeYOLO),
                                  "cv2": types.SimpleNamespace(VideoCapture=lambda _: cap)}):
        result, code = smoke.run("video.mp4", "model.pt", max_frames=2)
    assert code == 0
    assert result["detections"] == result["unique_track_ids"] == 0
    assert result["per_frame"] == [{"frame": 1, "detections": 0, "tracked_boxes": 0},
                                    {"frame": 2, "detections": 0, "tracked_boxes": 0}]

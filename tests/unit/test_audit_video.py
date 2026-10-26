import cv2
import numpy as np
import pytest
from scripts.audit_video import audit_video


def test_video_audit_reads_all_frames(tmp_path):
    path = tmp_path / "test.avi"
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (64, 48))
    assert out.isOpened()
    for i in range(6):
        out.write(np.full((48, 64, 3), i * 20, dtype=np.uint8))
    out.release()
    result = audit_video(path, sample_stride=2)
    assert result["frames_decoded"] == 6
    assert result["samples"] == 3
    assert result["all_reported_frames_decoded"] is True
    assert result["mean_sample_frame_change_0_255"] > 0


def test_invalid_stride(tmp_path):
    with pytest.raises(ValueError, match="sample_stride"):
        audit_video(tmp_path / "missing.mp4", 0)

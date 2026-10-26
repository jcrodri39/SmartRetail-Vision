from datetime import datetime, timedelta
from types import SimpleNamespace
import pytest
from app.vision.timing import VideoClock, close_at_last_seen

def test_file_video_uses_video_duration_not_processing_speed():
    clock=VideoClock(datetime(2026,1,1),25.0,True)
    a=clock.at_frame(1,0)
    b=clock.at_frame(501,20000)
    assert (b-a).total_seconds()==20

def test_file_video_falls_back_to_frame_count_if_position_unavailable():
    clock=VideoClock(datetime(2026,1,1),25.0,True)
    clock.at_frame(1,0)
    assert (clock.at_frame(51,0)-clock.started_at).total_seconds()==2

def test_video_without_time_reference_is_rejected():
    with pytest.raises(ValueError):VideoClock(datetime(2026,1,1),0,True).at_frame(3,None)

def test_lost_track_closes_at_last_observation():
    start=datetime(2026,1,1)
    ev=SimpleNamespace(entrada=start,salida=None,permanencia_seg=0)
    close_at_last_seen(ev,start+timedelta(seconds=8))
    assert ev.permanencia_seg==8

def test_live_clock_uses_monotonic_elapsed():
    start=datetime(2026,1,1)
    clock=VideoClock(start,0,False)
    assert (clock.at_frame(4,live_elapsed=3.5)-start).total_seconds()==3.5

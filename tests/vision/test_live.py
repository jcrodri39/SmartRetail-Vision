from app.vision.live import LiveVision
def test_live_initial_state():v=LiveVision();assert not v.running and v.stats["frames"]==0
def test_stop_idempotent():v=LiveVision();v.stop();assert not v.running

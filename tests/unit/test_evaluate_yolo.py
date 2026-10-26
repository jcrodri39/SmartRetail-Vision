import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from evaluate_yolo import evaluate, iou

def evidence(*entries):
    return {"status":"EXECUTED","per_frame":list(entries)}

def obs(*boxes):
    return [{"bbox_xyxy":list(b),"confidence":0.9,"track_id":None} for b in boxes]

def test_iou_identical_and_disjoint():
    assert iou([0,0,10,10],[0,0,10,10]) == 1
    assert iou([0,0,10,10],[20,20,30,30]) == 0

def test_one_to_one_and_false_positives():
    ev=evidence({"frame":1,"observations":obs([0,0,10,10],[0,0,10,10])},
                {"frame":2,"observations":obs()})
    labels={"frames":[{"frame":1,"boxes":[[0,0,10,10]]},
                      {"frame":2,"boxes":[[0,0,10,10]]}]}
    r=evaluate(ev,labels)
    assert (r["tp"],r["fp"],r["fn"])==(1,1,1)
    assert r["precision"]==0.5 and r["recall"]==0.5 and r["f1"]==0.5

def test_only_annotated_frames_count():
    ev=evidence({"frame":1,"observations":obs([0,0,10,10])},
                {"frame":2,"observations":obs([0,0,10,10])})
    r=evaluate(ev,{"frames":[{"frame":1,"boxes":[[0,0,10,10]]}]})
    assert (r["tp"],r["fp"],r["fn"],r["annotated_frames"])==(1,0,0,1)

def test_reject_simulated_or_incomplete_evidence():
    with pytest.raises(ValueError,match="ejecución YOLO real"):
        evaluate({"status":"FAILED","per_frame":[]},{"frames":[{"frame":1,"boxes":[]}]})
    with pytest.raises(ValueError,match="observaciones"):
        evaluate(evidence({"frame":1,"detections":1}),{"frames":[{"frame":1,"boxes":[]}]})

def test_reject_duplicate_or_unknown_annotation_frame():
    ev=evidence({"frame":1,"observations":obs()})
    with pytest.raises(ValueError):
        evaluate(ev,{"frames":[{"frame":2,"boxes":[]}]})
    with pytest.raises(ValueError):
        evaluate(ev,{"frames":[{"frame":1,"boxes":[]},{"frame":1,"boxes":[]}]})

def test_reject_invalid_boxes_and_threshold():
    ev=evidence({"frame":1,"observations":obs([0,0,0,10])})
    with pytest.raises(ValueError,match="Caja inválida"):
        evaluate(ev,{"frames":[{"frame":1,"boxes":[]}]})
    with pytest.raises(ValueError,match="umbral"):
        evaluate(ev,{"frames":[{"frame":1,"boxes":[]}]},0)

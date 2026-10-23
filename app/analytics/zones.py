import json,cv2,numpy as np
def valid_polygon(raw):
    try:p=json.loads(raw);return isinstance(p,list) and len(p)>=3 and all(isinstance(x,list) and len(x)==2 for x in p)
    except Exception:return False
def inside(raw,point):
    if not valid_polygon(raw):return False
    return cv2.pointPolygonTest(np.array(json.loads(raw),dtype=np.int32),point,False)>=0

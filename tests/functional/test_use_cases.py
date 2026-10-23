UCS={
"UC001":"login/logout","UC002":"video source CRUD/upload","UC003":"visual polygon zones",
"UC004":"YOLO live/tracking/events","UC005":"dashboard KPIs","UC006":"heatmap",
"UC007":"CSV reports/history","UC008":"users/roles/status"}
def test_all_eight_use_cases_catalogued():assert len(UCS)==8 and set(UCS)=={f"UC{i:03d}" for i in range(1,9)}

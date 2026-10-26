# Fase 6 — filtros por sesión

Se añadió el parámetro opcional `processing_id` al dashboard, reportes JSON, CSV y XLSX. Cuando se selecciona una sesión, se restringen tracks, detecciones y eventos de zona. Se comprueba que la sesión exista y pertenezca a la tienda solicitada. Si se omite el parámetro se conservan los agregados históricos, que pueden sumar reprocesamientos; no representan visitantes únicos. Las plantillas aún requieren selector visual de sesión.

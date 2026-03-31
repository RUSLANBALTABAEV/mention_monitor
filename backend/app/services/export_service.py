import csv
import json
import io
from typing import List, Dict
import pandas as pd
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

class ExportService:
    @staticmethod
    def export_to_csv(mentions: List[Dict]) -> StreamingResponse:
        if not mentions:
            return StreamingResponse(io.StringIO(""), media_type="text/csv",
                                     headers={"Content-Disposition": "attachment; filename=mentions.csv"})
        output = io.StringIO()
        fieldnames = ["id", "text", "source_type", "source_url", "author", "date",
                      "geo_country", "geo_city", "keyword", "content_type", "ocr_text", "media_url"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for m in mentions:
            row = {k: m.get(k, "") for k in fieldnames}
            writer.writerow(row)
        return StreamingResponse(io.StringIO(output.getvalue()), media_type="text/csv",
                                 headers={"Content-Disposition": "attachment; filename=mentions.csv"})

    @staticmethod
    def export_to_excel(mentions: List[Dict]) -> StreamingResponse:
        output = io.BytesIO()
        if not mentions:
            pd.DataFrame().to_excel(output, index=False)
        else:
            df = pd.DataFrame(mentions)
            df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 headers={"Content-Disposition": "attachment; filename=mentions.xlsx"})

    @staticmethod
    def export_to_json(mentions: List[Dict]) -> StreamingResponse:
        json_str = json.dumps(mentions, default=str, ensure_ascii=False, indent=2)
        return StreamingResponse(io.BytesIO(json_str.encode('utf-8')), media_type="application/json",
                                 headers={"Content-Disposition": "attachment; filename=mentions.json"})
"""Export builders. Callers must pass a queryset already scoped to the requester."""
from io import BytesIO
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def grades_dataframe(rows):
    return pd.DataFrame.from_records(rows, columns=["student_number", "student_name", "class_code", "assessment", "score"])

def grades_excel(rows):
    frame=grades_dataframe(rows)
    output=BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        frame.to_excel(writer, index=False, sheet_name="Notas")
    return output.getvalue()

def grades_pdf(rows, title="Relatério de notas"):
    frame=grades_dataframe(rows)
    output=BytesIO(); doc=SimpleDocTemplate(output, pagesize=landscape(A4), title=title)
    styles=getSampleStyleSheet(); elements=[Paragraph(title, styles["Title"]), Spacer(1,12)]
    data=[list(frame.columns)] + frame.fillna("").astype(str).values.tolist()
    table=Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    elements.append(table); doc.build(elements); return output.getvalue()

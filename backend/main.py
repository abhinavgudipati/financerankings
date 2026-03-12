from fastapi import FastAPI
from ranking import compute_rankings
from fastapi.responses import StreamingResponse
import csv
import io

app = FastAPI(title="Finance Rankings API")

@app.get("/")
def root():
    return {"message": "Finance Rankings API is running"}

@app.get("/rankings")
def get_rankings(start_year: int = 2018, end_year: int = 2024):
    return compute_rankings(start_year, end_year)


@app.get("/rankings/export")
def export_csv(start_year: int = 2018, end_year: int = 2024):

    data = compute_rankings(start_year, end_year)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Institution", "Country", "Score", "Citations", "Papers"])

    for row in data:
        writer.writerow([
            row["institution"],
            row["country"],
            row["score"],
            row["citations"],
            row["papers"],
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rankings.csv"},
    )
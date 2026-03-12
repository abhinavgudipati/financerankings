from sqlalchemy import func
from database import SessionLocal
from models import Institution, Authorship, Publication, Journal


def compute_rankings(start_year=2018, end_year=2024):

    db = SessionLocal()

    results = (
        db.query(
            Institution.name,
            Institution.country_name,
            func.sum(Journal.weight / Authorship.num_authors).label("score"),
            func.sum(Publication.citations).label("citations"),
            func.count(Publication.id).label("papers")
        )
        .join(Authorship, Authorship.institution_id == Institution.id)
        .join(Publication, Publication.id == Authorship.publication_id)
        .join(Journal, Journal.id == Publication.journal_id)
        .filter(Publication.year >= start_year)
        .filter(Publication.year <= end_year)
        .group_by(Institution.id)
        .order_by(func.sum(Journal.weight / Authorship.num_authors).desc())
        .all()
    )

    db.close()

    return [
        {
            "institution": r[0],
            "country": r[1],
            "score": float(r[2] or 0),
            "citations": int(r[3] or 0),
            "papers": int(r[4] or 0),
        }
        for r in results
    ]
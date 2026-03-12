import json
from collections import defaultdict
from database import SessionLocal
from models import Institution, Author, Publication, Authorship, Journal

db = SessionLocal()

data = {}

results = (
    db.query(
        Institution.name.label("institution"),
        Institution.country_name.label("country"),
        Author.name.label("author"),
        Author.orcid.label("orcid"),
        Publication.title.label("title"),
        Publication.year.label("year"),
        Publication.doi.label("doi"),
        Journal.name.label("journal"),
        Publication.citations.label("citations"),
        (Journal.weight / Authorship.num_authors).label("credit"),
    )
    .select_from(Authorship)
    .join(Institution, Institution.id == Authorship.institution_id)
    .join(Author, Author.id == Authorship.author_id)
    .join(Publication, Publication.id == Authorship.publication_id)
    .join(Journal, Journal.id == Publication.journal_id)
    .filter(Publication.year >= 2016)
    .all()
)

for row in results:

    inst = row.institution
    author = row.author
    credit = float(row.credit or 0)
    citations = int(row.citations or 0)
    doi = row.doi if row.doi else None

    # -----------------------
    # Institution
    # -----------------------

    if inst not in data:
        data[inst] = {
            "country": row.country,
            "total_score": 0.0,
            "total_citations": 0,
            "authors": {},
        }

    # -----------------------
    # Author
    # -----------------------

    if author not in data[inst]["authors"]:
        data[inst]["authors"][author] = {
            "orcid": row.orcid,
            "total_score": 0.0,
            "total_citations": 0,
            "papers": [],
        }

    # -----------------------
    # Paper
    # -----------------------

    data[inst]["authors"][author]["papers"].append(
        {
            "title": row.title,
            "year": row.year,
            "journal": row.journal,
            "credit": round(credit, 4),
            "citations": citations,
            "doi": doi,
        }
    )

    # -----------------------
    # Aggregate Scores
    # -----------------------

    data[inst]["authors"][author]["total_score"] += credit
    data[inst]["authors"][author]["total_citations"] += citations
    data[inst]["total_score"] += credit
    data[inst]["total_citations"] += citations


# -----------------------
# Sorting (Important)
# -----------------------

# Sort authors inside each institution
for inst in data:
    sorted_authors = sorted(
        data[inst]["authors"].items(),
        key=lambda x: x[1]["total_score"],
        reverse=True,
    )

    data[inst]["authors"] = {
        author: {
            **info,
            "total_score": round(info["total_score"], 4),
        }
        for author, info in sorted_authors
    }

    data[inst]["total_score"] = round(data[inst]["total_score"], 4)


# Sort institutions by total_score
data = dict(
    sorted(
        data.items(),
        key=lambda x: x[1]["total_score"],
        reverse=True,
    )
)

db.close()

# -----------------------
# Export
# -----------------------

output_path = "../financerankings-site/rankings_detailed.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Exported rankings_detailed.json")
print("Total rows:", len(results))
import requests
import time
from database import SessionLocal, engine
from models import Base, Institution, Author, Publication, Journal, Authorship

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# ------------------------------
# Configuration
# ------------------------------

JOURNALS = {
    "https://openalex.org/S5353659": ("Journal of Finance", 1.0),
    "https://openalex.org/S149240962": ("Journal of Financial Economics", 1.0),
    "https://openalex.org/S170137484": ("Review of Financial Studies", 1.0),
}

BASE_URL = "https://api.openalex.org/works"

HEADERS = {
    "User-Agent": "financerankings.org (abhinav@example.com)"
}

EDUCATION_ONLY = True

COUNTRY_MAP = {
    "US": "United States",
    "GB": "United Kingdom",
    "CH": "Switzerland",
    "HK": "Hong Kong",
    "SG": "Singapore",
    "CA": "Canada",
    "DE": "Germany",
    "FR": "France",
    "CN": "China",
    "IN": "India",
}

# ------------------------------
# Utility Functions
# ------------------------------

def normalize_doi(work):
    """
    Extract DOI safely from OpenAlex response.
    Ensures canonical format: https://doi.org/xxxx
    """
    doi = work.get("doi")

    # Sometimes stored under ids
    if not doi:
        ids = work.get("ids", {})
        doi = ids.get("doi")

    if not doi:
        return None

    doi = doi.strip()

    # Remove any prefix
    doi = doi.replace("https://doi.org/", "")
    doi = doi.replace("http://doi.org/", "")

    return f"https://doi.org/{doi}"


# ------------------------------
# Main Ingestion Logic
# ------------------------------

def ingest_journal(journal_openalex_id, journal_name, weight):

    db = SessionLocal()

    # Ensure journal exists
    journal = db.query(Journal).filter_by(openalex_id=journal_openalex_id).first()
    if not journal:
        journal = Journal(
            name=journal_name,
            openalex_id=journal_openalex_id,
            weight=weight,
        )
        db.add(journal)
        db.commit()

    cursor = "*"

    while True:

        params = {
            "filter": f"primary_location.source.id:{journal_openalex_id},publication_year:>2015",
            "per_page": 200,
            "cursor": cursor,
        }

        response = requests.get(BASE_URL, params=params, headers=HEADERS)

        if response.status_code != 200:
            print("Request failed:", response.text)
            break

        data = response.json()
        works = data.get("results", [])

        if not works:
            break

        print(f"Fetched {len(works)} papers from {journal_name}")

        for work in works:

            openalex_id = work.get("id")
            if not openalex_id:
                continue

            # Skip duplicate publications
            existing_pub = db.query(Publication).filter_by(
                openalex_id=openalex_id
            ).first()

            if existing_pub:
                continue

            publication = Publication(
                title=work.get("title"),
                openalex_id=openalex_id,
                doi=normalize_doi(work),
                year=work.get("publication_year"),
                citations=work.get("cited_by_count", 0),
                journal_id=journal.id,
            )

            db.add(publication)
            db.flush()

            authorships = work.get("authorships", [])
            num_authors = len(authorships) or 1

            for position, author_data in enumerate(authorships):

                author_info = author_data.get("author")
                if not author_info:
                    continue

                author_openalex_id = author_info.get("id")
                author_name = author_info.get("display_name")
                orcid = author_info.get("orcid")

                if not author_openalex_id:
                    continue

                institutions = author_data.get("institutions")
                if not institutions:
                    continue

                # Prefer education institution
                edu_insts = [
                    inst for inst in institutions
                    if inst.get("type") == "education"
                ]

                inst_data = edu_insts[0] if edu_insts else institutions[0]

                inst_type = inst_data.get("type")

                if EDUCATION_ONLY and inst_type != "education":
                    continue

                inst_name = inst_data.get("display_name")
                inst_openalex = inst_data.get("id")
                ror = inst_data.get("ror")
                country_code = inst_data.get("country_code")
                country_name = COUNTRY_MAP.get(country_code, country_code)

                # Get or create institution
                institution = db.query(Institution).filter_by(
                    openalex_id=inst_openalex
                ).first()

                if not institution:
                    institution = Institution(
                        name=inst_name,
                        openalex_id=inst_openalex,
                        ror=ror,
                        type=inst_type,
                        country_code=country_code,
                        country_name=country_name,
                    )
                    db.add(institution)
                    db.flush()

                # Get or create author
                author = db.query(Author).filter_by(
                    openalex_id=author_openalex_id
                ).first()

                if not author:
                    author = Author(
                        name=author_name,
                        openalex_id=author_openalex_id,
                        orcid=orcid,
                        institution_id=institution.id,  # optional consistency
                    )
                    db.add(author)
                    db.flush()

                # Prevent duplicate authorship
                existing_authorship = db.query(Authorship).filter_by(
                    author_id=author.id,
                    publication_id=publication.id,
                ).first()

                if existing_authorship:
                    continue

                authorship = Authorship(
                    author_id=author.id,
                    publication_id=publication.id,
                    institution_id=institution.id,
                    position=position + 1,
                    num_authors=num_authors,
                )

                db.add(authorship)

        db.commit()

        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

        time.sleep(1)  # polite API usage

    db.close()


# ------------------------------
# Run Script
# ------------------------------

if __name__ == "__main__":
    for journal_id, (journal_name, weight) in JOURNALS.items():
        print(f"\nIngesting {journal_name}")
        ingest_journal(journal_id, journal_name, weight)
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from database import Base


# ======================
# Institution
# ======================

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True)

    # Core identity
    name = Column(String, nullable=False, index=True)
    openalex_id = Column(String, unique=True, index=True)
    ror = Column(String, nullable=True, index=True)

    # Classification
    country_code = Column(String, index=True)   # US, CH, HK
    country_name = Column(String, index=True)   # USA, Switzerland
    type = Column(String, index=True)           # education, company, gov

    # Relationships
    authors = relationship("Author", back_populates="institution")

    __table_args__ = (
        UniqueConstraint("name", "country_code", name="unique_inst_name_country"),
    )


# ======================
# Author
# ======================

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)

    name = Column(String, index=True)
    openalex_id = Column(String, unique=True, index=True)
    orcid = Column(String, nullable=True, index=True)

    institution_id = Column(Integer, ForeignKey("institutions.id"), index=True)
    institution = relationship("Institution", back_populates="authors")

    authorships = relationship("Authorship", back_populates="author")

    __table_args__ = (
        Index("idx_author_name_institution", "name", "institution_id"),
    )


# ======================
# Journal
# ======================

class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True, index=True)
    openalex_id = Column(String, unique=True, index=True)
    weight = Column(Float)

    publications = relationship("Publication", back_populates="journal")


# ======================
# Publication
# ======================

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True)

    title = Column(String)
    openalex_id = Column(String, unique=True, index=True)
    doi = Column(String, nullable=True, index=True)

    year = Column(Integer, index=True)
    citations = Column(Integer, default=0)

    journal_id = Column(Integer, ForeignKey("journals.id"), index=True)
    journal = relationship("Journal", back_populates="publications")

    authorships = relationship("Authorship", back_populates="publication")

    __table_args__ = (
        Index("idx_pub_year_journal", "year", "journal_id"),
    )


# ======================
# Authorship
# ======================

class Authorship(Base):
    __tablename__ = "authorships"

    id = Column(Integer, primary_key=True)

    author_id = Column(Integer, ForeignKey("authors.id"))
    publication_id = Column(Integer, ForeignKey("publications.id"))
    institution_id = Column(Integer, ForeignKey("institutions.id"))  # ← ADD THIS

    position = Column(Integer)
    num_authors = Column(Integer)

    author = relationship("Author", back_populates="authorships")
    publication = relationship("Publication", back_populates="authorships")
    institution = relationship("Institution")  # ← ADD THIS

    __table_args__ = (
        UniqueConstraint("author_id", "publication_id", name="unique_authorship"),
    )
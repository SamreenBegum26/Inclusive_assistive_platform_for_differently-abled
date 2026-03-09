from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    disability_type = Column(String, nullable=False)  # physical, visual, hearing, mental, all
    eligibility = Column(Text, nullable=False)
    how_to_apply = Column(Text, nullable=False)
    documents_required = Column(Text, nullable=False)
    official_link = Column(String, nullable=False)
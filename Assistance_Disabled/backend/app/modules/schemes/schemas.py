from pydantic import BaseModel


class SchemeResponse(BaseModel):
    id: int
    name: str
    description: str
    disability_type: str
    eligibility: str
    how_to_apply: str
    documents_required: str
    official_link: str

    class Config:
        from_attributes = True


class SchemeCreate(BaseModel):
    name: str
    description: str
    disability_type: str   # physical, visual, hearing, mental, all
    eligibility: str
    how_to_apply: str
    documents_required: str
    official_link: str
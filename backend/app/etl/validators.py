from pydantic import BaseModel, field_validator
import re

class PaperSchema(BaseModel):
    arxiv_id:     str
    title:        str
    abstract:     str
    authors:      list[str]
    category:     str
    pdf_url:      str
    arxiv_url:    str
    published_at: str

    @field_validator("title", "abstract")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("arxiv_id")
    @classmethod
    def valid_arxiv_id(cls, v: str) -> str:
        if not re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", v):
            raise ValueError(f"Invalid arxiv_id: {v}")
        return v
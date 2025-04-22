from pydantic import BaseModel
from typing import List

class ResultSection(BaseModel):
    title: str
    text: str
    figures: List[str]  # paths to figure files

class Paper(BaseModel):
    title: str
    introduction: str
    methods: str
    results: List[ResultSection]
    discussion: str
    references: List[str]

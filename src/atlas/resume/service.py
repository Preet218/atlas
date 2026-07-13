"""
High-level orchestration: extract -> parse -> map.
"""

from atlas.resume.extractor import ResumeExtractor
from atlas.resume.parser import ResumeParser
from atlas.resume.mapper import ResumeMapper


class ResumeService:
    def __init__(self):
        self.extractor = ResumeExtractor()
        self.parser = ResumeParser()
        self.mapper = ResumeMapper()

    def process(self, file_path: str) -> dict:
        raw_text = self.extractor.extract(file_path)
        parsed = self.parser.parse(raw_text)
        return self.mapper.map(parsed)

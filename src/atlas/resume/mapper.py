"""
Maps parsed resume fields onto internal schema / models.
"""


class ResumeMapper:
    def map(self, parsed_data: dict) -> dict:
        """Map parsed resume data to the internal candidate schema."""
        raise NotImplementedError

from dataclasses import dataclass


@dataclass
class RetrievalChunk:
    """Represents a chunk retrieved from the database."""
    text: str
    start_time: float
    end_time: float
    distance: float

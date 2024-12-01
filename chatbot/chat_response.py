from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatResponse:
    user_id: str
    query: str
    query_type: str
    topics : [str]
    response : [str]
    doc_scores : Optional[list] = None

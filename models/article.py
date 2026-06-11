from pydantic import BaseModel

class Article(BaseModel):
    title: str
    category: str
    excerpt: str
    content: str
    published_at: str

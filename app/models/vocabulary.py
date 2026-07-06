from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Vocabulary(Base):
    __tablename__ = "vocabularies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word = Column(String, nullable=False, index=True)
    language = Column(Enum("en", "zh", name="vocab_language"), nullable=False)
    definitions = Column(JSON, default=list)
    pronunciation_url = Column(String, nullable=True)
    examples = Column(JSON, default=list)
    synonyms = Column(JSON, default=list)
    memory_tip = Column(Text, nullable=True)
    learned_date = Column(Date, nullable=True)

    user = relationship("User", backref="vocabularies")

    __table_args__ = (
        UniqueConstraint("user_id", "word", "language", name="uq_user_word_lang"),
    )

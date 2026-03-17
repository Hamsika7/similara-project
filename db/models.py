from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, LargeBinary, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id           = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    description  = Column(Text, default="")
    image_url    = Column(String, default="")
    category     = Column(String, default="")
    created_at   = Column(DateTime, default=datetime.utcnow)


class Embedding(Base):
    __tablename__ = "embeddings"

    id           = Column(Integer, primary_key=True, index=True)
    content_key  = Column(String, unique=True, index=True)
    # ^ this is the product_name for text, image_url for images
    source       = Column(String, default="text")
    # ^ "text" or "image"
    vector       = Column(LargeBinary, nullable=False)
    # ^ numpy array stored as bytes
    dimensions   = Column(Integer, default=384)
    # ^ 384 for SBERT, 512 for CLIP
    created_at   = Column(DateTime, default=datetime.utcnow)


class MatchResult(Base):
    __tablename__ = "match_results"

    id            = Column(Integer, primary_key=True, index=True)
    product_a     = Column(String, index=True)
    product_b     = Column(String, index=True)
    fuzzy_score   = Column(Float)
    text_sim      = Column(Float)
    image_sim     = Column(Float)
    final_score   = Column(Float)
    is_duplicate  = Column(Boolean)
    created_at    = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    email        = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin     = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)
"""
Script seed curriculum ngữ pháp.
Đọc data/grammar_curriculum.yaml và upsert vào bảng grammar_topics.

Cách chạy:
    cd VisionNest
    python scripts/seed_grammar.py

Yêu cầu:
    - Database đang chạy (docker-compose up -d)
    - Đã chạy alembic upgrade head
    - pip install pyyaml
"""

import asyncio
import os
import sys
from pathlib import Path

# Thêm thư mục gốc vào PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.grammar_topic import GrammarTopic


async def seed():
    """Đọc YAML và upsert topics vào database"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("LỖI: Chưa set DATABASE_URL trong .env")
        sys.exit(1)

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Đọc file YAML
    yaml_path = Path(__file__).resolve().parent.parent / "data" / "grammar_curriculum.yaml"
    if not yaml_path.exists():
        print(f"LỖI: Không tìm thấy {yaml_path}")
        sys.exit(1)

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    topics = data.get("topics", [])
    print(f"Đọc được {len(topics)} topics từ YAML")

    async with async_session() as session:
        count_created = 0
        count_updated = 0

        for topic_data in topics:
            # Kiểm tra topic đã tồn tại chưa (theo order_num + level)
            result = await session.execute(
                select(GrammarTopic).where(
                    GrammarTopic.order_num == topic_data["order"],
                    GrammarTopic.level == topic_data["level"],
                )
            )
            existing = result.scalars().first()

            if existing:
                # Update
                existing.topic = topic_data["topic"]
                existing.category = topic_data["category"]
                existing.description = topic_data.get("description", "")
                existing.is_active = True
                count_updated += 1
            else:
                # Create
                topic = GrammarTopic(
                    order_num=topic_data["order"],
                    topic=topic_data["topic"],
                    level=topic_data["level"],
                    category=topic_data["category"],
                    description=topic_data.get("description", ""),
                    is_active=True,
                )
                session.add(topic)
                count_created += 1

        await session.commit()
        print(f"Seed hoàn tất: {count_created} created, {count_updated} updated")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

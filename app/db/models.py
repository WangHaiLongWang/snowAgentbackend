from datetime import datetime
from typing import List, Optional

from app.server.extensions import db


class Item(db.Model):
    """示例数据模型：用于 /api/data 接口."""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """转换为字典格式，兼容原来的返回结构."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def list_items() -> List[Item]:
    """获取所有 Item 记录."""
    return Item.query.order_by(Item.id.asc()).all()


def get_by_id(item_id: int) -> Optional[Item]:
    """根据 ID 获取单条记录."""
    return Item.query.get(item_id)


def create_item(name: str, description: str) -> Item:
    """创建新 Item 记录并返回模型实例."""
    item = Item(name=name, description=description)
    db.session.add(item)
    db.session.commit()
    return item


def seed_items_if_empty() -> None:
    """在应用启动时，如果表为空则写入一些初始数据."""
    if Item.query.first() is not None:
        return

    samples = [
        Item(name="Item 1", description="First item"),
        Item(name="Item 2", description="Second item"),
        Item(name="Item 3", description="Third item"),
    ]
    db.session.add_all(samples)
    db.session.commit()


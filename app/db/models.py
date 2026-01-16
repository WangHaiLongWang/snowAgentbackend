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


class Resort(db.Model):
    """雪场信息模型"""

    __tablename__ = "resorts"

    id = db.Column(db.String(32), primary_key=True)  # beidahu, songhuahu, koktokay
    name = db.Column(db.String(64), nullable=False)  # 北大湖、松花湖、可可托海
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Slope(db.Model):
    """雪道信息模型"""

    __tablename__ = "slopes"

    id = db.Column(db.Integer, primary_key=True)
    resort_id = db.Column(db.String(32), db.ForeignKey("resorts.id"), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(16), nullable=False)  # open, partial, closed
    difficulty = db.Column(db.String(16), nullable=False)  # 初级、中级、高级、专家
    length = db.Column(db.Integer, nullable=False)  # 长度（米）
    elevation = db.Column(db.Integer, nullable=False)  # 海拔（米）
    notes = db.Column(db.String(256))  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    resort = db.relationship("Resort", backref="slopes")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "status": self.status,
            "difficulty": self.difficulty,
            "length": self.length,
            "elevation": self.elevation,
            "notes": self.notes,
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


def get_resort_by_id(resort_id: str) -> Optional[Resort]:
    """根据 ID 获取雪场."""
    return Resort.query.get(resort_id)


def get_slopes_by_resort(resort_id: str) -> List[Slope]:
    """获取指定雪场的所有雪道."""
    return Slope.query.filter_by(resort_id=resort_id).all()


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


def seed_resorts_if_empty() -> None:
    """初始化雪场数据."""
    if Resort.query.first() is not None:
        return

    resorts = [
        Resort(id="beidahu", name="北大湖"),
        Resort(id="songhuahu", name="松花湖"),
        Resort(id="koktokay", name="可可托海"),
    ]
    db.session.add_all(resorts)
    db.session.commit()


def seed_slopes_if_empty() -> None:
    """初始化雪道数据（示例数据）."""
    if Slope.query.first() is not None:
        return

    # 北大湖雪道
    beidahu_slopes = [
        Slope(
            resort_id="beidahu",
            name="初级雪道1",
            status="open",
            difficulty="初级",
            length=800,
            elevation=1200,
            notes="适合初学者",
        ),
        Slope(
            resort_id="beidahu",
            name="中级雪道1",
            status="open",
            difficulty="中级",
            length=1200,
            elevation=1400,
        ),
        Slope(
            resort_id="beidahu",
            name="高级雪道1",
            status="partial",
            difficulty="高级",
            length=1500,
            elevation=1600,
            notes="部分区域维护中",
        ),
    ]

    # 松花湖雪道
    songhuahu_slopes = [
        Slope(
            resort_id="songhuahu",
            name="初级雪道1",
            status="open",
            difficulty="初级",
            length=600,
            elevation=1100,
        ),
        Slope(
            resort_id="songhuahu",
            name="中级雪道1",
            status="open",
            difficulty="中级",
            length=1000,
            elevation=1300,
        ),
    ]

    # 可可托海雪道
    koktokay_slopes = [
        Slope(
            resort_id="koktokay",
            name="专家雪道1",
            status="open",
            difficulty="专家",
            length=2000,
            elevation=2000,
            notes="高难度雪道",
        ),
    ]

    db.session.add_all(beidahu_slopes + songhuahu_slopes + koktokay_slopes)
    db.session.commit()

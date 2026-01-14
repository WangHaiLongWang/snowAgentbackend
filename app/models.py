# 模拟数据存储 - 与原始功能保持一致
class Item:
    """项目数据模型"""
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

class ItemRepository:
    """项目数据仓库，处理数据的CRUD操作"""
    def __init__(self):
        # 初始化模拟数据
        self.items = [
            Item(1, 'Item 1', 'First item'),
            Item(2, 'Item 2', 'Second item'),
            Item(3, 'Item 3', 'Third item')
        ]
        self.next_id = 4
    
    def get_all(self):
        """获取所有项目"""
        return [item.to_dict() for item in self.items]
    
    def get_by_id(self, item_id):
        """根据ID获取项目"""
        for item in self.items:
            if item.id == item_id:
                return item.to_dict()
        return None
    
    def create(self, name, description):
        """创建新项目"""
        new_item = Item(self.next_id, name, description)
        self.items.append(new_item)
        self.next_id += 1
        return new_item.to_dict()

# 创建全局仓库实例
item_repo = ItemRepository()
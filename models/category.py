import uuid
from datetime import datetime

class Category:
    def __init__(self, name: str, category_type: str, user_id: str):
        """
        Khởi tạo một danh mục thu/chi
        
        Parameters:
            name (str): Tên danh mục (ví dụ: Lương, Ăn uống, Giải trí)
            category_type (str): Loại danh mục - chỉ nhận "income" hoặc "expense"
            user_id (str): ID của người dùng sở hữu danh mục này
        """
        self.category_id = str(uuid.uuid4())
        self.user_id = user_id
        self.name = name.strip()                    # Loại bỏ khoảng trắng thừa
        self.category_type = category_type.lower()  # Chuẩn hóa thành chữ thường
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Kiểm tra loại danh mục hợp lệ
        if self.category_type not in ["income", "expense"]:
            raise ValueError("category_type chỉ được là 'income' hoặc 'expense'")

    def is_income(self) -> bool:
        """Kiểm tra xem danh mục này có phải thu nhập không"""
        return self.category_type == "income"

    def is_expense(self) -> bool:
        """Kiểm tra xem danh mục này có phải chi tiêu không"""
        return self.category_type == "expense"

    def to_dict(self) -> dict:
        """Chuyển đối tượng Category thành dict để lưu vào JSON"""
        return {
            "category_id": self.category_id,
            "user_id": self.user_id,
            "name": self.name,
            "category_type": self.category_type,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Tạo đối tượng Category từ dict (khi đọc từ JSON)"""
        category = cls(
            name=data["name"],
            category_type=data["category_type"],
            user_id=data["user_id"]
        )
        # Gán lại các giá trị đã có sẵn trong JSON
        category.category_id = data.get("category_id", str(uuid.uuid4()))
        category.created_at = data.get("created_at")
        return category

    def __str__(self):
        return f"Category: {self.name} ({self.category_type})"
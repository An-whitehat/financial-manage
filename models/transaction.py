import uuid
from datetime import datetime

class Transaction:
    def __init__(self, 
                 user_id: str, 
                 date: str, 
                 amount: float, 
                 category_id: str, 
                 transaction_type: str, 
                 note: str = ""):
        """
        Khởi tạo một giao dịch thu/chi
        
        Parameters:
            user_id (str): ID của người dùng
            date (str): Ngày giao dịch theo định dạng YYYY-MM-DD
            amount (float): Số tiền (luôn > 0)
            category_id (str): ID của danh mục
            transaction_type (str): "income" hoặc "expense"
            note (str): Ghi chú (tùy chọn)
        """
        self.transaction_id = str(uuid.uuid4())
        self.user_id = user_id
        self.date = date.strip()
        self.amount = float(amount)                 # Đảm bảo là số thực
        self.category_id = category_id
        self.transaction_type = transaction_type.lower()
        self.note = note.strip()
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Validation
        if self.amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
        
        if self.transaction_type not in ["income", "expense"]:
            raise ValueError("transaction_type chỉ được là 'income' hoặc 'expense'")

    def is_income(self) -> bool:
        """Kiểm tra giao dịch này có phải thu nhập không"""
        return self.transaction_type == "income"

    def is_expense(self) -> bool:
        """Kiểm tra giao dịch này có phải chi tiêu không"""
        return self.transaction_type == "expense"

    def to_dict(self) -> dict:
        """Chuyển đối tượng Transaction thành dict để lưu JSON"""
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "date": self.date,
            "amount": self.amount,
            "category_id": self.category_id,
            "transaction_type": self.transaction_type,
            "note": self.note,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Tạo đối tượng Transaction từ dict (khi đọc từ JSON)"""
        transaction = cls(
            user_id=data["user_id"],
            date=data["date"],
            amount=data["amount"],
            category_id=data["category_id"],
            transaction_type=data["transaction_type"],
            note=data.get("note", "")
        )
        transaction.transaction_id = data.get("transaction_id", str(uuid.uuid4()))
        transaction.created_at = data.get("created_at")
        return transaction

    def __str__(self):
        loai = "Thu" if self.is_income() else "Chi"
        return f"[{self.date}] {loai}: {self.amount:,.0f}đ - {self.note}"
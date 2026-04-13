import uuid
from datetime import datetime

class Budget:
    def __init__(self, 
                 user_id: str, 
                 category_id: str, 
                 amount_limit: float, 
                 period: str, 
                 start_date: str = None):
        """
        Khởi tạo một Ngân sách cho danh mục
        
        Parameters:
            user_id (str): ID của người dùng
            category_id (str): ID của danh mục cần đặt ngân sách (ví dụ: Ăn uống)
            amount_limit (float): Giới hạn chi tiêu
            period (str): Kỳ hạn ngân sách (ví dụ: "2023-10" cho tháng 10/2023)
            start_date (str): Ngày bắt đầu tính ngân sách (YYYY-MM-DD)
        """
        self.budget_id = str(uuid.uuid4())
        self.user_id = user_id
        self.category_id = category_id
        self.amount_limit = float(amount_limit)
        self.period = period
        self.start_date = start_date if start_date else datetime.now().strftime("%Y-%m-%d")
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.amount_limit <= 0:
            raise ValueError("Giới hạn ngân sách phải lớn hơn 0")

    def get_actual_spent(self, transactions: list) -> float:
        """
        Tính tổng số tiền thực tế đã chi cho danh mục này trong kỳ hạn
        (Dựa vào list class Transaction truyền vào)
        """
        total_spent = 0.0
        for t in transactions:
            # Kiểm tra xem giao dịch có thuộc user, category này, là expense và khớp kỳ hạn không
            # Giả sử t.date có định dạng YYYY-MM-DD, ta kiểm tra xem t.date có chứa chuỗi period (YYYY-MM) không
            if (t.user_id == self.user_id and 
                t.category_id == self.category_id and 
                t.is_expense() and 
                self.period in t.date):
                total_spent += t.amount
        return total_spent

    def get_progress_percentage(self, transactions: list) -> float:
        """Tính phần trăm ngân sách đã sử dụng"""
        spent = self.get_actual_spent(transactions)
        percentage = (spent / self.amount_limit) * 100
        return round(percentage, 2)

    def is_exceeded(self, transactions: list) -> bool:
        """Kiểm tra xem đã chi vượt ngân sách chưa (warning)"""
        return self.get_actual_spent(transactions) > self.amount_limit

    def to_dict(self) -> dict:
        """Chuyển đối tượng Budget thành dict để lưu JSON"""
        return {
            "budget_id": self.budget_id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "amount_limit": self.amount_limit,
            "period": self.period,
            "start_date": self.start_date,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Tạo đối tượng Budget từ dict (khi đọc từ JSON)"""
        budget = cls(
            user_id=data["user_id"],
            category_id=data["category_id"],
            amount_limit=data["amount_limit"],
            period=data["period"],
            start_date=data.get("start_date")
        )
        budget.budget_id = data.get("budget_id", str(uuid.uuid4()))
        budget.created_at = data.get("created_at")
        return budget

    def __str__(self):
        return f"Budget [{self.period}]: Limit {self.amount_limit:,.0f}đ"


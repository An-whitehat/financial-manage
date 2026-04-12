import uuid
from datetime import datetime

class SavingsGoal:
    def __init__(self, 
                 user_id: str, 
                 name: str, 
                 target_amount: float, 
                 deadline: str, 
                 current_amount: float = 0.0):
        """
        Khởi tạo một Mục tiêu tiết kiệm dài hạn
        
        Parameters:
            user_id (str): ID của người dùng
            name (str): Tên mục tiêu (VD: "Mua xe máy", "Đi du lịch")
            target_amount (float): Số tiền cần đạt
            deadline (str): Hạn chót định dạng YYYY-MM-DD
            current_amount (float): Số tiền hiện tại đã tích lũy được
        """
        self.goal_id = str(uuid.uuid4())
        self.user_id = user_id
        self.name = name.strip()
        self.target_amount = float(target_amount)
        self.current_amount = float(current_amount)
        self.deadline = deadline.strip()
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.target_amount <= 0:
            raise ValueError("Số tiền mục tiêu phải lớn hơn 0")

    def add_fund(self, amount: float):
        """
        Thêm tiền vào mục tiêu (Cập nhật current_amount khi có thu nhập được chọn thêm vào đây)
        """
        if amount <= 0:
            raise ValueError("Số tiền thêm vào phải lớn hơn 0")
        self.current_amount += amount

    def get_completion_percentage(self) -> float:
        """Tính phần trăm hoàn thành để hiển thị progress bar"""
        percentage = (self.current_amount / self.target_amount) * 100
        # Đảm bảo không vượt quá 100% về mặt hiển thị nếu tích lũy dư
        return round(min(percentage, 100.0), 2)

    def get_days_remaining(self) -> int:
        """Tính số ngày còn lại đến hạn deadline"""
        try:
            deadline_date = datetime.strptime(self.deadline, "%Y-%m-%d")
            today = datetime.now()
            delta = deadline_date - today
            return max(0, delta.days) # Trả về 0 nếu đã quá hạn
        except ValueError:
            return 0 # Trả về 0 nếu định dạng ngày sai

    def is_falling_behind(self) -> bool:
        """
        Cảnh báo nếu tiến độ chậm. 
        Ví dụ đơn giản: Đã qua 50% thời gian (giả sử tạo cách đây 1 khoảng) mà chưa đạt 50% tiền.
        Hàm này mình cung cấp logic cơ bản cảnh báo theo deadline để bạn tùy biến thêm.
        """
        days_left = self.get_days_remaining()
        progress = self.get_completion_percentage()
        
        # Ví dụ: Còn ít hơn 30 ngày mà chưa đạt 80% thì cảnh báo
        if days_left <= 30 and progress < 80.0:
            return True
        return False

    def to_dict(self) -> dict:
        """Chuyển đối tượng SavingsGoal thành dict để lưu JSON"""
        return {
            "goal_id": self.goal_id,
            "user_id": self.user_id,
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "deadline": self.deadline,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Tạo đối tượng SavingsGoal từ dict (khi đọc từ JSON)"""
        goal = cls(
            user_id=data["user_id"],
            name=data["name"],
            target_amount=data["target_amount"],
            deadline=data["deadline"],
            current_amount=data.get("current_amount", 0.0)
        )
        goal.goal_id = data.get("goal_id", str(uuid.uuid4()))
        goal.created_at = data.get("created_at")
        return goal

    def __str__(self):
        return f"Goal '{self.name}': {self.current_amount:,.0f}đ / {self.target_amount:,.0f}đ ({self.get_completion_percentage()}%)"

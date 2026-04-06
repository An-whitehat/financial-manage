import hashlib
from datetime import datetime
import uuid

class User:
    def __init__(self, username: str, password: str, role: str = "user"):
        # Tạo một ID duy nhất cho từng người dùng (dùng uuid để tránh trùng lặp)
        # uuid4() tạo ra một chuỗi ngẫu nhiên rất khó trùng, sau này dùng để liên kết 
        # với Transaction, Budget, SavingsGoal...
        self.user_id = str(uuid.uuid4())
        
        self.username = username
        
        # Mã hóa mật khẩu trước khi lưu (không lưu mật khẩu dạng văn bản thô)
        self.password_hash = self._hash_password(password)
        
        self.role = role                                    # "user" hoặc "admin"
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_login = None

    def _hash_password(self, password: str) -> str:
        """Hash password đơn giản bằng SHA256"""
        # hashlib.sha256(): hàm mã hóa một chiều (không thể giải ngược)
        # .encode('utf-8'): chuyển chuỗi thành bytes để hàm sha256 xử lý
        # .hexdigest(): chuyển kết quả mã hóa thành chuỗi hex (dễ lưu)
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password: str) -> bool:
        """Kiểm tra mật khẩu khi đăng nhập"""
        return self.password_hash == self._hash_password(password)

    def to_dict(self) -> dict:
        """Chuyển đối tượng User thành dictionary để lưu vào JSON"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "password_hash": self.password_hash,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Tạo đối tượng User từ dictionary (khi đọc từ file JSON)"""
        # Tạo user với password rỗng tạm thời vì chúng ta đã có password_hash
        user = cls(data["username"], "")
        user.user_id = data.get("user_id", str(uuid.uuid4()))
        user.password_hash = data["password_hash"]
        user.role = data.get("role", "user")
        user.created_at = data.get("created_at")
        user.last_login = data.get("last_login")
        return user

    def __str__(self):
        return f"User: {self.username} [{self.role}]"
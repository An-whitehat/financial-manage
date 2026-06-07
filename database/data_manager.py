import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Thêm đường dẫn root của dự án vào sys.path để tránh lỗi import khi chạy trực tiếp file trong thư mục con
CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parents[1]  # Nhảy ra 2 cấp: data_manager.py -> database -> financial-manage

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models.budget import Budget
from models.user import User
from models.category import Category
from models.transaction import Transaction

class DataManager:
    """
    Lớp quản lý dữ liệu chính (AppManager / FinanceManager)
    Chịu trách nhiệm load/save JSON và quản lý logic giữa các model
    """

    def __init__(self):
        self.data_dir = "database"
        self.users = {}                 # {user_id: User}
        self.categories = {}            # {category_id: Category}
        self.transactions = []          # list of Transaction
        self.budgets = {}               # {budget_id: Budget}
        self.current_user = None        # User đang đăng nhập

        os.makedirs(self.data_dir, exist_ok=True)
        self.load_all_data()

    # ====================== LOAD & SAVE ======================
    def load_all_data(self):
        """Load tất cả dữ liệu từ các file JSON"""
        try:
            # Load users
            user_path = os.path.join(self.data_dir, "user.json")
            if os.path.exists(user_path):
                with open(user_path, "r", encoding="utf-8") as f:
                    for u in json.load(f):
                        user = User.from_dict(u)
                        self.users[user.user_id] = user

            # Load categories
            cat_path = os.path.join(self.data_dir, "category.json")
            if os.path.exists(cat_path):
                with open(cat_path, "r", encoding="utf-8") as f:
                    for c in json.load(f):
                        cat = Category.from_dict(c)
                        self.categories[cat.category_id] = cat

            # Load transactions
            trans_path = os.path.join(self.data_dir, "transaction.json")
            if os.path.exists(trans_path):
                with open(trans_path, "r", encoding="utf-8") as f:
                    for t in json.load(f):
                        trans = Transaction.from_dict(t)
                        self.transactions.append(trans)

            # Load budgets ← đã thêm
            budget_path = os.path.join(self.data_dir, "budgets.json")
            if os.path.exists(budget_path):
                with open(budget_path, "r", encoding="utf-8") as f:
                    for b in json.load(f):
                        budget = Budget.from_dict(b)
                        self.budgets[budget.budget_id] = budget

            print("[DataManager] Da load du lieu thanh cong!")

        except Exception as e:
            print(f"[DataManager] Loi khi load du lieu: {e}")

    def save_all_data(self):
        """Save tất cả dữ liệu ra JSON"""
        try:
            # Save users
            user_path = os.path.join(self.data_dir, "user.json")
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump([u.to_dict() for u in self.users.values()],
                          f, ensure_ascii=False, indent=4)

            # Save categories
            cat_path = os.path.join(self.data_dir, "category.json")
            with open(cat_path, "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in self.categories.values()],
                          f, ensure_ascii=False, indent=4)

            # Save transactions
            trans_path = os.path.join(self.data_dir, "transaction.json")
            with open(trans_path, "w", encoding="utf-8") as f:
                json.dump([t.to_dict() for t in self.transactions],
                          f, ensure_ascii=False, indent=4)

            # Save budgets ← đã thêm
            budget_path = os.path.join(self.data_dir, "budgets.json")
            with open(budget_path, "w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.budgets.values()],
                          f, ensure_ascii=False, indent=4)

            print("[DataManager] Da luu du lieu thanh cong!")

        except Exception as e:
            print(f"[DataManager] Loi khi luu du lieu: {e}")

    # ====================== USER ======================
    def register_user(self, username: str, password: str, role: str = "user"):
        for user in self.users.values():
            if user.username == username:
                raise ValueError("Tên đăng nhập đã tồn tại!")
        new_user = User(username, password, role)
        self.users[new_user.user_id] = new_user
        self.save_all_data()
        return new_user

    def login(self, username: str, password: str):
        for user in self.users.values():
            if user.username == username and user.check_password(password):
                self.current_user = user
                user.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_all_data()
                return user
        raise ValueError("Sai tên đăng nhập hoặc mật khẩu!")

    def logout(self):
        self.current_user = None

    # ====================== TRANSACTION ======================
    def add_transaction(self, date: str, amount: float, category_id: str,
                        transaction_type: str, note: str = ""):
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        new_trans = Transaction(
            user_id=self.current_user.user_id,
            date=date,
            amount=amount,
            category_id=category_id,
            transaction_type=transaction_type,
            note=note
        )
        self.transactions.append(new_trans)
        self.save_all_data()
        return new_trans

    def update_transaction(self, transaction_id: str, **kwargs):
        """Cập nhật giao dịch theo transaction_id"""
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        for trans in self.transactions:
            if trans.transaction_id != transaction_id:
                continue
            if not self.is_admin() and trans.user_id != self.current_user.user_id:
                raise PermissionError("Không có quyền sửa giao dịch này!")
            if "date" in kwargs:
                trans.date = kwargs["date"].strip()
            if "amount" in kwargs:
                if float(kwargs["amount"]) <= 0:
                    raise ValueError("Số tiền phải lớn hơn 0!")
                trans.amount = float(kwargs["amount"])
            if "category_id" in kwargs:
                trans.category_id = kwargs["category_id"]
            if "transaction_type" in kwargs:
                t = kwargs["transaction_type"].lower()
                if t not in ["income", "expense"]:
                    raise ValueError("transaction_type chỉ được là 'income' hoặc 'expense'")
                trans.transaction_type = t
            if "note" in kwargs:
                trans.note = kwargs["note"].strip()
            self.save_all_data()
            return trans
        raise ValueError(f"Không tìm thấy giao dịch ID: {transaction_id}")

    def delete_transaction(self, transaction_id: str):
        """Xóa giao dịch theo transaction_id"""
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        for trans in self.transactions:
            if trans.transaction_id != transaction_id:
                continue
            if not self.is_admin() and trans.user_id != self.current_user.user_id:
                raise PermissionError("Không có quyền xóa giao dịch này!")
            self.transactions.remove(trans)
            self.save_all_data()
            return True
        raise ValueError(f"Không tìm thấy giao dịch ID: {transaction_id}")

    def get_transactions(self, start_date=None, end_date=None,
                         category_id=None, transaction_type=None,
                         min_amount=None, max_amount=None,
                         keyword=None) -> list:
        """Lấy danh sách giao dịch có filter, mới nhất trước"""
        if not self.current_user:
            return []
        results = list(self.transactions) if self.is_admin() else \
                  [t for t in self.transactions if t.user_id == self.current_user.user_id]
        if start_date:
            results = [t for t in results if t.date >= start_date]
        if end_date:
            results = [t for t in results if t.date <= end_date]
        if category_id:
            results = [t for t in results if t.category_id == category_id]
        if transaction_type:
            results = [t for t in results if t.transaction_type == transaction_type.lower()]
        if min_amount is not None:
            results = [t for t in results if t.amount >= min_amount]
        if max_amount is not None:
            results = [t for t in results if t.amount <= max_amount]
        if keyword:
            results = [t for t in results if keyword.lower() in t.note.lower()]
        return sorted(results, key=lambda t: (t.date, t.created_at), reverse=True)

    def get_user_transactions(self) -> list:
        """Lấy tất cả giao dịch của user hiện tại"""
        if not self.current_user:
            return []
        return [t for t in self.transactions if t.user_id == self.current_user.user_id]

    # ====================== CATEGORY ======================
    def add_category(self, name: str, category_type: str):
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        for cat in self.categories.values():
            if (cat.user_id == self.current_user.user_id and
                    cat.name.lower() == name.strip().lower()):
                raise ValueError(f"Danh mục '{name}' đã tồn tại!")
        new_cat = Category(name, category_type, self.current_user.user_id)
        self.categories[new_cat.category_id] = new_cat
        self.save_all_data()
        return new_cat

    def update_category(self, category_id: str, name: str):
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        cat = self.categories.get(category_id)
        if not cat:
            raise ValueError("Không tìm thấy danh mục!")
        if not self.is_admin() and cat.user_id != self.current_user.user_id:
            raise PermissionError("Không có quyền sửa danh mục này!")
        for c in self.categories.values():
            if (c.category_id != category_id and
                    c.user_id == self.current_user.user_id and
                    c.name.lower() == name.strip().lower()):
                raise ValueError(f"Danh mục '{name}' đã tồn tại!")
        cat.name = name.strip()
        self.save_all_data()
        return cat

    def delete_category(self, category_id: str):
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        cat = self.categories.get(category_id)
        if not cat:
            raise ValueError("Không tìm thấy danh mục!")
        if not self.is_admin() and cat.user_id != self.current_user.user_id:
            raise PermissionError("Không có quyền xóa danh mục này!")
        in_use = [t for t in self.transactions if t.category_id == category_id]
        if in_use:
            raise ValueError(f"Không thể xóa! Danh mục đang có {len(in_use)} giao dịch.")
        del self.categories[category_id]
        self.save_all_data()
        return True

    def get_user_categories(self, category_type: str = None) -> list:
        if not self.current_user:
            return []
        results = [c for c in self.categories.values()
                   if c.user_id == self.current_user.user_id]
        if category_type:
            results = [c for c in results if c.category_type == category_type.lower()]
        return sorted(results, key=lambda c: c.name)

    # ====================== BUDGET ======================
    def add_budget(self, category_id: str, amount_limit: float,
                   period: str, start_date: str = None):
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        for b in self.budgets.values():
            if (b.user_id == self.current_user.user_id and
                    b.category_id == category_id and
                    b.period == period):
                raise ValueError(f"Đã có ngân sách cho danh mục này trong kỳ {period}!")
        new_budget = Budget(self.current_user.user_id, category_id,
                            amount_limit, period, start_date)
        self.budgets[new_budget.budget_id] = new_budget
        self.save_all_data()
        return new_budget

    def update_budget(self, budget_id: str, amount_limit: float):
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        budget = self.budgets.get(budget_id)
        if not budget:
            raise ValueError("Không tìm thấy ngân sách!")
        if not self.is_admin() and budget.user_id != self.current_user.user_id:
            raise PermissionError("Không có quyền sửa ngân sách này!")
        if amount_limit <= 0:
            raise ValueError("Giới hạn ngân sách phải lớn hơn 0!")
        budget.amount_limit = float(amount_limit)
        self.save_all_data()
        return budget

    def delete_budget(self, budget_id: str):
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")
        budget = self.budgets.get(budget_id)
        if not budget:
            raise ValueError("Không tìm thấy ngân sách!")
        if not self.is_admin() and budget.user_id != self.current_user.user_id:
            raise PermissionError("Không có quyền xóa ngân sách này!")
        del self.budgets[budget_id]
        self.save_all_data()
        return True

    def get_user_budgets(self, period: str = None) -> list:
        if not self.current_user:
            return []
        results = [b for b in self.budgets.values()
                   if b.user_id == self.current_user.user_id]
        if period:
            results = [b for b in results if b.period == period]
        return results

    def check_budget_status(self, period: str = None) -> list:
        """Trả về list dict: budget + % đã dùng + có vượt không"""
        if not period:
            period = datetime.now().strftime("%Y-%m")
        budgets = self.get_user_budgets(period)
        transactions = self.get_user_transactions()
        return [{
            "budget": b,
            "spent": b.get_actual_spent(transactions),
            "percentage": b.get_progress_percentage(transactions),
            "exceeded": b.is_exceeded(transactions)
        } for b in budgets]
    def create_sample_data(self):
        if not self.current_user:
            return

        if len(self.get_user_transactions()) > 0:
            return
            
        # Sửa lại thụt lề (tab/4 spaces) cho các dòng dưới đây:
        food = self.add_category("Ăn uống", "expense")
        transport = self.add_category("Di chuyển", "expense")
        entertainment = self.add_category("Giải trí", "expense")
        salary = self.add_category("Lương", "income")

        self.add_transaction(
            "2025-06-01",
            15000000,
            salary.category_id,
            "income",
            "Lương tháng"
        )

        self.add_transaction(
            "2025-06-02",
            120000,
            food.category_id,
            "expense",
            "Ăn trưa"
        )

        self.add_transaction(
            "2025-06-03",
            80000,
            transport.category_id,
            "expense",
            "Đổ xăng"
        )

        self.add_transaction(
            "2025-06-05",
            300000,
            entertainment.category_id,
            "expense",
            "Xem phim"
        )
   

    # ====================== UTILITY ======================
    def get_current_user(self):
        return self.current_user

    def is_admin(self) -> bool:
        return self.current_user and self.current_user.role == "admin"

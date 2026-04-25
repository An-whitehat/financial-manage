import json
import os
from datetime import datetime
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
        self.users = {}                    # {user_id: User}
        self.categories = {}               # {category_id: Category}
        self.transactions = []             # list of Transaction
        self.current_user = None           # User đang đăng nhập

        # Tạo thư mục database nếu chưa có
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
                    users_data = json.load(f)
                    for u in users_data:
                        user = User.from_dict(u)
                        self.users[user.user_id] = user

            # Load categories
            cat_path = os.path.join(self.data_dir, "category.json")   # hoặc categories.json
            if os.path.exists(cat_path):
                with open(cat_path, "r", encoding="utf-8") as f:
                    cats_data = json.load(f)
                    for c in cats_data:
                        cat = Category.from_dict(c)
                        self.categories[cat.category_id] = cat

            # Load transactions
            trans_path = os.path.join(self.data_dir, "transaction.json")
            if os.path.exists(trans_path):
                with open(trans_path, "r", encoding="utf-8") as f:
                    trans_data = json.load(f)
                    for t in trans_data:
                        trans = Transaction.from_dict(t)
                        self.transactions.append(trans)

            print("✅ Đã load dữ liệu thành công!")

        except Exception as e:
            print(f"⚠️ Lỗi khi load dữ liệu: {e}")

    def save_all_data(self):
        """Save tất cả dữ liệu ra JSON"""
        try:
            # Save users
            user_path = os.path.join(self.data_dir, "user.json")
            users_list = [user.to_dict() for user in self.users.values()]
            with open(user_path, "w", encoding="utf-8") as f:
                json.dump(users_list, f, ensure_ascii=False, indent=4)

            # Save categories
            cat_path = os.path.join(self.data_dir, "category.json")
            cats_list = [cat.to_dict() for cat in self.categories.values()]
            with open(cat_path, "w", encoding="utf-8") as f:
                json.dump(cats_list, f, ensure_ascii=False, indent=4)

            # Save transactions
            trans_path = os.path.join(self.data_dir, "transaction.json")
            trans_list = [trans.to_dict() for trans in self.transactions]
            with open(trans_path, "w", encoding="utf-8") as f:
                json.dump(trans_list, f, ensure_ascii=False, indent=4)

            print("✅ Đã lưu dữ liệu thành công!")

        except Exception as e:
            print(f"❌ Lỗi khi lưu dữ liệu: {e}")

    # ====================== USER ======================
    def register_user(self, username: str, password: str, role: str = "user"):
        # Kiểm tra username đã tồn tại chưa...
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

    # ====================== TRANSACTION ======================
     # ====================== CATEGORY ======================

    def add_category(self, name: str, category_type: str):
        if not self.current_user:
            raise ValueError("Chưa đăng nhập!")

        name = name.strip()

        # check trùng tên trong cùng user
        for cat in self.categories.values():
            if (
                cat.name.lower() == name.lower()
                and cat.user_id == self.current_user.user_id
            ):
                raise ValueError("Danh mục đã tồn tại!")

        new_cat = Category(name, category_type, self.current_user.user_id)
        self.categories[new_cat.category_id] = new_cat

        self.save_all_data()
        return new_cat


    def update_category(self, category_id: str, name: str):
        if category_id not in self.categories:
            raise ValueError("Không tìm thấy danh mục!")

        name = name.strip()

        # check trùng tên (trừ chính nó)
        for cat in self.categories.values():
            if (
                cat.name.lower() == name.lower()
                and cat.user_id == self.current_user.user_id
                and cat.category_id != category_id
            ):
                raise ValueError("Tên danh mục đã tồn tại!")

        self.categories[category_id].name = name
        self.save_all_data()


    def delete_category(self, category_id: str):
        if category_id not in self.categories:
            raise ValueError("Không tồn tại!")

        # check có transaction dùng không
        for t in self.transactions:
            if t.category_id == category_id:
                raise ValueError("Danh mục đang được sử dụng, không thể xóa!")

        del self.categories[category_id]
        self.save_all_data()


    def get_user_categories(self, category_type=None):
        if not self.current_user:
            return []

        result = []
        for cat in self.categories.values():
            if cat.user_id == self.current_user.user_id:
                if category_type and cat.category_type != category_type:
                    continue
                result.append(cat)

        return result
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

    def get_user_transactions(self):
        """Lấy tất cả giao dịch của user hiện tại"""
        if not self.current_user:
            return []
        return [t for t in self.transactions if t.user_id == self.current_user.user_id]

    # ====================== UTILITY ======================
    def get_current_user(self):
        return self.current_user

    def is_admin(self) -> bool:
        return self.current_user and self.current_user.role == "admin"

import sys
import os
from pathlib import Path
import random
from datetime import datetime, timedelta

# Dam bao import duoc cac module tu thu muc goc
CURRENT_FILE = Path(__file__).resolve()
ROOT_DIR = CURRENT_FILE.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.data_manager import DataManager

def generate_data():
    dm = DataManager()
    
    # 1. Thong tin tai khoan kiem thu
    username = "testuser"
    password = "password123"
    
    # Tim kiem xem tai khoan da ton tai chua
    user = None
    for u in dm.users.values():
        if u.username == username:
            user = u
            break
            
    if not user:
        print(f"Tao nguoi dung moi: {username}...")
        user = dm.register_user(username, password, role="user")
    else:
        print(f"Su dung tai khoan kiem thu hien co: {username}")
    
    # Dang nhap vao he thong
    dm.login(username, password)
    
    # Xoa du lieu cu cua rieng testuser de chay lai script nhieu lan khong bi cong don
    print("Dang don dep du lieu cu cua testuser...")
    dm.transactions = [t for t in dm.transactions if t.user_id != user.user_id]
    dm.budgets = {bid: b for bid, b in dm.budgets.items() if b.user_id != user.user_id}
    
    # Xoa cac danh muc cu cua testuser
    cat_ids_to_del = [cid for cid, c in dm.categories.items() if c.user_id == user.user_id]
    for cid in cat_ids_to_del:
        del dm.categories[cid]
        
    dm.save_all_data()
    
    # 2. Tao cac Danh muc Thu/Chi da dang
    print("Dang tao bo danh muc Thu/Chi...")
    categories = {}
    
    # Khoan thu (Income)
    categories["Lương"] = dm.add_category("Lương cố định", "income")
    categories["Kinh doanh"] = dm.add_category("Kinh doanh online", "income")
    categories["Đầu tư"] = dm.add_category("Lãi đầu tư", "income")
    
    # Khoan chi (Expense)
    categories["Ăn uống"] = dm.add_category("Ăn uống & Cà phê", "expense")
    categories["Đi lại"] = dm.add_category("Xăng xe & Grab", "expense")
    categories["Nhà cửa"] = dm.add_category("Tiền thuê nhà", "expense")
    categories["Hóa đơn"] = dm.add_category("Điện, Nước & Internet", "expense")
    categories["Giải trí"] = dm.add_category("Giải trí & Xem phim", "expense")
    categories["Mua sắm"] = dm.add_category("Mua sắm cá nhân", "expense")
    categories["Sức khỏe"] = dm.add_category("Thuốc men & Sức khỏe", "expense")
    
    # 3. Sinh du lieu giao dich mo phong trong vong 6 thang qua (khoang 150 giao dich)
    print("Dang sinh hon 150 giao dich ngau nhien tu thang 01/2026 den nay...")
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 6, 7)
    delta_days = (end_date - start_date).days
    
    # Luong co dinh & Tien nha & Hoa don hang thang
    for month in range(1, 7):
        # Nhan luong vao ngay 5 hang thang
        salary_date = datetime(2026, month, 5).strftime("%Y-%m-%d")
        salary_amount = random.choice([20000000.0, 25000000.0, 22000000.0])
        dm.add_transaction(salary_date, salary_amount, categories["Lương"].category_id, "income", f"Lương công ty tháng {month:02d}")
        
        # Tien nha dong vao ngay 1 hang thang
        rent_date = datetime(2026, month, 1).strftime("%Y-%m-%d")
        dm.add_transaction(rent_date, 4500000.0, categories["Nhà cửa"].category_id, "expense", f"Tiền thuê nhà tháng {month:02d}")
        
        # Hoa don dich vu dong vao ngay 10 hang thang
        bill_date = datetime(2026, month, 10).strftime("%Y-%m-%d")
        bill_amount = float(random.randint(600000, 1300000))
        dm.add_transaction(bill_date, bill_amount, categories["Hóa đơn"].category_id, "expense", f"Điện nước mạng tháng {month:02d}")

    # Cac khoan thu nhap tu do/dau tu ngau nhien khac
    for i in range(15):
        rand_days = random.randint(0, delta_days)
        tx_date = (start_date + timedelta(days=rand_days)).strftime("%Y-%m-%d")
        tx_type = random.choice(["Kinh doanh", "Đầu tư"])
        tx_amount = float(random.choice([500000, 1000000, 1500000, 3000000, 5000000]))
        note = "Thu nhập kinh doanh thêm" if tx_type == "Kinh doanh" else "Lãi nhận từ quỹ đầu tư"
        dm.add_transaction(tx_date, tx_amount, categories[tx_type].category_id, "income", note)

    # Chi tiet hoa cac hoat dong chi tieu hang ngay
    expense_details = {
        "Ăn uống": [
            ("Ăn sáng phở/bún", 35000, 65000),
            ("Ăn trưa cơm văn phòng", 50000, 85000),
            ("Đi chợ mua thức ăn cả tuần", 200000, 500000),
            ("Cà phê Highland/Starbucks", 45000, 120000),
            ("Liên hoan tối cuối tuần", 300000, 900000)
        ],
        "Đi lại": [
            ("Đổ xăng xe máy", 50000, 80000),
            ("Đặt xe GrabBike đi làm", 40000, 90000),
            ("Thay dầu/sửa phanh xe máy", 150000, 350000)
        ],
        "Giải trí": [
            ("Vé xem phim CGV + bắp nước", 150000, 250000),
            ("Mua sắm game online", 120000, 450000),
            ("Đi uống bia với đồng nghiệp", 200000, 500000),
            ("Đi picnic dã ngoại cuối tuần", 400000, 1200000)
        ],
        "Mua sắm": [
            ("Mua áo thun mới", 150000, 350000),
            ("Mua giày chạy bộ", 600000, 1500000),
            ("Đồ dùng gia đình thiết yếu", 100000, 400000)
        ],
        "Sức khỏe": [
            ("Mua thuốc cảm/ho", 40000, 100000),
            ("Khám răng định kỳ tại nha khoa", 150000, 400000),
            ("Mua thẻ tập gym/yoga tháng", 350000, 600000)
        ]
    }
    
    # Sinh khoang 120 giao dich chi tieu sinh hoat ngau nhien phan bo deu
    for _ in range(120):
        rand_days = random.randint(0, delta_days)
        tx_date = (start_date + timedelta(days=rand_days)).strftime("%Y-%m-%d")
        
        # Chon ngau nhien nhom chi tieu
        cat_key = random.choice(list(expense_details.keys()))
        cat_id = categories[cat_key].category_id
        
        # Chon ngau nhien mo ta chi tiet va sinh so tien thuc te
        detail, min_val, max_val = random.choice(expense_details[cat_key])
        amount = float(random.randint(min_val, max_val))
        
        dm.add_transaction(tx_date, amount, cat_id, "expense", detail)
        
    # 4. Thiet lap han muc Ngan sach thang nay (2026-06)
    print("Dang thiet lap han muc Ngan sach thang nay...")
    current_period = datetime.now().strftime("%Y-%m")
    # An uong
    dm.add_budget(categories["Ăn uống"].category_id, 5000000.0, current_period)
    # Di lai
    dm.add_budget(categories["Đi lại"].category_id, 700000.0, current_period)
    # Giai tri
    dm.add_budget(categories["Giải trí"].category_id, 3000000.0, current_period)
    
    dm.save_all_data()
    print("\n[OK] HOAN THANH SINH DU LIEU KIEM THU THANH CONG!")
    print("-" * 50)
    print(f"Tai khoan kiem thu moi cua ban:")
    print(f"  * Ten dang nhap: {username}")
    print(f"  * Mat khau: {password}")
    print("-" * 50)
    print("Hay khoi chay lai phan mem va dang nhap bang tai khoan nay de trai nghiem!")

if __name__ == "__main__":
    generate_data()

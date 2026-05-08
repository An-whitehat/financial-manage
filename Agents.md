# AGENT CONTEXT - QLTCN Project

**Last updated:** 2026-04-19

**Dự án:** Quản lý Tài chính Cá nhân (Python + Tkinter + OOP)

### Cấu trúc hiện tại
- `models/`          : User, Category, Transaction, Budget, SavingsGoal, ReportGenerator
- `database/`        : data_manager.py (AppManager chính), *.json
- `gui/`             : chưa làm

- Tuần này: **Chỉ làm Backend + Logic**, chưa làm GUI.

### Các class đã có
- **User**: user_id, username, password_hash, role, to_dict/from_dict
- **Category**: category_id, user_id, name, category_type ("income"/"expense")
- **Transaction**: transaction_id, user_id, date, amount, category_id, transaction_type, note
- **DataManager** (database/data_manager.py): load/save JSON, current_user, register, login, add_transaction...

### Trạng thái hiện tại
- DataManager đã có phiên bản cơ bản
- Đang cần hoàn thiện:
  - CRUD đầy đủ cho Transaction
  - ReportGenerator (balance, tổng thu/chi, % category)
  - Test console
  - Load/Save JSON ổn định

### Phong cách code
- Code đơn giản, có chú thích tiếng Việt
- Mọi class có `to_dict()` / `from_dict()`
- Validation cơ bản
- Ưu tiên: DataManager → CRUD Transaction → ReportGenerator
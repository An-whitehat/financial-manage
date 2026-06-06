import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

class BudgetFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        self.category_map = {}
        
        # ==========================================
        # 1. GIAO DIỆN FORM THIẾT LẬP
        # ==========================================
        setup_frame = tk.LabelFrame(self, text="Thiết lập ngân sách tháng này", bg="white")
        setup_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(setup_frame, text="Danh mục (Chi):", bg="white").grid(row=0, column=0, padx=5, pady=10)
        self.category_combobox = ttk.Combobox(setup_frame, state="readonly", width=20)
        self.category_combobox.grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(setup_frame, text="Ngân sách (VNĐ):", bg="white").grid(row=0, column=2, padx=5, pady=10)
        self.budget_entry = ttk.Entry(setup_frame, width=20)
        self.budget_entry.grid(row=0, column=3, padx=5, pady=10)
        
        self.btn_save = ttk.Button(setup_frame, text="Lưu thiết lập", command=self.save_budget)
        self.btn_save.grid(row=0, column=4, padx=15, pady=10)
        
        # ==========================================
        # 2. KHUNG CHỨA CÁC THANH PROGRESS BAR
        # ==========================================
        self.progress_frame = tk.LabelFrame(self, text="Tình trạng chi tiêu so với ngân sách", bg="white")
        self.progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tự động nạp tiến độ ngân sách khi mở tab
        self.bind("<Visibility>", lambda e: self.refresh_data())

    # ==========================================
    # 3. CÁC HÀM XỬ LÝ (LOGIC)
    # ==========================================
    def refresh_data(self):
        dm = self.controller.data_manager
        
        # Nạp các danh mục chi vào Combobox
        expense_cats = dm.get_user_categories("expense")
        self.category_map = {c.name: c.category_id for c in expense_cats}
        self.category_combobox['values'] = list(self.category_map.keys())
        if self.category_map and self.category_combobox.get() == "":
            self.category_combobox.current(0)
            
        # Xóa các thanh Progress Bar cũ để vẽ lại cái mới
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
            
        period = datetime.now().strftime("%Y-%m")
        budgets_status = dm.check_budget_status(period)
        
        if not budgets_status:
            tk.Label(self.progress_frame, text="Chưa có ngân sách nào được thiết lập trong tháng này.", bg="white", font=("Helvetica", 10, "italic")).pack(pady=20)
            return
            
        cat_map_reverse = {c.category_id: c.name for c in expense_cats}
        
        # Bắt đầu duyệt qua từng ngân sách và tạo thanh Progress Bar
        for item in budgets_status:
            b = item["budget"]
            cat_name = cat_map_reverse.get(b.category_id, "Không rõ")
            limit_str = f"{b.amount_limit:,.0f}"
            spent_str = f"{item['spent']:,.0f}"
            percentage = item['percentage']
            exceeded = item['exceeded']
            
            # Khung con chứa 1 ngân sách
            item_frame = tk.Frame(self.progress_frame, bg="white")
            item_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Label hiển thị thông tin
            info_text = f"Danh mục: {cat_name}  |  Đã chi: {spent_str} / {limit_str} VNĐ ({percentage}%)"
            color = "red" if exceeded else "black"
            tk.Label(item_frame, text=info_text, bg="white", fg=color, font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
            
            # Khung chứa thanh bar và nút xóa
            bar_frame = tk.Frame(item_frame, bg="white")
            bar_frame.pack(fill=tk.X, pady=5)
            
            # Thanh Progress bar (Tối đa 100% để thanh không bị vỡ)
            bar_value = percentage if percentage <= 100 else 100
            pb = ttk.Progressbar(bar_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
            pb['value'] = bar_value
            pb.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Nút xóa nằm cạnh thanh Progress Bar
            btn_del = ttk.Button(bar_frame, text="Xóa", width=5, command=lambda bid=b.budget_id: self.delete_budget_by_id(bid))
            btn_del.pack(side=tk.RIGHT, padx=10)
            
            # Dòng cảnh báo bên dưới
            status_text = "⚠️ Cảnh báo: Quá hạn mức!" if exceeded else "✅ Trong mức an toàn"
            status_color = "red" if exceeded else "green"
            tk.Label(item_frame, text=status_text, bg="white", fg=status_color, font=("Helvetica", 9, "italic")).pack(anchor=tk.W, pady=2)
            
            # Kẻ một đường phân cách mờ mờ cho đẹp
            ttk.Separator(self.progress_frame, orient='horizontal').pack(fill='x', pady=5)

    def save_budget(self):
        cat_name = self.category_combobox.get()
        amount_str = self.budget_entry.get().replace(',', '')
        
        if not cat_name or not amount_str:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đủ thông tin!")
            return
            
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("Lỗi", "Số tiền không hợp lệ!")
            return
            
        cat_id = self.category_map.get(cat_name)
        if not cat_id:
            messagebox.showwarning("Lỗi", "Danh mục không hợp lệ!")
            return
            
        period = datetime.now().strftime("%Y-%m")
        dm = self.controller.data_manager
        
        # Nếu ngân sách đã tồn tại thì Cập nhật, chưa có thì Thêm mới
        existing = None
        for b in dm.get_user_budgets(period):
            if b.category_id == cat_id:
                existing = b
                break
                
        try:
            if existing:
                dm.update_budget(existing.budget_id, amount)
                messagebox.showinfo("Thành công", "Đã cập nhật mức ngân sách!")
            else:
                dm.add_budget(cat_id, amount, period)
                messagebox.showinfo("Thành công", "Đã thiết lập ngân sách mới!")
                
            self.budget_entry.delete(0, tk.END)
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            
    def delete_budget_by_id(self, budget_id):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa cảnh báo ngân sách này?"):
            try:
                self.controller.data_manager.delete_budget(budget_id)
                self.refresh_data()
                messagebox.showinfo("Thành công", "Đã xóa ngân sách!")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

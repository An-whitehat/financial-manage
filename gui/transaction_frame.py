import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

class TransactionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        self.category_map = {}
        self.selected_transaction_id = None
        
        # ==========================================
        # 1. GIAO DIỆN (UI)
        # ==========================================
        # --- Phần Bộ lọc Tìm Kiếm ---
        search_frame = tk.LabelFrame(self, text="Bộ lọc tìm kiếm", bg="white")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="Từ ngày:", bg="white").pack(side=tk.LEFT, padx=5, pady=10)
        self.search_start_date = ttk.Entry(search_frame, width=12)
        self.search_start_date.pack(side=tk.LEFT, padx=5)
        
        tk.Label(search_frame, text="Đến ngày:", bg="white").pack(side=tk.LEFT, padx=5)
        self.search_end_date = ttk.Entry(search_frame, width=12)
        self.search_end_date.pack(side=tk.LEFT, padx=5)

        tk.Label(search_frame, text="Ghi chú:", bg="white").pack(side=tk.LEFT, padx=(15, 5))
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.btn_search = ttk.Button(search_frame, text="Lọc / Tìm")
        self.btn_search.pack(side=tk.LEFT, padx=10)
        
        self.btn_clear_search = ttk.Button(search_frame, text="Bỏ lọc")
        self.btn_clear_search.pack(side=tk.LEFT, padx=5)

        # --- Phần Form Thêm/Sửa/Xóa ---
        form_frame = tk.LabelFrame(self, text="Thông tin giao dịch", bg="white")
        form_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(form_frame, text="Ngày (YYYY-MM-DD):", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Số tiền:", bg="white").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Danh mục:", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.category_combobox = ttk.Combobox(form_frame, state="readonly")
        self.category_combobox.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Ghi chú:", bg="white").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.note_entry = ttk.Entry(form_frame)
        self.note_entry.grid(row=1, column=3, padx=5, pady=5)

        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        self.btn_add = ttk.Button(btn_frame, text="Thêm")
        self.btn_add.pack(side=tk.LEFT, padx=5)
        self.btn_update = ttk.Button(btn_frame, text="Sửa")
        self.btn_update.pack(side=tk.LEFT, padx=5)
        self.btn_delete = ttk.Button(btn_frame, text="Xóa")
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        # --- Phần Treeview (Bảng hiển thị) ---
        tree_frame = tk.Frame(self, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("id", "date", "amount", "category", "note")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Ngày")
        self.tree.heading("amount", text="Số tiền")
        self.tree.heading("category", text="Danh mục")
        self.tree.heading("note", text="Ghi chú")
        
        self.tree.column("id", width=0, stretch=tk.NO)
        self.tree.column("date", width=100, anchor=tk.CENTER)
        self.tree.column("amount", width=120, anchor=tk.E)
        self.tree.column("category", width=150)
        self.tree.column("note", width=250)

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ==========================================
        # 2. KHỞI TẠO LOGIC VÀ KẾT NỐI SỰ KIỆN
        # ==========================================
        self.btn_add.config(command=self.add_transaction)
        self.btn_update.config(command=self.update_transaction)
        self.btn_delete.config(command=self.delete_transaction)
        self.btn_search.config(command=self.search_transactions)
        self.btn_clear_search.config(command=self.clear_search)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Cập nhật Danh mục mỗi khi mở tab Giao dịch
        self.bind("<Visibility>", lambda e: self.load_categories())
        
        self.load_categories()
        self.load_data_to_tree()

    # ==========================================
    # 3. CÁC HÀM XỬ LÝ (CONTROLLER LOGIC)
    # ==========================================
    def load_categories(self):
        dm = self.controller.data_manager
        categories = dm.get_user_categories()
        
        self.category_map = {c.name: c.category_id for c in categories}
        self.category_combobox['values'] = list(self.category_map.keys())
        
        if self.category_map and self.category_combobox.get() == "":
            self.category_combobox.current(0)
            
    def load_data_to_tree(self, transactions=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        dm = self.controller.data_manager
        if transactions is None:
            transactions = dm.get_user_transactions()
            
        cat_map_reverse = {c.category_id: c.name for c in dm.get_user_categories()}
            
        for t in transactions:
            cat_name = cat_map_reverse.get(t.category_id, "Không rõ")
            formatted_amount = f"{t.amount:,.0f}" 
            self.tree.insert("", tk.END, values=(t.transaction_id, t.date, formatted_amount, cat_name, t.note))

    def get_form_data(self):
        date = self.date_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        cat_name = self.category_combobox.get().strip()
        note = self.note_entry.get().strip()
        
        if not date or not amount_str or not cat_name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đủ ngày, số tiền và danh mục!")
            return None
            
        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showwarning("Lỗi nhập liệu", "Số tiền phải là một con số!")
            return None
            
        cat_id = self.category_map.get(cat_name)
        if not cat_id:
            messagebox.showwarning("Lỗi dữ liệu", "Danh mục không hợp lệ!")
            return None
            
        dm = self.controller.data_manager
        cat_obj = dm.categories.get(cat_id)
        trans_type = cat_obj.category_type if cat_obj else "expense"
            
        return {
            "date": date,
            "amount": amount,
            "category_id": cat_id,
            "transaction_type": trans_type,
            "note": note
        }
            
    def add_transaction(self):
        data = self.get_form_data()
        if data:
            dm = self.controller.data_manager
            try:
                dm.add_transaction(**data)
                messagebox.showinfo("Thành công", "Đã thêm giao dịch mới!")
                self.load_data_to_tree()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        values = item['values']
        
        self.clear_form(keep_date=False)
        self.selected_transaction_id = str(values[0])
        self.date_entry.insert(0, values[1])
        self.amount_entry.insert(0, str(values[2]).replace(',', ''))
        self.category_combobox.set(values[3])
        self.note_entry.insert(0, values[4] if len(values) > 4 else "")
        
    def update_transaction(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng click chọn một giao dịch dưới bảng để sửa!")
            return
            
        data = self.get_form_data()
        if data:
            dm = self.controller.data_manager
            try:
                dm.update_transaction(self.selected_transaction_id, **data)
                messagebox.showinfo("Thành công", "Đã cập nhật giao dịch!")
                self.load_data_to_tree()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
    def delete_transaction(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng click chọn một giao dịch dưới bảng để xóa!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa giao dịch này?"):
            dm = self.controller.data_manager
            try:
                dm.delete_transaction(self.selected_transaction_id)
                messagebox.showinfo("Thành công", "Đã xóa giao dịch!")
                self.load_data_to_tree()
                self.clear_form()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
    def search_transactions(self):
        """Xử lý nút Lọc / Tìm (Hỗ trợ lọc theo Keyword và Khoảng thời gian)"""
        keyword = self.search_entry.get().strip()
        start_date = self.search_start_date.get().strip()
        end_date = self.search_end_date.get().strip()
        
        # Đóng gói các điều kiện lọc (chỉ thêm vào nếu người dùng có nhập)
        filters = {}
        if keyword:
            filters["keyword"] = keyword
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
            
        dm = self.controller.data_manager
        # Gọi hàm lấy giao dịch với các điều kiện đã đóng gói
        results = dm.get_transactions(**filters)
        self.load_data_to_tree(results)
        
    def clear_search(self):
        """Xử lý nút Bỏ lọc (Xóa hết chữ trong ô tìm kiếm và hiển thị toàn bộ)"""
        self.search_entry.delete(0, tk.END)
        self.search_start_date.delete(0, tk.END)
        self.search_end_date.delete(0, tk.END)
        
        # Load lại không có bộ lọc
        self.load_data_to_tree()
            
    def clear_form(self, keep_date=True):
        self.date_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.selected_transaction_id = None
        
        if keep_date:
            self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

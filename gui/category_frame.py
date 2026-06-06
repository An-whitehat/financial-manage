import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class CategoryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller
        
        self.selected_category_id = None
        
        # ==========================================
        # 1. GIAO DIỆN (UI)
        # ==========================================
        form_frame = tk.LabelFrame(self, text="Quản lý Danh mục", bg="white")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(form_frame, text="Tên danh mục:", bg="white").grid(row=0, column=0, padx=5, pady=10)
        self.cat_name_entry = ttk.Entry(form_frame, width=30)
        self.cat_name_entry.grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(form_frame, text="Loại:", bg="white").grid(row=0, column=2, padx=5, pady=10)
        self.cat_type_combobox = ttk.Combobox(form_frame, values=["Thu", "Chi"], state="readonly", width=15)
        self.cat_type_combobox.grid(row=0, column=3, padx=5, pady=10)
        self.cat_type_combobox.current(1) # Mặc định chọn "Chi"
        
        btn_frame = tk.Frame(form_frame, bg="white")
        btn_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        self.btn_add = ttk.Button(btn_frame, text="Thêm mới")
        self.btn_add.pack(side=tk.LEFT, padx=5)
        self.btn_update = ttk.Button(btn_frame, text="Cập nhật")
        self.btn_update.pack(side=tk.LEFT, padx=5)
        self.btn_delete = ttk.Button(btn_frame, text="Xóa")
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(self, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("id", "name", "type")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Tên danh mục")
        self.tree.heading("type", text="Phân loại (Thu/Chi)")
        
        self.tree.column("id", width=0, stretch=tk.NO) # Ẩn cột ID
        self.tree.column("name", width=300)
        self.tree.column("type", width=150, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ==========================================
        # 2. KHỞI TẠO LOGIC VÀ KẾT NỐI SỰ KIỆN
        # ==========================================
        self.btn_add.config(command=self.add_category)
        self.btn_update.config(command=self.update_category)
        self.btn_delete.config(command=self.delete_category)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Tự động refresh dữ liệu mỗi khi click vào tab Danh mục
        self.bind("<Visibility>", lambda e: self.load_data_to_tree())
        self.load_data_to_tree()

    # ==========================================
    # 3. CÁC HÀM XỬ LÝ (CONTROLLER LOGIC)
    # ==========================================
    def load_data_to_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        dm = self.controller.data_manager
        categories = dm.get_user_categories()
            
        for c in categories:
            # Quy đổi "income" -> "Thu", "expense" -> "Chi" để hiển thị
            type_display = "Thu" if c.category_type == "income" else "Chi"
            self.tree.insert("", tk.END, values=(c.category_id, c.name, type_display))
            
    def clear_form(self):
        self.cat_name_entry.delete(0, tk.END)
        self.selected_category_id = None
        self.cat_type_combobox.state(['!disabled']) # Mở khóa combobox để chọn Thu/Chi khi thêm mới
        self.cat_type_combobox.current(1)
        
    def add_category(self):
        name = self.cat_name_entry.get().strip()
        type_str = self.cat_type_combobox.get()
        
        if not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên danh mục!")
            return
            
        # Chuyển đổi "Thu"/"Chi" thành "income"/"expense" để lưu vào database
        cat_type = "income" if type_str == "Thu" else "expense"
        dm = self.controller.data_manager
        
        try:
            dm.add_category(name, cat_type)
            messagebox.showinfo("Thành công", f"Đã thêm danh mục: {name}")
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
        
        self.clear_form()
        self.selected_category_id = str(values[0])
        self.cat_name_entry.insert(0, values[1])
        self.cat_type_combobox.set(values[2])
        
        # Khóa nút chọn Thu/Chi lại khi nhấn Sửa (Vì đổi Thu/Chi sẽ làm loạn các giao dịch cũ)
        self.cat_type_combobox.state(['disabled'])

    def update_category(self):
        if not self.selected_category_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một danh mục dưới bảng để sửa!")
            return
            
        name = self.cat_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Thiếu thông tin", "Tên danh mục không được để trống!")
            return
            
        dm = self.controller.data_manager
        try:
            dm.update_category(self.selected_category_id, name)
            messagebox.showinfo("Thành công", "Đã cập nhật tên danh mục!")
            self.load_data_to_tree()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            
    def delete_category(self):
        if not self.selected_category_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một danh mục dưới bảng để xóa!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa danh mục này?"):
            dm = self.controller.data_manager
            try:
                dm.delete_category(self.selected_category_id)
                messagebox.showinfo("Thành công", "Đã xóa danh mục!")
                self.load_data_to_tree()
                self.clear_form()
            except Exception as e:
                # Hệ thống sẽ báo lỗi nếu bạn cố xóa danh mục đang có giao dịch sử dụng
                messagebox.showerror("Lỗi", str(e))

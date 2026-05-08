import tkinter as tk
from tkinter import ttk
import sys
import os

# Giữ nguyên logic đường dẫn hệ thống
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.data_manager import DataManager
from gui.login_frame import LoginFrame

# Khi có file của An, chỉ cần bỏ dấu #
# from gui.dashboard import DashboardFrame
# from gui.transaction_frame import TransactionFrame
# from gui.budget_frame import BudgetFrame
# from gui.report_frame import ReportFrame

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quản lý tài chính cá nhân")
        self.geometry("1100x750")
        self.configure(bg="#F0F7F4") # Nền trắng xanh nhạt dịu mắt
        
        self.data_manager = DataManager()
        
        # --- CẤU HÌNH STYLE ---
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure("TNotebook", background="#F0F7F4", borderwidth=0)
        style.configure("TNotebook.Tab", 
                        background="#D1E8E2", 
                        foreground="#1E3932", 
                        padding=[25, 10], 
                        font=("Helvetica", 10, "bold"))
        
        # Màu 
        style.map("TNotebook.Tab", 
                  background=[("selected", "#2ECC71")], 
                  foreground=[("selected", "white")])

        self.container = tk.Frame(self, bg="#F0F7F4")
        self.container.pack(fill="both", expand=True)
        
        self.show_login()

    def show_login(self):
        self.clear_container()
        LoginFrame(self.container, self).pack(fill="both", expand=True)

    def login_success(self):
        self.show_dashboard()

    def show_dashboard(self):
        self.clear_container()
        
        user = self.data_manager.get_current_user()
        # Header màu Xanh
        header = tk.Frame(self.container, bg="#1E8449", height=80)
        header.pack(side="top", fill="x")
        
        tk.Label(header, text=f"Chào bạn, {user.username}! 👋", font=("Helvetica", 16, "bold"), 
                 bg="#1E8449", fg="white").pack(side="left", padx=30, pady=20)
        
        tk.Button(header, text="Đăng xuất", command=self.show_login, 
                  bg="#27AE60", fg="white", activebackground="#2ECC71",
                  font=("Helvetica", 10, "bold"), relief="flat", padx=15, cursor="hand2").pack(side="right", padx=30, pady=20)
        
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
 
        self.setup_tabs()

    def setup_tabs(self):
        # Tab 1
        try:
            self.tab_home = DashboardFrame(self.notebook, self)
            self.notebook.add(self.tab_home, text="  Tổng quan  ")
        except NameError:
            self.tab_home = tk.Frame(self.notebook, bg="white")
            self.notebook.add(self.tab_home, text="  Tổng quan  ")

        # Tab 2
        try:
            self.tab_trans = TransactionFrame(self.notebook, self)
            self.notebook.add(self.tab_trans, text="  Giao dịch  ")
        except NameError:
            self.tab_trans = tk.Frame(self.notebook, bg="white")
            self.notebook.add(self.tab_trans, text="  Giao dịch  ")

        # Tab 3
        try:
            self.tab_budget = BudgetFrame(self.notebook, self)
            self.notebook.add(self.tab_budget, text="  Ngân sách  ")
        except NameError:
            self.tab_budget = tk.Frame(self.notebook, bg="white")
            self.notebook.add(self.tab_budget, text="  Ngân sách  ")

        # Tab 4
        try:
            self.tab_report = ReportFrame(self.notebook, self)
            self.notebook.add(self.tab_report, text="  Báo cáo  ")
        except NameError:
            self.tab_report = tk.Frame(self.notebook, bg="white")
            self.notebook.add(self.tab_report, text="  Báo cáo  ")

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", lambda: [app.data_manager.save_all_data(), app.destroy()])
    app.mainloop()

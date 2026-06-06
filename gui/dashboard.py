import tkinter as tk
from tkinter import ttk

class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        # Tiêu đề
        tk.Label(
            self,
            text="TỔNG QUAN TÀI CHÍNH",
            font=("Helvetica", 18, "bold"),
            bg="white"
        ).pack(pady=20)

        card_frame = tk.Frame(self, bg="white")
        card_frame.pack(pady=20)

        # Tạo các thẻ nhưng lưu lại biến label chứa giá trị tiền (để sau này cập nhật số)
        self.income_label = self.create_card(card_frame, "Tổng thu", "0 VNĐ", "#2ECC71", 0)
        self.expense_label = self.create_card(card_frame, "Tổng chi", "0 VNĐ", "#E74C3C", 1)
        self.balance_label = self.create_card(card_frame, "Số dư", "0 VNĐ", "#3498DB", 2)

        # Tính toán lần đầu khi mở app
        self.refresh_data()

        # Tuyệt chiêu: Tự động chạy hàm refresh_data mỗi khi tab này được hiển thị lên màn hình
        self.bind("<Visibility>", lambda event: self.refresh_data())

    def create_card(self, parent, title, value, color, col_index):
        """Tạo giao diện cho 1 thẻ và trả về đúng cái Label chứa số tiền"""
        frame = tk.Frame(parent, bg=color, width=220, height=120)
        frame.pack_propagate(False)
        frame.grid(row=0, column=col_index, padx=20)

        tk.Label(
            frame,
            text=title,
            font=("Helvetica", 12, "bold"),
            bg=color,
            fg="white"
        ).pack(pady=10)

        # Label hiển thị số tiền
        value_label = tk.Label(
            frame,
            text=value,
            font=("Helvetica", 14, "bold"),
            bg=color,
            fg="white"
        )
        value_label.pack()

        return value_label

    def refresh_data(self):
        """Hàm lấy dữ liệu mới nhất và cập nhật lại số trên thẻ"""
        dm = self.controller.data_manager
        transactions = dm.get_user_transactions()

        # Tính lại tổng thu, tổng chi
        income = sum(t.amount for t in transactions if t.transaction_type == "income")
        expense = sum(t.amount for t in transactions if t.transaction_type == "expense")
        balance = income - expense

        # Cập nhật chữ (text) cho các label
        self.income_label.config(text=f"{income:,.0f} VNĐ")
        self.expense_label.config(text=f"{expense:,.0f} VNĐ")
        self.balance_label.config(text=f"{balance:,.0f} VNĐ")

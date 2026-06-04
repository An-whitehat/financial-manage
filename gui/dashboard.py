# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

class DashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")

        self.controller = controller
        dm = controller.data_manager

        transactions = dm.get_user_transactions()

        income = sum(
            t.amount for t in transactions
            if t.transaction_type == "income"
        )

        expense = sum(
            t.amount for t in transactions
            if t.transaction_type == "expense"
        )

        balance = income - expense

        tk.Label(
            self,
            text="TỔNG QUAN TÀI CHÍNH",
            font=("Helvetica", 18, "bold"),
            bg="white"
        ).pack(pady=20)

        card_frame = tk.Frame(self, bg="white")
        card_frame.pack(pady=20)

        self.create_card(
            card_frame,
            "Tổng thu",
            f"{income:,.0f} VNĐ",
            "#2ECC71"
        ).grid(row=0, column=0, padx=20)

        self.create_card(
            card_frame,
            "Tổng chi",
            f"{expense:,.0f} VNĐ",
            "#E74C3C"
        ).grid(row=0, column=1, padx=20)

        self.create_card(
            card_frame,
            "Số dư",
            f"{balance:,.0f} VNĐ",
            "#3498DB"
        ).grid(row=0, column=2, padx=20)

    def create_card(self, parent, title, value, color):
        frame = tk.Frame(
            parent,
            bg=color,
            width=220,
            height=120
        )

        frame.pack_propagate(False)

        tk.Label(
            frame,
            text=title,
            font=("Helvetica", 12, "bold"),
            bg=color,
            fg="white"
        ).pack(pady=10)

        tk.Label(
            frame,
            text=value,
            font=("Helvetica", 14, "bold"),
            bg=color,
            fg="white"
        ).pack()

        return frame
# -*- coding: utf-8 -*-
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ReportFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")

        self.controller = controller

        tk.Label(
            self,
            text="BÁO CÁO THU CHI",
            font=("Helvetica", 18, "bold"),
            bg="white"
        ).pack(pady=15)

        self.draw_chart()

    def draw_chart(self):

        dm = self.controller.data_manager

        transactions = dm.get_user_transactions()

        income = sum(
            t.amount for t in transactions
            if t.transaction_type == "income"
        )

        expense = sum(
            t.amount for t in transactions
            if t.transaction_type == "expense"
        )

        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)

        values = [income, expense]
        labels = ["Thu nhập", "Chi tiêu"]

        if sum(values) > 0:
            ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%"
            )
            ax.set_title("Tỷ lệ Thu / Chi")
        else:
            ax.text(
                0.5,
                0.5,
                "Chưa có dữ liệu giao dịch",
                ha="center",
                va="center",
                fontsize=14
            )
            ax.set_title("Báo cáo")

        canvas = FigureCanvasTkAgg(
            fig,
            master=self
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            pady=20
        )
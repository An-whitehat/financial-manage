from collections import defaultdict

class ReportGenerator:
    def __init__(self, data_manager):
        self.data_manager = data_manager

    # ================= INTERNAL =================
    def _get_transactions(self):
        return self.data_manager.get_user_transactions()

    # ================= BASIC =================
    def get_total_income(self, period=None):
        total = 0
        for t in self._get_transactions():
            if t.transaction_type == "income":
                if period and not t.date.startswith(period):
                    continue
                total += t.amount
        return total

    def get_total_expense(self, period=None):
        total = 0
        for t in self._get_transactions():
            if t.transaction_type == "expense":
                if period and not t.date.startswith(period):
                    continue
                total += t.amount
        return total

    def get_balance(self):
        return self.get_total_income() - self.get_total_expense()

    def get_income_expense_summary(self, month_year=None):
        income = self.get_total_income(month_year)
        expense = self.get_total_expense(month_year)
        return {
            "income": income,
            "expense": expense,
            "balance": income - expense
        }

    # ================= CATEGORY =================
    def get_category_summary(self):
        result = defaultdict(float)
        for t in self._get_transactions():
            if t.transaction_type == "expense":  # chỉ tính chi cho hợp lý
                result[t.category_id] += t.amount
        return dict(result)

    def get_category_percentages(self):
        summary = self.get_category_summary()
        total_expense = sum(summary.values())

        percentages = {}
        for cat, amount in summary.items():
            if total_expense > 0:
                percentages[cat] = (amount / total_expense) * 100
            else:
                percentages[cat] = 0
        return percentages

    def get_top_expense_categories(self, limit=5):
        summary = self.get_category_summary()
        sorted_list = sorted(summary.items(), key=lambda x: x[1], reverse=True)
        return sorted_list[:limit]

    def get_top_income_categories(self, limit=5):
        summary = defaultdict(float)
        for t in self._get_transactions():
            if t.transaction_type == "income":
                summary[t.category_id] += t.amount

        sorted_list = sorted(summary.items(), key=lambda x: x[1], reverse=True)
        return sorted_list[:limit]

    # ================= TIME =================
    def get_monthly_report(self, year_month):
        return self.get_income_expense_summary(year_month)

    def get_monthly_summary(self, year=None):
        result = defaultdict(lambda: {"income": 0, "expense": 0})

        for t in self._get_transactions():
            month = t.date[:7]  # YYYY-MM

            if year and not month.startswith(str(year)):
                continue

            if t.transaction_type == "income":
                result[month]["income"] += t.amount
            else:
                result[month]["expense"] += t.amount

        return dict(result)

    def get_yearly_report(self, year):
        return self.get_monthly_summary(year)

    # ================= EXTRA =================
    def get_transactions_by_type(self, transaction_type):
        return [
            t for t in self._get_transactions()
            if t.transaction_type == transaction_type
        ]

    def get_expense_by_category(self, category_id):
        total = 0
        for t in self._get_transactions():
            if t.transaction_type == "expense" and t.category_id == category_id:
                total += t.amount
        return total

    def generate_full_report(self):
        return {
            "total_income": self.get_total_income(),
            "total_expense": self.get_total_expense(),
            "balance": self.get_balance(),
            "top_expense_categories": self.get_top_expense_categories(),
            "top_income_categories": self.get_top_income_categories()
        }

    def __str__(self):
        report = self.generate_full_report()
        return f"""
===== FINANCIAL REPORT =====
Income: {report['total_income']}
Expense: {report['total_expense']}
Balance: {report['balance']}
Top Expense: {report['top_expense_categories']}
Top Income: {report['top_income_categories']}
"""
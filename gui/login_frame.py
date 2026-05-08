import tkinter as tk
from tkinter import messagebox

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#27AE60") 
        
        # Card đăng nhập màu trắng bo viền xanh
        login_card = tk.Frame(self, bg="#FFFFFF", highlightbackground="#2ECC71", 
                              highlightthickness=2, padx=40, pady=40)
        login_card.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(login_card, text="QUẢN LÝ TÀI CHÍNH", font=("Helvetica", 22, "bold"), 
                 bg="#FFFFFF", fg="#1E8449").pack(pady=(0, 5))
        
   
        
        self.create_input(login_card, "Tên đăng nhập", "ent_username")
        self.create_input(login_card, "Mật khẩu", "ent_password", is_password=True)
        
        # Nút Đăng nhập xanh lá rực rỡ
        btn_login = tk.Button(login_card, text="ĐĂNG NHẬP NGAY", bg="#2ECC71", fg="white", 
                              activebackground="#27AE60", activeforeground="white",
                              font=("Helvetica", 12, "bold"), width=25, bd=0, 
                              cursor="hand2", pady=10, command=self.handle_login)
        btn_login.pack(pady=(20, 10))
        
        btn_reg = tk.Button(login_card, text="Chưa có tài khoản? Đăng ký", bg="#FFFFFF", 
                            fg="#27AE60", font=("Helvetica", 10, "bold"), bd=0, 
                            cursor="hand2", command=self.handle_register)
        btn_reg.pack()

    def create_input(self, parent, label_text, attr_name, is_password=False):
        tk.Label(parent, text=label_text, bg="#FFFFFF", font=("Helvetica", 10, "bold"), 
                 fg="#2C3E50").pack(anchor="w", pady=(10, 5))
        
        # Ô nhập liệu có viền xanh nhạt
        entry = tk.Entry(parent, width=35, font=("Helvetica", 11), bg="#F8F9F9", 
                         relief="flat", highlightbackground="#D5DBDB", highlightthickness=1)
        if is_password:
            entry.config(show="●")
        entry.pack(ipady=8, pady=(0, 10))
        
        # Hiệu ứng đổi màu viền khi chọn vào ô
        entry.bind("<FocusIn>", lambda e: entry.config(highlightbackground="#2ECC71", highlightthickness=2))
        entry.bind("<FocusOut>", lambda e: entry.config(highlightbackground="#D5DBDB", highlightthickness=1))
        
        setattr(self, attr_name, entry)

    # GIỮ NGUYÊN LOGIC CŨ
    def handle_login(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()
        try:
            self.controller.data_manager.login(username, password)
            self.controller.login_success()
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

    def handle_register(self):
        username = self.ent_username.get().strip()
        password = self.ent_password.get().strip()
        try:
            self.controller.data_manager.register_user(username, password)
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))

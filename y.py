import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime

class BankingApp:
    def __init__(self):
        self.users = {
            '123': {
                'password': 'pass123',
                'name': 'John Doe',
                'account_type': 'Pichincha',
                'balance': 1000.00,
                'transactions': []
            },
            '456': {
                'password': 'pass456',
                'name': 'John Doe',
                'account_type': 'Produbanco',
                'balance': 1000.00,
                'transactions': []
            }
        }
        self.max_daily_transaction = 500.00
        self.daily_transaction_total = 0.00
        self.current_user = None
        self.login_attempts = 0
        self.blocked_accounts = set()

        self.root = tk.Tk()
        self.root.title("Banking Application")
        self.root.geometry("400x300")
        
        self.create_login_screen()
        
    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="User ID:").pack(pady=10)
        self.user_id_entry = tk.Entry(self.root)
        self.user_id_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=10)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        login_button = tk.Button(self.root, text="Login", command=self.verify_login)
        login_button.pack(pady=20)

        unlock_button = tk.Button(self.root, text="Unlock Account", command=self.unlock_account_screen)
        unlock_button.pack(pady=10)

    def verify_login(self):
        user_id = self.user_id_entry.get()
        password = self.password_entry.get()

        if user_id in self.blocked_accounts:
            messagebox.showerror("Error", "Esta cuenta está bloqueada. Use la opción de desbloqueo.")
            return

        if user_id in self.users and self.users[user_id]['password'] == password:
            self.current_user = user_id
            self.login_attempts = 0
            self.show_main_menu()
        else:
            self.login_attempts += 1
            if self.login_attempts >= 3:
                self.blocked_accounts.add(user_id)
                messagebox.showerror("Bloqueo", "Cuenta bloqueada por 3 intentos fallidos.")
                self.create_login_screen()
            else:
                messagebox.showerror("Error", f"Contraseña incorrecta. Intentos restantes: {3 - self.login_attempts}")

    def unlock_account_screen(self):
        unlock_window = tk.Toplevel(self.root)
        unlock_window.title("Desbloquear Cuenta")
        unlock_window.geometry("300x200")

        tk.Label(unlock_window, text="ID de Usuario:").pack(pady=10)
        user_id_entry = tk.Entry(unlock_window)
        user_id_entry.pack(pady=5)

        tk.Label(unlock_window, text="Contraseña:").pack(pady=10)
        password_entry = tk.Entry(unlock_window, show="*")
        password_entry.pack(pady=5)

        def validate_unlock():
            user_id = user_id_entry.get()
            password = password_entry.get()

            if user_id in self.users and self.users[user_id]['password'] == password:
                self.blocked_accounts.discard(user_id)
                messagebox.showinfo("Éxito", "Cuenta desbloqueada exitosamente.")
                unlock_window.destroy()
            else:
                messagebox.showerror("Error", "Credenciales incorrectas.")

        unlock_button = tk.Button(unlock_window, text="Desbloquear", command=validate_unlock)
        unlock_button.pack(pady=20)

    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        menu_options = [
            ("Retiro", self.verify_account_type_withdraw),
            ("Depósito", self.verify_account_type_deposit),
            ("Ver Movimientos", self.verify_account_type_movements),
            ("Consultar Saldo", self.verify_account_type_balance),
            ("Realizar Pagos", self.verify_account_type_payments)
        ]

        for text, command in menu_options:
            tk.Button(self.root, text=text, command=command, width=20).pack(pady=10)

    def verify_account_type(self, next_action):
        verify_window = tk.Toplevel(self.root)
        verify_window.title("Verificar Tipo de Cuenta")
        verify_window.geometry("300x200")

        tk.Label(verify_window, text="Tipo de Cuenta:").pack(pady=10)
        account_types = ["Ahorros", "Corriente"]
        selected_type = tk.StringVar(verify_window)
        selected_type.set(account_types[0])

        account_dropdown = tk.OptionMenu(verify_window, selected_type, *account_types)
        account_dropdown.pack(pady=10)

        def proceed():
            account_type = selected_type.get()
            user_account_type = self.users[self.current_user]['account_type']

            if account_type not in account_types:
                messagebox.showerror("Error", "Tipo de cuenta inválido.")
                verify_window.destroy()
                return

            if user_account_type != "Pichincha":
                response = messagebox.askyesno("Comisión", "Se cobrará $0.52 por transacción. ¿Desea continuar?")
                if not response:
                    messagebox.showinfo("Información", "Gracias. Vuelva pronto.")
                    self.root.quit()
                    return

            verify_window.destroy()
            next_action()

        tk.Button(verify_window, text="Continuar", command=proceed).pack(pady=20)

    def verify_account_type_withdraw(self):
        self.verify_account_type(self.withdraw_menu)

    def verify_account_type_deposit(self):
        self.verify_account_type(self.deposit_menu)

    def verify_account_type_movements(self):
        self.verify_account_type(self.show_movements)

    def verify_account_type_balance(self):
        self.verify_account_type(self.check_balance)

    def verify_account_type_payments(self):
        self.verify_account_type(self.payment_menu)

    def withdraw_menu(self):
        withdraw_window = tk.Toplevel(self.root)
        withdraw_window.title("Retiro")
        withdraw_window.geometry("300x400")

        amounts = [10, 20, 40, 60, 80, 100, "Otro Valor"]

        def process_withdrawal(amount):
            if amount == "Otro Valor":
                amount = simpledialog.askfloat("Monto", "Ingrese el monto a retirar:")
                if amount is None:
                    return

            if amount > 500 or self.daily_transaction_total + amount > 500:
                messagebox.showerror("Error", "Límite de transacción diaria excedido.")
                withdraw_window.destroy()
                return

            user_balance = self.users[self.current_user]['balance']
            if user_balance >= amount:
                self.users[self.current_user]['balance'] -= amount
                self.daily_transaction_total += amount
                self.record_transaction('Retiro', -amount)
                messagebox.showinfo("Éxito", "Transacción exitosa.")
                withdraw_window.destroy()
                self.root.quit()
            else:
                messagebox.showerror("Error", "Saldo insuficiente.")
                withdraw_window.destroy()
                messagebox.showinfo("Información", "Gracias. Vuelva pronto.")
                self.root.quit()

        for amount in amounts:
            tk.Button(withdraw_window, text=f"${amount}", 
                    command=lambda a=amount: process_withdrawal(a), 
                    width=20).pack(pady=10)

    def deposit_menu(self):
        deposit_window = tk.Toplevel(self.root)
        deposit_window.title("Depósito")
        deposit_window.geometry("300x200")

        tk.Label(deposit_window, text="Número de Cuenta:").pack(pady=10)
        account_entry = tk.Entry(deposit_window)
        account_entry.pack(pady=5)

        def process_deposit():
            amount = simpledialog.askfloat("Monto", "Ingrese el monto a depositar:")
            if amount is None:
                return

            if amount > 500 or self.daily_transaction_total + amount > 500:
                messagebox.showerror("Error", "Límite de transacción diaria excedido.")
                deposit_window.destroy()
                return

            self.users[self.current_user]['balance'] += amount
            self.daily_transaction_total += amount
            self.record_transaction('Depósito', amount)
            messagebox.showinfo("Éxito", "Transacción exitosa.")
            deposit_window.destroy()
            self.root.quit()

        tk.Button(deposit_window, text="Continuar", command=process_deposit).pack(pady=20)

    def show_movements(self):
        movements_window = tk.Toplevel(self.root)
        movements_window.title("Historial de Movimientos")
        movements_window.geometry("400x300")

        transactions = self.users[self.current_user]['transactions']
        
        # Display transactions
        if transactions:
            for idx, transaction in enumerate(transactions, 1):
                tk.Label(movements_window, 
                        text=f"{idx}. {transaction['date']} - {transaction['type']}: ${transaction['amount']}").pack(pady=5)
        else:
            tk.Label(movements_window, text="No hay transacciones.").pack(pady=20)

        tk.Button(movements_window, text="Aceptar", command=movements_window.destroy).pack(pady=20)

    def check_balance(self):
        balance_window = tk.Toplevel(self.root)
        balance_window.title("Consulta de Saldo")
        balance_window.geometry("300x200")

        balance = self.users[self.current_user]['balance']
        tk.Label(balance_window, text=f"Saldo Actual: ${balance:.2f}", font=("Arial", 16)).pack(pady=20)

        def close_window():
            balance_window.destroy()
            self.root.quit()

        tk.Button(balance_window, text="Aceptar", command=close_window).pack(pady=20)

    def payment_menu(self):
        services = ["Luz", "Agua", "Teléfono", "Internet"]
        services_window = tk.Toplevel(self.root)
        services_window.title("Pago de Servicios")
        services_window.geometry("300x400")

        def select_service(service):
            amount = simpledialog.askfloat("Monto", f"Ingrese el monto a pagar por {service}:")
            if amount is None:
                return

            if amount > 500 or self.daily_transaction_total + amount > 500:
                messagebox.showerror("Error", "Límite de transacción diaria excedido.")
                services_window.destroy()
                return

            payment_method_window = tk.Toplevel(self.root)
            payment_method_window.title("Método de Pago")
            payment_method_window.geometry("300x200")

            def process_payment(method):
                current_balance = self.users[self.current_user]['balance']
                if current_balance >= amount:
                    self.users[self.current_user]['balance'] -= amount
                    self.daily_transaction_total += amount
                    self.record_transaction(f'Pago {service}', -amount)
                    messagebox.showinfo("Éxito", "Transacción exitosa.")
                    payment_method_window.destroy()
                    services_window.destroy()
                    self.root.quit()
                else:
                    messagebox.showerror("Error", "Saldo insuficiente.")
                    services_window.destroy()
                    self.root.quit()

            tk.Button(payment_method_window, text="Efectivo", command=lambda: process_payment("Efectivo")).pack(pady=10)
            tk.Button(payment_method_window, text="Tarjeta", command=lambda: process_payment("Tarjeta")).pack(pady=10)

        for service in services:
            tk.Button(services_window, text=service, 
                    command=lambda s=service: select_service(s), 
                    width=20).pack(pady=10)

    def record_transaction(self, transaction_type, amount):
        transaction = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': transaction_type,
            'amount': amount
        }
        self.users[self.current_user]['transactions'].append(transaction)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BankingApp()
    app.run()
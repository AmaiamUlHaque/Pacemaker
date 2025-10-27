"""
DCM (Device Controller-Monitor) GUI for Pacemaker Interface

Provides the graphical user interface for pacemaker configuration including
user authentication, mode selection, parameter management, and status monitoring.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.user_management import authenticate_user, register_user, MAX_USERS, list_users
from core.params import Parameters, load_parameters
from core.modes import PaceMakerMode, parse_mode


class DCMApplication:
    """Main application controller for DCM GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DCM - Device Controller-Monitor")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        self.current_user = None
        self.current_mode = None
        self.parameters = self._get_default_parameters()
        
        self._configure_styles()
        self.show_login_screen()
    
    def _configure_styles(self):
        """Configure GUI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Helvetica', 12), foreground='#34495e')
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'), foreground='#2c3e50')
        style.configure('Status.TLabel', font=('Helvetica', 10), foreground='#7f8c8d')
        style.configure('Mode.TButton', font=('Helvetica', 11), padding=10)
        style.configure('Action.TButton', font=('Helvetica', 11, 'bold'), padding=8)
        
    def _get_default_parameters(self):
        """Load parameters from file or return defaults"""
        try:
            return load_parameters()
        except:
            return Parameters(
                LRL=60, URL=120,
                atrial_amp=3.5, atrial_width=0.4,
                ventricular_amp=3.5, ventricular_width=0.4,
                VRP=320, ARP=250
            )
    
    def clear_window(self):
        """Clear all widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login screen"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=(0, 30))
        ttk.Label(title_frame, text="DCM System", style='Title.TLabel').pack()
        ttk.Label(title_frame, text="Device Controller-Monitor for Pacemaker Management", 
                 style='Subtitle.TLabel').pack(pady=(5, 0))
        
        login_frame = ttk.LabelFrame(main_frame, text="Login", padding="30")
        login_frame.pack(pady=20, padx=50, fill=tk.BOTH)
        
        ttk.Label(login_frame, text="Username:", font=('Helvetica', 11)).grid(
            row=0, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        username_entry = ttk.Entry(login_frame, width=30, font=('Helvetica', 11))
        username_entry.grid(row=0, column=1, pady=10)
        
        ttk.Label(login_frame, text="Password:", font=('Helvetica', 11)).grid(
            row=1, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        password_entry = ttk.Entry(login_frame, width=30, show="*", font=('Helvetica', 11))
        password_entry.grid(row=1, column=1, pady=10)
        
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Login", style='Action.TButton',
                  command=lambda: self._handle_login(username_entry.get(), password_entry.get())
                  ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Register New User",
                  command=self.show_registration_screen).pack(side=tk.LEFT, padx=5)
        
        self.login_status = ttk.Label(main_frame, text="", foreground='red', font=('Helvetica', 10))
        self.login_status.pack(pady=10)
        
        user_count = len(list_users())
        ttk.Label(main_frame, text=f"Registered users: {user_count}/{MAX_USERS}", 
                 style='Status.TLabel').pack(side=tk.BOTTOM, pady=10)
        
        username_entry.focus()
        password_entry.bind('<Return>', lambda e: self._handle_login(username_entry.get(), password_entry.get()))
    
    def show_registration_screen(self):
        """Display registration screen"""
        self.clear_window()
        
        if len(list_users()) >= MAX_USERS:
            messagebox.showerror("Registration Error", 
                               f"Maximum of {MAX_USERS} users reached.")
            self.show_login_screen()
            return
        
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Register New User", style='Title.TLabel').pack(pady=(0, 30))
        
        reg_frame = ttk.LabelFrame(main_frame, text="User Information", padding="30")
        reg_frame.pack(pady=20, padx=50, fill=tk.BOTH)
        
        ttk.Label(reg_frame, text="Username:", font=('Helvetica', 11)).grid(
            row=0, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        username_entry = ttk.Entry(reg_frame, width=30, font=('Helvetica', 11))
        username_entry.grid(row=0, column=1, pady=10)
        
        ttk.Label(reg_frame, text="Password:", font=('Helvetica', 11)).grid(
            row=1, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        password_entry = ttk.Entry(reg_frame, width=30, show="*", font=('Helvetica', 11))
        password_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(reg_frame, text="Confirm Password:", font=('Helvetica', 11)).grid(
            row=2, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        confirm_entry = ttk.Entry(reg_frame, width=30, show="*", font=('Helvetica', 11))
        confirm_entry.grid(row=2, column=1, pady=10)
        
        button_frame = ttk.Frame(reg_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Register", style='Action.TButton',
                  command=lambda: self._handle_registration(
                      username_entry.get(), password_entry.get(), confirm_entry.get())
                  ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel",
                  command=self.show_login_screen).pack(side=tk.LEFT, padx=5)
        
        self.reg_status = ttk.Label(main_frame, text="", foreground='red', font=('Helvetica', 10))
        self.reg_status.pack(pady=10)
        
        user_count = len(list_users())
        ttk.Label(main_frame, text=f"Registered users: {user_count}/{MAX_USERS}", 
                 style='Status.TLabel').pack(side=tk.BOTTOM, pady=10)
        
        username_entry.focus()
    
    def _handle_login(self, username, password):
        """Handle login attempt"""
        if not username or not password:
            self.login_status.config(text="Please enter both username and password")
            return
        
        if authenticate_user(username, password):
            self.current_user = username
            self.show_dashboard()
        else:
            self.login_status.config(text="Invalid username or password")
    
    def _handle_registration(self, username, password, confirm_password):
        """Handle user registration"""
        if not username or not password:
            self.reg_status.config(text="Please fill in all fields")
            return
        if len(username) < 3:
            self.reg_status.config(text="Username must be at least 3 characters")
            return
        if len(password) < 4:
            self.reg_status.config(text="Password must be at least 4 characters")
            return
        if password != confirm_password:
            self.reg_status.config(text="Passwords do not match")
            return
        
        if register_user(username, password):
            messagebox.showinfo("Success", f"User '{username}' registered successfully!")
            self.show_login_screen()
        else:
            if len(list_users()) >= MAX_USERS:
                self.reg_status.config(text=f"Maximum of {MAX_USERS} users reached")
            else:
                self.reg_status.config(text="Username already exists")
    
    def show_dashboard(self):
        """Display main dashboard"""
        self.clear_window()
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="DCM Dashboard", style='Title.TLabel').pack(side=tk.LEFT)
        
        user_frame = ttk.Frame(header_frame)
        user_frame.pack(side=tk.RIGHT)
        ttk.Label(user_frame, text=f"User: {self.current_user}", 
                 font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Button(user_frame, text="Logout", command=self._handle_logout).pack(side=tk.LEFT)
        
        status_frame = ttk.LabelFrame(main_frame, text="Communication Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        status_grid = ttk.Frame(status_frame)
        status_grid.pack()
        
        self.telemetry_canvas = tk.Canvas(status_grid, width=20, height=20, 
                                         highlightthickness=0, bg='#ecf0f1')
        self.telemetry_canvas.grid(row=0, column=0, padx=5)
        self.telemetry_led = self.telemetry_canvas.create_oval(2, 2, 18, 18, 
                                                               fill='red', outline='darkred')
        
        ttk.Label(status_grid, text="Telemetry Status:", font=('Helvetica', 10)).grid(
            row=0, column=1, padx=(0, 5))
        self.telemetry_status = ttk.Label(status_grid, text="Disconnected (No Hardware)", 
                                         font=('Helvetica', 10, 'bold'), foreground='red')
        self.telemetry_status.grid(row=0, column=2, padx=5)
        
        ttk.Label(status_grid, text="│", font=('Helvetica', 14), 
                 foreground='#bdc3c7').grid(row=0, column=3, padx=10)
        
        ttk.Label(status_grid, text="Device Status:", font=('Helvetica', 10)).grid(
            row=0, column=4, padx=(0, 5))
        self.device_status = ttk.Label(status_grid, text="Not Connected", 
                                      font=('Helvetica', 10), foreground='#7f8c8d')
        self.device_status.grid(row=0, column=5, padx=5)
        
        ttk.Label(status_frame, 
                 text="Note: Hardware communication will be implemented in future deliverables",
                 style='Status.TLabel', foreground='#95a5a6').pack(pady=(5, 0))
        
        mode_frame = ttk.LabelFrame(main_frame, text="Pacing Mode Selection", padding="15")
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(mode_frame, text="Select the pacing mode:", 
                 font=('Helvetica', 11)).pack(anchor=tk.W, pady=(0, 10))
        
        button_container = ttk.Frame(mode_frame)
        button_container.pack(fill=tk.X)
        
        self.mode_buttons = {}
        modes = [PaceMakerMode.AOO, PaceMakerMode.VOO, PaceMakerMode.AAI, PaceMakerMode.VVI]
        
        for idx, mode in enumerate(modes):
            mode_info = parse_mode(mode)
            btn = tk.Button(button_container, 
                          text=f"{mode.value}\n{mode_info.descrpt}",
                          font=('Helvetica', 10),
                          width=20, height=3,
                          relief=tk.RAISED, bd=2,
                          bg='#ecf0f1',
                          activebackground='#3498db',
                          command=lambda m=mode: self._select_mode(m))
            btn.grid(row=0, column=idx, padx=5, pady=5)
            self.mode_buttons[mode] = btn
        
        self.mode_display_frame = ttk.Frame(mode_frame)
        self.mode_display_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(self.mode_display_frame, text="Current Mode:", 
                 font=('Helvetica', 11, 'bold')).pack(side=tk.LEFT)
        self.current_mode_label = ttk.Label(self.mode_display_frame, 
                                           text="None Selected",
                                           font=('Helvetica', 11),
                                           foreground='#e74c3c')
        self.current_mode_label.pack(side=tk.LEFT, padx=10)
        
        self.param_frame = ttk.LabelFrame(main_frame, text="Programmable Parameters", 
                                         padding="15")
        self.param_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.param_widgets = {}
        self._display_parameter_message()
        
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="Save Parameters", style='Action.TButton',
                  command=self._save_parameters).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="Load Parameters",
                  command=self._load_parameters).pack(side=tk.LEFT, padx=5)
        
        self._select_mode(PaceMakerMode.VVI)
    
    def _display_parameter_message(self):
        """Display placeholder message"""
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.param_frame, 
                 text="Please select a pacing mode to view and edit parameters",
                 font=('Helvetica', 11, 'italic'),
                 foreground='#7f8c8d').pack(pady=40)
    
    def _select_mode(self, mode):
        """Handle mode selection"""
        self.current_mode = mode
        
        for m, btn in self.mode_buttons.items():
            if m == mode:
                btn.config(relief=tk.SUNKEN, bg='#3498db', fg='white')
            else:
                btn.config(relief=tk.RAISED, bg='#ecf0f1', fg='black')
        
        mode_info = parse_mode(mode)
        self.current_mode_label.config(text=f"{mode.value} - {mode_info.descrpt}",
                                      foreground='#27ae60')
        
        self._display_parameters_for_mode(mode)
    
    def _display_parameters_for_mode(self, mode):
        """Display parameter inputs for selected mode"""
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        self.param_widgets = {}
        
        canvas = tk.Canvas(self.param_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.param_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>",
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        mode_params = self._get_mode_parameters(mode)
        
        for row, param_info in enumerate(mode_params):
            param_row = ttk.Frame(scrollable_frame)
            param_row.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=8, padx=10)
            
            ttk.Label(param_row, text=f"{param_info['label']}:", 
                     font=('Helvetica', 10), width=25, anchor=tk.W).grid(
                         row=0, column=0, sticky=tk.W, padx=(0, 10))
            
            entry_var = tk.StringVar(value=str(getattr(self.parameters, param_info['name'])))
            entry = ttk.Entry(param_row, textvariable=entry_var, width=15,
                            font=('Helvetica', 10))
            entry.grid(row=0, column=1, padx=5)
            
            ttk.Label(param_row, text=param_info['unit'], 
                     font=('Helvetica', 10), foreground='#7f8c8d').grid(
                         row=0, column=2, sticky=tk.W, padx=5)
            
            ttk.Label(param_row, text=f"Range: {param_info['range']}", 
                     font=('Helvetica', 9), foreground='#95a5a6').grid(
                         row=0, column=3, sticky=tk.W, padx=10)
            
            self.param_widgets[param_info['name']] = {
                'var': entry_var,
                'entry': entry,
                'type': param_info['type']
            }
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _get_mode_parameters(self, mode):
        """Return parameters for the given mode"""
        common = [
            {'name': 'LRL', 'label': 'Lower Rate Limit', 'unit': 'ppm', 
             'range': '30-175', 'type': 'int'},
            {'name': 'URL', 'label': 'Upper Rate Limit', 'unit': 'ppm', 
             'range': '50-175', 'type': 'int'},
        ]
        
        atrial = [
            {'name': 'atrial_amp', 'label': 'Atrial Amplitude', 'unit': 'V', 
             'range': '0.1-5.0', 'type': 'float'},
            {'name': 'atrial_width', 'label': 'Atrial Pulse Width', 'unit': 'ms', 
             'range': '0.1-1.9', 'type': 'float'},
            {'name': 'ARP', 'label': 'Atrial Refractory Period', 'unit': 'ms', 
             'range': '150-500', 'type': 'int'},
        ]
        
        ventricular = [
            {'name': 'ventricular_amp', 'label': 'Ventricular Amplitude', 'unit': 'V', 
             'range': '0.1-5.0', 'type': 'float'},
            {'name': 'ventricular_width', 'label': 'Ventricular Pulse Width', 'unit': 'ms', 
             'range': '0.1-1.9', 'type': 'float'},
            {'name': 'VRP', 'label': 'Ventricular Refractory Period', 'unit': 'ms', 
             'range': '150-500', 'type': 'int'},
        ]
        
        if mode == PaceMakerMode.AOO:
            return [common[0], *atrial[:2]]
        elif mode == PaceMakerMode.VOO:
            return [common[0], *ventricular[:2]]
        elif mode == PaceMakerMode.AAI:
            return [*common, *atrial]
        elif mode == PaceMakerMode.VVI:
            return [*common, *ventricular]
        
        return []
    
    def _validate_mode_parameters(self, mode):
        """Validate parameters for current mode"""
        if not(30 <= self.parameters.LRL <= 175):
            raise ValueError(f"LRL {self.parameters.LRL} out of range (30-175 ppm)")
        
        if mode in [PaceMakerMode.AAI, PaceMakerMode.VVI]:
            if not(50 <= self.parameters.URL <= 175):
                raise ValueError(f"URL {self.parameters.URL} out of range (50-175 ppm)")
            if self.parameters.LRL >= self.parameters.URL:
                raise ValueError(f"URL must be greater than LRL")
        
        if mode in [PaceMakerMode.AOO, PaceMakerMode.AAI]:
            if not (0.1 <= self.parameters.atrial_amp <= 5.0):
                raise ValueError(f"Atrial Amplitude {self.parameters.atrial_amp} out of range (0.1-5.0 V)")
            if not (0.1 <= self.parameters.atrial_width <= 1.9):
                raise ValueError(f"Atrial Pulse Width {self.parameters.atrial_width} out of range (0.1-1.9 ms)")
            if mode == PaceMakerMode.AAI:
                if not (150 <= self.parameters.ARP <= 500):
                    raise ValueError(f"ARP {self.parameters.ARP} out of range (150-500 ms)")
        
        if mode in [PaceMakerMode.VOO, PaceMakerMode.VVI]:
            if not (0.1 <= self.parameters.ventricular_amp <= 5.0):
                raise ValueError(f"Ventricular Amplitude {self.parameters.ventricular_amp} out of range (0.1-5.0 V)")
            if not (0.1 <= self.parameters.ventricular_width <= 1.9):
                raise ValueError(f"Ventricular Pulse Width {self.parameters.ventricular_width} out of range (0.1-1.9 ms)")
            if mode == PaceMakerMode.VVI:
                if not (150 <= self.parameters.VRP <= 500):
                    raise ValueError(f"VRP {self.parameters.VRP} out of range (150-500 ms)")
        
        return True
    
    def _save_parameters(self):
        """Validate and save parameters"""
        if not self.current_mode:
            messagebox.showwarning("No Mode Selected", 
                                 "Please select a pacing mode before saving.")
            return
        
        try:
            for param_name, widget_info in self.param_widgets.items():
                value_str = widget_info['var'].get()
                value = int(value_str) if widget_info['type'] == 'int' else float(value_str)
                setattr(self.parameters, param_name, value)
            
            self._validate_mode_parameters(self.current_mode)
            
            params_file = os.path.join(os.path.dirname(__file__), "..", "storage", "params.json")
            with open(params_file, "w") as f:
                json.dump(self.parameters.to_dict(), f, indent=4)
            
            messagebox.showinfo("Success", 
                              f"Parameters saved for {self.current_mode.value} mode.")
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def _load_parameters(self):
        """Load parameters from file"""
        try:
            self.parameters = load_parameters()
            if self.current_mode:
                self._display_parameters_for_mode(self.current_mode)
            messagebox.showinfo("Success", "Parameters loaded successfully.")
        except FileNotFoundError:
            messagebox.showwarning("No Saved Parameters", "No saved parameters found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def _handle_logout(self):
        """Handle user logout"""
        if messagebox.askyesno("Confirm Logout", 
                              "Are you sure you want to logout?\n"
                              "Make sure you have saved any parameter changes."):
            self.current_user = None
            self.current_mode = None
            self.show_login_screen()


def main():
    """Main entry point for the DCM GUI application"""
    root = tk.Tk()
    app = DCMApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()


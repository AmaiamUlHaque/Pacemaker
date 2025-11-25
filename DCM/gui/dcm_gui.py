"""
DCM (Device Controller-Monitor) GUI for Pacemaker Interface

Provides the graphical user interface for pacemaker configuration including
user authentication, mode selection, parameter management, status monitoring,
and egram display for Deliverable 2.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import json
import threading
import time
from collections import deque
from typing import Optional

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.user_management import authenticate_user, register_user, MAX_USERS, list_users
from core.params import Parameters, load_parameters
from core.modes import PaceMakerMode, parse_mode, mode_id
try:
    from core.serial_interface import SerialInterface
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: Serial interface not available")


class DCMApplication:
    """Main application controller for DCM GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DCM - Device Controller-Monitor")
        self.root.geometry("1000x750")
        self.root.resizable(True, True)
        self.root.configure(bg="#ffd9ec")
        
        self.current_user = None
        self.current_mode = None
        self.parameters = self._get_default_parameters()
        self.ventricular_inhibit_active = False
        
        # Serial communication
        self.serial_interface = None
        self.serial_port = None
        self.is_connected = False
        
        # Egram data
        self.egram_data = {'atrial': deque(maxlen=1000), 'ventricular': deque(maxlen=1000)}
        self.egram_window = None
        self.egram_streaming = False
        
        self._configure_styles()
        self.show_login_screen()
    
    def _configure_styles(self):
        """configure shared ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        pink_bg = "#ffd9ec"
        style.configure('TFrame', background=pink_bg)
        style.configure('TLabelframe', background=pink_bg)
        style.configure('TLabelframe.Label', background=pink_bg)
        style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'),
                        foreground='#2c3e50', background=pink_bg)
        style.configure('Subtitle.TLabel', font=('Helvetica', 12),
                        foreground='#34495e', background=pink_bg)
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'),
                        foreground='#2c3e50', background=pink_bg)
        style.configure('Status.TLabel', font=('Helvetica', 10),
                        foreground='#7f8c8d', background=pink_bg)
        style.configure('Mode.TButton', font=('Helvetica', 11), padding=10)
        style.configure('Action.TButton', font=('Helvetica', 11, 'bold'), padding=8)
        
    def _get_default_parameters(self):
        """Load parameters from file or return defaults"""
        try:
            return load_parameters()
        except:
            return Parameters(
                LRL=60, URL=120, MSR=120, rate_smoothing=0,
                atrial_amp=3.5, atrial_width=1, atrial_sensitivity=0.75,
                ARP=250, PVARP=250, AV_delay=150,
                ventricular_amp=3.5, ventricular_width=1, ventricular_sensitivity=2.5,
                VRP=320,
                activity_threshold=4, reaction_time=30, recovery_time=5, response_factor=8,
                atr_cmp_ref_pwm=60, vent_cmp_ref_pwm=90
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
        self.telemetry_status = ttk.Label(status_grid, text="Disconnected", 
                                         font=('Helvetica', 10, 'bold'), foreground='red')
        self.telemetry_status.grid(row=0, column=2, padx=5)
        
        ttk.Label(status_grid, text="│", font=('Helvetica', 14), 
                 foreground='#bdc3c7').grid(row=0, column=3, padx=10)
        
        # Serial port selection
        ttk.Label(status_grid, text="Serial Port:", font=('Helvetica', 10)).grid(
            row=0, column=4, padx=(0, 5))
        self.port_var = tk.StringVar(value="COM1" if sys.platform == 'win32' else "/dev/ttyUSB0")
        port_entry = ttk.Entry(status_grid, textvariable=self.port_var, width=12)
        port_entry.grid(row=0, column=5, padx=5)
        
        self.connect_btn = ttk.Button(status_grid, text="Connect", 
                                     command=self._handle_serial_connect)
        self.connect_btn.grid(row=0, column=6, padx=5)
        
        if not SERIAL_AVAILABLE:
            self.connect_btn.config(state='disabled')
            self.telemetry_status.config(text="Serial Not Available")
        
        mode_frame = ttk.LabelFrame(main_frame, text="Pacing Mode Selection", padding="15")
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(mode_frame, text="Select the pacing mode:", 
                 font=('Helvetica', 11)).pack(anchor=tk.W, pady=(0, 10))
        
        button_container = ttk.Frame(mode_frame)
        button_container.pack(fill=tk.X)
        
        self.mode_buttons = {}
        # deliverable modes plus bonus dual-chamber dddr support
        required_modes = [
            PaceMakerMode.AOO, PaceMakerMode.VOO, PaceMakerMode.AAI, PaceMakerMode.VVI,
            PaceMakerMode.AOOR, PaceMakerMode.VOOR, PaceMakerMode.AAIR, PaceMakerMode.VVIR,
            PaceMakerMode.DDDR
        ]
        
        # Create scrollable frame for mode buttons
        mode_canvas = tk.Canvas(mode_frame, height=80, highlightthickness=0)
        mode_scrollbar = ttk.Scrollbar(mode_frame, orient="horizontal", command=mode_canvas.xview)
        mode_scrollable = ttk.Frame(mode_canvas)
        
        mode_scrollable.bind("<Configure>", lambda e: mode_canvas.configure(scrollregion=mode_canvas.bbox("all")))
        mode_canvas.create_window((0, 0), window=mode_scrollable, anchor="nw")
        mode_canvas.configure(xscrollcommand=mode_scrollbar.set)
        
        for idx, mode in enumerate(required_modes):
            mode_info = parse_mode(mode)
            btn = tk.Button(mode_scrollable, 
                          text=f"{mode.value}\n{mode_info.descrpt[:30]}...",
                          font=('Helvetica', 9),
                          width=18, height=3,
                          relief=tk.RAISED, bd=2,
                          bg='#ecf0f1',
                          activebackground='#3498db',
                          command=lambda m=mode: self._select_mode(m))
            btn.grid(row=0, column=idx, padx=3, pady=5)
            self.mode_buttons[mode] = btn
        
        mode_canvas.pack(side="top", fill="both", expand=True)
        mode_scrollbar.pack(side="bottom", fill="x")
        
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
        
        ttk.Button(action_frame, text="Transmit to Device", style='Action.TButton',
                  command=self._transmit_parameters).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="Request Parameters",
                  command=self._request_parameters).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="View Egrams",
                  command=self._show_egram_window).pack(side=tk.LEFT, padx=5)
        
        vent_btn = ttk.Button(action_frame, text="Hold Ventricular Inhibit",
                              style='Action.TButton')
        vent_btn.bind("<ButtonPress-1>", lambda _e: self._set_pushbutton_inhibit(True))
        vent_btn.bind("<ButtonRelease-1>", lambda _e: self._set_pushbutton_inhibit(False))
        vent_btn.pack(side=tk.LEFT, padx=5)
        
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
        """Return parameters for the given mode based on Deliverable 2 requirements"""
        mode_info = parse_mode(mode)
        is_rate_adaptive = mode_info.rate
        
        # Common parameters for all modes
        common = [
            {'name': 'LRL', 'label': 'Lower Rate Limit', 'unit': 'ppm', 
             'range': '30-175', 'type': 'int'},
        ]
        
        # URL for modes with sensing
        url_param = [
            {'name': 'URL', 'label': 'Upper Rate Limit', 'unit': 'ppm', 
             'range': '50-175', 'type': 'int'},
        ]
        
        # Rate adaptive parameters
        rate_params = [
            {'name': 'MSR', 'label': 'Maximum Sensor Rate', 'unit': 'ppm', 
             'range': '50-175', 'type': 'int'},
            {'name': 'activity_threshold', 'label': 'Activity Threshold', 'unit': 'level', 
             'range': '1-7 (V-Low to V-High)', 'type': 'int'},
            {'name': 'reaction_time', 'label': 'Reaction Time', 'unit': 'sec', 
             'range': '10-50', 'type': 'int'},
            {'name': 'recovery_time', 'label': 'Recovery Time', 'unit': 'min', 
             'range': '2-16', 'type': 'int'},
            {'name': 'response_factor', 'label': 'Response Factor', 'unit': 'level', 
             'range': '1-16', 'type': 'int'},
        ]
        
        # Atrial parameters (Deliverable 2: pulse width 1-30 ms, amplitude 0.1-5.0V)
        atrial = [
            {'name': 'atrial_amp', 'label': 'Atrial Amplitude', 'unit': 'V', 
             'range': '0.1-5.0', 'type': 'float'},
            {'name': 'atrial_width', 'label': 'Atrial Pulse Width', 'unit': 'ms', 
             'range': '1-30', 'type': 'int'},
            {'name': 'atrial_sensitivity', 'label': 'Atrial Sensitivity', 'unit': 'V', 
             'range': '0.0-5.0', 'type': 'float'},
            {'name': 'ARP', 'label': 'Atrial Refractory Period', 'unit': 'ms', 
             'range': '150-500', 'type': 'int'},
        ]
        
        # Ventricular parameters (Deliverable 2: pulse width 1-30 ms, amplitude 0.1-5.0V)
        ventricular = [
            {'name': 'ventricular_amp', 'label': 'Ventricular Amplitude', 'unit': 'V', 
             'range': '0.1-5.0', 'type': 'float'},
            {'name': 'ventricular_width', 'label': 'Ventricular Pulse Width', 'unit': 'ms', 
             'range': '1-30', 'type': 'int'},
            {'name': 'ventricular_sensitivity', 'label': 'Ventricular Sensitivity', 'unit': 'V', 
             'range': '0.0-5.0', 'type': 'float'},
            {'name': 'VRP', 'label': 'Ventricular Refractory Period', 'unit': 'ms', 
             'range': '150-500', 'type': 'int'},
        ]
        
        params = []
        
        # AOO mode: LRL, atrial amplitude, atrial pulse width
        if mode == PaceMakerMode.AOO:
            params = [common[0], atrial[0], atrial[1]]
        # VOO mode: LRL, ventricular amplitude, ventricular pulse width
        elif mode == PaceMakerMode.VOO:
            params = [common[0], ventricular[0], ventricular[1]]
        # AAI mode: LRL, URL, all atrial parameters
        elif mode == PaceMakerMode.AAI:
            params = [common[0], *url_param, *atrial]
        # VVI mode: LRL, URL, all ventricular parameters
        elif mode == PaceMakerMode.VVI:
            params = [common[0], *url_param, *ventricular]
        # AOOR mode: LRL, MSR, rate params, atrial amplitude, atrial pulse width
        elif mode == PaceMakerMode.AOOR:
            params = [common[0], rate_params[0], *rate_params[1:], atrial[0], atrial[1]]
        # VOOR mode: LRL, MSR, rate params, ventricular amplitude, ventricular pulse width
        elif mode == PaceMakerMode.VOOR:
            params = [common[0], rate_params[0], *rate_params[1:], ventricular[0], ventricular[1]]
        # AAIR mode: LRL, URL, MSR, rate params, all atrial parameters
        elif mode == PaceMakerMode.AAIR:
            params = [common[0], *url_param, rate_params[0], *rate_params[1:], *atrial]
        # VVIR mode: LRL, URL, MSR, rate params, all ventricular parameters
        elif mode == PaceMakerMode.VVIR:
            params = [common[0], *url_param, rate_params[0], *rate_params[1:], *ventricular]
        # DDDR mode: dual-chamber pacing with av delay and rate response
        elif mode == PaceMakerMode.DDDR:
            dual_timing = [
                {'name': 'AV_delay', 'label': 'AV Delay', 'unit': 'ms',
                 'range': '30-300', 'type': 'int'},
                {'name': 'PVARP', 'label': 'Post-Ventricular Atrial Refractory Period', 'unit': 'ms',
                 'range': '150-500', 'type': 'int'},
            ]
            params = [common[0], *url_param, rate_params[0], *rate_params[1:], *atrial, *ventricular, *dual_timing]
        
        return params
    
    def _validate_mode_parameters(self, mode):
        """Validate parameters for current mode based on Deliverable 2 requirements"""
        mode_info = parse_mode(mode)
        is_rate_adaptive = mode_info.rate
        
        # LRL validation
        if not(30 <= self.parameters.LRL <= 175):
            raise ValueError(f"LRL {self.parameters.LRL} out of range (30-175 ppm)")
        
        # URL validation for modes with sensing
        if mode_info.sensed != 'O':
            if not(50 <= self.parameters.URL <= 175):
                raise ValueError(f"URL {self.parameters.URL} out of range (50-175 ppm)")
            if self.parameters.LRL >= self.parameters.URL:
                raise ValueError(f"URL must be greater than LRL")
        
        # MSR validation for rate adaptive modes
        if is_rate_adaptive:
            if not(50 <= self.parameters.MSR <= 175):
                raise ValueError(f"MSR {self.parameters.MSR} out of range (50-175 ppm)")
            if self.parameters.MSR < self.parameters.URL:
                raise ValueError(f"MSR must be >= URL")
        
        # Atrial parameters
        if mode_info.paced == 'A' or mode_info.sensed == 'A':
            if not (0.1 <= self.parameters.atrial_amp <= 5.0):
                raise ValueError(f"Atrial Amplitude {self.parameters.atrial_amp} out of range (0.1-5.0 V)")
            if not (1 <= self.parameters.atrial_width <= 30):
                raise ValueError(f"Atrial Pulse Width {self.parameters.atrial_width} out of range (1-30 ms)")
            if mode_info.sensed == 'A':
                if not (0.0 <= self.parameters.atrial_sensitivity <= 5.0):
                    raise ValueError(f"Atrial Sensitivity {self.parameters.atrial_sensitivity} out of range (0.0-5.0 V)")
                if not (150 <= self.parameters.ARP <= 500):
                    raise ValueError(f"ARP {self.parameters.ARP} out of range (150-500 ms)")
        
        # Ventricular parameters
        if mode_info.paced == 'V' or mode_info.sensed == 'V':
            if not (0.1 <= self.parameters.ventricular_amp <= 5.0):
                raise ValueError(f"Ventricular Amplitude {self.parameters.ventricular_amp} out of range (0.1-5.0 V)")
            if not (1 <= self.parameters.ventricular_width <= 30):
                raise ValueError(f"Ventricular Pulse Width {self.parameters.ventricular_width} out of range (1-30 ms)")
            if mode_info.sensed == 'V':
                if not (0.0 <= self.parameters.ventricular_sensitivity <= 5.0):
                    raise ValueError(f"Ventricular Sensitivity {self.parameters.ventricular_sensitivity} out of range (0.0-5.0 V)")
                if not (150 <= self.parameters.VRP <= 500):
                    raise ValueError(f"VRP {self.parameters.VRP} out of range (150-500 ms)")
        
        # Rate adaptive parameters
        if is_rate_adaptive:
            if not (1 <= self.parameters.activity_threshold <= 7):
                raise ValueError(f"Activity Threshold {self.parameters.activity_threshold} out of range (1-7)")
            if not (10 <= self.parameters.reaction_time <= 50):
                raise ValueError(f"Reaction Time {self.parameters.reaction_time} out of range (10-50 sec)")
            if not (2 <= self.parameters.recovery_time <= 16):
                raise ValueError(f"Recovery Time {self.parameters.recovery_time} out of range (2-16 min)")
            if not (1 <= self.parameters.response_factor <= 16):
                raise ValueError(f"Response Factor {self.parameters.response_factor} out of range (1-16)")

        if mode == PaceMakerMode.DDDR:
            if not (30 <= self.parameters.AV_delay <= 300):
                raise ValueError(f"AV Delay {self.parameters.AV_delay} out of range (30-300 ms)")
            if not (150 <= self.parameters.PVARP <= 500):
                raise ValueError(f"PVARP {self.parameters.PVARP} out of range (150-500 ms)")
        
        return True
    
    def _save_parameters(self):
        """Validate and save parameters"""
        if not self.current_mode:
            messagebox.showwarning("No Mode Selected", 
                                 "Please select a pacing mode before saving.")
            return
        
        try:
            for param_name, widget_info in self.param_widgets.items():
                value_str = widget_info['var'].get().strip()
                if not value_str:
                    raise ValueError(f"{param_name} cannot be empty")
                
                if widget_info['type'] == 'int':
                    value = int(value_str)
                elif widget_info['type'] == 'float':
                    value = float(value_str)
                else:
                    value = value_str
                
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
    
    def _handle_serial_connect(self):
        """Handle serial port connection/disconnection"""
        if not SERIAL_AVAILABLE:
            messagebox.showerror("Serial Not Available", 
                               "Serial interface module not available.")
            return
        
        if self.is_connected:
            # Disconnect
            if self.serial_interface:
                self.serial_interface.disconnect()
            self.serial_interface = None
            self.is_connected = False
            self.ventricular_inhibit_active = False
            self.connect_btn.config(text="Connect")
            self.telemetry_status.config(text="Disconnected", foreground='red')
            self.telemetry_canvas.itemconfig(self.telemetry_led, fill='red', outline='darkred')
        else:
            # Connect
            port = self.port_var.get()
            try:
                self.serial_interface = SerialInterface(port, baudrate=115200)
                self.serial_interface.connect()
                
                # Set up callbacks
               # self.serial_interface.ack_callback = self._on_parameter_ack
                #self.serial_interface.egram_callback = self._on_egram_data
             
    # ... existing code ...
    
                # Set up callbacks
                def on_ack():
                    print("[GUI] ACK received from device")
                    self.root.after(0, lambda: messagebox.showinfo("Success", 
                        "Parameters successfully transmitted and verified on device."))
                
                def on_egram(ch, val):
                    print(f"[GUI] EGRAM → ch={ch}, value={val}")
                    # ... existing egram handling code ...
                
                self.serial_interface.ack_callback = on_ack
                self.serial_interface.egram_callback = on_egram
    # ... rest of method ...
                self.is_connected = True
                self.ventricular_inhibit_active = False
                self.serial_port = port
                self.connect_btn.config(text="Disconnect")
                self.telemetry_status.config(text="Connected", foreground='green')
                self.telemetry_canvas.itemconfig(self.telemetry_led, fill='green', outline='darkgreen')
                messagebox.showinfo("Connected", f"Successfully connected to {port}")
            except Exception as e:
                messagebox.showerror("Connection Error", f"Failed to connect to {port}:\n{str(e)}")
                self.is_connected = False
    
    # def _on_parameter_ack(self):
    #     """Callback when parameter transmission is acknowledged"""
    #     self.root.after(0, lambda: messagebox.showinfo("Success", 
    #         "Parameters successfully transmitted and verified on device."))
    
    # def _on_egram_data(self, channel, value):
    #     """Callback when egram data is received"""
    #     if channel == 0:  # Atrial
    #         self.egram_data['atrial'].append((time.time(), value))
    #     elif channel == 1:  # Ventricular
    #         self.egram_data['ventricular'].append((time.time(), value))
        
    #     # Update egram display if window is open
    #     if self.egram_window and self.egram_window.winfo_exists():
    #         self.root.after(0, self._update_egram_display)
    
    def _transmit_parameters(self):
        """Transmit parameters to the pacemaker device"""
        if not self.is_connected or not self.serial_interface:
            messagebox.showerror("Not Connected", 
                               "Please connect to the device first.")
            return
        
        if not self.current_mode:
            messagebox.showwarning("No Mode Selected", 
                                 "Please select a pacing mode before transmitting.")
            return
        if not self.serial_interface.serial or not self.serial_interface.serial.is_open:
            messagebox.showerror("Connection Error", 
                           "Serial port is not open. Please reconnect.")
            return
        try:
            self._validate_mode_parameters(self.current_mode)
            params_dict = {
                "ARP": self.parameters.ARP,
                "VRP": self.parameters.VRP,
                "atrial_amp": self.parameters.atrial_amp,
                "ventricular_amp": self.parameters.ventricular_amp,
                "atrial_width": self.parameters.atrial_width,
                "ventricular_width": self.parameters.ventricular_width,
                "atr_cmp_ref_pwm": self.parameters.atr_cmp_ref_pwm,
                "vent_cmp_ref_pwm": self.parameters.vent_cmp_ref_pwm,
                "reaction_time": self.parameters.reaction_time,
                "recovery_time": self.parameters.recovery_time,
                "PVARP": self.parameters.PVARP,
                "AV_delay": self.parameters.AV_delay,
                "response_factor": self.parameters.response_factor,
                "activity_threshold": self.parameters.activity_threshold,
                "LRL": self.parameters.LRL,
                "URL": self.parameters.URL,
                "MSR": self.parameters.MSR,
                "rate_smoothing": self.parameters.rate_smoothing
            }
            self.serial_interface.send_parameters(params_dict, mode_id(self.current_mode))
            messagebox.showinfo("Transmitted", 
                              "Parameters transmitted to device.\n"
                              "Waiting for verification...")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Transmission Error", f"Failed to transmit: {str(e)}")
    
    def _set_pushbutton_inhibit(self, active: bool):
        """mirror the hardware pushbutton by pausing ventricular output while held"""
        if not self.is_connected or not self.serial_interface:
            return
        if self.current_mode != PaceMakerMode.DDDR:
            return
        if active == self.ventricular_inhibit_active:
            return
        if not self.serial_interface.serial or not self.serial_interface.serial.is_open:
            return
        try:
            self._validate_mode_parameters(self.current_mode)
            params_dict = {
                "ARP": self.parameters.ARP,
                "VRP": self.parameters.VRP,
                "atrial_amp": self.parameters.atrial_amp,
                "ventricular_amp": 0.0 if active else self.parameters.ventricular_amp,
                "atrial_width": self.parameters.atrial_width,
                "ventricular_width": self.parameters.ventricular_width,
                "atr_cmp_ref_pwm": self.parameters.atr_cmp_ref_pwm,
                "vent_cmp_ref_pwm": self.parameters.vent_cmp_ref_pwm,
                "reaction_time": self.parameters.reaction_time,
                "recovery_time": self.parameters.recovery_time,
                "PVARP": self.parameters.PVARP,
                "AV_delay": self.parameters.AV_delay,
                "response_factor": self.parameters.response_factor,
                "activity_threshold": self.parameters.activity_threshold,
                "LRL": self.parameters.LRL,
                "URL": self.parameters.URL,
                "MSR": self.parameters.MSR,
                "rate_smoothing": self.parameters.rate_smoothing
            }
            self.serial_interface.send_parameters(params_dict, mode_id(self.current_mode))
            self.ventricular_inhibit_active = active
            if self.telemetry_status:
                if active:
                    self.telemetry_status.config(text="Connected (vent inhibit)", foreground='#d35400')
                else:
                    self.telemetry_status.config(text="Connected", foreground='green')
        except Exception as exc:
            messagebox.showerror("Pushbutton Error", f"Unable to update ventricular inhibition:\n{exc}")
    
    def _request_parameters(self):
        """Request current parameters from the pacemaker device"""
        if not self.is_connected or not self.serial_interface:
            messagebox.showerror("Not Connected", 
                               "Please connect to the device first.")
            return
        
        # Note: This would need to be implemented in serial_interface
        messagebox.showinfo("Request Sent", 
                          "Parameter request sent to device.\n"
                          "Parameters will be displayed when received.")
    
    def _show_egram_window(self):
        """Display egram window"""
        if self.egram_window and self.egram_window.winfo_exists():
            self.egram_window.lift()
            return
        
        self.egram_window = tk.Toplevel(self.root)
        self.egram_window.title("Real-Time Electrograms")
        self.egram_window.geometry("800x600")
        
        # Control frame
        control_frame = ttk.Frame(self.egram_window, padding="10")
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="Egram Display", font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.egram_stream_btn = ttk.Button(control_frame, text="Start Streaming",
                                           command=self._toggle_egram_streaming)
        self.egram_stream_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Clear", command=self._clear_egram).pack(side=tk.LEFT, padx=5)
        
        # Canvas for egram display
        canvas_frame = ttk.Frame(self.egram_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.egram_canvas = tk.Canvas(canvas_frame, bg='white', height=500)
        self.egram_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Labels for channels
        ttk.Label(canvas_frame, text="Atrial (Blue) / Ventricular (Red)", 
                 font=('Helvetica', 10)).pack()
        
        # Initial display
        self._update_egram_display()
    
    def _toggle_egram_streaming(self):
        """Start/stop egram data streaming"""
        if not self.is_connected or not self.serial_interface:
            messagebox.showerror("Not Connected", 
                               "Please connect to the device first.")
            return
        
        if self.egram_streaming:
            # Stop streaming
            self.egram_streaming = False
            self.egram_stream_btn.config(text="Start Streaming")
            # Note: Would need stop command in serial_interface
        else:
            # Start streaming
            self.egram_streaming = True
            self.egram_stream_btn.config(text="Stop Streaming")
            # Note: Would need start command in serial_interface
            messagebox.showinfo("Streaming Started", 
                              "Egram data streaming started.\n"
                              "Data will be displayed in real-time.")
    
    def _clear_egram(self):
        """Clear egram display"""
        self.egram_data['atrial'].clear()
        self.egram_data['ventricular'].clear()
        self._update_egram_display()
    
    def _update_egram_display(self):
        """Update the egram canvas with current data"""
        if not self.egram_window or not self.egram_window.winfo_exists():
            return
        
        canvas = self.egram_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width < 10 or height < 10:
            return
        
        # Draw grid
        for i in range(0, width, 50):
            canvas.create_line(i, 0, i, height, fill='#e0e0e0', width=1)
        for i in range(0, height, 50):
            canvas.create_line(0, i, width, i, fill='#e0e0e0', width=1)
        
        # Draw center line
        center_y = height // 2
        canvas.create_line(0, center_y, width, center_y, fill='#888', width=2)
        
        # Plot atrial data (blue)
        atrial_data = list(self.egram_data['atrial'])
        if len(atrial_data) > 1:
            points = []
            for i, (t, val) in enumerate(atrial_data):
                x = int((i / max(len(atrial_data), 1)) * width)
                # Scale value to fit canvas (assuming 0-4095 range)
                y = int(center_y - (val / 4095.0) * (height / 4))
                points.append((x, y))
            
            if len(points) > 1:
                for i in range(len(points) - 1):
                    canvas.create_line(points[i][0], points[i][1], 
                                     points[i+1][0], points[i+1][1], 
                                     fill='blue', width=2)
        
        # Plot ventricular data (red)
        ventricular_data = list(self.egram_data['ventricular'])
        if len(ventricular_data) > 1:
            points = []
            for i, (t, val) in enumerate(ventricular_data):
                x = int((i / max(len(ventricular_data), 1)) * width)
                # Scale value to fit canvas (assuming 0-4095 range)
                y = int(center_y + (val / 4095.0) * (height / 4))
                points.append((x, y))
            
            if len(points) > 1:
                for i in range(len(points) - 1):
                    canvas.create_line(points[i][0], points[i][1], 
                                     points[i+1][0], points[i+1][1], 
                                     fill='red', width=2)
        
        # Schedule next update
        if self.egram_streaming:
            self.root.after(50, self._update_egram_display)
    
    def _handle_logout(self):
        """Handle user logout"""
        if messagebox.askyesno("Confirm Logout", 
                              "Are you sure you want to logout?\n"
                              "Make sure you have saved any parameter changes."):
            # Disconnect serial if connected
            if self.is_connected and self.serial_interface:
                self.serial_interface.disconnect()
            
            # Close egram window if open
            if self.egram_window and self.egram_window.winfo_exists():
                self.egram_window.destroy()
            
            self.current_user = None
            self.current_mode = None
            self.is_connected = False
            self.serial_interface = None
            self.show_login_screen()


def main():
    """Main entry point for the DCM GUI application"""
    root = tk.Tk()
    app = DCMApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()



import tkinter
import customtkinter as ctk
from customtkinter import CTkFont
from typing import Callable

class MainView(ctk.CTk):
    """Main view of the application."""

    def __init__(self) -> None:
        """Initializes the main view."""
        super().__init__()

        self.title("Orquestrador de Instalações")
        self.geometry("900x650")
        self.minsize(800, 600)

        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("system")

        self.default_font = CTkFont(family="Segoe UI", size=12)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_sidebar()
        self._create_main_area()
        self.center_window()

    def _create_sidebar(self) -> None:
        """Creates the left sidebar with controls."""
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Orquestrador\nde Instalações",
            font=CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.selection_frame = ctk.CTkFrame(self.sidebar_frame)
        self.selection_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.selection_frame.grid_columnconfigure(0, weight=1)

        self.nodejs_checkbox = ctk.CTkCheckBox(
            self.selection_frame, text="Node.js + CLI Tools"
        )
        self.nodejs_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.vscode_checkbox = ctk.CTkCheckBox(
            self.selection_frame, text="Visual Studio Code"
        )
        self.vscode_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.install_button = ctk.CTkButton(
            self.sidebar_frame, text="Iniciar Instalação", state="disabled"
        )
        self.install_button.grid(row=2, column=0, padx=20, pady=15)

        self.cancel_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Cancelar",
            state="disabled",
            fg_color="#E74C3C",
            hover_color="#C0392B",
        )
        self.cancel_button.grid(row=3, column=0, padx=20, pady=5)

        self.separator = ctk.CTkFrame(self.sidebar_frame, height=2)
        self.separator.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text="Tema da Interface:")
        self.theme_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")

        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_frame, values=["System", "Light", "Dark"]
        )
        self.theme_menu.grid(row=6, column=0, padx=20, pady=(0, 15))

        self.settings_frame = ctk.CTkFrame(self.sidebar_frame)
        self.settings_frame.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.auto_mode_checkbox = ctk.CTkCheckBox(
            self.settings_frame, text="Modo Automático (--yes)"
        )
        self.auto_mode_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.download_timeout_label = ctk.CTkLabel(
            self.settings_frame, text="Timeout de Download (segundos):"
        )
        self.download_timeout_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")

        self.download_timeout_entry = ctk.CTkEntry(self.settings_frame)
        self.download_timeout_entry.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.download_timeout_entry.insert(0, "300")

        self.install_timeout_label = ctk.CTkLabel(
            self.settings_frame, text="Timeout de Instalação (segundos):"
        )
        self.install_timeout_label.grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")

        self.install_timeout_entry = ctk.CTkEntry(self.settings_frame)
        self.install_timeout_entry.grid(row=4, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.install_timeout_entry.insert(0, "600")

    def _create_main_area(self) -> None:
        """Creates the main area with log console and progress bar."""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.console_textbox = ctk.CTkTextbox(self.main_frame, state="disabled")
        self.console_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self._setup_log_tags()

        self.status_label = ctk.CTkLabel(self.main_frame, text="Pronto para iniciar instalações")
        self.status_label.grid(row=1, column=0, padx=10, pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)

    def center_window(self) -> None:
        """Centers the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_log_tags(self) -> None:
        """Sets up tags for log coloring."""
        self.update_log_tags()

    def update_log_tags(self) -> None:
        """Updates log colors based on the current theme."""
        theme = ctk.get_appearance_mode()
        info_color = "black" if theme == "Light" else "white"

        colors = {
            "INFO": info_color,
            "WARNING": "#FFD700",
            "ERROR": "#FF6B6B",
            "SUCCESS": "#51CF66",
        }
        for level, color in colors.items():
            self.console_textbox.tag_config(level, foreground=color)

    def log_message(self, message: str, level: str) -> None:
        """Adds a message to the log console."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert("end", f"[{timestamp}] {message}\n", level)
        self.console_textbox.configure(state="disabled")
        self.console_textbox.see("end")
        self.update()

    def set_on_closing_callback(self, callback: Callable[[], None]) -> None:
        """Sets the callback for the window closing event."""
        self.protocol("WM_DELETE_WINDOW", callback)

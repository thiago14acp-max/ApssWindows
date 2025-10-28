
import tkinter

class AppState:
    """Manages the application's state."""

    def __init__(self) -> None:
        """Initializes the application state."""
        self.installation_in_progress: bool = False
        self.cancel_requested: bool = False

        # Tool selection
        self.nodejs_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)
        self.vscode_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)

        # Settings
        self.auto_mode_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)
        self.download_timeout: str = "300"
        self.install_timeout: str = "600"

    def is_tool_selected(self) -> bool:
        """Checks if any tool is selected for installation."""
        return self.nodejs_var.get() or self.vscode_var.get()

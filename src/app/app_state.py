
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
        self.git_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)
        self.mcp_excel_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)
        self.antigravity_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)
        self.opencode_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)

        # Settings
        self.auto_mode_var: tkinter.BooleanVar = tkinter.BooleanVar(value=False)
        self.download_timeout: str = "300"
        self.install_timeout: str = "600"

    def is_tool_selected(self) -> bool:
        """Checks if any tool is selected for installation."""
        return (
            self.nodejs_var.get()
            or self.vscode_var.get()
            or self.git_var.get()
            or self.mcp_excel_var.get()
            or self.antigravity_var.get()
            or self.opencode_var.get()
        )

    def to_dict(self) -> dict:
        """Converts the state to a dictionary for serialization."""
        return {
            "nodejs": self.nodejs_var.get(),
            "vscode": self.vscode_var.get(),
            "git": self.git_var.get(),
            "mcp_excel": self.mcp_excel_var.get(),
            "antigravity": self.antigravity_var.get(),
            "opencode": self.opencode_var.get(),
            "auto_mode": self.auto_mode_var.get(),
            "download_timeout": self.download_timeout,
            "install_timeout": self.install_timeout,
        }

    def from_dict(self, data: dict) -> None:
        """Loads the state from a dictionary."""
        self.nodejs_var.set(data.get("nodejs", False))
        self.vscode_var.set(data.get("vscode", False))
        self.git_var.set(data.get("git", False))
        self.mcp_excel_var.set(data.get("mcp_excel", False))
        self.antigravity_var.set(data.get("antigravity", False))
        self.opencode_var.set(data.get("opencode", False))
        self.auto_mode_var.set(data.get("auto_mode", False))
        self.download_timeout = data.get("download_timeout", "300")
        self.install_timeout = data.get("install_timeout", "600")

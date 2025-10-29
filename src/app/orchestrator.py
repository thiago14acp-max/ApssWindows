
import tkinter.messagebox as messagebox
import threading
import queue
import customtkinter as ctk
from ..ui.main_view import MainView
from .app_state import AppState
from ..core.installation_service import InstallationService

class OrchestratorApp:
    """Orchestrator for the installation application."""

    def __init__(self, root: MainView) -> None:
        """Initializes the orchestrator."""
        self.root = root
        self.state = AppState()
        self.message_queue = queue.Queue()
        self.installation_service = InstallationService(self.message_queue)

        self._configure_ui_listeners()
        self.root.set_on_closing_callback(self._on_closing)

    def _configure_ui_listeners(self) -> None:
        """Configures listeners for UI events."""
        self.root.nodejs_checkbox.configure(variable=self.state.nodejs_var, command=self._on_checkbox_changed)
        self.root.vscode_checkbox.configure(variable=self.state.vscode_var, command=self._on_checkbox_changed)
        self.root.git_checkbox.configure(variable=self.state.git_var, command=self._on_checkbox_changed)
        self.root.mcp_excel_checkbox.configure(variable=self.state.mcp_excel_var, command=self._on_checkbox_changed)
        self.root.auto_mode_checkbox.configure(variable=self.state.auto_mode_var)

        self.root.install_button.configure(command=self.start_installation)
        self.root.cancel_button.configure(command=self.cancel_installation)
        self.root.theme_menu.configure(command=self._change_theme)

    def _on_checkbox_changed(self) -> None:
        """Handles checkbox state changes."""
        if self.state.is_tool_selected():
            self.root.install_button.configure(state="normal")
        else:
            self.root.install_button.configure(state="disabled")

    def _change_theme(self, theme_name: str) -> None:
        """Changes the application theme."""
        ctk.set_appearance_mode(theme_name.lower())
        self.root.update_log_tags()
        self.root.log_message(f"Tema alterado para: {theme_name}", "INFO")

    def _validate_settings(self) -> bool:
        """Validates the timeout settings."""
        try:
            download_timeout = int(self.root.download_timeout_entry.get())
            install_timeout = int(self.root.install_timeout_entry.get())
            if download_timeout <= 0 or install_timeout <= 0:
                self.root.log_message("Timeouts devem ser números positivos!", "ERROR")
                return False
            return True
        except ValueError:
            self.root.log_message("Timeouts devem ser números inteiros!", "ERROR")
            return False

    def start_installation(self) -> None:
        """Starts the installation process."""
        if not self._validate_settings():
            return

        self.state.installation_in_progress = True
        self._set_ui_state(installing=True)

        self.root.console_textbox.configure(state="normal")
        self.root.console_textbox.delete("1.0", "end")
        self.root.console_textbox.configure(state="disabled")

        self.installation_service.cancel_requested = False

        self.root.log_message("=== INICIANDO INSTALAÇÃO ===", "INFO")

        threading.Thread(
            target=self.installation_service.run_installations,
            args=(
                self.state.nodejs_var.get(),
                self.state.vscode_var.get(),
                self.state.git_var.get(),
                self.state.mcp_excel_var.get(),
                self.state.auto_mode_var.get(),
                int(self.root.download_timeout_entry.get()),
                int(self.root.install_timeout_entry.get()),
            ),
            daemon=True,
        ).start()

        self.root.after(100, self._process_queue)

    def cancel_installation(self) -> None:
        """Cancels the installation process."""
        self.installation_service.cancel_installation()
        self.root.cancel_button.configure(state="disabled")

    def _process_queue(self) -> None:
        """Processes messages from the installation service."""
        try:
            while True:
                message = self.message_queue.get_nowait()
                msg_type, *payload = message

                if msg_type == 'LOG':
                    self.root.log_message(payload[0], payload[1])
                elif msg_type == 'PROGRESS':
                    if self.root.progress_bar.cget("mode") == "indeterminate":
                        self.root.progress_bar.stop()
                        self.root.progress_bar.configure(mode="determinate")
                    self.root.progress_bar.set(payload[0])
                elif msg_type == 'COMPLETE':
                    self._installation_complete(*payload)
                    return
        except queue.Empty:
            pass
        except Exception as e:
            self.root.log_message(f"Erro ao processar mensagem da fila: {e}", "ERROR")

        if self.state.installation_in_progress:
            self.root.after(100, self._process_queue)

    def _installation_complete(self, success_count: int, failure_count: int) -> None:
        """Handles the completion of the installation."""
        self.state.installation_in_progress = False
        self._set_ui_state(installing=False)

        if self.root.progress_bar.cget("mode") == "indeterminate":
            self.root.progress_bar.stop()
        self.root.progress_bar.set(1.0)

        if failure_count == 0:
            self.root.log_message("=== INSTALAÇÃO CONCLUÍDA COM SUCESSO ===", "SUCCESS")
        else:
            self.root.log_message("=== INSTALAÇÃO CONCLUÍDA COM ERROS ===", "ERROR")

        self.root.status_label.configure(text=f"Concluído: {success_count} sucesso, {failure_count} falhas")
        self._on_checkbox_changed()

    def _set_ui_state(self, installing: bool) -> None:
        """Sets the UI state based on whether an installation is in progress."""
        state = "disabled" if installing else "normal"
        self.root.install_button.configure(state=state)
        self.root.nodejs_checkbox.configure(state=state)
        self.root.vscode_checkbox.configure(state=state)
        self.root.git_checkbox.configure(state=state)
        self.root.mcp_excel_checkbox.configure(state=state)
        self.root.cancel_button.configure(state="normal" if installing else "disabled")
        if installing:
            self.root.progress_bar.configure(mode="indeterminate")
            self.root.progress_bar.start()
        else:
            if self.root.progress_bar.cget("mode") == "indeterminate":
                self.root.progress_bar.stop()
            self.root.progress_bar.set(0)

    def _on_closing(self) -> None:
        """Handles the window closing event."""
        if self.state.installation_in_progress:
            if messagebox.askyesno(
                "Instalação em Andamento",
                "Deseja realmente sair e cancelar a instalação?",
                icon=messagebox.WARNING,
            ):
                self.cancel_installation()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self) -> None:
        """Runs the application."""
        self.root.mainloop()

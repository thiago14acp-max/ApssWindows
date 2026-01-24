
import os
import sys
import subprocess
import threading
from pathlib import Path
from queue import Queue
from typing import List, Optional

class InstallationService:
    """Handles the logic of running installation scripts."""

    def __init__(self, message_queue: Queue) -> None:
        """
        Initializes the InstallationService.
        Args:
            message_queue (Queue): Queue for inter-thread communication.
        """
        self.message_queue: Queue = message_queue
        self.current_process: Optional[subprocess.Popen] = None
        self.cancel_requested: bool = False

    def run_installations(
        self,
        node_selected: bool,
        vscode_selected: bool,
        antigravity_selected: bool,
        git_selected: bool,
        mcp_excel_selected: bool,
        opencode_selected: bool,
        auto_mode: bool,
        download_timeout: int,
        install_timeout: int,
    ) -> None:
        """
        Runs the installations in a separate thread.
        """
        try:
            total_steps = (
                int(node_selected)
                + int(vscode_selected)
                + int(antigravity_selected)
                + int(git_selected)
                + int(mcp_excel_selected)
                + int(opencode_selected)
            )
            completed_steps = 0
            success_count = 0
            failure_count = 0

            if total_steps == 0:
                self.message_queue.put(('LOG', "Nenhuma ferramenta selecionada para instalação", "WARNING"))
                self.message_queue.put(('COMPLETE', 0, 0))
                return

            if node_selected:
                self.message_queue.put(('LOG', "=== Instalando Node.js + CLI Tools ===", "INFO"))
                args = self._build_nodejs_args(auto_mode, download_timeout, install_timeout)
                return_code = self._run_script(args, "Node.js")

                if return_code == 0:
                    success_count += 1
                    self.message_queue.put(('LOG', "Node.js instalado com sucesso!", "SUCCESS"))
                else:
                    failure_count += 1
                    self.message_queue.put(('LOG', f"Falha na instalação do Node.js (código: {return_code})", "ERROR"))

                completed_steps += 1
                self.message_queue.put(('PROGRESS', completed_steps / total_steps))

                if self.cancel_requested:
                    self.message_queue.put(('LOG', "Instalação cancelada pelo usuário", "WARNING"))
                    self.message_queue.put(('COMPLETE', success_count, failure_count))
                    return

            if vscode_selected:
                self.message_queue.put(('LOG', "=== Instalando Visual Studio Code ===", "INFO"))
                args = self._build_vscode_args()
                return_code = self._run_script(args, "VS Code")

                if return_code == 0:
                    success_count += 1
                    self.message_queue.put(('LOG', "Visual Studio Code instalado com sucesso!", "SUCCESS"))
                else:
                    failure_count += 1
                    self.message_queue.put(('LOG', f"Falha na instalação do VS Code (código: {return_code})", "ERROR"))

                completed_steps += 1
                self.message_queue.put(('PROGRESS', completed_steps / total_steps))

                if self.cancel_requested:
                    self.message_queue.put(('LOG', "Instalação cancelada pelo usuário", "WARNING"))
                    self.message_queue.put(('COMPLETE', success_count, failure_count))
                    return


            if antigravity_selected:
                self.message_queue.put(('LOG', "=== Instalando Antigravity IDE ===", "INFO"))
                args = self._build_antigravity_args()
                return_code = self._run_script(args, "Antigravity IDE")

                if return_code == 0:
                    success_count += 1
                    self.message_queue.put(('LOG', "Antigravity IDE instalado com sucesso!", "SUCCESS"))
                else:
                    failure_count += 1
                    self.message_queue.put(('LOG', f"Falha na instalação do Antigravity IDE (código: {return_code})", "ERROR"))

                completed_steps += 1
                self.message_queue.put(('PROGRESS', completed_steps / total_steps))

                if self.cancel_requested:
                    self.message_queue.put(('LOG', "Instalação cancelada pelo usuário", "WARNING"))
                    self.message_queue.put(('COMPLETE', success_count, failure_count))
                    return

            if git_selected:
                self.message_queue.put(('LOG', "=== Instalando Git for Windows ===", "INFO"))
                args = self._build_git_args()
                return_code = self._run_script(args, "Git")

                if return_code == 0:
                    success_count += 1
                    self.message_queue.put(('LOG', "Git instalado com sucesso!", "SUCCESS"))
                else:
                    failure_count += 1
                    self.message_queue.put(('LOG', f"Falha na instalação do Git (código: {return_code})", "ERROR"))

                completed_steps += 1
                self.message_queue.put(('PROGRESS', completed_steps / total_steps))

                if self.cancel_requested:
                    self.message_queue.put(('LOG', "Instalação cancelada pelo usuário", "WARNING"))
                    self.message_queue.put(('COMPLETE', success_count, failure_count))
                    return

            if mcp_excel_selected:
                self.message_queue.put(('LOG', "=== Instalando MCP Excel Server ===", "INFO"))
                args = self._build_mcp_excel_args()
                return_code = self._run_script(args, "MCP Excel Server")

                if return_code == 0:
                    success_count += 1
                    self.message_queue.put(('LOG', "MCP Excel Server instalado com sucesso!", "SUCCESS"))
                else:
                    failure_count += 1
                    self.message_queue.put(('LOG', f"Falha na instalação do MCP Excel Server (código: {return_code})", "ERROR"))

                completed_steps += 1
                self.message_queue.put(('PROGRESS', completed_steps / total_steps))

                if self.cancel_requested:
                    self.message_queue.put(('LOG', "Instalação cancelada pelo usuário", "WARNING"))
                    self.message_queue.put(('COMPLETE', success_count, failure_count))
                    return

            if opencode_selected:
                self.message_queue.put(('LOG', "=== Instalando OpenCode CLI (Bun) ===", "INFO"))
                args = self._build_opencode_args()
                return_code = self._run_script(args, "OpenCode CLI")

                if return_code == 0:
                    success_count += 1
                    self.message_queue.put(('LOG', "OpenCode CLI instalado com sucesso!", "SUCCESS"))
                else:
                    failure_count += 1
                    self.message_queue.put(('LOG', f"Falha na instalação do OpenCode CLI (código: {return_code})", "ERROR"))

                completed_steps += 1
                self.message_queue.put(('PROGRESS', completed_steps / total_steps))

                if self.cancel_requested:
                    self.message_queue.put(('LOG', "Instalação cancelada pelo usuário", "WARNING"))
                    self.message_queue.put(('COMPLETE', success_count, failure_count))
                    return

            self.message_queue.put(('COMPLETE', success_count, failure_count))

        except Exception as e:
            self.message_queue.put(('LOG', f"Erro inesperado durante instalação: {str(e)}", "ERROR"))
            self.message_queue.put(('COMPLETE', 0, 1))

    def _run_script(self, args: List[str], tool_name: str) -> int:
        """
        Executes a script in a subprocess and captures its output.
        """
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"

            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            self.current_process = process

            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        line = line.strip()
                        if line:
                            self.message_queue.put(('LOG', line, 'INFO'))

                    if self.cancel_requested:
                        process.terminate()
                        try:
                            process.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        self.message_queue.put(('LOG', f"Instalação do {tool_name} cancelada", "WARNING"))
                        break

            return_code = process.wait()
            self.current_process = None
            return return_code

        except FileNotFoundError:
            self.message_queue.put(('LOG', f"Script não encontrado: {args[0]}", "ERROR"))
            return 1
        except subprocess.SubprocessError as e:
            self.message_queue.put(('LOG', f"Erro ao executar script do {tool_name}: {str(e)}", "ERROR"))
            return 1
        except Exception as e:
            self.message_queue.put(('LOG', f"Erro inesperado ao executar {tool_name}: {str(e)}", "ERROR"))
            return 1
        finally:
            self.current_process = None

    def cancel_installation(self) -> None:
        """Cancels the currently running installation."""
        self.cancel_requested = True
        self.message_queue.put(('LOG', "Cancelamento solicitado...", "WARNING"))

        if self.current_process:
            try:
                self.current_process.terminate()
                import time
                time.sleep(0.1)
                if self.current_process.poll() is None:
                    self.current_process.kill()
                    self.message_queue.put(('LOG', "Processo de instalação forçado a terminar", "WARNING"))
            except Exception as e:
                self.message_queue.put(('LOG', f"Erro ao tentar cancelar processo: {str(e)}", "ERROR"))

    def _get_base_path(self) -> Path:
        """Gets the base path of the application."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).parent.parent.parent

    def _build_nodejs_args(
        self, auto_mode: bool, download_timeout: int, install_timeout: int
    ) -> List[str]:
        """Builds the arguments for the Node.js installation script."""
        base_path = self._get_base_path()
        script_path = base_path / "nodeecli" / "install_nodejs_refactored.py"

        if getattr(sys, 'frozen', False):
            args = [str(base_path / 'install_nodejs.exe')]
        else:
            args = [sys.executable, str(script_path)]

        if auto_mode:
            args.append("--yes")

        args.append("--verbose")
        args.extend([
            f"--download-timeout={download_timeout}",
            f"--install-timeout={install_timeout}",
        ])
        return args

    def _build_vscode_args(self) -> List[str]:
        """Builds the arguments for the VS Code installation script."""
        base_path = self._get_base_path()
        script_path = base_path / "vscode" / "vscode_installer.py"

        if getattr(sys, 'frozen', False):
            return [str(base_path / 'vscode_installer.exe')]
        return [sys.executable, str(script_path)]

    def _build_antigravity_args(self) -> List[str]:
        """Builds the arguments for the Antigravity IDE installation script."""
        base_path = self._get_base_path()
        script_path = base_path / "antigravity" / "installer.py"

        if getattr(sys, 'frozen', False):
            return [str(base_path / 'antigravity_installer.exe')]
        return [sys.executable, str(script_path)]

    def _build_git_args(self) -> List[str]:
        """Builds the arguments for the Git installation script."""
        base_path = self._get_base_path()
        script_path = base_path / "git" / "git_installer.py"

        if getattr(sys, 'frozen', False):
            # Quando empacotado, o exe do Git fica em dist\git_installer\git_installer.exe
            return [str(base_path.parent / 'git_installer' / 'git_installer.exe')]
        return [sys.executable, str(script_path)]

    def _build_mcp_excel_args(self) -> List[str]:
        """Builds the arguments for the MCP Excel Server installation script."""
        base_path = self._get_base_path()
        script_path = base_path / "mcp_excel" / "mcp_excel_installer.py"

        if getattr(sys, 'frozen', False):
            return [str(base_path / 'mcp_excel_installer.exe')]
        return [sys.executable, str(script_path)]

    def _build_opencode_args(self) -> List[str]:
        """Builds the arguments for the OpenCode CLI (Bun) installation script."""
        base_path = self._get_base_path()
        script_path = base_path / "opencode" / "installer.py"

        if getattr(sys, 'frozen', False):
            return [str(base_path / 'opencode_installer.exe')]
        return [sys.executable, str(script_path)]

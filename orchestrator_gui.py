#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orquestrador de Instalações - Interface Gráfica
GUI para gerenciar a instalação de ferramentas de desenvolvimento como Node.js e Visual Studio Code.
"""

import os
import sys
import tkinter
from pathlib import Path
from datetime import datetime
import ctypes
import threading
import subprocess
import queue

# Importar CustomTkinter
try:
    import customtkinter as ctk
    from customtkinter import CTkFont
except ImportError:
    print("Erro: CustomTkinter não está instalado. Execute 'pip install customtkinter' para instalar.")
    sys.exit(1)

# Configuração de caminhos para os scripts de instalação
NODEJS_SCRIPT_PATH = Path(__file__).parent / "nodeecli" / "install_nodejs.py"
VSCODE_SCRIPT_PATH = Path(__file__).parent / "vscode" / "vscode_installer.py"


class OrchestratorApp(ctk.CTk):
    """Classe principal da aplicação Orquestrador de Instalações."""
    
    def __init__(self):
        """Inicializa a aplicação GUI."""
        super().__init__()
        
        # Configuração de High-DPI para Windows
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass  # Não é Windows ou ocorreu um erro, continuar sem High-DPI
        
        # Configurações da janela principal
        self.title("Orquestrador de Instalações")
        self.geometry("900x650")
        self.minsize(800, 600)
        
        # Configurações de tema e fonte
        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("system")  # System, Light, Dark
        
        # Fonte padrão para Windows 10/11
        self.default_font = CTkFont(family="Segoe UI", size=12)
        
        # Estado da aplicação
        self.installation_in_progress = False
        
        # Variáveis para controle de instalação em thread
        self.installation_thread = None
        self.message_queue = queue.Queue()
        self.cancel_requested = False
        self.current_process = None
        
        # Configurar a interface
        self.setup_ui()
        self.center_window()
        
        # Configurar evento de fechamento
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Configura o layout principal da interface com duas colunas."""
        # Configurar o grid principal
        self.grid_columnconfigure(1, weight=1)  # Área principal expansível
        self.grid_rowconfigure(0, weight=1)     # Área principal expansível
        
        # Criar sidebar esquerda
        self.create_sidebar()
        
        # Criar área principal
        self.create_main_area()
    
    def create_sidebar(self):
        """Cria a barra lateral esquerda com controles."""
        # Frame da sidebar (coluna 0)
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Logo/Título da aplicação
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Orquestrador\nde Instalações", 
            font=CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Frame de seleção de ferramentas
        self.selection_frame = ctk.CTkFrame(self.sidebar_frame)
        self.selection_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.selection_frame.grid_columnconfigure(0, weight=1)
        
        # Checkbox para Node.js
        self.nodejs_var = tkinter.BooleanVar(value=False)
        self.nodejs_checkbox = ctk.CTkCheckBox(
            self.selection_frame,
            text="Node.js + CLI Tools",
            variable=self.nodejs_var,
            command=self.on_checkbox_changed
        )
        self.nodejs_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Checkbox para VSCode
        self.vscode_var = tkinter.BooleanVar(value=False)
        self.vscode_checkbox = ctk.CTkCheckBox(
            self.selection_frame,
            text="Visual Studio Code",
            variable=self.vscode_var,
            command=self.on_checkbox_changed
        )
        self.vscode_checkbox.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Botão de instalação
        self.install_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Iniciar Instalação",
            command=self.start_installation,
            state="disabled"
        )
        self.install_button.grid(row=2, column=0, padx=20, pady=15)
        
        # Botão de cancelamento
        self.cancel_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Cancelar",
            command=self.cancel_installation,
            state="disabled",
            fg_color="#E74C3C",  # Cor vermelha para destacar
            hover_color="#C0392B"
        )
        self.cancel_button.grid(row=3, column=0, padx=20, pady=5)
        
        # Separador visual
        self.separator = ctk.CTkFrame(self.sidebar_frame, height=2)
        self.separator.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        # Configurações de tema
        self.theme_label = ctk.CTkLabel(self.sidebar_frame, text="Tema da Interface:")
        self.theme_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["System", "Light", "Dark"],
            command=self.change_theme
        )
        self.theme_menu.grid(row=6, column=0, padx=20, pady=(0, 15))
        
        # Frame de configurações expansível
        self.settings_frame = ctk.CTkFrame(self.sidebar_frame)
        self.settings_frame.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure(0, weight=1)
        
        # Checkbox de modo automático
        self.auto_mode_var = tkinter.BooleanVar(value=False)
        self.auto_mode_checkbox = ctk.CTkCheckBox(
            self.settings_frame,
            text="Modo Automático (--yes)",
            variable=self.auto_mode_var
        )
        self.auto_mode_checkbox.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Timeout de download
        self.download_timeout_label = ctk.CTkLabel(
            self.settings_frame, 
            text="Timeout de Download (segundos):"
        )
        self.download_timeout_label.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")
        
        self.download_timeout_entry = ctk.CTkEntry(self.settings_frame)
        self.download_timeout_entry.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.download_timeout_entry.insert(0, "300")
        
        # Timeout de instalação
        self.install_timeout_label = ctk.CTkLabel(
            self.settings_frame, 
            text="Timeout de Instalação (segundos):"
        )
        self.install_timeout_label.grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")
        
        self.install_timeout_entry = ctk.CTkEntry(self.settings_frame)
        self.install_timeout_entry.grid(row=4, column=0, padx=10, pady=(0, 5), sticky="ew")
        self.install_timeout_entry.insert(0, "600")
    
    def create_main_area(self):
        """Cria a área principal com console de logs e barra de progresso."""
        # Frame da área principal (coluna 1)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)  # Console expansível
        
        # Console de logs
        self.console_textbox = ctk.CTkTextbox(self.main_frame)
        self.console_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.console_textbox.configure(state="disabled")
        
        # Configurar tags para colorização de logs
        self.setup_log_tags()
        
        # Status textual
        self.status_label = ctk.CTkLabel(self.main_frame, text="Pronto para iniciar instalações")
        self.status_label.grid(row=1, column=0, padx=10, pady=(0, 5))
        
        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
    
    def center_window(self):
        """Centraliza a janela na tela."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def change_theme(self, theme_name):
        """Altera o tema da interface."""
        ctk.set_appearance_mode(theme_name.lower())
        self.log_message(f"Tema alterado para: {theme_name}")
    
    def on_checkbox_changed(self):
        """Habilita/desabilita o botão de instalação baseado nas seleções."""
        if self.nodejs_var.get() or self.vscode_var.get():
            self.install_button.configure(state="normal")
        else:
            self.install_button.configure(state="disabled")
    
    def setup_log_tags(self):
        """Configura as tags para colorização de logs no console."""
        # Cores para diferentes níveis de log
        colors = {
            "INFO": "#FFFFFF",      # Branco
            "WARNING": "#FFD700",   # Amarelo dourado
            "ERROR": "#FF6B6B",     # Vermelho claro
            "SUCCESS": "#51CF66"    # Verde claro
        }
        
        # Configurar tags para cada nível de log
        for level, color in colors.items():
            self.console_textbox.tag_config(level, foreground=color)
    
    def log_message(self, message, level="INFO"):
        """
        Adiciona mensagens ao console com timestamp e cor baseada no nível.
        Garante thread-safety verificando se está sendo chamado da thread principal.
        """
        # Verificar se está sendo chamado de uma thread secundária
        if threading.current_thread() != threading.main_thread():
            # Se estiver em uma thread secundária, colocar mensagem na fila
            self.message_queue.put(('LOG', message, level))
            return
        
        # Se estiver na thread principal, processar diretamente
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Habilitar o textbox para inserção
        self.console_textbox.configure(state="normal")
        
        # Inserir mensagem com timestamp
        self.console_textbox.insert("end", f"[{timestamp}] {message}\n", level)
        
        # Desabilitar o textbox novamente
        self.console_textbox.configure(state="disabled")
        
        # Auto-scroll para o final
        self.console_textbox.see("end")
        
        # Atualizar a interface
        self.update()
    
    def validate_settings(self):
        """Valida as configurações de timeout."""
        try:
            download_timeout = int(self.download_timeout_entry.get())
            install_timeout = int(self.install_timeout_entry.get())
            
            if download_timeout <= 0 or install_timeout <= 0:
                self.log_message("Timeouts devem ser números positivos!", "ERROR")
                return False
                
            return True
        except ValueError:
            self.log_message("Timeouts devem ser números inteiros!", "ERROR")
            return False
    
    def start_installation(self):
        """Inicia o processo de instalação com subprocessos em thread separada."""
        # Validar configurações
        if not self.validate_settings():
            return
        
        # Capturar estados dos checkboxes na thread principal
        node_selected = self.nodejs_var.get()
        vscode_selected = self.vscode_var.get()
        
        # Verificar o que foi selecionado
        selected_tools = []
        if node_selected:
            selected_tools.append("Node.js + CLI Tools")
        if vscode_selected:
            selected_tools.append("Visual Studio Code")
        
        # Desabilitar controles durante a instalação
        self.installation_in_progress = True
        self.install_button.configure(state="disabled")
        self.nodejs_checkbox.configure(state="disabled")
        self.vscode_checkbox.configure(state="disabled")
        self.cancel_button.configure(state="normal")  # Habilitar botão de cancelar
        
        # Iniciar barra de progresso indeterminada
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Limpar console antes de iniciar
        self.console_textbox.configure(state="normal")
        self.console_textbox.delete("1.0", "end")
        self.console_textbox.configure(state="disabled")
        
        # Resetar flag de cancelamento
        self.cancel_requested = False
        
        # Log das seleções
        self.log_message("=== INICIANDO INSTALAÇÃO ===", "INFO")
        self.log_message(f"Ferramentas selecionadas: {', '.join(selected_tools)}", "INFO")
        
        if self.auto_mode_var.get():
            self.log_message("Modo automático ativado (--yes)", "INFO")
        
        self.log_message("Preparando instalação...", "INFO")
        
        # Preparar argumentos para os scripts
        if getattr(sys, 'frozen', False):
            # Se estiver executando como executável standalone
            # Obter o diretório do executável atual
            app_dir = os.path.dirname(sys.executable)
            nodejs_args = [os.path.join(app_dir, 'install_nodejs.exe')]
            vscode_args = [os.path.join(app_dir, 'vscode_installer.exe')]
        else:
            # Se estiver executando como script Python
            nodejs_args = [sys.executable, str(NODEJS_SCRIPT_PATH)]
            vscode_args = [sys.executable, str(VSCODE_SCRIPT_PATH)]
        
        # Adicionar argumentos específicos do Node.js
        if self.auto_mode_var.get():
            nodejs_args.append("--yes")
        
        # Adicionar argumentos de verbose e timeout
        nodejs_args.append("--verbose")
        
        try:
            download_timeout = int(self.download_timeout_entry.get())
            install_timeout = int(self.install_timeout_entry.get())
            nodejs_args.extend([f"--download-timeout={download_timeout}", f"--install-timeout={install_timeout}"])
        except ValueError:
            self.log_message("Valores de timeout inválidos, usando padrões", "WARNING")
            nodejs_args.extend(["--download-timeout=300", "--install-timeout=600"])
        
        # Iniciar thread para instalação com os booleanos capturados
        self.installation_thread = threading.Thread(
            target=self.run_installations,
            args=(nodejs_args, vscode_args, node_selected, vscode_selected),
            daemon=True
        )
        self.installation_thread.start()
        
        # Iniciar processamento da fila de mensagens
        self.after(100, self.process_queue)
    
    def run_installations(self, nodejs_args, vscode_args, node_selected: bool, vscode_selected: bool):
        """
        Executa as instalações em uma thread separada.
        
        Args:
            nodejs_args (list): Argumentos para o script de instalação do Node.js
            vscode_args (list): Argumentos para o script de instalação do VS Code
            node_selected (bool): Indica se Node.js foi selecionado para instalação
            vscode_selected (bool): Indica se VS Code foi selecionado para instalação
        """
        try:
            # Inicializar contadores
            total_steps = int(node_selected) + int(vscode_selected)
            completed_steps = 0
            success_count = 0
            failure_count = 0
            
            # Verificar se há alguma instalação a ser feita
            if total_steps == 0:
                self.message_queue.put(('LOG', "Nenhuma ferramenta selecionada para instalação", "WARNING"))
                self.message_queue.put(('COMPLETE', 0, 0))
                return
            
            # Instalar Node.js se selecionado
            if node_selected:
                self.message_queue.put(('LOG', "=== Instalando Node.js + CLI Tools ===", "INFO"))
                return_code = self.run_script(nodejs_args, "Node.js")
                
                if return_code == 0:
                    success_count += 1
                    self.message_queue.put(('LOG', "Node.js instalado com sucesso!", "SUCCESS"))
                else:
                    failure_count += 1
                    self.message_queue.put(('LOG', f"Falha na instalação do Node.js (código: {return_code})", "ERROR"))
                
                completed_steps += 1
                self.message_queue.put(('PROGRESS', completed_steps / total_steps))
                
                # Verificar se foi solicitado cancelamento
                if self.cancel_requested:
                    self.message_queue.put(('LOG', "Instalação cancelada pelo usuário", "WARNING"))
                    self.message_queue.put(('COMPLETE', success_count, failure_count))
                    return
            
            # Instalar VS Code se selecionado
            if vscode_selected:
                self.message_queue.put(('LOG', "=== Instalando Visual Studio Code ===", "INFO"))
                return_code = self.run_script(vscode_args, "VS Code")
                
                if return_code == 0:
                    success_count += 1
                    self.message_queue.put(('LOG', "Visual Studio Code instalado com sucesso!", "SUCCESS"))
                else:
                    failure_count += 1
                    self.message_queue.put(('LOG', f"Falha na instalação do VS Code (código: {return_code})", "ERROR"))
                
                completed_steps += 1
                self.message_queue.put(('PROGRESS', completed_steps / total_steps))
                
                # Verificar se foi solicitado cancelamento
                if self.cancel_requested:
                    self.message_queue.put(('LOG', "Instalação cancelada pelo usuário", "WARNING"))
                    self.message_queue.put(('COMPLETE', success_count, failure_count))
                    return
            
            # Enviar mensagem de conclusão
            self.message_queue.put(('COMPLETE', success_count, failure_count))
            
        except Exception as e:
            self.message_queue.put(('LOG', f"Erro inesperado durante instalação: {str(e)}", "ERROR"))
            self.message_queue.put(('COMPLETE', 0, 1))
    
    def run_script(self, args, tool_name):
        """
        Executa um script em subprocesso e captura sua saída.
        
        Args:
            args (list): Argumentos para executar o script
            tool_name (str): Nome da ferramenta sendo instalada (para logs)
            
        Returns:
            int: Código de retorno do processo (0 para sucesso)
        """
        try:
            # Configurar ambiente com PYTHONUNBUFFERED para logs em tempo real
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            # Executar o subprocesso com codificação UTF-8
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW  # Windows específico para esconder console
            )
            
            # Armazenar referência ao processo para possível cancelamento
            self.current_process = process
            
            # Ler saída linha por linha
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        line = line.strip()
                        if line:
                            self.message_queue.put(('LOG', line, 'INFO'))
                    
                    # Verificar se foi solicitado cancelamento
                    if self.cancel_requested:
                        process.terminate()
                        try:
                            process.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        self.message_queue.put(('LOG', f"Instalação do {tool_name} cancelada", "WARNING"))
                        break
            
            # Esperar o processo completar
            return_code = process.wait()
            
            # Limpar referência ao processo
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
            # Garantir que a referência ao processo seja limpa
            self.current_process = None
    
    def process_queue(self):
        """
        Processa mensagens da fila de comunicação entre threads.
        Este método é executado na thread principal da GUI.
        """
        try:
            # Processar todas as mensagens disponíveis na fila
            while True:
                try:
                    message = self.message_queue.get_nowait()
                    message_type = message[0]
                    
                    if message_type == 'LOG':
                        # Formato: ('LOG', message, level)
                        _, log_message, level = message
                        self.log_message(log_message, level)
                    
                    elif message_type == 'PROGRESS':
                        # Formato: ('PROGRESS', value)
                        _, value = message
                        # Mudar para modo determinado se ainda estiver indeterminado
                        if self.progress_bar.cget("mode") == "indeterminate":
                            self.progress_bar.stop()
                            self.progress_bar.configure(mode="determinate")
                        self.progress_bar.set(value)
                    
                    elif message_type == 'COMPLETE':
                        # Formato: ('COMPLETE', success_count, failure_count)
                        _, success_count, failure_count = message
                        self.installation_complete(success_count, failure_count)
                        # Parar de processar a fila após a conclusão
                        return
                
                except queue.Empty:
                    break
        
        except Exception as e:
            # Em caso de erro no processamento da fila, logar e continuar
            try:
                self.log_message(f"Erro ao processar mensagem da fila: {str(e)}", "ERROR")
            except:
                # Se até mesmo o log falhar, apenas ignorar
                pass
        
        # Se a instalação ainda está em progresso, continuar processando a fila
        if self.installation_in_progress:
            self.after(100, self.process_queue)
    
    def cancel_installation(self):
        """Cancela o processo de instalação em andamento."""
        # Definir flag de cancelamento
        self.cancel_requested = True
        
        # Log de cancelamento
        self.log_message("Cancelamento solicitado...", "WARNING")
        
        # Tentar terminar o processo atual se existir
        if self.current_process is not None:
            try:
                self.current_process.terminate()
                # Dar um tempo para o processo terminar gracefulmente
                import time
                time.sleep(0.1)
                
                # Se ainda estiver ativo, forçar terminação
                if self.current_process.poll() is None:
                    self.current_process.kill()
                    self.log_message("Processo de instalação forçado a terminar", "WARNING")
            except Exception as e:
                self.log_message(f"Erro ao tentar cancelar processo: {str(e)}", "ERROR")
        
        # Desabilitar botão de cancelar
        self.cancel_button.configure(state="disabled")
    
    def installation_complete(self, success_count, failure_count):
        """
        Chamado quando a instalação é concluída (com sucesso ou erro).
        
        Args:
            success_count (int): Número de instalações bem-sucedidas
            failure_count (int): Número de instalações com falha
        """
        # Parar e resetar barra de progresso
        if self.progress_bar.cget("mode") == "indeterminate":
            self.progress_bar.stop()
        self.progress_bar.set(1.0)
        
        # Log de conclusão
        if failure_count == 0:
            self.log_message("=== INSTALAÇÃO CONCLUÍDA COM SUCESSO ===", "SUCCESS")
        else:
            self.log_message("=== INSTALAÇÃO CONCLUÍDA COM ERROS ===", "ERROR")
        
        # Estatísticas finais
        self.log_message(f"Estatísticas: {success_count} sucesso(s), {failure_count} falha(s)", "INFO")
        
        # Atualizar label de status
        self.status_label.configure(text=f"Concluído: {success_count} sucesso, {failure_count} falhas")
        
        # Reabilitar controles
        self.installation_in_progress = False
        self.nodejs_checkbox.configure(state="normal")
        self.vscode_checkbox.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        
        # Verificar estado dos checkboxes para habilitar/desabilitar botão de instalação
        self.on_checkbox_changed()
    
    def on_closing(self):
        """Handler para o evento de fechamento da janela."""
        if self.installation_in_progress:
            # Mostrar diálogo de confirmação
            import tkinter.messagebox as messagebox
            
            response = messagebox.askyesno(
                "Instalação em Andamento",
                "Uma instalação está em andamento. Deseja realmente sair?\n\n"
                "Isso cancelará a instalação atual.",
                icon=messagebox.WARNING
            )
            
            if response:
                # Usuário confirmou que deseja sair
                self.cancel_installation()
                
                # Aguardar um pouco para a thread de instalação terminar
                if self.installation_thread and self.installation_thread.is_alive():
                    self.installation_thread.join(timeout=1.0)
                
                # Destruir a janela
                self.destroy()
            # Se não confirmou, não faz nada (continua aberto)
        else:
            # Sem instalação em andamento, pode fechar normalmente
            self.destroy()


def main():
    """Ponto de entrada da aplicação."""
    app = OrchestratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
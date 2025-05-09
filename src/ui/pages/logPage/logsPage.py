from ui.pages.objects.pageObjects import *
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
import os


class LogReaderThread(QThread):
    logs_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    def __init__(self, filtro="", nivel="Todos", data_ini="", data_fim="", sistema="Todos", prioridade = "Todos"):
        super().__init__()
        self.filtro = filtro
        self.nivel = nivel
        self.data_ini = data_ini
        self.data_fim = data_fim
        self.sistema = sistema
        self.prioridade = prioridade
        self._is_running = True

    

    def run(self):
        log_path = "src/data/temp/simulator.logs"
        if not os.path.exists(log_path):
            self.error_occurred.emit("Arquivo de log não encontrado.")
            return

        linhas_filtradas = []
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for linha in f:
                    if not self._is_running:
                        break

                    try:
                        if not linha.startswith("["):
                            continue

                        # Extrai partes do log
                        parts = linha.split("]")
                        data_str = parts[0][1:]
                        restante = parts[1].strip()
                        
                        # Filtro por data
                        log_dt = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
                        
                        if self.data_ini:
                            dt_ini = datetime.strptime(self.data_ini, "%d/%m/%Y")
                            if log_dt.date() < dt_ini.date():
                                continue

                        if self.data_fim:
                            dt_fim = datetime.strptime(self.data_fim, "%d/%m/%Y")
                            if log_dt.date() > dt_fim.date():
                                continue

                        # Filtro por nível - VERSÃO CORRIGIDA
                        if self.nivel != "Todos":
                            # Verifica tanto [TYPE] quanto TYPE (com espaço antes e depois)
                            if (f" [{self.nivel}] " not in linha and 
                                f" {self.nivel} " not in linha):
                                continue
                        
                        # Filtro por sistema - VERSÃO CORRIGIDA
                        if self.sistema != "Todos":
                            if f"[{self.sistema}]" not in linha:
                                continue
                        
                        if self.prioridade != "Todos":
                            if f"({self.prioridade})" not in linha:
                                continue

                        # Filtro por texto
                        if self.filtro and self.filtro not in linha.lower():
                            continue

                        linhas_filtradas.append(linha.strip())
                    except Exception:
                        continue

        except Exception as e:
            self.error_occurred.emit(f"Erro ao ler os logs: {e}")
            return

        if linhas_filtradas:
            self.logs_ready.emit("\n".join(linhas_filtradas))
        else:
            self.logs_ready.emit("Nenhum log encontrado com os critérios informados.")

    def stop(self):
        self._is_running = False
        self.quit()
        self.wait()


class LogPage(BasicPage):
    def __init__(self,log_manager: LogManager = None):
        super().__init__("Logs", QIcon("src/assets/simulation.png"),log_manager)
        self.setObjectName("LogPage")
        self.log_reader_thread = None
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_logs)
        
        self.init_ui()
        self.refresh_logs()  # Carrega os logs imediatamente
        self.refresh_timer.start(5000)  # Atualiza a cada 5 segundos

        # Testando sistema de logs 
        self.log(LogType.INFO, LogPriority.HIGH,system=LogSystem.APP, message= "Página de Logs carregada com sucesso.")
    
    def init_ui(self):
        # Explanation section
        explanation_label = QLabel(
            "Visualize e filtre os logs do sistema em tempo real. Utilize os filtros avançados para encontrar eventos específicos."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("""
            font-size: 15px;
            margin-bottom: 18px;
            color: #444;
            background: #f8f8f8;
            border-radius: 8px;
            padding: 12px 20px;
        """)
        explanation_label.setFixedHeight(80)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Main container
        main_container = QWidget()
        main_container.setObjectName("logMainContainer")
        main_container.setStyleSheet("""
            #logMainContainer {
                background: #f4f4f7;
                border: 1.5px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QComboBox {
                selection-background-color: #e0ffe0;
                selection-color: #006400;
            }
            QSpinBox, QDoubleSpinBox {
                qproperty-buttonSymbols: UpDownArrows;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(36)

        # Terminal/logs area
        terminal_group = QGroupBox("Terminal de Logs")
        terminal_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px; font-weight: bold; color: #228B22;
            }
            QGroupBox::title {
                subcontrol-origin: content;
                subcontrol-position: top left;
                left: 10px;
                top: 4px;
                padding: 0 8px;
                background: transparent;
            }
            QWidget { background: #181818; border-radius: 10px; }
        """)
        terminal_layout = QVBoxLayout()
        terminal_layout.setContentsMargins(12, 30, 12, 12)
        terminal_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        terminal_layout.setSpacing(10)

        self.terminal_widget = QTextEdit()
        self.terminal_widget.setReadOnly(True)
        self.terminal_widget.setStyleSheet("""
            background-color: #181818;
            color: #e0e0e0;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            border-radius: 8px;
            padding: 12px;
        """)
        self.terminal_widget.setMinimumWidth(420)
        self.terminal_widget.setMinimumHeight(320)
        self.terminal_widget.setPlainText("Carregando logs do sistema...")
        terminal_layout.addWidget(self.terminal_widget)

        # Botão para limpar a exibição
        clear_button = QPushButton("Limpar Exibição")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #8B0000;
                color: white;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #A52A2A;
            }
        """)
        clear_button.clicked.connect(self.clear_display)
        terminal_layout.addWidget(clear_button, alignment=Qt.AlignmentFlag.AlignRight)

        terminal_group.setLayout(terminal_layout)
        main_layout.addWidget(terminal_group, stretch=2)

        # Filtros avançados
        filter_group = QGroupBox("Filtros Avançados")
        filter_group.setStyleSheet("""
            QGroupBox {
                font-size: 15px; font-weight: bold; color: #228B22;
            }
            QGroupBox::title {
                subcontrol-origin: content;
                subcontrol-position: top left;
                left: 10px;
                top: 4px;
                padding: 0 8px;
                background: transparent;
            }
            QWidget { background: #f8f8fa; border-radius: 10px; }
        """)
        filter_layout = QFormLayout()
        filter_layout.setContentsMargins(12, 40, 12, 12)
        filter_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        filter_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        filter_layout.setSpacing(20)

        # Filtro por texto
        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Palavra-chave ou expressão")
        self.filtro_input.setFixedWidth(180)
        filter_layout.addRow("Filtro de Texto:", self.filtro_input)

        # Filtro por nível
        self.nivel_input = QComboBox()
        self.nivel_input.addItems(["Todos", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.nivel_input.setFixedWidth(120)
        filter_layout.addRow("Nível de Log:", self.nivel_input)

        # Filtro por sistema
        self.sistema_input = QComboBox()    
        self.sistema_input.addItems(["Todos", "VISION", "SIMULATION", "COMMUNICATION", "SYSTEM APP"])
        self.sistema_input.setFixedWidth(120)
        filter_layout.addRow("Sistema:", self.sistema_input)

        # Filtro por sistema
        # No método init_ui, substitua o segundo sistema_input por:
        self.prioridade_input = QComboBox()
        self.prioridade_input.addItems(["Todos", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.prioridade_input.setFixedWidth(120)
        filter_layout.addRow("Prioridade:", self.prioridade_input)

        # Filtro por data
        self.data_ini_input = QLineEdit()
        self.data_ini_input.setPlaceholderText("dd/mm/aaaa")
        self.data_ini_input.setFixedWidth(120)
        filter_layout.addRow("Data Inicial:", self.data_ini_input)

        self.data_fim_input = QLineEdit()
        self.data_fim_input.setPlaceholderText("dd/mm/aaaa")
        self.data_fim_input.setFixedWidth(120)
        filter_layout.addRow("Data Final:", self.data_fim_input)

        # Botão de aplicação
        button_layout = QHBoxLayout()
        
        apply_button = QPushButton("Aplicar Filtro")
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)
        apply_button.clicked.connect(self.aplicar_filtro_logs)
        button_layout.addWidget(apply_button)

        reset_button = QPushButton("Redefinir")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        reset_button.clicked.connect(self.reset_filters)
        button_layout.addWidget(reset_button)

        filter_layout.addRow("", button_layout)
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group, stretch=1)

        self.add_widget(main_container)


    def aplicar_filtro_logs(self):
        filtro = self.filtro_input.text().strip().lower()
        nivel = self.nivel_input.currentText()
        sistema = self.sistema_input.currentText()
        prioridade = self.prioridade_input.currentText()
        data_ini = self.data_ini_input.text().strip()
        data_fim = self.data_fim_input.text().strip()

        if self.log_reader_thread and self.log_reader_thread.isRunning():
            self.log_reader_thread.stop()

        self.log_reader_thread = LogReaderThread(filtro, nivel, data_ini, data_fim, sistema,prioridade)
        self.log_reader_thread.logs_ready.connect(self.exibir_logs)
        self.log_reader_thread.error_occurred.connect(self.show_error)
        self.log_reader_thread.start()

    def refresh_logs(self):
        """Atualiza os logs com os filtros atuais"""
        self.aplicar_filtro_logs()

    def reset_filters(self):
        """Redefine todos os filtros para os valores padrão"""
        self.filtro_input.clear()
        self.nivel_input.setCurrentIndex(0)
        self.sistema_input.setCurrentIndex(0)
        self.data_ini_input.clear()
        self.data_fim_input.clear()
        self.refresh_logs()

    def clear_display(self):
        """Limpa a exibição de logs (não apaga o arquivo)"""
        self.terminal_widget.clear()

    def exibir_logs(self, logs):
        """Exibe os logs formatados com cores diferentes para cada tipo"""
        html_logs = []
        for log in logs.split('\n'):
            try:
                if not log:
                    continue
                    
                if not log.startswith("["):
                    html_logs.append(f'<span style="color: #AAAAAA;">{log}</span>')
                    continue

                # Extrai partes do log
                parts = log.split("]")
                timestamp = parts[0][1:]
                rest = "]".join(parts[1:]).strip()
                
                # Extrai sistema (está entre colchetes)
                system_part = rest.split("]")[0].strip()
                system = system_part[1:] if system_part.startswith("[") else system_part
                rest = rest[len(system_part)+1:].strip()
                
                # Extrai tipo (pode estar entre colchetes ou não)
                if rest.startswith("["):
                    type_part = rest.split("]")[0]
                    log_type = type_part[1:]
                    rest = rest[len(type_part)+1:].strip()
                else:
                    log_type = rest.split(" ")[0]
                    rest = " ".join(rest.split(" ")[1:])
                
                # Extrai mensagem (ignora a prioridade)
                message = rest.split("):")[-1].strip()

                # Define cores
                color_map = {
                    "DEBUG": "#ADD8E6",    # Azul claro
                    "INFO": "#90EE90",     # Verde claro
                    "WARNING": "#FFA500",  # Laranja
                    "ERROR": "#FF6347",    # Vermelho claro
                    "CRITICAL": "#FF0000"  # Vermelho
                }
                
                type_color = color_map.get(log_type, "#FFFFFF")
                system_color = "#00FF00"  # Verde

                html_log = (
                    f'<span style="color: {type_color}; font-weight: bold;">[{log_type}] </span> '
                    f'<span style="color: #FFFFFF;">[{timestamp}]</span> '
                    f'<span style="color: {system_color};">[{system}]: </span> '
                    f'<span style="color: #E0E0E0;">{message}</span>'
                )
                html_logs.append(html_log)
            except Exception as e:
                html_logs.append(f'<span style="color: #AAAAAA;">{log}</span>')

        self.terminal_widget.setHtml("<br>".join(html_logs))
    def show_error(self, message):
        """Exibe mensagens de erro no terminal de logs"""
        self.terminal_widget.append(f'<span style="color: #FF0000;">{message}</span>')

    def destroy(self):
        self.refresh_timer.stop()
        if self.log_reader_thread and self.log_reader_thread.isRunning():
            self.log_reader_thread.stop()
        super().destroy()
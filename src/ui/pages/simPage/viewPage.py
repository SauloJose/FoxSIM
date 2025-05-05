from ui.pages.objects.pageObjects import *
from ui.pages.objects.styles import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from ui.pages.objects.SimWidget import *

#Classe da página principal
class SimulationViewPage(BasicPage):
    def __init__(self):
        super().__init__("Simulação: Visão Geral", QIcon("src/assets/ATGK.png"))

        self.main_vlayout = QVBoxLayout()
        self.main_vlayout.setSpacing(10)
        self.main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.top_layout = self.create_top_section()
        self.bottom_widget = self.create_bottom_section()

        self.main_vlayout.addLayout(self.top_layout)
        self.main_vlayout.addWidget(self.bottom_widget)

        self.add_layout(self.main_vlayout)

    def create_top_section(self):
        self.top_hlayout = QHBoxLayout()
        self.top_hlayout.setSpacing(20)

        # === ESQUERDA ===
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)

        # Widget pai para o SimulatorWidget (tamanho 1.5x)
        parent_width = int(1.2 * 645)
        parent_height = int(1.2 * 413)
        self.sim_parent_widget = QWidget()
        # Remover setFixedSize para permitir expansão
        self.sim_parent_widget.setMinimumSize(parent_width, parent_height)
        self.sim_parent_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sim_parent_layout = QVBoxLayout(self.sim_parent_widget)
        sim_parent_layout.setContentsMargins(0, 0, 0, 0)
        sim_parent_layout.setSpacing(0)

        viewer_width = int(645)
        viewer_height = int(413)
        self.viewer = SimulatorWidget(parent=self.sim_parent_widget)
        self.viewer.set_background_image(Image("src/assets/field.png"))
        self.viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.viewer.setMinimumSize(viewer_width // 2, viewer_height // 2)
        self.viewer.setMaximumSize(parent_width, parent_height)

        # Adiciona o SimulatorWidget para ocupar todo o espaço do widget pai
        sim_parent_layout.addWidget(self.viewer)

        self.left_layout.addWidget(self.sim_parent_widget)
        self.top_hlayout.addWidget(self.left_widget, stretch=3)

        # === DIREITA ===
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(18)
        self.right_widget.setFixedWidth(340)  # width menor para a lateral direita

        # Placar encima
        self.scoreboard = QFrame()
        self.scoreboard.setStyleSheet("background-color: #f0f0f0;")
        self.scoreboard.setMinimumHeight(80)
        self.scoreObjs = QHBoxLayout(self.scoreboard)
        self.scoreObjs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scoreObjs.setContentsMargins(0, 0, 0, 0)

        self.score_widget_a = ScoreWidget("Time A", "blue")
        self.timer_widget = TimerWidget()
        self.score_widget_b = ScoreWidget("Time B", "red")

        self.scoreObjs.addWidget(self.score_widget_a)
        self.scoreObjs.addStretch(1)
        self.scoreObjs.addWidget(self.timer_widget)
        self.scoreObjs.addStretch(1)
        self.scoreObjs.addWidget(self.score_widget_b)

        self.right_layout.addWidget(self.scoreboard)

        # Labels para informações (você pode configurar depois)
        self.info_label1 = QLabel("Label 1: Informação")
        self.info_label2 = QLabel("Label 2: Informação")
        self.info_label3 = QLabel("Label 3: Informação")
        for lbl in [self.info_label1, self.info_label2, self.info_label3]:
            lbl.setStyleSheet("font-size: 15px; color: #333; background: none;")
            self.right_layout.addWidget(lbl)

        self.top_hlayout.addWidget(self.right_widget, stretch=1)
        return self.top_hlayout

    def create_bottom_section(self):
        self.bottom_frame = QFrame()
        self.bottom_layout = QHBoxLayout(self.bottom_frame)
        self.bottom_frame.setStyleSheet("background-color: white;")
        self.bottom_layout.setContentsMargins(10, 10, 10, 10)
        self.bottom_layout.setSpacing(10)

        # === ESQUERDA ===
        self.left_frame = QFrame()
        self.left_frame.setFixedWidth(300)
        self.left_layout = QVBoxLayout(self.left_frame)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label1 = QLabel("Clique para iniciar a simulação")
        self.buttonStart = QPushButton("Iniciar")
        self.buttonStart.setStyleSheet(StyleButtonStart)
        self.buttonStart.setFixedWidth(200)

        self.label2 = QLabel("Clique para reiniciar a simulação")
        self.buttonRestart = QPushButton("Reiniciar")
        self.buttonRestart.setStyleSheet(StyleButtonRestart)
        self.buttonStart.setFixedWidth(200)

        self.left_layout.addWidget(self.label1)
        self.left_layout.addWidget(self.buttonStart)
        self.left_layout.addWidget(self.label2)
        self.left_layout.addWidget(self.buttonRestart)

        # Conecta os botões ao SimulatorWidget
        self.buttonStart.clicked.connect(lambda: self.viewer.start_timer())
        self.buttonRestart.clicked.connect(lambda: self.viewer.reset_timer())

        # === CENTRO ===
        self.center_frame = QFrame()
        self.center_frame.setObjectName("CenterFrame")

        self.center_layout = QVBoxLayout(self.center_frame)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_frame.setContentsMargins(0, 0, 0, 0)
        self.center_frame.setFixedWidth(300)

        self.center_frame.setStyleSheet("""
            #CenterFrame {
                border-left: 2px solid #000;
                border-right: 2px solid #000;
                margin: 0px;
            }
        """)

        self.status_widget = StatusDisplay(self.center_frame)
        self.status_widget.update_status(False, False, False, False)
        self.center_layout.addWidget(self.status_widget)

        # === DIREITA ===
        self.right_frame = QFrame()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setMinimum(1)
        self.slider_speed.setMaximum(10)
        self.slider_speed.setValue(5)

        self.time_display = QLabel("Tempo: 0s")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.buttonPause = QPushButton("Pausar")
        self.buttonPause.setStyleSheet(StyleButtonStart)

        self.right_layout.addWidget(QLabel("Velocidade da simulação:"))
        self.right_layout.addWidget(self.slider_speed)
        self.right_layout.addSpacing(10)
        self.right_layout.addWidget(self.time_display)
        self.right_layout.addSpacing(10)
        self.right_layout.addWidget(self.buttonPause)

        self.bottom_layout.addWidget(self.left_frame, stretch=1)
        self.bottom_layout.addWidget(self.center_frame, stretch=1)
        self.bottom_layout.addWidget(self.right_frame, stretch=2)

        return self.bottom_frame

    def destroy(self):
        # Libere recursos de threads, viewers, etc.
        if hasattr(self, 'viewer') and hasattr(self.viewer, 'destroy'):
            self.viewer.destroy()
        # Libere outros recursos se necessário


#Classe para os Widgets

class ScoreWidget(QWidget):
    def __init__(self, team_name, color):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(0)

        self.team_label = QLabel(team_name)
        self.team_label.setFont(QFont('Arial', 10))
        self.team_label.setStyleSheet(f"color: {color};")
        self.team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.score_label = QLabel("0")
        self.score_label.setFont(QFont('Arial', 28, QFont.Weight.Bold))
        self.score_label.setStyleSheet(f"color: {color};")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.team_label)
        layout.addWidget(self.score_label)
        self.setLayout(layout)

    def set_score(self, value):
        self.score_label.setText(str(value))

    def destroy(self):
        pass

class TimerWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_label = QLabel("01:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Fonte garantida com tamanho grande
        font = QFont("Courier New")  # mais confiável
        font.setBold(True)
        font.setPointSize(24)
        self.timer_label.setFont(font)

        self.timer_label.setStyleSheet("""
            color: white;
            background-color: black;
            padding: 10px;
        """)

        layout.addWidget(self.timer_label)
        self.setLayout(layout)

    def set_time(self, minutes: int, seconds: int):
        """Define o tempo do timer em minutos e segundos."""
        minutes = max(0, minutes)
        seconds = max(0, min(seconds, 59))  # garante que segundos estejam entre 0 e 59
        formatted_time = f"{minutes:02}:{seconds:02}"
        self.timer_label.setText(formatted_time)

    def destroy(self):
        pass


class StatusDisplay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setObjectName("StatusDisplay")  # Para o seletor CSS
            
        # === Fontes ===
        title_font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        status_font = QFont("Arial", 8)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        self.title = QLabel("<b>CONFIGURAÇÕES DA EXIBIÇÃO</b>")
        self.title.setFont(title_font)  # Fonte maior para o título
        self.layout.addWidget(self.title)

        # Labels que serão atualizados dinamicamente
        self.paused_label = QLabel()
        self.paused_label.setFont(status_font)

        self.collision_label = QLabel()
        self.collision_label.setFont(status_font)

        self.grid_label = QLabel()
        self.grid_label.setFont(status_font)

        self.running_label = QLabel()
        self.running_label.setFont(status_font)

        self.layout.addWidget(self.paused_label)
        self.layout.addWidget(self.collision_label)
        self.layout.addWidget(self.grid_label)
        self.layout.addWidget(self.running_label)

        # Inicializa com todos False
        self.update_status(paused=False, show_collision=False, show_grid=False, running=False)

    def update_status(self, paused, show_collision, show_grid, running):
        # Utilidade para gerar o texto formatado
        def format_label(name, state, true_text, false_text):
            color = "green" if state else "red"
            text = true_text if state else false_text
            return f"{name}: <font color='{color}'>{text}</font>"

        self.paused_label.setText(format_label("Pausa ativada", paused, "SIM", "NÃO"))
        self.collision_label.setText(format_label("Objetos de Colisão", show_collision, "EXIBINDO", "OCULTO"))
        self.grid_label.setText(format_label("Particionamento Espacial", show_grid, "EXIBINDO", "OCULTO"))
        self.running_label.setText(format_label("Estado da simulação", running, "RODANDO", "PARADA"))

    def destroy(self):
        pass

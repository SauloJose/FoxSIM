from ui.pages.objects.pageObjects import *
from ui.pages.objects.styles import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from ui.pages.objects.SimWidget import *
from simulator.simulator import *

import os

#Classe da página principal
class SimulationViewPage(BasicPage):
    def __init__(self, log_manager: LogManager = None):
        super().__init__("Simulação: Visão Geral", QIcon("src/assets/ATGK.png"),log_manager)

        self.main_vlayout = QVBoxLayout()
        self.main_vlayout.setSpacing(10)
        self.main_vlayout.setContentsMargins(0, 0, 0, 0)

        self.top_layout = self.create_top_section()
        self.main_vlayout.addLayout(self.top_layout)
        self.add_layout(self.main_vlayout)

        # Criando objeto do simulado para controlar corretamente a simulação
        #self.simulator = Simulator(self, self.viewer, FPS = 60)
        #self.initialize_simulator()
        
    def create_top_section(self):
        self.top_hlayout = QHBoxLayout()
        self.top_hlayout.setSpacing(20)

        # === ESQUERDA ===
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)

        # --- Informações do time A ---
        self.team_a_info = TeamInfoWidget("A", ["src/assets/ATGK.png","src/assets/ATA1.png", "src/assets/ATA2.png"])
        wrapper_a = QWidget()
        wrapper_a.setFixedHeight(80)
        wrapper_a.setStyleSheet("background-color: #f5f5f7; border-radius: 8px;")
        wrapper_a_layout = QVBoxLayout(wrapper_a)
        wrapper_a_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_a_layout.setSpacing(0)
        wrapper_a_layout.addWidget(self.team_a_info)
        self.left_layout.addWidget(wrapper_a)

        # Widget pai para o SimulatorWidget (tamanho 1.2x)
        parent_width = int(1.2 * 645)
        parent_height = int(1.2 * 413)
        self.sim_parent_widget = QWidget()
        self.sim_parent_widget.setMinimumSize(parent_width, parent_height)
        self.sim_parent_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sim_parent_layout = QVBoxLayout(self.sim_parent_widget)
        sim_parent_layout.setContentsMargins(0, 0, 0, 0)
        sim_parent_layout.setSpacing(0)

        viewer_width = int(645)
        viewer_height = int(413)
        self.viewer = SimulatorWidget(parent=self.sim_parent_widget)
        self.viewer.set_background_image(Image("src/assets/field2.png"))
        self.viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.viewer.setMinimumSize(viewer_width // 2, viewer_height // 2)
        self.viewer.setMaximumSize(parent_width, parent_height)

        sim_parent_layout.addWidget(self.viewer)
        self.left_layout.addWidget(self.sim_parent_widget)

        # --- Informações do time B ---
        self.team_b_info = TeamInfoWidget("B", ["src/assets/ETGK.png","src/assets/ETA1.png", "src/assets/ETA2.png"])
        wrapper_b = QWidget()
        wrapper_b.setFixedHeight(80)
        wrapper_b.setStyleSheet("background-color: #f5f5f7; border-radius: 8px;")
        wrapper_b_layout = QVBoxLayout(wrapper_b)
        wrapper_b_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_b_layout.setSpacing(0)
        wrapper_b_layout.addWidget(self.team_b_info)
        self.left_layout.addWidget(wrapper_b)

        self.top_hlayout.addWidget(self.left_widget, stretch=3)

        # === DIREITA ===
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(20)  # Espaçamento maior entre os elementos
        self.right_widget.setFixedWidth(340)
        self.right_widget.setStyleSheet("background-color: #f5f5f7; border-radius: 8px;")  # cinza claro

        # Placar encima
        self.scoreboard = QFrame()
        self.scoreboard.setStyleSheet("background-color: #e0e3ea;")
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

        # === CONTROLES DE VISUALIZAÇÃO ===
        self.controls_group = QGroupBox()
        self.controls_group.setTitle("Controles de Visualização")
        self.controls_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 15px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                top: 2px;
                padding: 0 3px 0 3px;
            }
        """)
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(8)
        controls_layout.setContentsMargins(8, 18, 8, 8)  # espaço extra no topo para o título
        self.chk_trajetoria_bola = QCheckBox("Exibir trajetória da bola")
        self.chk_trajetoria_robos = QCheckBox("Exibir trajetória dos robôs")
        self.chk_grade = QCheckBox("Exibir grade do campo")
        self.chk_colisao = QCheckBox("Exibir objetos de colisão")
        self.chk_particionamento = QCheckBox("Exibir particionamento espacial")
        self.chk_pause = QCheckBox("Pausar simulação")
        controls_layout.addWidget(self.chk_trajetoria_bola)
        controls_layout.addWidget(self.chk_trajetoria_robos)
        controls_layout.addWidget(self.chk_grade)
        controls_layout.addWidget(self.chk_colisao)
        controls_layout.addWidget(self.chk_particionamento)
        controls_layout.addWidget(self.chk_pause)
        self.controls_group.setLayout(controls_layout)
        self.right_layout.addWidget(self.controls_group)

        # === LABEL ANTES DOS LOGS ===
        stats_label = QLabel("<b>Estatísticas da simulação</b>")
        stats_label.setStyleSheet("font-size:15px; margin-bottom:2px;")
        self.right_layout.addWidget(stats_label)

        # === LOGS ESTATÍSTICOS ===
        self.stats_log_widget = StatsLogWidget()
        self.right_layout.addWidget(self.stats_log_widget)

        # === BOTÕES DE CONTROLE (centralizados, com espaçamento adequado) ===
        btns_widget = QWidget()
        btns_layout = QHBoxLayout(btns_widget)
        btns_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(20)  # Espaçamento entre os botões

        self.buttonStart = QPushButton("Iniciar")
        self.buttonStart.setStyleSheet(StyleButtonStart)
        self.buttonStart.setFixedWidth(120)

        self.buttonRestart = QPushButton("Reiniciar")
        self.buttonRestart.setStyleSheet(StyleButtonRestart)
        self.buttonRestart.setFixedWidth(120)

        self.buttonStart.clicked.connect(lambda: self.viewer.start_timer())
        self.buttonRestart.clicked.connect(lambda: self.viewer.reset_timer())

        btns_layout.addWidget(self.buttonStart)
        btns_layout.addWidget(self.buttonRestart)
        self.right_layout.addSpacing(20)  # Espaçamento entre logs e botões
        self.right_layout.addWidget(btns_widget)

        self.right_layout.addStretch(1)
        self.top_hlayout.addWidget(self.right_widget, stretch=1)
        return self.top_hlayout

    # ==============================================================
    # Método para atualizar o placar
    def update_score(self, team_a_score, team_b_score):
        pass 

    # Método para atualizar as informações do robô
    def update_robot_info(self, team, robot_idx, pos, direction, v_left, v_right, dist_ball):
        pass 


    #Método para atualizar o cronometro 
    def update_timer(self, minutes, seconds):
        pass 


    #Método para atualizar os logs estatísticos 
    def update_stats_log(self, velocity, distances, collisions, time_str, state, events):
        pass 


    # Método para puxar variáveis dos arquivos e carregar no simulador
    def get_variables_simulation(self):
        pass 

    # Método para inicializar o simulador de forma correta 
    def initialize_simulator(self):
        pass 

    # ==============================================================

    # Método para dar início à simulação
    def start_simulation(self):
        pass 


    # Método para reiniciar a simulação 
    def restart_simulation(self):
        pass


    # Método para pausar a simulação 
    def pause_simulation(self):
        pass

    # Método para dar condições de DEBUG à simulação
    def debug_simulation(self):
        pass
    # ==============================================================

    def destroy(self):
        if hasattr(self, 'viewer') and hasattr(self.viewer, 'destroy'):
            self.viewer.destroy()
        # Libere outros recursos se necessário


# =====================================================================
# Classe para os Widgets

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


class StatsLogWidget(QFrame):
    """
    Widget para exibir logs estatísticos e informações dinâmicas.
    Os valores podem ser atualizados via métodos públicos.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background: #f0f2f5;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QLabel {
                font-size: 14px;
                color: #222;
                padding: 4px 0;
                background: transparent;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Espaçamento maior entre os logs
        layout.setContentsMargins(12, 10, 12, 10)

        self.lbl_vel_media = QLabel()
        layout.addWidget(self.lbl_vel_media)

        self.lbl_dist_robos = QLabel()
        layout.addWidget(self.lbl_dist_robos)

        self.lbl_colisoes = QLabel()
        layout.addWidget(self.lbl_colisoes)

        self.lbl_tempo = QLabel()
        layout.addWidget(self.lbl_tempo)

        self.lbl_estado = QLabel()
        layout.addWidget(self.lbl_estado)

        self.lbl_eventos = QLabel()
        self.lbl_eventos.setWordWrap(True)
        layout.addWidget(self.lbl_eventos)

        self.setLayout(layout)
        self.clear()

    def set_velocidade_media(self, valor):
        self.lbl_vel_media.setText(f"Velocidade média: <b>{valor:.2f} m/s</b>")

    def set_distancias(self, distancias: dict):
        txt = " | ".join([f"{k}: <b>{v:.2f} m</b>" for k, v in distancias.items()])
        self.lbl_dist_robos.setText(f"Distância: {txt}")

    def set_colisoes(self, n):
        self.lbl_colisoes.setText(f"Colisões: <b>{n}</b>")

    def set_tempo(self, tempo_str):
        self.lbl_tempo.setText(f"Tempo: <b>{tempo_str}</b>")

    def set_estado(self, estado):
        self.lbl_estado.setText(f"Estado: <b>{estado}</b>")

    def set_eventos(self, eventos: list):
        if eventos:
            txt = "<br>".join(eventos[-5:])
        else:
            txt = "Nenhum"
        self.lbl_eventos.setText(f"Eventos: {txt}")

    def clear(self):
        self.set_velocidade_media(0.0)
        self.set_distancias({})
        self.set_colisoes(0)
        self.set_tempo("0s")
        self.set_estado("Parada")
        self.set_eventos([])

# --- NOVAS CLASSES PARA INFORMAÇÕES DOS TIMES E ROBÔS ---

class TeamInfoWidget(QWidget):
    """
    Widget para exibir informações dos robôs de um time.
    """
    def __init__(self, team_label, robot_img_paths):
        super().__init__()
        self.setFixedHeight(80)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(12)
        self.robots = []
        self.robotNames = ["Goleiro (GK)", "Atacante 1 (A1)", "Atacante 2 (A2)"]
        for i, img_path in enumerate(robot_img_paths):
            self.layout.addStretch(1)
            robot_widget = RobotInfoWidget(img_path, self.robotNames[i])
            self.layout.addWidget(robot_widget)
            self.robots.append(robot_widget)
        self.layout.addStretch(1)

    def set_robot_info(self, robot_idx, pos, direction, v_left, v_right, dist_ball):
        """
        Atualiza as informações de um robô específico.
        robot_idx: índice do robô (0, 1, 2)
        """
        if 0 <= robot_idx < len(self.robots):
            self.robots[robot_idx].set_info(pos, direction, v_left, v_right, dist_ball)

class RobotInfoWidget(QWidget):
    """
    Widget para exibir informações de um robô.
    """
    def __init__(self, img_path, robot_label=""):
        super().__init__()
        self.setFixedHeight(72)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(30)

        # Imagem do robô, rotacionada 90 graus horário
        self.img_label = QLabel()
        self.img_label.setFixedSize(40, 40)
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            transform = QTransform().rotate(-90)
            rotated = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
            self.img_label.setPixmap(rotated.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.layout.addWidget(self.img_label)

        # Bloco de informações
        self.info_layout = QVBoxLayout()
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(1)

        font = QFont("Arial", 8)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

        self.lbl_robot = QLabel(f"<b>{robot_label}</b>")
        self.lbl_robot.setFont(font)
        self.lbl_robot.setStyleSheet("font-weight: bold; color: #444;")
        self.info_layout.addWidget(self.lbl_robot)
        self.info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_estado = QLabel("<b>Estado:</b> [0.00; 0.00; 0.0°]")
        self.lbl_estado.setFont(font)
        self.info_layout.addWidget(self.lbl_estado)

        self.lbl_rodas = QLabel("<b>[VL, VR]:</b> [0.00; 0.00] cm/s")
        self.lbl_rodas.setFont(font)
        self.info_layout.addWidget(self.lbl_rodas)

        self.lbl_dist = QLabel("<b>Dist. Bola:</b> 0.00 cm")
        self.lbl_dist.setFont(font)
        self.info_layout.addWidget(self.lbl_dist)

        self.layout.addLayout(self.info_layout)

    def set_info(self, pos, direction, v_left, v_right, dist_ball):
        """
        Atualiza as informações exibidas do robô.
        pos: tupla (x, y)
        direction: float (graus)
        v_left, v_right, dist_ball: float
        """
        self.lbl_estado.setText(f"<b>Estado:</b> ({pos[0]:.2f}; {pos[1]:.2f}; {direction:.1f}°)")
        self.lbl_rodas.setText(f"<b>[VL, VR]:</b> [{v_left:.2f}; {v_right:.2f}] cm/s")
        self.lbl_dist.setText(f"<b>Dist. Bola:</b> {dist_ball:.2f} cm")

from PyQt6.QtWidgets import (
    QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QFormLayout, QGroupBox, QSpinBox, QFileDialog, QWidget, QFrame
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from ui.pages.objects.pageObjects import *
import os, json
import pyqtgraph as pg
import numpy as np  # Corrigir: garantir import do numpy
from simulator.intelligence.logic.controll import *
import time 

#Objeto robô para simulação simples
class SimBot:
    """Classe simples de robô diferencial para simulação PID."""
    def __init__(self, x, y, angle, wheel_dist=7):
        self.position = np.array([x, y], dtype=float)
        self.angle = angle  # radianos
        self.wheel_dist = wheel_dist  # distância entre rodas
        self.history = [self.position.copy()]
        self.angles = [self.angle]

    def step(self, v_l, v_r, dt):
        v = (v_r + v_l) / 2.0
        w = (v_r - v_l) / self.wheel_dist
        self.angle += w * dt
        self.angle = np.arctan2(np.sin(self.angle), np.cos(self.angle))  # normaliza
        dx = v * np.cos(self.angle) * dt
        dy = v * np.sin(self.angle) * dt
        self.position += np.array([dx, dy])
        self.history.append(self.position.copy())
        self.angles.append(self.angle)

class CTPIDControlPage(BasicPage):
    def __init__(self):
        super().__init__("Controle: Ajuste do Controle PID", QIcon("src/assets/PID.png"))

        # Explicação curta
        explanation_label = QLabel("Ajuste os parâmetros PID e simule a trajetória entre dois estágios (posição e orientação).")
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("""
            font-size: 15px;
            margin-bottom: 10px;
            color: #444;
            background: #f8f8f8;
            border-radius: 8px;
            padding: 8px 16px;
        """)
        explanation_label.setFixedHeight(60)
        explanation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_widget(explanation_label)

        # Inicializa os controladores PID (valores default, podem ser 0)
        self.pid_dist = PIDController(0, 0, 0)
        self.pid_angle = PIDController(0, 0, 0)
        self.pid_final = PIDController(0, 0, 0)

        # Container principal
        main_container = QWidget()
        main_container.setObjectName("pidMainContainer")
        main_container.setStyleSheet("""
            #pidMainContainer {
                background: #ffffff;
                border: 1.5px solid #e0e0e0;
                border-radius: 16px;
                padding: 24px;
            }
        """)
        main_layout = QHBoxLayout(main_container)
        main_layout.setContentsMargins(32, 18, 32, 18)
        main_layout.setSpacing(32)

        # === Esquerda: Formulários e botões ===
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(6)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # Formulário estágio inicial
        stage_init_group = QGroupBox("Estágio Inicial")
        stage_init_group.setStyleSheet("""
            QGroupBox { font-size: 14px; font-weight: bold; color: #228B22; }
            QGroupBox::title {
                subcontrol-origin: content; subcontrol-position: top left;
                left: 10px; top: 4px; padding: 0 8px; background: transparent;
            }
        """)
        stage_init_form = QFormLayout()
        stage_init_form.setContentsMargins(10, 18, 10, 10)
        stage_init_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        stage_init_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        stage_init_form.setSpacing(8)
        self.init_x = QLineEdit(); self.init_x.setPlaceholderText("x"); self.init_x.setFixedWidth(60)
        self.init_y = QLineEdit(); self.init_y.setPlaceholderText("y"); self.init_y.setFixedWidth(60)
        self.init_alpha = QLineEdit(); self.init_alpha.setPlaceholderText("α (graus)"); self.init_alpha.setFixedWidth(60)
        init_row = QHBoxLayout()
        init_row.addWidget(QLabel("x:")); init_row.addWidget(self.init_x)
        init_row.addSpacing(2)
        init_row.addWidget(QLabel("y:")); init_row.addWidget(self.init_y)
        init_row.addSpacing(2)
        init_row.addWidget(QLabel("α:")); init_row.addWidget(self.init_alpha)
        stage_init_form.addRow("", init_row)
        stage_init_group.setLayout(stage_init_form)
        form_layout.addWidget(stage_init_group)

        # Formulário estágio final
        stage_final_group = QGroupBox("Estágio Final")
        stage_final_group.setStyleSheet(stage_init_group.styleSheet())
        stage_final_form = QFormLayout()
        stage_final_form.setContentsMargins(10, 18, 10, 10)
        stage_final_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        stage_final_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        stage_final_form.setSpacing(8)
        self.final_x = QLineEdit(); self.final_x.setPlaceholderText("x"); self.final_x.setFixedWidth(60)
        self.final_y = QLineEdit(); self.final_y.setPlaceholderText("y"); self.final_y.setFixedWidth(60)
        self.final_alpha = QLineEdit(); self.final_alpha.setPlaceholderText("α (graus)"); self.final_alpha.setFixedWidth(60)
        final_row = QHBoxLayout()
        final_row.addWidget(QLabel("x:")); final_row.addWidget(self.final_x)
        final_row.addSpacing(2)
        final_row.addWidget(QLabel("y:")); final_row.addWidget(self.final_y)
        final_row.addSpacing(2)
        final_row.addWidget(QLabel("α:")); final_row.addWidget(self.final_alpha)
        stage_final_form.addRow("", final_row)
        stage_final_group.setLayout(stage_final_form)
        form_layout.addWidget(stage_final_group)

        # Formulário PID
        pid_group = QGroupBox("Constantes PID")
        pid_group.setStyleSheet("""
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
        """)
        pid_form = QFormLayout()
        pid_form.setContentsMargins(12, 24, 12, 12)
        pid_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        pid_form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        pid_form.setSpacing(12)
        self.pid_inputs = {}
        pid_labels = [
            ("Distância até o alvo", "dist"),
            ("Ângulo até o alvo", "angle"),
            ("Ângulo final ao chegar", "final_angle"),
        ]
        for label, key in pid_labels:
            kp = QLineEdit(); kp.setPlaceholderText("Kp"); kp.setFixedWidth(60)
            ki = QLineEdit(); ki.setPlaceholderText("Ki"); ki.setFixedWidth(60)
            kd = QLineEdit(); kd.setPlaceholderText("Kd"); kd.setFixedWidth(60)
            row = QHBoxLayout()
            row.addWidget(QLabel("Kp:")); row.addWidget(kp)
            row.addSpacing(8)
            row.addWidget(QLabel("Ki:")); row.addWidget(ki)
            row.addSpacing(8)
            row.addWidget(QLabel("Kd:")); row.addWidget(kd)
            pid_form.addRow(f"{label}:", row)
            self.pid_inputs[key] = (kp, ki, kd)
        pid_group.setLayout(pid_form)
        form_layout.addWidget(pid_group)

        # Botões de ação (Salvar, Restaurar)
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Salvar Configurações")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #006400;
                color: white;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)
        restore_btn = QPushButton("Restaurar Padrão")
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #bbb;
                color: #222;
                border-radius: 6px;
                padding: 8px 22px;
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #888;
                color: white;
            }
        """)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(restore_btn)
        form_layout.addLayout(btn_row)

        # Botão iniciar simulação (abaixo dos outros)
        sim_btn = QPushButton("Iniciar Simulação")
        sim_btn.setStyleSheet("""
            QPushButton {
                background-color: #228B22;
                color: white;
                border-radius: 6px;
                padding: 10px 28px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 18px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #006400;
            }
        """)

        # Botão parar simulação
        stop_btn = QPushButton("Parar Simulação")
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #b22222;
                color: white;
                border-radius: 6px;
                padding: 10px 28px;
                font-size: 15px;
                font-weight: bold;
                margin-top: 18px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #800000;
            }
        """)

        # Adicionando funcionalidades aso botões
        save_btn.clicked.connect(self.save_pidvars)
        restore_btn.clicked.connect(lambda: self.load_pidvars(self.get_pidvarR_path()))
        self.load_pidvars()  # Carrega automaticamente ao abrir a página

        sim_btn.clicked.connect(self.run_simulation)  # Para rodar a simulação e atualizar os gráficos
        stop_btn.clicked.connect(self.stop_simulation)

        sim_stop_row = QHBoxLayout()
        sim_stop_row.addWidget(sim_btn)
        sim_stop_row.addWidget(stop_btn)
        form_layout.addLayout(sim_stop_row)
        form_layout.addStretch(1)

        # === Direita: Gráficos ===
        self.graph_widget = QWidget()
        self.graph_widget.setStyleSheet("""
            QWidget {
                padding: 5px;
            }
        """)
        self.graph_layout = QVBoxLayout(self.graph_widget)
        self.graph_layout.setSpacing(6)
        self.graph_layout.setContentsMargins(0, 0, 0, 0)

        # Título acima dos gráficos menores
        top_graphs_title = QLabel("Gráficos PID")
        top_graphs_title.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #228B22;
            margin-bottom: 2px;
        """)
        self.graph_layout.addWidget(top_graphs_title)

        # Linha de 3 gráficos lado a lado (parte superior, menor)
        self.top_graphs_row = QHBoxLayout()
        self.top_graphs_row.setSpacing(4)  # Diminui o espaço entre os gráficos

        self.top_graph_titles = [
            "Erro de Distância",
            "Erro de Ãngulo até o alvo",
            "Erro de Ângulo Final"
        ]
        self.top_graph_frames = []
        self.top_graph_widgets = []
        self.top_graph_curves = []
        for i, title in enumerate(self.top_graph_titles):
            vbox = QVBoxLayout()
            vbox.setSpacing(0)
            vbox.setContentsMargins(0, 0, 0, 0)
            label = QLabel(title)
            label.setStyleSheet("""
                font-size: 13px;
                font-weight: bold;
                color: #228B22;
                margin-bottom: 2px;
            """)
            vbox.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
            graph_frame = QFrame()
            graph_frame.setStyleSheet("""
                QFrame {
                    background: #e0e0e0;
                    border: none;
                }
            """)
            graph_frame.setMinimumSize(120, 100)
            # Cria o PlotWidget e curva
            plot_widget = pg.PlotWidget()
            plot_widget.setTitle("")
            plot_widget.setContentsMargins(0, 0, 0, 0)
            plot_widget.getPlotItem().layout.setContentsMargins(0, 0, 0, 0)
            plot_widget.getPlotItem().setContentsMargins(0, 0, 0, 0)
            plot_widget.getPlotItem().getViewBox()
            curve = plot_widget.plot([], pen=pg.mkPen('b', width=2))
            self.top_graph_widgets.append(plot_widget)
            self.top_graph_curves.append(curve)
            layout = QVBoxLayout(graph_frame)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(plot_widget)
            vbox.addWidget(graph_frame)
            self.top_graphs_row.addLayout(vbox)
            self.top_graph_frames.append(graph_frame)
        self.graph_layout.addLayout(self.top_graphs_row)

        # Gráfico maior para trajetória (ocupa o restante do espaço)
        self.traj_frame = QFrame()
        self.traj_frame.setStyleSheet("""
                QFrame {
                    background: #e0e0e0;
                    border: none;
                }
            """)
        self.traj_frame.setMinimumHeight(280)
        self.traj_vbox = QVBoxLayout(self.traj_frame)
        self.traj_vbox.setContentsMargins(0, 0, 0, 0)
        self.traj_vbox.setSpacing(0)
        self.traj_plot = pg.PlotWidget()
        self.traj_plot.setAspectLocked(True)
        self.traj_plot.setTitle("")
        self.traj_plot.setContentsMargins(0, 0, 0, 0)
        self.traj_plot.getPlotItem().layout.setContentsMargins(0, 0, 0, 0)
        self.traj_plot.getPlotItem().setContentsMargins(0, 0, 0, 0)
        self.traj_plot.getPlotItem().getViewBox()
        self.traj_plot.setXRange(0, 150)
        self.traj_plot.setYRange(0, 130)
        self.traj_curve = self.traj_plot.plot([], [], pen=pg.mkPen('r', width=2), name="Trajetória")
        self.traj_start = self.traj_plot.plot([], [], pen=None, symbol='o', symbolBrush='g', symbolSize=12, name="Início")
        self.traj_goal = self.traj_plot.plot([], [], pen=None, symbol='x', symbolBrush='b', symbolSize=14, name="Alvo")
        self.robot_dot = self.traj_plot.plot([], [], pen=None, symbol='o', symbolBrush='y', symbolSize=18, name="Robô")
        self.robot_arrow = self.traj_plot.plot([], [], pen=pg.mkPen('y', width=3), name="Direção")
        
        traj_title = QLabel("Gráfico de trajetória do robô")
        traj_title.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #228B22;
            margin-bottom: 4px;
        """)
        traj_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.graph_layout.addWidget(traj_title)
        self.traj_vbox.addWidget(self.traj_plot)
        self.graph_layout.addWidget(self.traj_frame, stretch=10)

        self.graph_layout.addStretch(0)

        # Adiciona ao layout principal
        main_layout.addWidget(form_widget, stretch=3)   # 25%
        main_layout.addWidget(self.graph_widget, stretch=7)  # 75%

        self.add_widget(main_container)

    def destroy(self):
        # Libere threads, arquivos, etc.
        pass

    # ========= Funções de simulação e gráficos =========
    def get_pidvar_path(self):
        return os.path.join("src", "data", "temp", "PIDvar.json")

    def get_pidvarR_path(self):
        return os.path.join("src", "data", "temp", "PIDvarR.json")

    def save_pidvars(self):
        data = {
            "init": [self.init_x.text(), self.init_y.text(), self.init_alpha.text()],
            "final": [self.final_x.text(), self.final_y.text(), self.final_alpha.text()],
            "pid": {
                key: [w.text() for w in self.pid_inputs[key]]
                for key in self.pid_inputs
            }
        }
        with open(self.get_pidvar_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_pidvars(self, path=None):
        if path is None:
            path = self.get_pidvar_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.init_x.setText(data["init"][0])
            self.init_y.setText(data["init"][1])
            self.init_alpha.setText(data["init"][2])
            self.final_x.setText(data["final"][0])
            self.final_y.setText(data["final"][1])
            self.final_alpha.setText(data["final"][2])
            for key in self.pid_inputs:
                for i, w in enumerate(self.pid_inputs[key]):
                    w.setText(data["pid"][key][i])

    def plot_error_graph(self, frame, error_list, title):
        # Remove widgets antigos
        layout = frame.layout()
        if layout is None:
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(0, 0, 0, 0)
        else:
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
        plot_widget = pg.PlotWidget()
        plot_widget.plot(error_list, pen=pg.mkPen('b', width=2))
        plot_widget.setTitle(title)
        layout.addWidget(plot_widget)

    # ================ Método para simular o gráfico ===============
    def stop_simulation(self):
        self._stop_simulation = True

    def run_simulation(self):
        self._stop_simulation = False
        try:
            x0 = float(self.init_x.text())
            y0 = float(self.init_y.text())
            a0 = np.deg2rad(float(self.init_alpha.text()))
            x1 = float(self.final_x.text())
            y1 = float(self.final_y.text())
            a1 = np.deg2rad(float(self.final_alpha.text()))
            kp_dist, ki_dist, kd_dist = [float(w.text()) for w in self.pid_inputs["dist"]]
            kp_angle, ki_angle, kd_angle = [float(w.text()) for w in self.pid_inputs["angle"]]
            kp_final, ki_final, kd_final = [float(w.text()) for w in self.pid_inputs["final_angle"]]
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Parâmetro inválido: {e}")
            return

        # Atualiza os ganhos e reseta os controladores PID
        self.pid_dist.set_new_consts(kp_dist, ki_dist, kd_dist)
        self.pid_angle.set_new_consts(kp_angle, ki_angle, kd_angle)
        self.pid_final.set_new_consts(kp_final, ki_final, kd_final)
        
        bot = SimBot(x0, y0, a0)
        dt = 0.1
        max_steps = 1000

        dist_errors = []
        angle_errors = []
        final_angle_errors = []

        for _ in range(max_steps):
            if self._stop_simulation:
                break
            pos_error = np.array([x1, y1]) - bot.position
            distance = np.linalg.norm(pos_error)
            angle_to_target = np.arctan2(pos_error[1], pos_error[0])
            heading_error = np.arctan2(np.sin(angle_to_target - bot.angle), np.cos(angle_to_target - bot.angle))
            final_angle_error = np.arctan2(np.sin(a1 - bot.angle), np.cos(a1 - bot.angle))

            # Estratégia: quando longe, prioriza heading; quando perto, prioriza orientação final
            if distance < 10.0:
                w = self.pid_final.compute(final_angle_error, dt)
            else:
                w = self.pid_angle.compute(heading_error, dt)
            v = self.pid_dist.compute(distance, dt)

            v = np.clip(v, -50, 50)
            w = np.clip(w, -3, 3)

            v_l = v - (w * bot.wheel_dist / 2)
            v_r = v + (w * bot.wheel_dist / 2)
            bot.step(v_l, v_r, dt)

            dist_errors.append(distance)
            angle_errors.append(heading_error)
            final_angle_errors.append(final_angle_error)

            # Atualiza os dados das curvas dos gráficos de erro
            self.top_graph_curves[0].setData(dist_errors)
            self.top_graph_curves[1].setData(angle_errors)
            self.top_graph_curves[2].setData(final_angle_errors)

            # Atualiza a curva da trajetória
            history = np.array(bot.history)
            self.traj_curve.setData(history[:, 0], history[:, 1])
            self.traj_start.setData([x0], [y0])
            self.traj_goal.setData([x1], [y1])

            # Atualiza o círculo do robô
            self.robot_dot.setData([bot.position[0]], [bot.position[1]])

            # Atualiza a seta de direção (tamanho 10)
            arrow_len = 10
            arrow_x = bot.position[0] + arrow_len * np.cos(bot.angle)
            arrow_y = bot.position[1] + arrow_len * np.sin(bot.angle)
            self.robot_arrow.setData([bot.position[0], arrow_x], [bot.position[1], arrow_y])
            
            QApplication.processEvents()
            time.sleep(0.01)

            if distance < 1.0 and abs(final_angle_error) < np.deg2rad(5):
                break
from ui.mainWindow.MainWindows import *

class VSVisionPage(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Visão Geral", QIcon("src/assets/statistics.png"))

        
        # Layout principal (vertical): top (esquerda + direita) + bottom
        main_vlayout = QVBoxLayout()
        main_vlayout.setSpacing(10)
        main_vlayout.setContentsMargins(0, 0, 0, 0)

        # Layout da parte superior (esquerda + direita)
        top_hlayout = QHBoxLayout()
        top_hlayout.setSpacing(10)

        # Frame ESQUERDA
        left_widget = QFrame()
        left_widget.setMinimumSize(645, 613)
        left_layout = QVBoxLayout(left_widget)
        left_label = QLabel("Área Esquerda (Ex: Visualização)")
        left_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        left_layout.addWidget(left_label)
        top_hlayout.addWidget(left_widget, stretch=3)

        
        # Frame DIREITA
        right_widget = QFrame()
        right_widget.setStyleSheet("background-color: #ffe6cc; border: 2px solid #ff9900;")
        right_widget.setMinimumWidth(100)
        right_layout = QVBoxLayout(right_widget)
        right_label = QLabel("Área Direita (Ex: Controles)")
        right_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(right_label)
        top_hlayout.addWidget(right_widget, stretch=1)

        # Frame INFERIOR
        bottom_widget = QFrame()
        bottom_widget.setStyleSheet("background-color: #e6ffcc; border: 2px solid #66cc00;")
        bottom_widget.setMinimumHeight(150)
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_label = QLabel("Área Inferior (Ex: Logs, Console)")
        bottom_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        bottom_layout.addWidget(bottom_label)

        # Montar layout geral
        main_vlayout.addLayout(top_hlayout)
        main_vlayout.addWidget(bottom_widget)

        self.add_layout(main_vlayout)
from ui.pages.objects.pageObjects import *


class VSCalibrationPage(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Calibração", QIcon("src/assets/control-panel.png"))

        
        # Adicionando um texto e botão como exemplo
        self.add_widget(QLabel("Bem-vindo ao simulador!"))

        btn = QPushButton("Iniciar simulação")
        self.add_widget(btn)
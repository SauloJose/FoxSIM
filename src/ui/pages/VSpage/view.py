from ui.mainWindow.MainWindows import *

class VSVisionPage(BasicPage):
    def __init__(self):
        super().__init__("Sistema de Visão: Visão Geral", QIcon("src/assets/statistics.png"))

        
        # Adicionando um texto e botão como exemplo
        self.add_widget(QLabel("Bem-vindo ao simulador!"))

        btn = QPushButton("Iniciar simulação")
        self.add_widget(btn)
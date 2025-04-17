from ui.mainWindow.MainWindows import *

class ConfigRobotsPage(BasicPage):
    def __init__(self):
        super().__init__("Simulador: Configuração dos robôs", QIcon("src/assets/robot.png"))

        
        # Adicionando um texto e botão como exemplo
        self.add_widget(QLabel("Bem-vindo ao simulador!"))

        btn = QPushButton("Iniciar simulação")
        self.add_widget(btn)
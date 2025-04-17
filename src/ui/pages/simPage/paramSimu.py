from ui.mainWindow.MainWindows import *

class ParamSimuPage(BasicPage):
    def __init__(self):
        super().__init__("Simulador: Parâmetros da Simulação", QIcon("src/assets/control-panel.png"))

        
        # Adicionando um texto e botão como exemplo
        self.add_widget(QLabel("Bem-vindo ao simulador!"))

        btn = QPushButton("Iniciar simulação")
        self.add_widget(btn)
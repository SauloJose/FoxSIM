from ui.pages.objects.pageObjects import *


class COMSysPage(BasicPage):
    def __init__(self):
        super().__init__("Comunicação: comunicação entre os sistemas", QIcon("src/assets/USB.png"))

        # Adicionando um texto e botão como exemplo
        self.add_widget(QLabel("Bem-vindo ao simulador!"))

        btn = QPushButton("Iniciar simulação")
        self.add_widget(btn)
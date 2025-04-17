from ui.pages.objects.pageObjects import *


class CTstrategyPage(BasicPage):
    def __init__(self):
        super().__init__("Controle: Seleção de estratégia", QIcon("src/assets/PID.png"))

        # Adicionando um texto e botão como exemplo
        self.add_widget(QLabel("Bem-vindo ao simulador!"))

        btn = QPushButton("Iniciar simulação")
        self.add_widget(btn)
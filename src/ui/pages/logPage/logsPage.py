from ui.pages.objects.pageObjects import *


class LogPage(BasicPage):
    def __init__(self):
        super().__init__("Monitoramento: LOGs e Alertas do sistema", QIcon("src/assets/simulation.png"))

        # Adicionando um texto e botão como exemplo
        self.add_widget(QLabel("Bem-vindo ao simulador!"))

        btn = QPushButton("Iniciar simulação")
        self.add_widget(btn)
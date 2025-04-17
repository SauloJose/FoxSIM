from ui.pages.objects.pageObjects import *


class CTneuralPage(BasicPage):
    def __init__(self):
        super().__init__("Controle: Redes Neurais", QIcon("src/assets/IA.png"))

        
        # Adicionando um texto e botão como exemplo
        self.add_widget(QLabel("Bem-vindo ao simulador!"))

        btn = QPushButton("Iniciar simulação")
        self.add_widget(btn)
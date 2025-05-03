from ui.pages.objects.pageObjects import *


class COMrobotPage(BasicPage):
    def __init__(self):
        super().__init__("Comunicação: comunicação entre os robôs", QIcon("src/assets/USB.png"))

        # Explanation section
        explanation_label = QLabel(
            "Nesta página, você pode configurar os protocolos de comunicação entre os robôs e ajustar as configurações "
            "de rede. Isso inclui a escolha de protocolos e parâmetros de conexão."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.add_widget(explanation_label)

        # Form layout
        form_layout = QHBoxLayout()

        # Left column: Communication protocols
        left_column = QVBoxLayout()
        left_column.addWidget(QLabel("<b>Protocolos de Comunicação:</b>"))
        left_column.addWidget(QLabel("Protocolo 1:"))
        left_column.addWidget(QLineEdit())
        left_column.addWidget(QLabel("Protocolo 2:"))
        left_column.addWidget(QLineEdit())

        # Right column: Network settings
        right_column = QVBoxLayout()
        right_column.addWidget(QLabel("<b>Configurações de Rede:</b>"))
        right_column.addWidget(QLabel("Endereço IP:"))
        right_column.addWidget(QLineEdit())
        right_column.addWidget(QLabel("Porta:"))
        right_column.addWidget(QLineEdit())

        form_layout.addLayout(left_column)
        form_layout.addLayout(right_column)

        # Add form to the page
        self.add_layout(form_layout)

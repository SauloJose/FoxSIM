from ui.pages.objects.pageObjects import *


class COMSysPage(BasicPage):
    def __init__(self):
        super().__init__("Comunicação: comunicação entre os sistemas", QIcon("src/assets/USB.png"))

        # Explanation section
        explanation_label = QLabel(
            "Nesta página, você pode configurar os protocolos de comunicação entre os sistemas e ajustar as configurações "
            "de sincronização de dados. Isso é essencial para garantir a troca de informações entre diferentes módulos."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.add_widget(explanation_label)

        # Form layout
        form_layout = QHBoxLayout()

        # Left column: System communication protocols
        left_column = QVBoxLayout()
        left_column.addWidget(QLabel("<b>Protocolos de Comunicação:</b>"))
        left_column.addWidget(QLabel("Protocolo A:"))
        left_column.addWidget(QLineEdit())
        left_column.addWidget(QLabel("Protocolo B:"))
        left_column.addWidget(QLineEdit())

        # Right column: Data synchronization settings
        right_column = QVBoxLayout()
        right_column.addWidget(QLabel("<b>Configurações de Sincronização:</b>"))
        right_column.addWidget(QLabel("Intervalo de Sincronização (ms):"))
        right_column.addWidget(QLineEdit())
        right_column.addWidget(QLabel("Tamanho do Buffer (MB):"))
        right_column.addWidget(QLineEdit())

        form_layout.addLayout(left_column)
        form_layout.addLayout(right_column)

        # Add form to the page
        self.add_layout(form_layout)
from ui.pages.objects.pageObjects import *


class CTstrategyPage(BasicPage):
    def __init__(self):
        super().__init__("Controle: Seleção de estratégia", QIcon("src/assets/PID.png"))

        # Explanation section
        explanation_label = QLabel("Nesta página, você pode selecionar e configurar estratégias de controle.")
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.add_widget(explanation_label)

        # Form layout
        form_layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(QLabel("<b>Estratégia 1:</b>"))
        left_column.addWidget(QLineEdit())
        left_column.addWidget(QLabel("<b>Estratégia 2:</b>"))
        left_column.addWidget(QLineEdit())

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(QLabel("<b>Estratégia 3:</b>"))
        right_column.addWidget(QLineEdit())
        right_column.addWidget(QLabel("<b>Estratégia 4:</b>"))
        right_column.addWidget(QLineEdit())

        form_layout.addLayout(left_column)
        form_layout.addLayout(right_column)

        # Add form to the page
        self.add_layout(form_layout)
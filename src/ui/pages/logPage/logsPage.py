from ui.pages.objects.pageObjects import *


class LogPage(BasicPage):
    def __init__(self):
        super().__init__("Monitoramento: LOGs e Alertas do sistema", QIcon("src/assets/simulation.png"))

        # Explanation section
        explanation_label = QLabel(
            "Nesta página, você pode configurar os filtros para os logs do sistema e visualizar os logs principais "
            "em tempo real. Isso ajuda a monitorar o comportamento do sistema e identificar problemas rapidamente."
        )
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.add_widget(explanation_label)

        # Form layout
        form_layout = QHBoxLayout()

        # Left column: Log filtering
        left_column = QVBoxLayout()
        left_column.addWidget(QLabel("<b>Filtros de Logs:</b>"))
        left_column.addWidget(QLabel("Nível de Log:"))
        left_column.addWidget(QLineEdit())
        left_column.addWidget(QLabel("Palavras-chave:"))
        left_column.addWidget(QLineEdit())
        left_column.addWidget(QLabel("Formato do Log:"))
        left_column.addWidget(QLineEdit())

        # Right column: Terminal-like display
        right_column = QVBoxLayout()
        right_column.addWidget(QLabel("<b>Terminal de Logs:</b>"))
        terminal_display = QFrame()
        terminal_display.setStyleSheet("background-color: black; color: white; border: 1px solid gray;")
        terminal_display.setFixedHeight(300)
        terminal_layout = QVBoxLayout(terminal_display)
        terminal_label = QLabel("Logs do sistema aparecerão aqui...")
        terminal_label.setStyleSheet("color: white; font-family: monospace;")
        terminal_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        terminal_layout.addWidget(terminal_label)
        right_column.addWidget(terminal_display)

        form_layout.addLayout(left_column)
        form_layout.addLayout(right_column)

        # Add form to the page
        self.add_layout(form_layout)
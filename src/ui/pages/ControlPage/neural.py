from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QIcon
from ui.pages.objects.pageObjects import *


class CTneuralPage(BasicPage):
    def __init__(self):
        super().__init__("Controle: Redes Neurais", QIcon("src/assets/IA.png"))

        # Explanation section
        explanation_label = QLabel("Nesta página, você pode configurar os parâmetros relacionados às redes neurais.")
        explanation_label.setWordWrap(True)
        explanation_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        self.add_widget(explanation_label)

        # Form layout
        form_layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        left_column.addWidget(QLabel("<b>Parâmetro 1:</b>"))
        left_column.addWidget(QLineEdit())
        left_column.addWidget(QLabel("<b>Parâmetro 2:</b>"))
        left_column.addWidget(QLineEdit())

        # Right column
        right_column = QVBoxLayout()
        right_column.addWidget(QLabel("<b>Parâmetro 3:</b>"))
        right_column.addWidget(QLineEdit())
        right_column.addWidget(QLabel("<b>Parâmetro 4:</b>"))
        right_column.addWidget(QLineEdit())

        form_layout.addLayout(left_column)
        form_layout.addLayout(right_column)

        # Add form to the page
        self.add_layout(form_layout)
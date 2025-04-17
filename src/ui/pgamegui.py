import sys
import pygame
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, 
    QLabel, QPushButton, QHBoxLayout, QSplitter, QStackedWidget, QFrame, QStyle,QStyleFactory
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPainter

# Função auxiliar para criar o widget indicador (o "espaço em branco")
def create_indicator(text):
    indicator = QFrame()
    indicator.setFixedHeight(50)
    # Estilo: fundo branco com borda inferior para destacar
    indicator.setStyleSheet("background-color: white; border-bottom: 2px solid #cccccc;")
    layout = QHBoxLayout(indicator)
    layout.setContentsMargins(10, 0, 0, 0)
    label = QLabel(text)
    label.setStyleSheet("font-weight: bold;")
    layout.addWidget(label)
    return indicator

# Widget customizado com suporte ao Pygame para a Página 1
class PygameWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Inicializa o Pygame e cria uma superfície para renderização
        pygame.init()
        # Define um tamanho fixo para a área de desenho (ajuste conforme necessário)
        self.surface = pygame.Surface((800, 400))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pygame)
        self.timer.start(16)  # Aproximadamente 60 FPS

    def update_pygame(self):
        # Exemplo de atualização: limpar o fundo e desenhar um círculo animado
        self.surface.fill((0, 0, 0))
        pygame.draw.circle(self.surface, (255, 0, 0), (400, 200), 50)
        self.update()  # Solicita a atualização do widget (chama paintEvent)

    def paintEvent(self, event):
        # Converte a superfície do Pygame para um array e ajusta a orientação
        arr = pygame.surfarray.array3d(self.surface)
        arr = np.rot90(arr)  # Corrige a orientação
        height, width, channels = arr.shape
        # Converter o array para bytes
        data = arr.tobytes()
        # Cria um QImage a partir dos bytes do array
        image = QImage(data, width, height, width * channels, QImage.Format_RGB888)
        painter = QPainter(self)
        painter.drawImage(0, 0, image)
        painter.end()

# Definição das páginas (cada uma é uma classe separada)
class Page1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Indicador para mostrar que esta é a Página 1 ativa
        layout.addWidget(create_indicator("Página 1 Ativa"))
        # Adiciona o widget do Pygame para renderização de gráficos
        pygame_widget = PygameWidget(self)
        layout.addWidget(pygame_widget)
        # Botão extra para demonstração
        layout.addWidget(QPushButton("Botão P1"))

class Page1_1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 1.1 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 1.1"))
        layout.addWidget(QPushButton("Botão P1_1"))

class Page1_2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 1.2 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 1.2"))
        layout.addWidget(QPushButton("Botão P1_2"))

class Page2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Página 2 Ativa"))
        layout.addWidget(QLabel("Você está na Página 2"))
        layout.addWidget(QPushButton("Botão P2"))

class Page2_1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 2.1 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 2.1"))
        layout.addWidget(QPushButton("Botão P2_1"))

class Page2_2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 2.2 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 2.2"))
        layout.addWidget(QPushButton("Botão P2_2"))

class Page3(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Página 3 Ativa"))
        layout.addWidget(QLabel("Você está na Página 3"))
        layout.addWidget(QPushButton("Botão P3"))

class Page3_1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 3.1 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 3.1"))
        layout.addWidget(QPushButton("Botão P3_1"))

class Page3_2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 3.2 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 3.2"))
        layout.addWidget(QPushButton("Botão P3_2"))

class Page4(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Página 3 Ativa"))
        layout.addWidget(QLabel("Você está na Página 3"))
        layout.addWidget(QPushButton("Botão P3"))

class Page4_1(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 3.1 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 3.1"))
        layout.addWidget(QPushButton("Botão P3_1"))

class Page4_2(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 3.2 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 3.2"))
        layout.addWidget(QPushButton("Botão P3_2"))


class Page5(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(create_indicator("Subpágina 3.2 Ativa"))
        layout.addWidget(QLabel("Você está na Subpágina 3.2"))
        layout.addWidget(QPushButton("Botão P3_2"))

# Janela principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SysFox - Sistema de Controle e Visão para VSSS ')
        self.setFixedSize(1400, 900)
        self.setWindowIcon(QIcon("src/assets/logo_minus.png"))

        # Criação da barra de menus no topo
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Arquivo")
        edit_menu = menu_bar.addMenu("Editar")
        view_menu = menu_bar.addMenu("Visualizar")
        help_menu = menu_bar.addMenu("Ajuda")

        # Exemplo de ação na barra de menus: Sair (fecha a aplicação)
        exit_action = file_menu.addAction("Sair")
        exit_action.triggered.connect(self.close)

        splitter = QSplitter(Qt.Horizontal)

        # Criação do menu de navegação (árvore) no lado esquerdo
        tree_widget = QTreeWidget()
        tree_widget.setHeaderLabel('   Visão Geral do Sistema')
        tree_widget.setFixedWidth(300)

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.astyle = self.style()


        # Simulador
        sim_item = QTreeWidgetItem(tree_widget, ['Simulador'])
        sim_item.setIcon(0, QIcon("src/assets/ATGK.png"))  # Pasta
        QTreeWidgetItem(sim_item, ['Visualização']).setIcon(0, QIcon("src/assets/statistics.png"))  # Tela azul - index 0
        QTreeWidgetItem(sim_item, ['Configuração de Robôs']).setIcon(0,QIcon("src/assets/robot.png") )  # Ícone de drive - index 1
        QTreeWidgetItem(sim_item, ['Parâmetros da simulação']).setIcon(0,QIcon("src/assets/control-panel.png"))  # Ícone de drive - index 2
        sim_item.setExpanded(True)

        # Sistema de Visão
        vision_item = QTreeWidgetItem(tree_widget, ['Sistema de Visão'])
        vision_item.setIcon(0, QIcon("src/assets/vision.png"))  # Pasta
        QTreeWidgetItem(vision_item, ['Visualização']).setIcon(0, QIcon("src/assets/statistics.png"))  # Tela azul - index 3

        # Subgrupo de configurações
        vis_conf = QTreeWidgetItem(vision_item, ['Configurações'])
        vis_conf.setIcon(0, QIcon("src/assets/config.png"))  # Ícone de drive
        QTreeWidgetItem(vis_conf, ['Entrada de dados']).setIcon(0,QIcon("src/assets/USB.png"))  # Ícone de drive - index 4
        QTreeWidgetItem(vis_conf, ['Calibração']).setIcon(0, QIcon("src/assets/control-panel.png"))  # Ícone de drive - index 5
        QTreeWidgetItem(vis_conf, ['Otimização']).setIcon(0, QIcon("src/assets/control-panel.png"))  # Ícone de drive - index 6
        QTreeWidgetItem(vis_conf, ['Identificação de Cores']).setIcon(0,QIcon("src/assets/control-panel.png" ))  # Ícone de drive - index 7
        vision_item.setExpanded(True)
        vis_conf.setExpanded(True)

        # Controle
        ctrl_item = QTreeWidgetItem(tree_widget, ['Controle'])
        ctrl_item.setIcon(0, QIcon("src/assets/control.png"))  # Pasta
        QTreeWidgetItem(ctrl_item, ['Redes Neurais']).setIcon(0,QIcon("src/assets/IA.png" ))  # Ícone de drive - index 8
        QTreeWidgetItem(ctrl_item, ['Estratégias de Controle']).setIcon(0, QIcon("src/assets/PID.png"))  # Ícone de drive - index 9
        ctrl_item.setExpanded(True)

        # Comunicação
        com_item = QTreeWidgetItem(tree_widget, ['Comunicação'])
        com_item.setIcon(0, QIcon("src/assets/message.png"))  # Pasta
        QTreeWidgetItem(com_item, ['Entre Robôs']).setIcon(0,QIcon("src/assets/USB.png" ))  # Ícone de rede - index 10
        QTreeWidgetItem(com_item, ['Entre Sistemas']).setIcon(0,QIcon("src/assets/USB.png" ))  # Ícone de rede - index 11
        com_item.setExpanded(True)

        # Monitoramento
        mon_item = QTreeWidgetItem(tree_widget, ['Monitoramento'])
        mon_item.setIcon(0,QIcon("src/assets/monitor.png") )  # Pasta
        QTreeWidgetItem(mon_item, ['LOGs']).setIcon(0,QIcon("src/assets/simulation.png" ))  # Ícone de drive - index 12

        mon_item.setExpanded(True)



        # Criação do QStackedWidget para alternar entre as páginas
        self.stack = QStackedWidget()
        self.stack.addWidget(Page1())      # index 0 -> Simulador > Visualização
        self.stack.addWidget(Page1_1())    # index 1 -> Simulador > Configuração de Robôs
        self.stack.addWidget(Page1_2())    # index 2 -> Simulador > Parâmetros Gerais
        self.stack.addWidget(Page2())      # index 3 -> Sistema de Visão > Visualização
        self.stack.addWidget(Page2_1())    # index 4 -> Sistema de Visão > Câmera
        self.stack.addWidget(Page2_2())    # index 5 -> Sistema de Visão > Calibração
        self.stack.addWidget(Page3())      # index 6 -> Sistema de Visão > Otimização
        self.stack.addWidget(Page3_1())    # index 7 -> Sistema de Visão > Identificação de Cores
        self.stack.addWidget(Page3_2())    # index 8 -> Controle > Redes Neurais
        self.stack.addWidget(Page4())      # index 9 -> Controle > Estratégias de Controle
        self.stack.addWidget(Page4_1())    # index 10 -> Comunicação > Entre Robôs
        self.stack.addWidget(Page4_2())    # index 11 -> Comunicação > Entre Sistemas
        self.stack.addWidget(Page5())      # index 12 -> Monitoramento > Configuração de Gráficos

        splitter.addWidget(tree_widget)
        splitter.addWidget(self.stack)
        self.setCentralWidget(splitter)

        # Conecta o clique no menu à mudança de página
        tree_widget.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item, column):
        mapping = {
            'Simulador': {
                'Visualização': 0,
                'Configuração de Robôs': 1,
                'Parâmetros Gerais': 2,
            },
            'Sistema de Visão': {
                'Visualização': 3,
            },
            'Configurações': {
                'Câmera': 4,
                'Calibração': 5,
                'Otimização': 6,
                'Identificação de Cores': 7,
            },
            'Controle': {
                'Redes Neurais': 8,
                'Estratégias de Controle': 9,
            },
            'Comunicação': {
                'Entre Robôs': 10,
                'Entre Sistemas': 11,
            },
            'Monitoramento': {
                'Configuração de Gráficos': 12,
            },
        }

        parent = item.parent()
        if parent:
            parent_text = parent.text(0)
            child_text = item.text(0)
            if parent_text in mapping and child_text in mapping[parent_text]:
                self.stack.setCurrentIndex(mapping[parent_text][child_text])
        else:
            text = item.text(0)
            if text in mapping and None in mapping[text]:
                self.stack.setCurrentIndex(mapping[text][None])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("src/assets/logo_minus.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

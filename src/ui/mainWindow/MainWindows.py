import sys
import pygame
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, 
    QLabel, QPushButton, QHBoxLayout, QSplitter, QStackedWidget, QFrame, QStyle,QStyleFactory
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QImage, QPainter

#Puxando as páginas da aplicação do simulador
from ui.pages.simPage.viewPage import *
from ui.pages.simPage.paramSimu import *
from ui.pages.simPage.configRobots import *

from ui.pages.comPage.comRobots import *
from ui.pages.comPage.comSys    import *

from ui.pages.ControlPage.neural      import *
from ui.pages.ControlPage.strategy      import *

from ui.pages.logPage.logsPage          import *

from ui.pages.VSpage.view           import *
from ui.pages.VSpage.configs.calibration     import *
from ui.pages.VSpage.configs.colors          import *
from ui.pages.VSpage.configs.entry          import *




# Janela principal
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SyFox - Sistema de Controle e Visão para VSSS ')
        self.setFixedSize(1400, 900)
        self.setWindowIcon(QIcon("src/assets/logo_minus.png"))

        self.create_menu_bar()

        self.create_menu_navegate()

        self.stack =QStackedWidget()


    def create_menu_bar(self):
        '''
            Cria menu superior da aplicação
        '''
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Arquivo")
        edit_menu = menu_bar.addMenu("Editar")
        view_menu = menu_bar.addMenu("Visualizar")
        help_menu = menu_bar.addMenu("Ajuda")

        # Exemplo de ação na barra de menus: Sair (fecha a aplicação)
        exit_action = file_menu.addAction("Sair")
        exit_action.triggered.connect(self.close)
    
    def create_menu_navegate(self):
        '''
            Cria menu de navegação da aplicação
        '''
        self.splitter = QSplitter(Qt.Horizontal)

        # Criação do menu de navegação (árvore) no lado esquerdo
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel('Menu')
        self.tree_widget.setFixedWidth(300)

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.style = self.style()


        # Simulador
        sim_item = QTreeWidgetItem(self.tree_widget, ['Simulador'])
        sim_item.setIcon(0, QIcon("src/assets/ATGK.png"))  # Pasta
        QTreeWidgetItem(sim_item, ['Visualização']).setIcon(0, QIcon("src/assets/statistics.png"))  # Tela azul - index 0
        QTreeWidgetItem(sim_item, ['Configuração de Robôs']).setIcon(0,QIcon("src/assets/robot.png") )  # Ícone de drive - index 1
        QTreeWidgetItem(sim_item, ['Parâmetros da simulação']).setIcon(0,QIcon("src/assets/control-panel.png"))  # Ícone de drive - index 2
        sim_item.setExpanded(True)

        # Sistema de Visão
        vision_item = QTreeWidgetItem(self.tree_widget, ['Sistema de Visão'])
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
        ctrl_item = QTreeWidgetItem(self.tree_widget, ['Controle'])
        ctrl_item.setIcon(0, QIcon("src/assets/control.png"))  # Pasta
        QTreeWidgetItem(ctrl_item, ['Redes Neurais']).setIcon(0,QIcon("src/assets/IA.png" ))  # Ícone de drive - index 8
        QTreeWidgetItem(ctrl_item, ['Estratégias de Controle']).setIcon(0, QIcon("src/assets/PID.png"))  # Ícone de drive - index 9
        ctrl_item.setExpanded(True)

        # Comunicação
        com_item = QTreeWidgetItem(self.tree_widget, ['Comunicação'])
        com_item.setIcon(0, QIcon("src/assets/message.png"))  # Pasta
        QTreeWidgetItem(com_item, ['Entre Robôs']).setIcon(0,QIcon("src/assets/USB.png" ))  # Ícone de rede - index 10
        QTreeWidgetItem(com_item, ['Entre Sistemas']).setIcon(0,QIcon("src/assets/USB.png" ))  # Ícone de rede - index 11
        com_item.setExpanded(True)

        # Monitoramento
        mon_item = QTreeWidgetItem(self.tree_widget, ['Monitoramento'])
        mon_item.setIcon(0,QIcon("src/assets/monitor.png") )  # Pasta
        QTreeWidgetItem(mon_item, ['LOGs']).setIcon(0,QIcon("src/assets/simulation.png" ))  # Ícone de drive - index 12


        # Criação do QStackedWidget para alternar entre as páginas
        self.stack = QStackedWidget()
        self.stack.addWidget(SimulationViewPage())      # index 0 -> Simulador > Visualização
        self.stack.addWidget(SimulationViewPage())    # index 1 -> Simulador > Configuração de Robôs
        self.stack.addWidget(SimulationViewPage())    # index 2 -> Simulador > Parâmetros Gerais
        self.stack.addWidget(SimulationViewPage())      # index 3 -> Sistema de Visão > Visualização
        self.stack.addWidget(SimulationViewPage())    # index 4 -> Sistema de Visão > Câmera
        self.stack.addWidget(SimulationViewPage())    # index 5 -> Sistema de Visão > Calibração
        self.stack.addWidget(SimulationViewPage())      # index 6 -> Sistema de Visão > Otimização
        self.stack.addWidget(SimulationViewPage())    # index 7 -> Sistema de Visão > Identificação de Cores
        self.stack.addWidget(SimulationViewPage())    # index 8 -> Controle > Redes Neurais
        self.stack.addWidget(SimulationViewPage())      # index 9 -> Controle > Estratégias de Controle
        self.stack.addWidget(SimulationViewPage())    # index 10 -> Comunicação > Entre Robôs
        self.stack.addWidget(SimulationViewPage())    # index 11 -> Comunicação > Entre Sistemas
        self.stack.addWidget(SimulationViewPage())      # index 12 -> Monitoramento > Configuração de Gráficos

        self.splitter.addWidget(self.tree_widget)
        self.splitter.addWidget(self.stack)
        self.setCentralWidget(self.splitter)

        # Conectar o click à mudança de página
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
    
    def on_item_clicked(self, item, column):
        # Se o item possui pai, é um submenu
        if item.parent() is not None:
            parent_text = item.parent().text(0)
            child_text = item.text(0)
            if parent_text == 'Página 1':
                if child_text == 'Subpágina 1.1':
                    self.stack.setCurrentIndex(1)
                elif child_text == 'Subpágina 1.2':
                    self.stack.setCurrentIndex(2)
            elif parent_text == 'Página 2':
                if child_text == 'Subpágina 2.1':
                    self.stack.setCurrentIndex(4)
                elif child_text == 'Subpágina 2.2':
                    self.stack.setCurrentIndex(5)
            elif parent_text == 'Página 3':
                if child_text == 'Subpágina 3.1':
                    self.stack.setCurrentIndex(7)
                elif child_text == 'Subpágina 3.2':
                    self.stack.setCurrentIndex(8)
        else:
            text = item.text(0)
            if text == 'Página 1':
                self.stack.setCurrentIndex(0)
            elif text == 'Página 2':
                self.stack.setCurrentIndex(3)
            elif text == 'Página 3':
                self.stack.setCurrentIndex(6)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("src/assets/logo_minus.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
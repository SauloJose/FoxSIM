import sys
import pygame
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, 
    QLabel, QPushButton, QHBoxLayout, QSplitter, QStackedWidget, QFrame, QStyle,QStyleFactory
)

from PyQt5.QtCore import Qt, QTimer,QSize
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
from ui.pages.VSpage.configs.otm            import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Informações básicas da maior janela
        self.setWindowTitle('SyFox - Sistema de Controle e Visão para VSSS ')
        self.setWindowIcon(QIcon("src/assets/logo_minus.png"))

        self.showMaximized()

        self.setFixedSize(self.size())


        self.create_menu_bar()

        self.create_menu_navegate()



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
        '''Cria menu de navegação da aplicação'''
        self.splitter = QSplitter(Qt.Horizontal)

        # Criação do menu de navegação (árvore) no lado esquerdo
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel('Menu de Navegação')
        self.tree_widget.setFixedWidth(350)
        
        # Aumenta o tamanho dos ícones
        self.tree_widget.setIconSize(QSize(32, 32))  # Pode ajustar o tamanho

        # Acesso ao cabeçalho
        header = self.tree_widget.header()

        # Estilo do cabeçalho
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #333;
                font-weight: bold;
                font-size: 18px;
                padding: 6px;
                border: 1px solid #ccc;
            }
        """)

        # Centraliza o texto do cabeçalho (opcional)
        header.setDefaultAlignment(Qt.AlignCenter)

        # Estilo
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.style = self.style()

        # Mapeamento de ícones
        self.icons = {
            "Simulador": "src/assets/ATGK.png",
            "Visualização": "src/assets/statistics.png",
            "Configuração de Robôs": "src/assets/robot.png",
            "Parâmetros da simulação": "src/assets/control-panel.png",
            "Sistema de Visão": "src/assets/vision.png",
            "Entrada de dados": "src/assets/USB.png",
            "Calibração": "src/assets/control-panel.png",
            "Otimização": "src/assets/control-panel.png",
            "Identificação de Cores": "src/assets/control-panel.png",
            "Controle": "src/assets/control.png",
            "Redes Neurais": "src/assets/IA.png",
            "Estratégias de Controle": "src/assets/PID.png",
            "Comunicação": "src/assets/message.png",
            "Entre Robôs": "src/assets/USB.png",
            "Entre Sistemas": "src/assets/USB.png",
            "Monitoramento": "src/assets/monitor.png",
            "LOGs": "src/assets/simulation.png"
        }

        # Mapa do menu
        self.page_map = {
                # Simulador
                "Simulador > Visualização": 0,
                "Simulador > Configuração de Robôs": 1,
                "Simulador > Parâmetros da simulação": 2,

                # Sistema de Visão
                "Sistema de Visão > Visualização": 3,
                "Sistema de Visão > Configurações > Entrada de dados": 4,
                "Sistema de Visão > Configurações > Calibração": 5,
                "Sistema de Visão > Configurações > Otimização": 6,
                "Sistema de Visão > Configurações > Identificação de Cores": 7,

                # Controle
                "Controle > Redes Neurais": 8,
                "Controle > Estratégias de Controle": 9,

                # Comunicação
                "Comunicação > Entre Robôs": 10,
                "Comunicação > Entre Sistemas": 11,

                # Monitoramento
                "Monitoramento > LOGs": 12
            }


        # Função para adicionar ícones aos itens
        def add_item(parent, text, icon_key):
            item = QTreeWidgetItem(parent, [text])
            item.setIcon(0, QIcon(self.icons[icon_key]))
            return item

        # Simulador
        sim_item = QTreeWidgetItem(self.tree_widget, ['Simulador'])
        sim_item.setIcon(0, QIcon(self.icons["Simulador"]))
        add_item(sim_item, 'Visualização', 'Visualização')
        add_item(sim_item, 'Configuração de Robôs', 'Configuração de Robôs')
        add_item(sim_item, 'Parâmetros da simulação', 'Parâmetros da simulação')
        sim_item.setExpanded(True)

        # Sistema de Visão
        vision_item = QTreeWidgetItem(self.tree_widget, ['Sistema de Visão'])
        vision_item.setIcon(0, QIcon(self.icons["Sistema de Visão"]))
        add_item(vision_item, 'Visualização', 'Visualização')
        vis_conf = QTreeWidgetItem(vision_item, ['Configurações'])
        vis_conf.setIcon(0, QIcon(self.icons["Calibração"]))
        add_item(vis_conf, 'Entrada de dados', 'Entrada de dados')
        add_item(vis_conf, 'Calibração', 'Calibração')
        add_item(vis_conf, 'Otimização', 'Otimização')
        add_item(vis_conf, 'Identificação de Cores', 'Identificação de Cores')
        vision_item.setExpanded(True)
        vis_conf.setExpanded(True)

        # Controle
        ctrl_item = QTreeWidgetItem(self.tree_widget, ['Controle'])
        ctrl_item.setIcon(0, QIcon(self.icons["Controle"]))
        add_item(ctrl_item, 'Redes Neurais', 'Redes Neurais')
        add_item(ctrl_item, 'Estratégias de Controle', 'Estratégias de Controle')
        ctrl_item.setExpanded(True)

        # Comunicação
        com_item = QTreeWidgetItem(self.tree_widget, ['Comunicação'])
        com_item.setIcon(0, QIcon(self.icons["Comunicação"]))
        add_item(com_item, 'Entre Robôs', 'Entre Robôs')
        add_item(com_item, 'Entre Sistemas', 'Entre Sistemas')
        com_item.setExpanded(True)

        # Monitoramento
        mon_item = QTreeWidgetItem(self.tree_widget, ['Monitoramento'])
        mon_item.setIcon(0, QIcon(self.icons["Monitoramento"]))
        add_item(mon_item, 'LOGs', 'LOGs')

        # Criação do QStackedWidget para alternar entre as páginas
        self.stack = QStackedWidget()
        self.add_pages_to_stack()

        self.splitter.addWidget(self.tree_widget)
        self.splitter.addWidget(self.stack)
        self.setCentralWidget(self.splitter)

        # Conectar o click à mudança de página
        self.tree_widget.itemClicked.connect(self.on_item_clicked)

    def add_pages_to_stack(self):
        self.stack.addWidget(SimulationViewPage())      # index 0 -> Simulador > Visualização
        self.stack.addWidget(ConfigRobotsPage())    # index 1 -> Simulador > Configuração de Robôs
        self.stack.addWidget(ParamSimuPage())    # index 2 -> Simulador > Parâmetros Gerais
        self.stack.addWidget(VSVisionPage())      # index 3 -> Sistema de Visão > Visualização
        self.stack.addWidget(VSEntryDataPage())    # index 4 -> Sistema de Visão > Câmera
        self.stack.addWidget(VSCalibrationPage())    # index 5 -> Sistema de Visão > Calibração
        self.stack.addWidget(VSOtimizationPage())      # index 6 -> Sistema de Visão > Otimização
        self.stack.addWidget(VSselectColor())    # index 7 -> Sistema de Visão > Identificação de Cores
        self.stack.addWidget(CTneuralPage())    # index 8 -> Controle > Redes Neurais
        self.stack.addWidget(CTstrategyPage())      # index 9 -> Controle > Estratégias de Controle
        self.stack.addWidget(COMrobotPage())    # index 10 -> Comunicação > Entre Robôs
        self.stack.addWidget(COMSysPage())    # index 11 -> Comunicação > Entre Sistemas
        self.stack.addWidget(LogPage())      # index 12 -> Monitoramento > Configuração de Gráficos

    def on_item_clicked(self, item, column):
        texts = []
        current = item
        while current is not None:
            texts.insert(0, current.text(0))
            current = current.parent()
        
        path = " > ".join(texts)

        if path in self.page_map:
            self.stack.setCurrentIndex(self.page_map[path])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("src/assets/logo_minus.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
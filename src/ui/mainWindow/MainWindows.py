import sys
import numpy as np
from PyQt6.QtWidgets import *

from PyQt6.QtCore import *
from PyQt6.QtGui import *

from ui.pages.objects.pageObjects import *

#Puxando as páginas da aplicação do simulador
from ui.pages.simPage.viewPage import SimulationViewPage  # Certifique-se de que a classe está corretamente importada
from ui.pages.simPage.paramSimu import ParamSimuPage
from ui.pages.simPage.configRobots import ConfigRobotsPage

from ui.pages.comPage.comRobots import COMrobotPage
from ui.pages.comPage.comSys import COMSysPage

from ui.pages.ControlPage.neural import CTneuralPage
from ui.pages.ControlPage.strategy import CTstrategyPage
from ui.pages.ControlPage.PIDcontrol import CTPIDControlPage  # ADICIONADO

from ui.pages.logPage.logsPage import LogPage

from ui.pages.VSpage.view import VSVisionPage
from ui.pages.VSpage.configs.calibration import VSCalibrationPage
from ui.pages.VSpage.configs.colors import VSselectColor
from ui.pages.VSpage.configs.entry import VSEntryDataPage
from ui.pages.VSpage.configs.otm import VSOtimizationPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #Informações básicas da maior janela
        self.setWindowTitle('SyFox - Sistema de Controle e Visão para VSSS - Por: Saulo José')
        self.setWindowIcon(QIcon("src/assets/logo_minus.png"))
        self.setMinimumSize(1600, 900)
        self.showMaximized()

        self.create_menu_bar()  
        self.create_menu_navegate()

        # Lazy loading: dicionário para instâncias das páginas
        self.page_instances = {}
        self.page_classes = [
            SimulationViewPage, ConfigRobotsPage, ParamSimuPage, VSVisionPage,
            VSEntryDataPage, VSCalibrationPage, VSOtimizationPage, VSselectColor,
            CTneuralPage, CTPIDControlPage, CTstrategyPage, COMrobotPage, COMSysPage, LogPage
        ]

        # Cria e exibe a página inicial (Simulador > Visualização)
        self.show_initial_page()

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
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

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
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        # Estilo
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.style = self.style()

        # Mapeamento de ícones
        self.icons = {
            "Simulador": "src/assets/SIM.png",
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
            "Configuração PID": "src/assets/PID.png",
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
                "Controle > Configuração PID": 9,
                "Controle > Estratégias de Controle": 10,

                # Comunicação
                "Comunicação > Entre Robôs": 11,
                "Comunicação > Entre Sistemas": 12,

                # Monitoramento
                "Monitoramento > LOGs": 13
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
        add_item(ctrl_item, 'Configuração PID', 'Configuração PID')  # NOVA LINHA
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
        # Adiciona widgets vazios como placeholders
        for _ in range(len(self.page_map)):
            self.stack.addWidget(QWidget())
        self.splitter.addWidget(self.tree_widget)
        self.splitter.addWidget(self.stack)
        self.setCentralWidget(self.splitter)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)

    def show_initial_page(self):
        # Página inicial: Simulador > Visualização (índice 0)
        idx = 0
        page = self.page_classes[idx]()
        self.page_instances[idx] = page
        self.stack.insertWidget(idx, page)
        self.stack.setCurrentIndex(idx)
        # Seleciona o item correspondente na árvore
        root = self.tree_widget.topLevelItem(0)
        if root:
            root.child(0).setSelected(True)

    def add_pages_to_stack(self):
        self.stack.addWidget(SimulationViewPage())      # index 0 -> Simulador > Visualização
        self.stack.addWidget(ConfigRobotsPage())        # index 1 -> Simulador > Configuração de Robôs
        self.stack.addWidget(ParamSimuPage())           # index 2 -> Simulador > Parâmetros Gerais
        self.stack.addWidget(VSVisionPage())            # index 3 -> Sistema de Visão > Visualização
        self.stack.addWidget(VSEntryDataPage())         # index 4 -> Sistema de Visão > Entrada de dados
        self.stack.addWidget(VSCalibrationPage())       # index 5 -> Sistema de Visão > Calibração
        self.stack.addWidget(VSOtimizationPage())       # index 6 -> Sistema de Visão > Otimização
        self.stack.addWidget(VSselectColor())           # index 7 -> Sistema de Visão > Identificação de Cores
        self.stack.addWidget(CTneuralPage())            # index 8 -> Controle > Redes Neurais
        self.stack.addWidget(CTPIDControlPage())        # index 9 -> Controle > Configuração PID
        self.stack.addWidget(CTstrategyPage())          # index 10 -> Controle > Estratégias de Controle
        self.stack.addWidget(COMrobotPage())            # index 11 -> Comunicação > Entre Robôs
        self.stack.addWidget(COMSysPage())              # index 12 -> Comunicação > Entre Sistemas
        self.stack.addWidget(LogPage())                 # index 13 -> Monitoramento > LOGs

    def on_item_clicked(self, item, column):
        texts = []
        current = item
        while current is not None:
            texts.insert(0, current.text(0))
            current = current.parent()
        path = " > ".join(texts)
        if path in self.page_map:
            idx = self.page_map[path]
            # Destrói a página anterior (se não for placeholder)
            current_widget = self.stack.currentWidget()
            # Evita destruir a própria página se clicou nela mesma
            if hasattr(current_widget, "destroy") and current_widget is not self.page_instances.get(idx):
                current_widget.destroy()
                self.stack.removeWidget(current_widget)
                for k, v in list(self.page_instances.items()):
                    if v is current_widget:
                        del self.page_instances[k]
                        break
            # Cria a página se ainda não existe
            if idx not in self.page_instances:
                page = self.page_classes[idx]()
                self.page_instances[idx] = page
                self.stack.insertWidget(idx, page)
            self.stack.setCurrentIndex(idx)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("src/assets/logo_minus.png"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
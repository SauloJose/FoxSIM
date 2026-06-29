from abc import ABC, abstractmethod
from typing import Any

class ControlInterface(ABC):
    '''
        Classe básica para representar a interface de controle para o simulador.
        Todas as classes de controle precisarão ser feitas como filhos dessa classe principal
        @Saulo.
    '''
    @abstractmethod
    def initialize(self, simulator: Any) -> None:
        """Chamado quando a estratégia é carregada."""
        pass

    @abstractmethod
    def update(self, simulator: Any, dt: float) -> None:
        """
        Calcula e aplica comandos diretamente nos robôs.
        - Acessa simulator.robots, simulator.ball, etc.
        """
        pass

    @abstractmethod
    def on_event(self, simulator: Any, event: str, data: dict) -> None:
        """Reage a eventos com acesso ao simulador."""
        pass
"""
bt_core.py

Primitivas básicas de Behavior Tree (BT): Status, Node, Selector e Sequence.

A lógica funcional deste arquivo não foi alterada em relação à versão
original — apenas foram adicionadas docstrings para deixar explícito o
contrato de cada nó, já que isso é justamente o que abre espaço para o bug
mais crítico encontrado na revisão (ver bt_actions.py): nós com estado
próprio (ex.: contadores de tempo) sendo reutilizados entre múltiplos robôs.
"""


class Status:
    """Resultado de um tick de nó da árvore."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


class Node:
    """
    Nó base. Qualquer subclasse deve implementar tick().

    IMPORTANTE (arquitetura): se a MESMA instância de um nó folha for usada
    para tickar mais de um robô (ex.: uma árvore construída uma única vez
    por time, não por robô), qualquer estado guardado em `self` dentro do
    nó (contadores, temporizadores, últimas decisões etc.) deve ser mantido
    por robô — por exemplo em um dict indexado por `robot.id_robot` — nunca
    como um único valor escalar. Essa é a causa raiz do bug corrigido em
    SpinShootNode e WallClearanceSpinNode (ver bt_actions.py).
    """
    def tick(self, robot, ball, team, enemy_team, dt):
        raise NotImplementedError


class Selector(Node):
    """
    Tenta cada filho em ordem até um retornar algo diferente de FAILURE.
    Representa uma escolha por prioridade ("tente A, senão B, senão C...").
    """
    def __init__(self, children):
        self.children = children

    def tick(self, robot, ball, team, enemy_team, dt):
        for child in self.children:
            status = child.tick(robot, ball, team, enemy_team, dt)
            if status != Status.FAILURE:
                return status
        return Status.FAILURE


class Sequence(Node):
    """
    Executa cada filho em ordem enquanto todos retornarem SUCCESS.
    Representa uma cadeia de pré-condição + ação ("se A, então faça B").
    """
    def __init__(self, children):
        self.children = children

    def tick(self, robot, ball, team, enemy_team, dt):
        for child in self.children:
            status = child.tick(robot, ball, team, enemy_team, dt)
            if status != Status.SUCCESS:
                return status
        return Status.SUCCESS
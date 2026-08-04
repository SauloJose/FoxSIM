from simulator.intelligence.bt_core import Selector, Sequence
from simulator.intelligence.bt_config import (
    FIELD_LIMITS,
    WALL_MARGIN,
    DEFENSE_RADIUS,
    SUPPORT_DEFENSE_RADIUS,
    MIN_SUPPORT_TO_BALL_DIST_STANDARD,
    MIN_SUPPORT_TO_BALL_DIST_AGGRESSIVE,
)
from simulator.intelligence.bt_conditions import (
    IsRoleNode,
    IsClosestAttackerNode,
    IsBallInCornerNode,
    CanShootDirectlyNode,
    IsBallInDefenseZoneNode,
    IsNearWallNode,
)
from simulator.intelligence.bt_actions import (
    DefendGoalNode,
    AttackBallNode,
    SpinShootNode,
    UnstuckCornerNode,
    SupportAttackerNode,
    ClearBallNode,
    DefensiveWallNode,
    WallClearanceSpinNode,
)
from ui.interface_config import GOALKEEPER


def build_standard_strategy(own_goal, enemy_goal, forward_angle):
    """Estratégia Padrão com Árvore Aninhada e Hierarquia Tática."""

    # --- SUB-ÁRVORE DO GOLEIRO ---
    goalkeeper_actions = Selector([
        Sequence([IsBallInCornerNode(), UnstuckCornerNode()]),
        DefendGoalNode(own_goal=own_goal, forward_angle=forward_angle)
    ])

    goalkeeper_branch = Sequence([
        IsRoleNode(GOALKEEPER),
        goalkeeper_actions
    ])

    # --- SUB-ÁRVORE DO ATACANTE (SELECTORS ANINHADOS) ---
    # 1. Recuperações Físicas de Emergência
    attacker_recovery_selector = Selector([
        Sequence([IsBallInCornerNode(), UnstuckCornerNode()]),
        Sequence([IsNearWallNode(field_limits=FIELD_LIMITS, wall_margin=WALL_MARGIN), WallClearanceSpinNode(enemy_goal=enemy_goal)]),
    ])

    # 2. Oportunidades Claras de Gol
    attacker_scoring_selector = Selector([
        Sequence([CanShootDirectlyNode(enemy_goal=enemy_goal), SpinShootNode(enemy_goal=enemy_goal)]),
    ])

    # 3. Decisão Tática do Atacante (Hierarquia de Prioridades)
    attacker_tactical_selector = Selector([
        attacker_recovery_selector,  # Sub-seletor 1: Se estiver preso/parede, resolve primeiro
        attacker_scoring_selector,   # Sub-seletor 2: Se tem chute claro, finaliza
        AttackBallNode(enemy_goal=enemy_goal)  # Fallback: Condução e ataque padrão de frente
    ])

    primary_attacker_branch = Sequence([
        IsClosestAttackerNode(hysteresis_margin=5.0),
        attacker_tactical_selector
    ])

    # --- SUB-ÁRVORE DO SUPORTE (TRANSIÇÃO DINÂMICA) ---
    support_tactical_selector = Selector([
        # Se a bola entrar na área defensiva, o suporte vira barreira automaticamente
        Sequence([
            IsBallInDefenseZoneNode(own_goal=own_goal, defense_radius=SUPPORT_DEFENSE_RADIUS),
            DefensiveWallNode(own_goal=own_goal)
        ]),
        # Caso contrário, mantém posicionamento de suporte ao ataque, com distância
        # mínima padrão em relação à bola para não disputar espaço com o atacante
        SupportAttackerNode(own_goal=own_goal, min_ball_distance=MIN_SUPPORT_TO_BALL_DIST_STANDARD)
    ])

    # --- RAIZ DA ÁRVORE ---
    return Selector([
        goalkeeper_branch,
        primary_attacker_branch,
        support_tactical_selector
    ])


def build_defensive_strategy(own_goal, enemy_goal, forward_angle):
    """Estratégia Defensiva Aninhada: Foco em cobertura dupla e isolamento."""

    goalkeeper_branch = Sequence([
        IsRoleNode(GOALKEEPER),
        DefendGoalNode(own_goal=own_goal, forward_angle=forward_angle)
    ])

    # Atacante Defensivo: Prioriza tirar a bola da área antes de contra-atacar
    defensive_attacker_tactical = Selector([
        Sequence([IsBallInCornerNode(), UnstuckCornerNode()]),
        Sequence([IsNearWallNode(field_limits=FIELD_LIMITS, wall_margin=WALL_MARGIN), WallClearanceSpinNode(enemy_goal=enemy_goal)]),
        Sequence([IsBallInDefenseZoneNode(own_goal=own_goal, defense_radius=DEFENSE_RADIUS), ClearBallNode()]),
        AttackBallNode(enemy_goal=enemy_goal)
    ])

    primary_attacker_branch = Sequence([
        IsClosestAttackerNode(hysteresis_margin=5.0),
        defensive_attacker_tactical
    ])

    # Suporte Defensivo: Barreira constante cobrindo o gol
    defensive_support = DefensiveWallNode(own_goal=own_goal)

    return Selector([
        goalkeeper_branch,
        primary_attacker_branch,
        defensive_support
    ])


def build_aggressive_strategy(own_goal, enemy_goal, forward_angle):
    """Estratégia Agressiva Aninhada: Pressão total e chutes rápidos."""

    goalkeeper_branch = Sequence([
        IsRoleNode(GOALKEEPER),
        DefendGoalNode(own_goal=own_goal, forward_angle=forward_angle)
    ])

    aggressive_attacker_tactical = Selector([
        Sequence([CanShootDirectlyNode(enemy_goal=enemy_goal), SpinShootNode(enemy_goal=enemy_goal)]),
        Sequence([IsBallInCornerNode(), UnstuckCornerNode()]),
        Sequence([IsNearWallNode(field_limits=FIELD_LIMITS, wall_margin=WALL_MARGIN), WallClearanceSpinNode(enemy_goal=enemy_goal)]),
        AttackBallNode(enemy_goal=enemy_goal)
    ])

    primary_attacker_branch = Sequence([
        IsClosestAttackerNode(hysteresis_margin=3.5),
        aggressive_attacker_tactical
    ])

    # Suporte Agressivo: acompanha mais perto da bola para brigar pelo rebote.
    # Usa uma distância mínima menor que o padrão (ainda suficiente para não
    # sobrepor fisicamente o atacante), refletindo a intenção original do
    # comentário "aproxima para rebote" sem reabrir o risco de empurrão.
    support_branch = SupportAttackerNode(own_goal=own_goal, min_ball_distance=MIN_SUPPORT_TO_BALL_DIST_AGGRESSIVE)

    return Selector([
        goalkeeper_branch,
        primary_attacker_branch,
        support_branch
    ])
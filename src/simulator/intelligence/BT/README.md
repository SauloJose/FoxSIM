# Behavior Trees do FoxSIM

Este diretorio contem a inteligencia dos robos. Cada robo recebe uma Behavior Tree e a arvore e executada por `tick(...)` a cada atualizacao da simulacao.

A estrutura atual e:

```text
BT/
├── bt_core.py        # Node, Status, Selector e Sequence
├── bt_conditions.py  # Condicoes que observam o jogo
├── bt_actions.py     # Acoes que comandam os robos
├── strategies.py     # Fabrica das arvores por papel e perfil
└── README.md         # Este guia
```

## Como o tick funciona

Todo no recebe a mesma interface:

```python
status = node.tick(robot, ball, team, enemy_team, dt)
```

- `robot`: robo que esta executando a arvore.
- `ball`: bola da partida.
- `team`: lista de robos do proprio time.
- `enemy_team`: lista de robos adversarios.
- `dt`: tempo do frame em segundos.
- Retorno: `Status.SUCCESS`, `Status.FAILURE` ou `Status.RUNNING`.

A regra principal e simples:

- `Selector`: prioridade, equivalente a um fallback. Para no primeiro filho que nao falhar.
- `Sequence`: cadeia de condicoes e acao. Para no primeiro filho que nao tiver sucesso.

Exemplo:

```python
Selector([
    Sequence([CondicaoPerigo(), AcaoRecuar()]),
    AcaoAtacar(),
    AcaoApoiar(),
])
```

A arvore tenta recuar quando ha perigo. Se nao houver, tenta atacar. Se nao puder atacar, apoia.

## Onde modificar

### `bt_core.py`

Modifique apenas quando precisar de um novo tipo de controle da arvore, por exemplo:

- `Parallel`: executa filhos simultaneamente.
- `Inverter`: troca `SUCCESS` por `FAILURE`.
- `Cooldown`: impede que uma acao seja chamada em todos os frames.

As classes atuais `Selector` e `Sequence` ja sao suficientes para a maior parte das estrategias.

### `bt_conditions.py`

Coloque aqui perguntas sobre o estado do jogo. Uma condicao nao deve comandar o robo; deve apenas retornar um `Status`.

Exemplo de condicao:

```python
class IsBallOnOurSide(Node):
    def __init__(self, center_x):
        self.center_x = center_x

    def tick(self, robot, ball, team, enemy_team, dt):
        if ball.x < self.center_x:
            return Status.SUCCESS
        return Status.FAILURE
```

Condicoes uteis para atacar:

- distancia do robo ate a bola;
- distancia dos adversarios;
- bola perto da parede;
- bola no campo de ataque ou defesa;
- robos aliados ocupando uma zona;
- robo atual como atacante principal;
- bola livre ou cercada.

Nao use `or` de forma permissiva ao filtrar papeis. Para considerar somente atacantes, use:

```python
if robot.role in (ATACKER1, ATACKER2)
```

### `bt_actions.py`

Coloque aqui comportamentos que comandam rodas e alvos. Uma acao deve chamar `robot.set_wheel_speeds(...)` ou `robot.go_to_point(...)`.

Exemplo de acao:

```python
class MoveToSupportPoint(Node):
    def __init__(self, offset):
        self.offset = np.asarray(offset, dtype=float)

    def tick(self, robot, ball, team, enemy_team, dt):
        target = ball.position + self.offset
        left, right = robot.go_to_point(target, target_angle=None, dt=dt)
        robot.set_wheel_speeds(left, right)
        return Status.RUNNING
```

Use `robot.go_to_point(...)` para atualizar `robot.target_position` e permitir que o target apareca no debug visual.

Nao altere `robot.body.velocity` dentro de uma acao a cada frame. O controle atual calcula velocidades desejadas e `apply_motor_forces()` aplica as forcas, permitindo que o Pymunk resolva colisoes.

### `strategies.py`

Este e o principal arquivo para montar e trocar arvores. A classe `TeamStrategy` recebe:

- `enemy_goal_pos`: posicao do gol adversario;
- `ally_goal_x`: coordenada X do gol defendido.

Os metodos importantes sao:

- `create_goalkeeper_tree()`: arvore do goleiro. Esta arvore ja esta considerada estavel.
- `create_attacker_tree(aggressiveness)`: arvore dos atacantes.
- `_recovery_branch()`: recuperacao quando o robo esta preso.
- `_wall_escape_branch()`: afastamento da bola da parede.
- `_primary_attacker_branch(...)`: disputa pela bola e ataque.
- `_support_branch()`: comportamento do atacante que nao e o principal.
- `create_tree_for_robot(...)`: escolhe a arvore de acordo com `robot.role`.

A ordem atual da arvore de atacante e:

```text
1. Recuperacao de colisao
2. Verifica se este e o atacante mais proximo
   2.1. Escapa da parede se necessario
   2.2. Executa SimplePushToGoalNode
3. Caso contrario, executa SupportAttackNode
```

A ordem importa. Um ramo que retorna `RUNNING` impede que os ramos seguintes sejam executados naquele frame.

### `simulation.py`

A simulacao apenas instancia as estrategias e executa os ticks:

```python
blue_manager = StrategyManager(
    profile="aggressive",
    factory=TeamStrategy(enemy_goal_pos=..., ally_goal_x=...),
)
blue_trees = blue_manager.build_trees_for_team(blue_team.robots)
```

Para trocar uma estrategia, prefira criar uma nova classe ou uma nova factory e injeta-la no `StrategyManager`. Evite colocar regras de estrategia diretamente no loop de `Simulation.update()`.

## Perfis de estrategia

`StrategyManager` aceita tres perfis:

- `aggressive`: multiplicador `1.4` no ataque.
- `balanced`: multiplicador `1.0`.
- `defensive`: multiplicador `0.8`.

Hoje o perfil muda principalmente a velocidade do `SimplePushToGoalNode`. Ele nao cria uma arvore completamente diferente. Se for necessario mudar prioridades, crie factories distintas.

## Por que os atacantes podem estar errados

A arvore atual e uma base reativa, nao uma estrategia completa de futebol. Os principais limites sao:

1. Somente o atacante mais proximo disputa a bola. O outro cai diretamente em suporte.
2. O suporte segue a bola, mas os parametros atuais de repulsao estao desativados (`SUP_AVOID_RADIUS = 0` e `SUP_AVOID_WEIGHT = 0`).
3. O ataque usa `SimplePushToGoalNode`, que somente aproxima o robo por tras da bola ou tenta empurra-la na direcao do gol. Ele nao avalia passe, marcacao, bloqueio ou companheiro livre.
4. A fuga de parede usa um giro curto, sem uma etapa clara de reposicionamento para retomar o ataque.
5. `IsClosestToBall` usa histerese global por equipe. Isso evita troca excessiva, mas pode manter um atacante como principal por mais tempo que o desejado.
6. Os atacantes nao possuem estados taticos persistentes, como `Pursue`, `Approach`, `Push`, `Recover` e `Support`.

Esses pontos sao locais seguros para estudo. A arvore do goleiro e criada separadamente e nao precisa ser alterada para melhorar os atacantes.

## Como criar uma nova estrategia de atacante

### Opcao 1: trocar somente uma acao

Mantenha as condicoes atuais e substitua `SimplePushToGoalNode` por uma acao nova em `_primary_attacker_branch()`.

```python
return Sequence([
    IsClosestToBall(hysteresis=CLOSEST_TO_BALL_HYSTERESIS),
    SmartAttackNode(enemy_goal_pos=self.enemy_goal_pos),
])
```

Use esta opcao quando a atribuicao do atacante principal estiver correta e o problema estiver apenas na movimentacao.

### Opcao 2: trocar a arvore inteira

Crie uma nova factory:

```python
class PossessionStrategy(TeamStrategy):
    def create_attacker_tree(self, aggressiveness=PROFILE_BALANCED_MULT):
        return Selector([
            self._recovery_branch(),
            Sequence([
                HasClearPath(),
                IsClosestToBall(hysteresis=5.0),
                ControlAndPushBall(self.enemy_goal_pos, aggressiveness),
            ]),
            RepositionBehindBall(self.enemy_goal_pos),
        ])
```

Depois injete a factory:

```python
manager = StrategyManager(
    profile="balanced",
    factory=PossessionStrategy(
        enemy_goal_pos=MID_GOALAREA_E,
        ally_goal_x=MID_GOALAREA_A[0],
    ),
)
```

### Opcao 3: estrategias diferentes para A1 e A2

Atualmente `create_tree_for_robot()` usa a mesma arvore para `ATACKER1` e `ATACKER2`. Para diferencia-los:

```python
class TeamStrategy(OriginalTeamStrategy):
    def create_tree_for_robot(self, robot, aggressiveness=PROFILE_BALANCED_MULT):
        if robot.role == GOALKEEPER:
            return self.create_goalkeeper_tree()
        if robot.role == ATACKER1:
            return self.create_primary_attacker_tree(aggressiveness)
        if robot.role == ATACKER2:
            return self.create_support_attacker_tree(aggressiveness)
        raise ValueError(f"Papel nao suportado: {robot.role}")
```

Essa e a opcao recomendada quando A1 deve pressionar a bola e A2 deve abrir espaco, ocupar uma linha de passe ou proteger a defesa.

## Cuidados com estado

Uma arvore nova e criada para cada robo, mas nos com estado de classe ou estado global podem misturar informacoes entre robos. Nao use um unico contador para todos os jogadores.

Prefira:

```python
self.last_action_by_robot = {}
robot_id = robot.id_robot
self.last_action_by_robot[robot_id] = "approach"
```

A condicao `IsClosestToBall` ja separa seu estado por equipe. Se criar uma nova condicao com memoria, inclua tambem o time na chave.

## Ciclo recomendado para uma estrategia melhor

Para um atacante mais robusto, implemente a seguinte prioridade:

```text
1. Halt/Stop imposto pelo arbitro
2. Recuperar de colisao ou travamento
3. Evitar bola presa ou parede
4. Definir atacante principal
5. Atacar se houver caminho livre
6. Reposicionar atras da bola
7. Apoiar em uma zona taticamente util
```

Cada item deve ser uma `Sequence` com condicoes explicitas e uma acao. Teste cada condicao isoladamente antes de combinar tudo na arvore.

## Debug e testes

Durante a simulacao:

- `D`: ativa o debug de estrategia.
- `Ctrl+1`: goleiro.
- `Ctrl+2`: atacante 1.
- `Ctrl+3`: atacante 2.
- `Ctrl+4`: todos.
- `C`: objetos de colisao.

O debug mostra o target atual, a orientacao e a velocidade desejada. Para validar uma nova arvore:

```powershell
python -m unittest discover -s tests -v
```

Adicione testes para:

- condicao verdadeira e falsa;
- alvo produzido pela acao;
- velocidades das rodas;
- selecao do atacante principal;
- comportamento quando a bola esta na parede;
- independencia entre BLUE e RED.

## Checklist antes de alterar uma estrategia

- A condicao retorna `SUCCESS`, `FAILURE` ou `RUNNING` corretamente?
- A acao atualiza o target por `go_to_point()`?
- A acao define as duas rodas e respeita `dt`?
- O robo pode ficar preso em um ramo que sempre retorna `RUNNING`?
- O goleiro continua fora das condicoes de atacante?
- A estrategia funciona para BLUE e RED, com gols invertidos?
- O estado interno esta separado por robo e por equipe?
- O comportamento foi validado com debug e testes unitarios?

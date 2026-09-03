#  Sistema de Tomada de Decisão Baseado em Árvore de Comportamento (Behavior Tree) para Futebol de Robôs (VSSS)

Este repositório contém a implementação completa e profissional da arquitetura de inteligência artificial e tomada de decisão para equipes de robôs da categoria **Very Small Size Soccer (VSSS)**. O sistema é estruturado em **Árvores de Comportamento (*Behavior Trees - BT*)**, integrando Campos Potenciais Artificiais (APF - *Artificial Potential Fields*), navegação reativa, planejamento de trajetória em tempo real (**ERRT** - *Execution Extended Random Tree*), controle proporcional de orientação e histerese temporal para atribuição de papéis.

---

##  Sumário
1. [Visão Geral e Arquitetura](#-visão-geral-e-arquitetura)
2. [Estrutura do Projeto e Módulos](#-estrutura-do-projeto-e-módulos)
3. [Módulo Core: `bt_core.py`](#-módulo-core-bt_corepy)
4. [Módulo de Condições: `bt_conditions.py`](#-módulo-de-condições-bt_conditionspy)
5. [Módulo de Ações e Comportamentos: `bt_actions.py`](#-módulo-de-ações-e-comportamentos-bt_actionspy)
6. [Módulo de Estratégias e Configuração: `bt_strategies.py`](#-módulo-de-estratégias-e-configuração-bt_strategiespy)
7. [Detalhamento Completo das Fórmulas Matemáticas e Físicas](#-detalhamento-completo-das-fórmulas-matemáticas-e-físicas)
8. [Fluxo de Execução e Ciclo do Tick](#-fluxo-de-execução-e-ciclo-do-tick)

---

##  Visão Geral e Arquitetura

O sistema gerencia autonomamente múltiplos robôs no campo (Goleiro, Atacante Principal e Suporte/Segundo Atacante). A tomada de decisão ocorre periodicamente a cada passo de simulação/controle executando o método `tick(...)` na raiz da árvore atribuída a cada robô.

```
              ┌──────────────────────────────┐
              │       StrategyManager        │
              └──────────────┬───────────────┘
                             │
             ┌───────────────┴───────────────┐
             ▼                               ▼
   Goleiro (GOALKEEPER)            Atacantes (ATACKER)
  ┌────────────────────┐          ┌────────────────────┐
  │  Goalkeeper Tree   │          │   Attacker Tree    │
  └────────────────────┘          └────────────────────┘

```


### Principais Diferenciais da Arquitetura:
1. **Histerese Temporal de Papéis:** Elimina a oscilação rápida (*chattering* ou *flickering*) de atribuição de papéis entre o atacante principal e o suporte.
2. **Campos Potenciais Repulsivos Limitados:** Sistema de fuga de colisão que calcula vetores de repulsão combinados de todos os robôs próximos (aliados e inimigos).
3. **Desvio Proativo no Suporte:** O robô de suporte se move em direção à bola enquanto aplica repulsão de obstáculos para realizar desvios suaves antes da colisão física.
4. **Giro de Desobstrução Físico-Direcionado (*Spin Clearance Physics*):** Determina dinamicamente a direção do giro (Horário ou Anti-Horário) por meio da projeção vetorial (produto escalar) entre a velocidade tangencial de contato da roda e a direção segura de afastamento.
5. **Navegação com ERRT e Validação de Ângulo:** Garante que o atacante se aproxime por trás da bola na direção do gol adversário, contornando a bola e outros robôs quando desalinhado.

---

##  Estrutura do Projeto e Módulos

```text
src/
└── intelligence/
    ├── bt_core.py        # Primitivas fundamentais da árvore (Status, Node, Selector, Sequence)
    ├── bt_conditions.py  # Nós de verificação lógica, sensoriamento e histerese
    ├── bt_actions.py     # Nós de ação cinemática, controle, planejamento e funções matemáticas
    └── bt_strategies.py # Fábrica de árvores (TeamStrategy) e Gerenciador de Perfis (StrategyManager)

```

---

##  Módulo Core: `bt_core.py`

O arquivo `bt_core.py` define o arcabouço base de execução da Árvore de Comportamento.

### 1. Classe `Status`

Enumeração dos estados possíveis após a avaliação de qualquer nó na árvore:

* `Status.SUCCESS`: O nó cumpriu seu objetivo/condição.
* `Status.FAILURE`: A condição não foi atendida ou a ação falhou.
* `Status.RUNNING`: A ação está em execução contínua e precisa ser avaliada novamente no próximo ciclo.

### 2. Classe `Node` (Abstrata)

Classe base para todos os nós da árvore.

* **Método `tick(robot, ball, team, enemy_team, dt)**`:
* `robot`: Objeto com o estado atual do robô (posição $\mathbf{p}_r = [x_r, y_r]^T$, orientação $\theta$, papel `role`, ID `id_robot`, etc.).
* `ball`: Objeto com o estado da bola ($\mathbf{p}_b = [x_b, y_b]^T$, velocidade, etc.).
* `team`: Lista de robôs da equipe aliada.
* `enemy_team`: Lista de robôs da equipe adversária.
* `dt`: Intervalo de tempo (*delta time*) em segundos desde o último ciclo.
* *Retorno:* Retorna obrigatoriamente um valor de `Status`.



### 3. Classe `Selector(Node)`

Nó de controle lógico **Fallback / Prioridade** (Operador OU lógico).

* **Comportamento:** Percorre a lista de filhos (`children`) em ordem sequencial. Se um filho retornar `SUCCESS` ou `RUNNING`, interrompe a avaliação dos demais e retransmite o status. Retorna `FAILURE` apenas se **todos** os filhos falharem.

### 4. Classe `Sequence(Node)`

Nó de controle lógico **Cadeia / Pré-condição + Ação** (Operador E lógico).

* **Comportamento:** Percorre a lista de filhos em ordem. Se qualquer filho retornar `FAILURE` ou `RUNNING`, interrompe a execução imediatamente e retransmite esse status. Retorna `SUCCESS` apenas se **todos** os filhos retornarem `SUCCESS`.

---

## 🔍 Módulo de Condições: `bt_conditions.py`

Agrupa os nós de sensorização virtual, checagem de regras de jogo e estado geográfico.

### 1. `IsBallNearWall`

Verifica se a bola está próxima às bordas (paredes) do campo de jogo.

* **Construtor:** `IsBallNearWall(margin=3.5, field_bounds=None)`
* **Variáveis:**
* `margin` *(float)*: Largura da faixa de borda (em cm).
* `field_bounds` *(tuple)*: Limites do campo $(x_{\min}, x_{\max}, y_{\min}, y_{\max})$.


* **Lógica:** Avalia se $x_b \le x_{\min} + \text{margin}$, $x_b \ge x_{\max} - \text{margin}$, $y_b \le y_{\min} + \text{margin}$ ou $y_b \ge y_{\max} - \text{margin}$.
* **Retorno:** `Status.SUCCESS` se próxima a qualquer parede; senão `Status.FAILURE`.

### 2. `IsClosestToBall`

Determina se o robô é o atacante de linha mais próximo da bola, aplicando **histerese temporal com desempate determinístico**.

* **Construtor:** `IsClosestToBall(hysteresis=5.0)`
* **Variáveis e Estado Interno:**
* `hysteresis` *(float)*: Margem de distância extra (em cm) exigida para um substituto tomar a vaga do titular.
* `_last_primary` *(dict de classe)*: Dicionário que armazena o ID do robô titular do ciclo anterior indexado pela tupla de IDs da equipe.


* **Lógica:**
1. Descarta goleiros (`GOALKEEPER`).
2. Filtra atacantes de linha (`ATACKER1`, `ATACKER2`).
3. Ordena os candidatos pela tupla $(d(R_i, B), \text{ID}_i)$ para garantir desempate determinístico sem arbitrariedade.
4. Mantém o titular anterior se o novo candidato não for mais próximo que uma margem superior a `hysteresis`.


* **Retorno:** `Status.SUCCESS` se o robô for o titular selecionado; senão `Status.FAILURE`.

### 3. `IsBallInGKZone`

Verifica se a bola está na grande área defensiva do goleiro.

* **Construtor:** `IsBallInGKZone(ally_goal_x, max_dist_x=40.0)`
* **Lógica:** Avalia se $\vert{}x_b - x_{\text{gol\_aliado}}\vert{} \le \text{max\_dist\_x}$.
* **Retorno:** `Status.SUCCESS` se a bola estiver dentro do limite $X$ da grande área; senão `Status.FAILURE`.

### 4. `IsNearWall`

Checa se o próprio robô está excessivamente próximo das bordas do campo.

* **Construtor:** `IsNearWall(margin=15.0, field_width=150.0, field_height=130.0)`
* **Retorno:** `Status.SUCCESS` se a posição do robô estiver dentro da faixa de margem da parede; senão `Status.FAILURE`.

### 5. `IsBallInDefenseZone`

Verifica se a bola está situada na metade defensiva do campo.

* **Construtor:** `IsBallInDefenseZone(field_center_x=fieldC[0])`
* **Retorno:** `Status.SUCCESS` se $x_b < x_{\text{centro}}$; senão `Status.FAILURE`.

### 6. `IsBallWithinDistance`

Verifica a proximidade da bola em relação ao robô.

* **Construtor:** `IsBallWithinDistance(max_distance=35.0)`
* **Retorno:** `Status.SUCCESS` se $\Vert{}\mathbf{p}_b - \mathbf{p}_r\Vert{}_2 \le \text{max\_distance}$; senão `Status.FAILURE`.

### 7. `IsTangledWithRobot`

Detecta colisão ou engavetamento com outros robôs (aliados ou inimigos), ignorando a colisão quando a bola está colada ao robô (disputa de bola).

* **Construtor:** `IsTangledWithRobot(min_dist=11.0, ball_ignore_dist=18.0)`
* **Lógica:** Se a distância até a bola for menor que `ball_ignore_dist`, retorna `Status.FAILURE` para permitir a disputa física. Caso contrário, se a distância até qualquer outro robô for menor que `min_dist`, retorna `Status.SUCCESS`.

---

## ⚡ Módulo de Ações e Comportamentos: `bt_actions.py`

Contém os nós de ação executáveis e funções matemáticas de baixo nível.

### 🛠️ Funções Utilitárias Matemáticas

* **`is_closest_field_robot(robot, ball, team, hysteresis=5.0)`**: Função utilitária mantida para compatibilidade legada.
* **`goal_escape_direction(ally_goal_x, field_center_x)`**: Retorna o vetor unitário $[1, 0]^T$ se o gol aliado for na esquerda ($x_{\text{gol}} < x_{\text{centro}}$) ou $[-1, 0]^T$ se for na direita.
* **`wall_escape_direction(ball_pos, field_bounds, margin=20.0)`**: Soma vetorialmente as contribuições repulsivas das 4 paredes quando a bola está próxima às margens.
* **`compute_repulsion_vector(robot_pos, robot_id, all_robots, influence_radius, min_dist_safety=3.0)`**: Calcula a força resultante repulsiva do campo potencial gerado por todos os outros robôs a uma distância menor que `influence_radius`.

---

### 🏃 Nós de Ação (Subclasses de `Node`)

#### 1. `DefendGoalNode`

Patrulha a linha do gol trancando a coordenada $Y$ da bola na largura da meta.

* **Construtor:** `DefendGoalNode(goal_x=MID_GOALAREA_A[0], goal_y_center=MID_GOALAREA_A[1], goal_width=40.0)`
* **Comportamento:**
* Aplica saturação na coordenada $Y$ da bola: $y_{\text{alvo}} = \text{clip}(y_b, y_{\text{center}} - \frac{w}{2}, y_{\text{center}} + \frac{w}{2})$.
* Se a distância ao ponto de patrulha for maior que $5.0\text{ cm}$, utiliza `robot.go_to_point`.
* Se menor ou igual a $5.0\text{ cm}$, executa controle P de orientação angular no próprio eixo com ganho $K_p = 40.0$.


* **Retorno:** Sempre `Status.RUNNING`.

#### 2. `InterceptBallNode`

Desloca o robô diretamente para a posição atual da bola sem impor restrição de orientação final (`target_angle=None`).

* **Retorno:** Sempre `Status.RUNNING`.

#### 3. `PushToGoalNode`

Movimento linear simples para empurrar a bola na direção do gol adversário.

* **Construtor:** `PushToGoalNode(enemy_goal_pos, aggressiveness_multiplier=1.0)`
* **Retorno:** Sempre `Status.RUNNING`.

#### 4. `ReverseNode`

Executa recuo direto em linha reta aplicando velocidades negativas prioritárias nas rodas ($v_l = v_r = -v_{\text{reverse}}$).

* **Construtor:** `ReverseNode(reverse_speed=60.0)`

#### 5. `PotentialFieldAvoidNode`

Recuperação reativa de colisão usando Campo Potencial Repulsivo Artificiail.

* **Construtor:** `PotentialFieldAvoidNode(influence_radius=25.0, escape_speed=45.0, min_dist_safety=3.0)`
* **Lógica:**
* Calcula o vetor resultante de repulsão de todos os robôs.
* Se o vetor resultante for nulo (forças simétricas opostas), aplica *fallback* apontando para o centro do campo.
* Define o ponto-alvo na direção de fuga e satura as velocidades de roda em $\pm \text{escape\_speed}$.


* **Retorno:** Sempre `Status.RUNNING`.

#### 6. `SupportAttackNode`

Comportamento proativo do segundo atacante (suporte) combinando atração e repulsão.

* **Construtor:** `SupportAttackNode(ally_goal_x, enemy_goal_pos=MID_GOALAREA_A, support_speed=5.0, avoid_radius=20.0, avoid_weight=1.5, min_dist_safety=3.0)`
* **Lógica:**
* Calcula o vetor de atração até a bola e o vetor de repulsão dos robôs vizinhos.
* Soma vetorialmente com peso `avoid_weight`.
* Se houver repulsão significativa ($\Vert{}\vec{F}_{\text{rep}}\Vert{} > 10^{-3}$), remove a trava de ângulo (`target_angle=None`) para permitir mobilidade translacional imediata sem rotação no lugar.


* **Retorno:** Sempre `Status.RUNNING`.

#### 7. `SpinClearanceNode`

Gira o robô para desobstruir a bola colada no gol ou paredes.

* **Construtor:** `SpinClearanceNode(spin_speed=80.0, away_direction_fn=None)`
* **Lógica:** Utiliza o modelo físico de produto escalar entre os vetores de velocidade tangencial da roda no ponto de contato e a direção segura para definir dinamicamente se o giro deve ser Horário ou Anti-Horário.
* **Retorno:** Sempre `Status.RUNNING`.

#### 8. `SmartPushToGoalNode`

Atacante principal com planejamento de caminho **ERRT** e checagem de alinhamento.

* **Construtor:** `SmartPushToGoalNode(enemy_goal_pos, ally_goal_x, aggressiveness_multiplier=1.0, field_bounds=None, field_margin=10.0, side_alignment_threshold=0.15)`
* **Lógica Avançada:**
* Clampa todos os pontos de navegação dentro das bordas do campo.
* Avalia o produto escalar entre o vetor robô-bola e bola-gol.
* Se o robô estiver atrás da bola e próximo ($d \le 18.0\text{ cm}$), empurra a bola diretamente.
* Se não estiver alinhado, gera caminho via ERRT para o ponto de aproximação situando-se $12.0\text{ cm}$ atrás da bola.


* **Retorno:** Sempre `Status.RUNNING`.

---

## 🌳 Módulo de Estratégias e Configuração: `bt_strategies.py`

### 📊 Constantes Físicas e Operacionais

| Constante | Valor | Descrição / Aplicação |
| --- | --- | --- |
| `GK_EMERGENCY_SPIN_DIST` | `6.5 cm` | Distância para giro de emergência do goleiro |
| `GK_EMERGENCY_SPIN_SPEED` | `85.0 rad/s` | Velocidade das rodas no giro do goleiro |
| `GK_INTERCEPT_DIST` | `25.0 cm` | Distância para interceptação curta do goleiro |
| `GK_MAX_OUT_DIST` | `25.0 cm` | Limite de saída $X$ do goleiro da linha do gol |
| `ATK_WALL_MARGIN` | `4.5 cm` | Margem de segurança de bola na parede |
| `ATK_WALL_SPIN_DIST` | `7.0 cm` | Distância para ativar o giro do atacante na parede |
| `ATK_WALL_SPIN_SPEED` | `85.0 rad/s` | Velocidade de giro do atacante na parede |
| `SUP_SPEED` | `15.0 cm/s` | Velocidade máxima de aproximação do suporte |
| `SUP_AVOID_RADIUS` | `15.0 cm` | Raio de desvio repulsivo proativo do suporte |
| `SUP_AVOID_WEIGHT` | `2.5` | Peso do vetor de repulsão no nó de suporte |
| `TANGLE_MIN_DIST` | `12.0 cm` | Distância limiar para detecção de colisão física |
| `TANGLE_BALL_IGNORE_DIST` | `18.0 cm` | Distância à bola que desativa fuga de colisão |
| `RECOVERY_INFLUENCE_RADIUS` | `25.0 cm` | Raio de atuação do campo repulsivo de recuperação |
| `RECOVERY_ESCAPE_SPEED` | `35.0 cm/s` | Velocidade máxima de fuga durante recuperação |
| `CLOSEST_TO_BALL_HYSTERESIS` | `5.0 cm` | Margem de histerese para troca do atacante principal |

---

### 🏗️ Classe `TeamStrategy`

Fábrica responsável por instanciar a estrutura topológica das árvores de decisão.

#### Árvore do Goleiro (`create_goalkeeper_tree`)

```text
Selector (Goleiro)
├── Sequence (Recuperação Reativa de Colisão)
│   ├── IsTangledWithRobot (min_dist=12.0, ball_ignore_dist=18.0)
│   └── PotentialFieldAvoidNode (influence_radius=25.0, escape_speed=35.0)
├── Sequence (Chute/Giro de Emergência na Área)
│   ├── IsBallWithinDistance (max_distance=6.5)
│   └── SpinClearanceNode (spin_speed=85.0, away_direction_fn=goal_escape_direction)
├── Sequence (Interceptação na Pequena Área)
│   ├── IsBallWithinDistance (max_distance=25.0)
│   ├── IsBallInGKZone (max_dist_x=25.0)
│   └── InterceptBallNode
└── DefendGoalNode (Patrulha em Linha no Gol)

```

#### Árvore do Atacante (`create_attacker_tree`)

```text
Selector (Atacante / Suporte)
├── Sequence (Recuperação Reativa de Colisão)
│   ├── IsTangledWithRobot (min_dist=12.0, ball_ignore_dist=18.0)
│   └── PotentialFieldAvoidNode (influence_radius=25.0, escape_speed=35.0)
├── Sequence (Ramo do Atacante Principal)
│   ├── IsClosestToBall (hysteresis=5.0)
│   └── Selector
│       ├── Sequence (Desobstrução de Bola na Parede)
│       │   ├── IsBallNearWall (margin=4.5)
│       │   ├── IsBallWithinDistance (max_distance=7.0)
│       │   └── SpinClearanceNode (spin_speed=85.0, away_direction_fn=wall_escape_direction)
│       └── SmartPushToGoalNode (Condução Inteligente com ERRT)
└── SupportAttackNode (Segundo Atacante / Suporte Proativo)

```

---

### ⚙️ Classe `StrategyManager`

Gerencia a instanciação e perfis táticos da equipe.

* **Instanciação:** `StrategyManager(profile="balanced")` (`"aggressive"`, `"balanced"`, `"defensive"`).
* **Método `build_trees_for_team(robots)**`: Retorna o dicionário `{ id_robot: bt_root_node }`.

---

## 🧮 Detalhamento Completo das Fórmulas Matemáticas e Físicas

Esta seção fornece a dedução formal, significado físico e equações utilizadas nos algoritmos do sistema.

---

### 1. Distância Euclidiana e Vetores Unitários de Orientação

Dada a posição do robô $\mathbf{p}_r = [x_r, y_r]^T$ e a posição da bola $\mathbf{p}_b = [x_b, y_b]^T$:

1. **Distância Euclidiana $d(R, B)$:**

$$d(R, B) = \Vert{}\mathbf{p}_b - \mathbf{p}_r\Vert{}_2 = \sqrt{(x_b - x_r)^2 + (y_b - y_r)^2}$$


2. **Vetor Direcional Unitário Robô-Bola $\hat{u}_{RB}$:**

$$\hat{u}_{RB} = \frac{\mathbf{p}_b - \mathbf{p}_r}{\Vert{}\mathbf{p}_b - \mathbf{p}_r\Vert{}_2} = \begin{bmatrix} \frac{x_b - x_r}{d(R, B)} \\ \frac{y_b - y_r}{d(R, B)} \end{bmatrix}$$



---

### 2. Campo Potencial Artificiai Repulsivo (APF)

Utilizado nas funções `compute_repulsion_vector`, `PotentialFieldAvoidNode` e `SupportAttackNode`.

Para um robô em $\mathbf{p}_r$ e um conjunto de robôs obstáculos $\mathcal{O} = \{\mathbf{p}_{o,1}, \mathbf{p}_{o,2}, \dots, \mathbf{p}_{o,N}\}$ (aliados e inimigos, exceto o próprio robô):

1. **Vetor Deslocamento:**

$$\Delta\mathbf{p}_i = \mathbf{p}_r - \mathbf{p}_{o,i}$$


2. **Distância Distorcida e Saturada $d_{\text{safe}, i}$:**

$$d_i = \Vert{}\Delta\mathbf{p}_i\Vert{}_2, \quad d_{\text{safe}, i} = \max(d_i, d_{\text{min\_safety}})$$



*Significado Físico:* A saturação por $d_{\text{min\_safety}} = 3.0\text{ cm}$ previne divisão por zero ou forças infinitas quando dois robôs sobrepõem seus centros.
3. **Magnitude de Repulsão Normalizada:**

$$M_i = \begin{cases} \frac{r_{\text{inf}} - d_{\text{safe}, i}}{r_{\text{inf}}}, & \text{se } d_i < r_{\text{inf}} \\ 0, & \text{caso contrário} \end{cases}$$



onde $r_{\text{inf}} = \text{influence\_radius}$ (25.0 cm na recuperação, 15.0 cm no suporte).
4. **Vetor de Força Repulsiva Resultante $\vec{F}_{\text{rep}}$:**

$$\vec{F}_{\text{rep}} = \sum_{i \in \mathcal{O}, d_i < r_{\text{inf}}} \left( \frac{\Delta\mathbf{p}_i}{d_{\text{safe}, i}} \right) \cdot M_i$$


5. **Tratamento de Singularidade de Força Nula:**
Se $\Vert{}\vec{F}_{\text{rep}}\Vert{}_2 < 10^{-6}$ (por exemplo, dois obstáculos em posições perfeitamente simétricas em relação ao robô), o sistema chaveia para um vetor de fuga na direção do centro do campo $\mathbf{p}_{\text{centro}} = [x_c, y_c]^T$:

$$\hat{d}_{\text{escape}} = \frac{\mathbf{p}_{\text{centro}} - \mathbf{p}_r}{\Vert{}\mathbf{p}_{\text{centro}} - \mathbf{p}_r\Vert{}_2}$$



---

### 3. Combinação de Campos Potenciais no Suporte (`SupportAttackNode`)

O robô de suporte combina o vetor de atração em direção à bola com a repulsão dos obstáculos vizinhos.

1. **Vetor Atractor $\vec{F}_{\text{att}}$:**

$$\vec{F}_{\text{att}} = \hat{u}_{RB} = \frac{\mathbf{p}_b - \mathbf{p}_r}{\Vert{}\mathbf{p}_b - \mathbf{p}_r\Vert{}_2}$$


2. **Vetor de Campo Combinado $\vec{F}_{\text{comb}}$:**

$$\vec{F}_{\text{comb}} = \vec{F}_{\text{att}} + w_{\text{avoid}} \cdot \vec{F}_{\text{rep}}$$



onde $w_{\text{avoid}} = 2.5$ (`SUP_AVOID_WEIGHT`).
3. **Direção Resultante Combinada $\hat{d}_{\text{comb}}$:**

$$\hat{d}_{\text{comb}} = \begin{cases} \frac{\vec{F}_{\text{comb}}}{\Vert{}\vec{F}_{\text{comb}}\Vert{}_2}, & \text{se } \Vert{}\vec{F}_{\text{comb}}\Vert{}_2 > 10^{-6} \\ \vec{F}_{\text{att}}, & \text{caso contrário} \end{cases}$$


4. **Ponto Virtual de Aproximação (*Lookahead Target*):**

$$\mathbf{p}_{\text{target}} = \mathbf{p}_r + \hat{d}_{\text{comb}} \cdot \min(d(R, B), L_{\text{max}})$$



onde $L_{\text{max}} = 40.0\text{ cm}$.

---

### 4. Modelo Físico do Giro de Desobstrução (`SpinClearanceNode`)

Quando o robô gira no próprio eixo para tirar a bola de uma situação perigosa (gol ou parede), o sentido de rotação deve garantir que a velocidade tangencial no ponto de contato empurre a bola para a região segura.

```
       Giro CCW (+90°)              Giro CW (-90°)
       v_push = [-ry, rx]           v_push = [ry, -rx]
             ▲                            │
             │                            ▼
      [Bola] ● ◄────── r ─────── [Robô] ● ─────── r ──────► ● [Bola]

```

1. **Vetor do Centro do Robô à Bola:**

$$\vec{r} = \mathbf{p}_b - \mathbf{p}_r, \quad \hat{r} = \frac{\vec{r}}{\Vert{}\vec{r}\Vert{}_2} = \begin{bmatrix} \hat{r}_x \\ \hat{r}_y \end{bmatrix}$$


2. **Velocidade Tangencial de Contato por Sentido de Rotação:**
* **Giro Anti-Horário (CCW - *Counter-Clockwise*):** Vel. das rodas $(v_l, v_r) = (-s, s)$ com $s > 0$. Rotação $\omega > 0$. O vetor tangencial no ponto de contato é a rotação de $+90^\circ$ ($\frac{\pi}{2}$ rad) de $\hat{r}$:

$$\hat{v}_{\text{push, CCW}} = R\left(+\frac{\pi}{2}\right) \hat{r} = \begin{bmatrix} 0 & -1 \\ 1 & 0 \end{bmatrix} \begin{bmatrix} \hat{r}_x \\ \hat{r}_y \end{bmatrix} = \begin{bmatrix} -\hat{r}_y \\ \hat{r}_x \end{bmatrix}$$


* **Giro Horário (CW - *Clockwise*):** Vel. das rodas $(v_l, v_r) = (s, -s)$ com $s > 0$. Rotação $\omega < 0$. O vetor tangencial no ponto de contato é a rotação de $-90^\circ$ ($-\frac{\pi}{2}$ rad) de $\hat{r}$:

$$\hat{v}_{\text{push, CW}} = R\left(-\frac{\pi}{2}\right) \hat{r} = \begin{bmatrix} 0 & 1 \\ -1 & 0 \end{bmatrix} \begin{bmatrix} \hat{r}_x \\ \hat{r}_y \end{bmatrix} = \begin{bmatrix} \hat{r}_y \\ -\hat{r}_x \end{bmatrix}$$




3. **Pontuação de Alinhamento via Produto Escalar:**
Seja $\hat{u}_{\text{fuga}} = \frac{\vec{d}_{\text{fuga}}}{\Vert{}\vec{d}_{\text{fuga}}\Vert{}_2}$ o vetor unitário da direção segura desejada (calculado por `goal_escape_direction` ou `wall_escape_direction`). A projeção escalar de cada direção de empurrão em relação à direção segura é:

$$\text{Score}_{\text{CCW}} = \hat{v}_{\text{push, CCW}} \cdot \hat{u}_{\text{fuga}} = -\hat{r}_y u_x + \hat{r}_x u_y$$


$$\text{Score}_{\text{CW}} = \hat{v}_{\text{push, CW}} \cdot \hat{u}_{\text{fuga}} = \hat{r}_y u_x - \hat{r}_x u_y$$


4. **Regra de Decisão:**

$$\text{Sentido de Giro} = \begin{cases} \text{Horário (CW)}, & \text{se } \text{Score}_{\text{CW}} > \text{Score}_{\text{CCW}} \\ \text{Anti-Horário (CCW)}, & \text{caso contrário} \end{cases}$$



---

### 5. Campo de Fuga de Parede e Canto (`wall_escape_direction`)

Seja a posição da bola $\mathbf{p}_b = [x_b, y_b]^T$, os limites do campo $(x_{\min}, x_{\max}, y_{\min}, y_{\max})$ e a margem $m = 20.0\text{ cm}$.

1. **Distâncias às Bordas:**

$$d_{\text{left}} = x_b - x_{\min}, \quad d_{\text{right}} = x_{\max} - x_b$$


$$d_{\text{bottom}} = y_b - y_{\min}, \quad d_{\text{top}} = y_{\max} - y_b$$


2. **Componentes Repulsivos Direcionais:**

$$\mathbf{p}_{\text{left}} = \begin{bmatrix} 1 \\ 0 \end{bmatrix} \cdot \max(0, m - d_{\text{left}}), \quad \mathbf{p}_{\text{right}} = \begin{bmatrix} -1 \\ 0 \end{bmatrix} \cdot \max(0, m - d_{\text{right}})$$


$$\mathbf{p}_{\text{bottom}} = \begin{bmatrix} 0 \\ 1 \end{bmatrix} \cdot \max(0, m - d_{\text{bottom}}), \quad \mathbf{p}_{\text{top}} = \begin{bmatrix} 0 \\ -1 \end{bmatrix} \cdot \max(0, m - d_{\text{top}})$$


3. **Vetor Repulsivo Resultante da Parede:**

$$\vec{P}_{\text{wall}} = \mathbf{p}_{\text{left}} + \mathbf{p}_{\text{right}} + \mathbf{p}_{\text{bottom}} + \mathbf{p}_{\text{top}}$$



*Propriedade para Cantos:* Perto de um canto (ex: canto inferior esquerdo), $\mathbf{p}_{\text{left}}$ e $\mathbf{p}_{\text{bottom}}$ serão simultaneamente não nulos, gerando um vetor diagonal $[1, 1]^T$ que empurra a bola para o interior do campo, sem colidir contra a outra parede.

---

### 6. Histerese Temporal e Desempate Determinístico (`IsClosestToBall`)

1. **Ordenação por Tupla com Desempate Perfeito:**
Para cada robô de linha $i \in \{\text{ATACKER1}, \text{ATACKER2}\}$:

$$\text{Candidato Puro } i^* = \arg\min_{i} \left( d(R_i, B), \text{ID}_i \right)$$


2. **Equação de Atualização do Atacante Titular com Histerese $h = 5.0\text{ cm}$:**
Seja $i_{\text{last}}$ o ID do titular do ciclo anterior:

$$i_{\text{titular}} = \begin{cases} i^*, & \text{se } i_{\text{last}} \text{ é nulo ou } d(R_{i^*}, B) + h < d(R_{i_{\text{last}}}, B) \\ i_{\text{last}}, & \text{caso contrário} \end{cases}$$



---

### 7. Validação de Alinhamento Angular no `SmartPushToGoalNode`

Para evitar que o robô empurre a bola na direção do próprio gol ao tentar chutar sem estar posicionado atrás dela:

```
                  [Gol Adv]
                     ▲
                     │ u_BG
                     │
                  [Bola] ●
                     ▲
                     │ u_RB
                     │
                 [Robô] 🤖

```

1. **Vetor Bola-para-Gol Adversário $\hat{u}_{BG}$:**

$$\vec{v}_{BG} = \mathbf{p}_{\text{gol\_adv}} - \mathbf{p}_b, \quad \hat{u}_{BG} = \frac{\vec{v}_{BG}}{\|\vec{v}_{BG}\|_2}$$


2. **Vetor Robô-para-Bola $\hat{u}_{RB}$:**

$$\vec{v}_{RB} = \mathbf{p}_b - \mathbf{p}_r, \quad \hat{u}_{RB} = \frac{\vec{v}_{RB}}{\|\vec{v}_{RB}\|_2}$$


3. **Métrica de Alinhamento por Produto Escalar:**

$$\text{Alignment} = \hat{u}_{RB} \cdot \hat{u}_{BG} = \cos(\theta)$$



onde $\theta$ é o ângulo entre a linha de aproximação do robô e a linha do gol.
4. **Condição de Engajamento Direto de Chute:**

$$\text{Modo Chute Direto} = (d(R, B) \le d_{\text{engagement}}) \land (\text{Alignment} \ge \tau_{\text{side\_alignment}})$$



onde $d_{\text{engagement}} = 18.0\text{ cm}$ e $\tau_{\text{side\_alignment}} = 0.15$ (correspondendo a um ângulo limite $\theta_{\max} = \arccos(0.15) \approx 81.37^\circ$).
5. **Ponto de Aproximação Via ERRT quando Desalinhado:**

$$\mathbf{p}_{\text{approach}} = \text{ClampToField}\left( \mathbf{p}_b - 12.0 \cdot \hat{u}_{BG} \right)$$


6. **Operação de Clamping aos Limites de Campo:**

$$\text{ClampToField}\left(\begin{bmatrix} x \\ y \end{bmatrix}\right) = \begin{bmatrix} \text{clip}(x, x_{\min} + m_{\text{field}}, x_{\max} - m_{\text{field}}) \\[4pt] \text{clip}(y, y_{\min} + m_{\text{field}}, y_{\max} - m_{\text{field}}) \end{bmatrix}$$



onde $m_{\text{field}} = 10.0\text{ cm}$.

---

### 8. Controle Proporcional de Orientação no Goleiro (`DefendGoalNode`)

1. **Truncamento da Posição Alvo $Y$ do Goleiro:**

$$y_{\text{alvo}} = \text{clip}\left( y_b, y_{\text{centro}} - \frac{w_{\text{gol}}}{2}, y_{\text{centro}} + \frac{w_{\text{gol}}}{2} \right)$$


2. **Ângulo Alvo de Orientação $\theta_{\text{alvo}}$:**

$$\theta_{\text{alvo}} = \begin{cases} 0, & \text{se } x_{\text{gol}} < x_{\text{centro}} \text{ (Gol na Esquerda)} \\ \pi, & \text{se } x_{\text{gol}} \ge x_{\text{centro}} \text{ (Gol na Direita)} \end{cases}$$


3. **Cálculo do Erro Angular Envolvente $e_\theta \in [-\pi, \pi]$:**

$$e_\theta = \text{atan2}\left( \sin(\theta_{\text{alvo}} - \theta_{\text{atual}}), \cos(\theta_{\text{alvo}} - \theta_{\text{atual}}) \right)$$


4. **Controle Proporcional P de Rotação em Malha Fechada:**

$$\omega = K_p \cdot e_\theta \implies v_l = -\omega, \quad v_r = +\omega$$



onde $K_p = 40.0$.

---

## 🔄 Fluxo de Execução e Ciclo do Tick

O loop principal da simulação ou do software de visão e controle chama a árvore periodicamente:

```python
# Instanciação do gerenciador tático
strategy_manager = StrategyManager(profile="balanced")

# Loop principal de controle (rodando no dt do simulador/visão)
def control_loop(team_robots, enemy_robots, ball, dt):
    # Constrói/obtém as árvores por ID do robô
    trees = strategy_manager.build_trees_for_team(team_robots)

    for robot in team_robots:
        tree = trees[robot.id_robot]
        # Avalia a árvore de comportamento
        status = tree.tick(
            robot=robot,
            ball=ball,
            team=team_robots,
            enemy_team=enemy_robots,
            dt=dt
        )

```

1. A avaliação começa pela raiz `Selector`.
2. **Prioridade 1:** Checa se o robô está preso em colisão (`IsTangledWithRobot`). Se verdadeiro, aciona a fuga por campo potencial (`PotentialFieldAvoidNode`).
3. **Prioridade 2:** Verifica se o robô é o atacante principal (`IsClosestToBall`). Se for o principal, decide entre desobstruir bola na parede ou executar condução avançada via ERRT (`SmartPushToGoalNode`).
4. **Fallback:** Se não for o atacante principal, o nó `IsClosestToBall` retorna `FAILURE` e o `Selector` direciona a execução para o suporte proativo (`SupportAttackNode`).

---

*Documentação técnica e matemática desenvolvida com foco em rigor científico e alto desempenho para a categoria VSSS.*
"""

with open("README.md", "w", encoding="utf-8") as f:
f.write(readme_expanded)

print("README.md atualizado com sucesso!")

```

```text?code_stdout&code_event_index=1
README.md atualizado com sucesso!


```

Abaixo está uma **explicação detalhada e didática de cada uma das fórmulas matemáticas e físicas** utilizadas no sistema de inteligência e tomada de decisão para o futebol de robôs (VSSS).

O arquivo **`README.md`** do projeto foi atualizado com este conteúdo detalhado.

---

## 🧮 1. Campos Potenciais Artificiais Repulsivos (APF)

Os **Campos Potenciais Artificiais (APF - *Artificial Potential Fields*)** são usados para afastar o robô de obstáculos (outros robôs aliados e adversários) de forma reativa e contínua.

### A Fórmula:

Para um robô em posição $\mathbf{p}_r = [x_r, y_r]^T$ e um obstáculo em $\mathbf{p}_o = [x_o, y_o]^T$:

1. **Vetor Deslocamento ($\Delta\mathbf{p}_i$):**

$$\Delta\mathbf{p}_i = \mathbf{p}_r - \mathbf{p}_{o,i}$$



*Significado:* É o vetor que aponta diretamente do obstáculo em direção ao nosso robô.
2. **Distância Segura Saturada ($d_{\text{safe}, i}$):**

$$d_i = \|\Delta\mathbf{p}_i\|_2 = \sqrt{(x_r - x_o)^2 + (y_r - y_o)^2}$$


$$d_{\text{safe}, i} = \max(d_i, d_{\text{min\_safety}})$$



*Por que saturar?* Se dois robôs colidirem exatamente no mesmo ponto ($d_i \to 0$), haveria uma divisão por zero (singularidade) gerando forças infinitas. A saturação por $d_{\text{min\_safety}} = 3.0\text{ cm}$ estabiliza o cálculo numérico.
3. **Magnitude de Repulsão Normalizada ($M_i$):**

$$M_i = \begin{cases} \frac{r_{\text{inf}} - d_{\text{safe}, i}}{r_{\text{inf}}}, & \text{se } d_i < r_{\text{inf}} \\ 0, & \text{caso contrário} \end{cases}$$



*Significado Físico:*
* Se a distância for maior que o raio de influência ($r_{\text{inf}}$), a repulsão é zero.
* À medida que o robô se aproxima do obstáculo, $M_i$ cresce linearmente de $0$ até próximo de $1.0$.


4. **Vetor de Força Repulsiva Resultante ($\vec{F}_{\text{rep}}$):**

$$\vec{F}_{\text{rep}} = \sum_{i \in \mathcal{O}, d_i < r_{\text{inf}}} \left( \frac{\Delta\mathbf{p}_i}{d_{\text{safe}, i}} \right) \cdot M_i$$



*Significado:* Soma vetorial das contribuições de todos os robôs dentro do raio de influência. O termo $\frac{\Delta\mathbf{p}_i}{d_{\text{safe}, i}}$ é o vetor unitário de direção, multiplicando a magnitude $M_i$.
5. **Tratamento de Anulação Simétrica (Singularidade Nula):**
Se o robô estiver exatamente no meio de dois obstáculos simétricos, a soma vetorial resultará em $\vec{F}_{\text{rep}} = \mathbf{0}$. Nesses casos, o sistema chaveia automaticamente para um vetor de fuga em direção ao centro do campo:

$$\hat{d}_{\text{escape}} = \frac{\mathbf{p}_{\text{centro}} - \mathbf{p}_r}{\|\mathbf{p}_{\text{centro}} - \mathbf{p}_r\|_2}$$



---

## 🧭 2. Combinação de Campos (Atração + Repulsão Proativa no Suporte)

O robô de suporte precisa se mover em direção à bola, mas sem esbarrar nos robôs no caminho. Em vez de parar para planejar um caminho complexo, ele combina forças atrativas e repulsivas.

### A Fórmula:

1. **Vetor Atractivo ($\vec{F}_{\text{att}}$):**

$$\vec{F}_{\text{att}} = \frac{\mathbf{p}_{\text{bola}} - \mathbf{p}_r}{\|\mathbf{p}_{\text{bola}} - \mathbf{p}_r\|_2}$$


2. **Combinação Ponderada ($\vec{F}_{\text{comb}}$):**

$$\vec{F}_{\text{comb}} = \vec{F}_{\text{att}} + w_{\text{avoid}} \cdot \vec{F}_{\text{rep}}$$



onde $w_{\text{avoid}} = 2.5$ dá peso maior à esquiva de obstáculos para garantir segurança.
3. **Ponto Virtual Alvo (*Lookahead Target Point*):**

$$\mathbf{p}_{\text{target}} = \mathbf{p}_r + \left(\frac{\vec{F}_{\text{comb}}}{\|\vec{F}_{\text{comb}}\|_2}\right) \cdot \min(d(R, B), L_{\text{max}})$$



*Significado Físico:* Cria um "ponto fantasma" à frente do robô na direção resultante. O robô navega em direção a esse ponto, desviando suavemente de obstáculos em tempo real (*desvio proativo*).

---

## 🔄 3. Giro de Desobstrução Físico-Direcionado (*Spin Clearance Physics*)

Quando a bola fica presa na parede ou perto do gol, o robô precisa girar no próprio eixo para "desajeitar" e liberar a bola. Mas **para qual lado girar (Horário ou Anti-Horário)?**

### A Física e Geometria do Giro:

Ao girar no próprio eixo, as rodas do robô transferem momento linear para a bola através da velocidade tangencial no ponto de contato.

```
       Giro Anti-Horário (CCW: +90°)       Giro Horário (CW: -90°)
       v_push = [-ry, rx]                   v_push = [ry, -rx]
             ▲                                    │
             │                                    ▼
      [Bola] ● ◄────── r ─────── [Robô] ● ─────── r ──────► ● [Bola]

```

1. **Vetor Normalizado Robô-Bola ($\hat{r}$):**

$$\vec{r} = \mathbf{p}_{\text{bola}} - \mathbf{p}_r \implies \hat{r} = \begin{bmatrix} \hat{r}_x \\ \hat{r}_y \end{bmatrix}$$


2. **Velocidade Tangencial no Ponto de Contato:**
* **Giro Anti-Horário (CCW - *Counter-Clockwise*):** O vetor velocidade no ponto de contato é a rotação de $+90^\circ$ ($\frac{\pi}{2}$ rad) de $\hat{r}$:

$$\hat{v}_{\text{push, CCW}} = \begin{bmatrix} 0 & -1 \\ 1 & 0 \end{bmatrix} \begin{bmatrix} \hat{r}_x \\ \hat{r}_y \end{bmatrix} = \begin{bmatrix} -\hat{r}_y \\ \hat{r}_x \end{bmatrix}$$


* **Giro Horário (CW - *Clockwise*):** O vetor velocidade é a rotação de $-90^\circ$ ($-\frac{\pi}{2}$ rad) de $\hat{r}$:

$$\hat{v}_{\text{push, CW}} = \begin{bmatrix} 0 & 1 \\ -1 & 0 \end{bmatrix} \begin{bmatrix} \hat{r}_x \\ \hat{r}_y \end{bmatrix} = \begin{bmatrix} \hat{r}_y \\ -\hat{r}_x \end{bmatrix}$$




3. **Seleção por Produto Escalar (Projeção Ortogonal):**
Seja $\hat{u}_{\text{fuga}}$ o vetor unitário que aponta para a zona livre de perigo. O produto escalar mede o quão alinhada está cada opção de giro com a direção segura:

$$\text{Score}_{\text{CCW}} = \hat{v}_{\text{push, CCW}} \cdot \hat{u}_{\text{fuga}} = (-\hat{r}_y \cdot u_x + \hat{r}_x \cdot u_y)$$


$$\text{Score}_{\text{CW}} = \hat{v}_{\text{push, CW}} \cdot \hat{u}_{\text{fuga}} = (\hat{r}_y \cdot u_x - \hat{r}_x \cdot u_y)$$


4. **Decisão:**

$$\text{Decisão de Giro} = \begin{cases} \text{Horário (CW)}, & \text{se } \text{Score}_{\text{CW}} > \text{Score}_{\text{CCW}} \\ \text{Anti-Horário (CCW)}, & \text{caso contrário} \end{cases}$$



---

## 🧱 4. Campo de Fuga de Parede e Cantos (`wall_escape_direction`)

Garante que o robô saiba para onde empurrar a bola quando ela está na borda do campo, tratando os cantos de forma geométrica.

### A Fórmula:

Para as 4 bordas do campo com limites $[x_{\min}, x_{\max}, y_{\min}, y_{\max}]$ e margem $m = 20.0\text{ cm}$:

1. **Distâncias às Paredes:**

$$d_{\text{left}} = x_b - x_{\min}, \quad d_{\text{right}} = x_{\max} - x_b$$


$$d_{\text{bottom}} = y_b - y_{\min}, \quad d_{\text{top}} = y_{\max} - y_b$$


2. **Repulsão Individual de Cada Parede:**

$$\mathbf{p}_{\text{left}} = \begin{bmatrix} 1 \\ 0 \end{bmatrix} \cdot \max(0, m - d_{\text{left}}), \quad \mathbf{p}_{\text{right}} = \begin{bmatrix} -1 \\ 0 \end{bmatrix} \cdot \max(0, m - d_{\text{right}})$$


$$\mathbf{p}_{\text{bottom}} = \begin{bmatrix} 0 \\ 1 \end{bmatrix} \cdot \max(0, m - d_{\text{bottom}}), \quad \mathbf{p}_{\text{top}} = \begin{bmatrix} 0 \\ -1 \end{bmatrix} \cdot \max(0, m - d_{\text{top}})$$


3. **Vetor Resultante:**

$$\vec{P}_{\text{wall}} = \mathbf{p}_{\text{left}} + \mathbf{p}_{\text{right}} + \mathbf{p}_{\text{bottom}} + \mathbf{p}_{\text{top}}$$



*Efeito em Cantos:* Se a bola estiver no canto inferior esquerdo, as componentes $\mathbf{p}_{\text{left}}$ e $\mathbf{p}_{\text{bottom}}$ serão ativadas simultaneamente, resultando no vetor diagonal $[1, 1]^T$. Isso faz o robô empurrar a bola diretamente para o centro do campo, escapando das duas paredes de uma vez!

---

## ⏱️ 5. Histerese Temporal e Desempate Determinístico de Papéis

Para evitar que dois robôs fiquem alternando o papel de atacante principal várias vezes por segundo (*flickering* ou *chattering*):

### A Fórmula:

1. **Seleção Determinística do Candidato Mais Próximo ($i^*$):**
Utiliza a tupla de ordenação $(\text{distância}, \text{ID})$ para eliminar empate estocástico:

$$i^* = \arg\min_{i \in \text{Atacantes}} \left( d(R_i, B), \text{ID}_i \right)$$


2. **Atualização do Titular com Histerese ($h = 5.0\text{ cm}$):**
Seja $i_{\text{last}}$ o ID do atacante titular no ciclo anterior:

$$i_{\text{titular}} = \begin{cases} i^*, & \text{se } i_{\text{last}} \text{ não existe ou } d(R_{i^*}, B) + h < d(R_{i_{\text{last}}}, B) \\ i_{\text{last}}, & \text{caso contrário} \end{cases}$$



*Significado:* Um robô só perde o posto de atacante principal se outro aliado estiver **pelo menos $5.0\text{ cm}$ mais perto** da bola do que ele.

---

## 🎯 6. Validação de Alinhamento Angular de Chute (`SmartPushToGoalNode`)

Antes de empurrar a bola para o gol adversário, o robô avalia se está posicionado na direção correta (atrás da bola em relação ao gol) para evitar fazer gol contra ou chutar a bola para trás.

### A Fórmula:

1. **Vetor Bola $\to$ Gol Adversário ($\hat{u}_{BG}$):**

$$\hat{u}_{BG} = \frac{\mathbf{p}_{\text{gol\_adv}} - \mathbf{p}_b}{\|\mathbf{p}_{\text{gol\_adv}} - \mathbf{p}_b\|_2}$$


2. **Vetor Robô $\to$ Bola ($\hat{u}_{RB}$):**

$$\hat{u}_{RB} = \frac{\mathbf{p}_b - \mathbf{p}_r}{\|\mathbf{p}_b - \mathbf{p}_r\|_2}$$


3. **Métrica de Alinhamento Angular ($\cos \theta$):**

$$\text{Alignment} = \hat{u}_{RB} \cdot \hat{u}_{BG} = \cos(\theta)$$


4. **Condição de Engajamento Direto:**

$$\text{Chute Direto} = (d(R, B) \le 18.0\text{ cm}) \land (\text{Alignment} \ge 0.15)$$



*Nota:* $\cos(\theta) \ge 0.15$ equivale a um ângulo limite $\theta \le \arccos(0.15) \approx 81.37^\circ$. Se o robô não estiver alinhado dentro dessa faixa, ele aciona o algoritmo **ERRT** para contornar a bola e se posicionar $12.0\text{ cm}$ atrás dela.

---

## 🧤 7. Controle Proporcional P Angular no Goleiro (`DefendGoalNode`)

O goleiro patrulha a linha do gol em movimento translacional mantendo-se sempre virado para a frente ($0$ ou $\pi$ radianos).

### A Fórmula:

1. **Erro Angular Normalizado no Intervalo $[-\pi, \pi]$:**

$$e_\theta = \text{atan2}\left( \sin(\theta_{\text{alvo}} - \theta_{\text{atual}}), \cos(\theta_{\text{alvo}} - \theta_{\text{atual}}) \right)$$


2. **Controle Proporcional (P):**

$$\omega = K_p \cdot e_\theta \implies v_l = -\omega, \quad v_r = +\omega$$



onde $K_p = 40.0$.

*Significado:* Se o goleiro se desalinhar da orientação paralela à linha do gol, este controlador aplica torque proporcional no próprio eixo para restabelecer a orientação de defesa instantaneamente.
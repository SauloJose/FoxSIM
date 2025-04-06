# ⚽ Simulador 2D com SAT e Resposta Física

Este projeto é um simulador 2D focado em interações físicas realistas entre robôs, bola e estruturas fixas dentro de um campo, com detecção e resposta de colisão baseada no Teorema do Eixo Separador (Separating Axis Theorem - SAT).

---

## 🟠 1. Objetos Móveis

### `ball.py`
Contém a classe `Ball`, responsável por representar a bola no campo:

- Possui atributos de posição (`x`, `y`), velocidade (`velocity`), massa, raio e ângulo.
- A bola interage fisicamente com os robôs e com os limites do campo (`FIELD`) por meio do sistema de colisões.
- Seu corpo de colisão é um polígono circular aproximado, que pode ser detectado via SAT.
- Utiliza o coeficiente de restituição `COEFFICIENT_RESTITUTION_BALL_ROBOT = 1.0` para colisões com robôs (colisão perfeitamente elástica).
- E `COEFFICIENT_RESTITUTION_BALL_FIELD = 0.6` para colisões com as bordas do campo (perde energia).

### `robot.py`
Contém a classe `Robot`, que representa os jogadores móveis:

- Cada robô tem massa, velocidade, direção, posição, raio e um corpo de colisão poligonal.
- Pode receber comandos de movimento e rotação, além de ter um identificador de time.
- Colide com outros robôs e com a bola.
- Utiliza os coeficientes:
  - `COEFFICIENT_RESTITUTION_ROBOT_ROBOT = 0.2` para colisões entre robôs (colisão inelástica).
  - `COEFFICIENT_FRICTION_ROBOT_ROBOT = 0.9` para simular o atrito na colisão robô-robô.

---

## 🟢 2. Objetos Estruturais (Structures)

### `field.py`
Define a classe `Field`, que representa o campo de jogo.

- Apesar de ser um objeto fixo (não se move), o campo interage fisicamente com robôs e bola.
- Serve como **limite físico** do jogo: os objetos móveis não podem ultrapassar suas bordas.
- Internamente, possui um corpo de colisão definido por retângulos e linhas, compatíveis com o sistema de detecção via SAT.
- Outros objetos do tipo `STRUCTURE`, como áreas de gol, pontos de interesse ou zonas de goleiro, **não colidem fisicamente** com os robôs ou bola, servem apenas como zonas de verificação lógica (ex: "robô chegou no ponto X", "bola entrou na área").

---

## 🔷 3. Objetos de Colisão

### `collision_manager.py`
Contém a classe `CollisionManagerSAT`, que realiza:

#### 🔍 Detecção de Colisões com SAT
- Utiliza o **Separating Axis Theorem** para detectar colisões entre os corpos poligonais.
- Verifica se há interseção nos eixos normais dos lados dos objetos.
- Se não houver eixo separador, os objetos colidem.

#### 🧩 Particionamento Espacial (Spatial Hashing)
- Otimiza a detecção dividindo o espaço em células (`cell_size`).
- Só testa colisões entre objetos que ocupam células próximas, reduzindo a complexidade de `O(n²)` para aproximadamente `O(n)`.

#### ⚖️ Resposta Física
- Aplica conservação do momento linear com diferentes massas.
- Considera o coeficiente de restituição e aplica correções de posição para evitar sobreposição.
- Inclui atrito entre robôs.

#### 📦 Integração com Objetos
- Trata colisões entre: robô-robô, bola-robô e bola-campo.
- Campo impede o movimento dos robôs e rebate a bola.

### `collision_polygon.py`, `collision_circle.py`, `collision_rectangle.py`, `collision_line.py`
Implementações dos corpos de colisão usados:

- `CollisionPolygon`: corpo genérico poligonal (usado para robôs e bola).
- `CollisionCircle`: corpo circular (usado em versões simplificadas ou testes).
- `CollisionRectangle`: usado para paredes e partes retangulares do campo.
- `CollisionLine`: útil para fronteiras e zonas lógicas do campo (ex: linha do gol).

Cada um desses objetos possui o método `collides_with(other)` que permite verificar colisões entre si de forma unificada.

---

## 🧠 4. Objetos Lógicos

### `timer.py`
- Implementa um temporizador interno.
- Pode ser usado para controlar o tempo de jogo, tempo de ações específicas, delays, etc.

### `team.py`
- Representa uma equipe.
- Armazena os robôs aliados e inimigos, podendo controlar comportamentos, estratégias e identificação de time.

### `game_logic.py`
> *(Preencher com a lógica principal do jogo, regras e controladores de rodada)*

---

## 📌 Observações

- O sistema foi projetado para suportar **diversas formas e colisões complexas**.
- Os objetos `STRUCTURES` são passivos, exceto o campo.
- É possível facilmente adicionar novos tipos de objetos ou regras na camada lógica (`game_logic.py`).

---


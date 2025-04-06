
---

## 📦 Estrutura Geral da Classe CollisionManagerSATA

```python
class CollisionManagerSAT:
    def __init__(self, cell_size=100):
```

A classe foi criada para gerenciar **detecção e resolução de colisões com resposta física**, utilizando:
- **SAT (Separating Axis Theorem)** para detecção de colisão entre polígonos.
- **Particionamento espacial com hash (Spatial Hashing)** para evitar testes desnecessários.
- **Coeficientes físicos (massa, restituição, atrito)** para aplicar respostas reais às colisões.

O `cell_size` define o **tamanho da célula da grade virtual** usada no particionamento espacial. Isso afeta o número de colisões verificadas por iteração.

---

## 🧠 Organização dos Objetos

```python
self.moving_objects = []     # Robôs e bola
self.static_objects = []     # Campo, gols, áreas, pontos, etc.
```

- `moving_objects`: armazenam os objetos **dinâmicos** (robôs e bola).
- `static_objects`: armazenam as **estruturas fixas**, como campo e áreas.

---

## 📦 Inserção de Objetos

```python
def add_object(self, obj):
    if obj.type_object in [ROBOT_OBJECT, BALL_OBJECT]:
        self.moving_objects.append(obj)
    else:
        self.static_objects.append(obj)
```

- Os objetos são separados logo ao serem adicionados.
- Os objetos móveis são os únicos considerados na resposta de colisão.
- As `STRUCTURES` são usadas só para informação (exceto o campo, que bloqueia robôs e rebate a bola).

---

## 📌 **Particionamento Espacial** – Spatial Hashing

### 🧮 Hash de Posição

```python
def get_cell(self, x, y):
    return int(x // self.cell_size), int(y // self.cell_size)
```

Cada objeto pertence a uma célula `(i, j)` da grade virtual.
Essa célula é obtida dividindo a posição `(x, y)` pela `cell_size`.

---

### 🔍 Mapeando Objetos em Células

```python
def build_spatial_map(self, objects):
    spatial_map = {}
    for obj in objects:
        cells = self.get_covered_cells(obj)
        for cell in cells:
            if cell not in spatial_map:
                spatial_map[cell] = []
            spatial_map[cell].append(obj)
    return spatial_map
```

- Cria um **mapa hash** com cada célula contendo os objetos que ocupam ela.
- O método `get_covered_cells()` retorna todas as células cobertas pelo polígono (objeto de colisão).

---

## 🎯 Detecção e Resolução de Colisões

```python
def handle_collisions(self):
    spatial_map = self.build_spatial_map(self.moving_objects)
```

- Apenas objetos **móveis** são considerados no mapeamento.
- Evita comparar objetos que não estão próximos.

---

### 🔍 Verificando Colisões com SAT

```python
if obj1.collision_object.collides_with(obj2.collision_object):
```

- Aqui ocorre a **detecção de colisão com SAT**.
- `SAT` verifica se existe um eixo onde as projeções dos dois polígonos **não se sobrepõem**.
- Se **não existir nenhum eixo separador**, há colisão.

---

### ⚖️ Cálculo da Resposta Física

```python
normal = self.get_collision_normal(obj1.collision_object, obj2.collision_object)
```

- A **normal da colisão** é usada para aplicar as forças corretamente.

---

### 📏 Separação de Objetos

```python
overlap = self.get_overlap(obj1.collision_object, obj2.collision_object, normal)
...
obj1.x -= correction[0]
obj1.y -= correction[1]
```

- Calcula o quanto os objetos estão sobrepostos e os separa antes de aplicar a resposta de velocidade.

---

### 📐 Conservação de Momento Linear

```python
v1n = np.dot(v1, normal)
v2n = np.dot(v2, normal)

...
v1n_post = (v1n * (m1 - e * m2) + (1 + e) * m2 * v2n) / (m1 + m2)
v2n_post = (v2n * (m2 - e * m1) + (1 + e) * m1 * v1n) / (m1 + m2)
```

- Essa fórmula aplica a **conservação de momento linear** com **restituição `e`**.
- `e = 1` para colisão perfeitamente elástica (ex: bola com robô).
- `e = 0` para inelástica (ex: robô com outro robô, com atrito).

---

### 🧲 Aplicação de Velocidade Pós-Colisão

```python
obj1.velocity = new_v1
obj2.velocity = new_v2
```

A nova velocidade é a soma da **componente normal pós-colisão** com a **componente tangencial inalterada** (assumindo atrito conservado parcialmente).

---

## ⚙️ Objeto Estrutural (Field)

```python
if obj2.type_object == FIELD_OBJECT:
```

- Apenas o campo interage com objetos móveis.
- Reflete a velocidade na direção da **normal do campo**, multiplicando pelo coeficiente de restituição.

---

## 🧠 Extras Importantes

### 💨 Friction (Atrito)

```python
friction = COEFFICIENT_FRICTION_ROBOT_ROBOT
```

- Aplica um fator de atrito à componente tangencial da velocidade.
- Útil para simular a energia perdida em colisões entre robôs.

---

## ✅ Conclusão

### O que esse sistema oferece:

✔️ Evita o problema de **verificar todos os pares** (usa spatial hashing)  
✔️ Detecta colisões **com precisão de polígonos rotacionados (SAT)**  
✔️ Calcula **resposta física realista** com **massa, velocidade, restituição e atrito**  
✔️ Suporta **múltiplos tipos de colisão** (bola-robô, robô-robô, bola-campo)  
✔️ Organizado e fácil de extender (ex: adicionar sensores, detector de entrada em área etc)

---

Se quiser, posso também te mostrar:
- Como logar os vetores e forças para debug
- Como desenhar as **normais de colisão** para visualizar as reações
- Como limitar a velocidade máxima pós-impacto pra evitar bugs de tunelamento

Só pedir 😎
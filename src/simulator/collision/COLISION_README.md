
# 🛠️ Sistema de Detecção e Resolução de Colisões 2D

Este módulo implementa um sistema robusto de detecção e resposta de colisões entre objetos geométricos em um ambiente 2D. Ele utiliza o algoritmo **Separating Axis Theorem (SAT)** para detectar colisões entre formas convexas, além de lógica de resposta física com impulso, torque e atrito. O sistema conta com separação espacial com grades para otimizar a resolução das colisões.

---

## 📦 Arquitetura Geral

- **Base:** Todas as formas herdam de `CollisionObject`.
- **Tipos de objetos:**
  - `CollisionPoint`: Ponto
  - `CollisionCircle`: Círculo
  - `CollisionRectangle`: Retângulo rotacionado
  - `CollisionLine`: Linha (segmento de reta finita)
  - `CollisionGroup`: Grupo de objetos (ex: campo ou carro com múltiplas peças)

---

## 🚦 MOVING vs STRUCTURE

- **MOVING:** Objetos com massa e momento de inércia. Ex: bolas, robôs.
  - Colidem entre si e com STRUCTURE.
- **STRUCTURE:** Estruturas estáticas (massa infinita). Ex: linhas do campo.
  - Apenas reagem a colisões com MOVING.

---

## 🔍 Detecção de Colisão

A detecção usa lógica polimórfica com `check_collision(other)`, que retorna:

```python
[True, mtv]  # Se colidiu
[False, None]  # Se não colidiu
```

Onde `mtv` é o **vetor mínimo de translação** para separar os objetos (atuando sempre sobre o MOVING).

### 🔧 Implementações:

- **SAT (Separating Axis Theorem):** Usado para retângulos, linhas e colisões complexas.
- **Interseção de Segmentos:** Para colisões entre linhas e retângulos.
- **AABB prévia:** `CollisionGroup` pode usar bounding boxes para otimizar detecção entre múltiplos objetos.

---

## 🔁 Resolução de Colisão

A função `resolve_collision_with_field(obj, mtv, contact_point)` aplica:

- Correção de posição com `mtv`
- Impulso normal para rebote (coeficiente de restituição)
- Impulso de atrito com base na velocidade tangencial
- Torque se houver deslocamento do ponto de contato

### Parâmetros físicos:

- `mass`, `inertia`: definidos nos MOVING
- `velocity`, `angular_velocity`: são atualizados com o tempo
- `apply_impulse(force, point)`: aplica impulso no centro ou em um ponto

---

## 📐 Colisão Retângulo × Linha

- A linha é tratada como um segmento finito.
- Colisão é detectada se:
  - Houver interseção direta com os lados do retângulo, **ou**
  - As projeções nas normais (SAT) se sobrepõem.
- O MTV resultante **atua sobre o retângulo (MOVING)** e aponta para fora do campo (STRUCTURE).

---

## ⚙️ Transformações

- Todos os objetos possuem métodos para `rotate(angle, center)` e manipulação da posição.
- O sistema trabalha em **coordenadas contínuas (cm)** e pode ser convertido para tela (pixels) externamente.

---

## 📌 Exemplo de Uso

```python
ball = Ball(x=50, y=50, radius=5)
line = CollisionLine(start=(0, 60), end=(100, 60))

collided, mtv = line.check_collision(ball.collision_object)
if collided:
    resolve_collision_with_field(ball, mtv)
```

---

## 🧪 Testes Recomendados

- ✅ Bola colidindo com linha horizontal e rebatendo corretamente
- ✅ Robô (retângulo rotacionado) colidindo com bordas e sendo empurrado para fora
- ✅ MTV sempre empurrando o MOVING para fora da STRUCTURE

---

## 📄 Observações

- O sistema de colisão é desacoplado da renderização.
- O MTV é sempre calculado com direção a partir da **linha ou estrutura** em direção ao **objeto móvel**.
- A lógica da direção do MTV é ajustada dinamicamente se necessário dentro da resolução da colisão.

---

## 📚 Dependências

- `numpy` para álgebra vetorial

---

## 🔄 Futuras Expansões

- Suporte a polígonos arbitrários convexos
- Otimização com spatial hashing
- Carros compostos por múltiplos `CollisionRectangle`
- Resolver BUGs com as bordas

# Melhorias para organizar dentro do sistema de colisões

---

### **Checklist de Otimização de Colisão**
| Ordem | Técnica                          | Dificuldade | Benefício Esperado                     | Como Verificar Sucesso            |
|-------|----------------------------------|-------------|----------------------------------------|-----------------------------------|
| 1     | **Perfilagem Inicial**           | Baixa       | Identifica gargalos reais              | `cProfile` + `snakeviz`           |
| 2     | **Early Exits**                  | Baixa       | Reduz verificações desnecessárias      | Menos chamadas a `check_collision` |
| 3     | **Cache de Spatial Hashing**     | Média       | Acelera busca por vizinhos             | Tempo reduzido em `_get_nearby_objects` |
| 4     | **Numba para Círculos**          | Média       | 10-100x mais rápido em colisões simples | Benchmarks com `timeit`           |
| 5     | **Pré-computar Matrizes de Rotação** | Alta    | Elimina recálculos trigonométricos     | CPU usage ↓ em rotações           |
| 6     | **Batch Processing com NumPy**   | Alta        | Vetoriza operações de pontos           | Tempo reduzido em `_extract_points` |
| 7     | **Otimização SAT (Normais em Cache)** | Alta   | Acelera colisão retângulo-retângulo    | Menos tempo em `check_collision_with_rectangle` |
| 8     | **Paralelização para Pares**     | Alta        | Distribui carga em CPUs múltiplas      | Uso de CPU ≈100% em testes        |
| 9     | **Ajuste de Parâmetros (CELL_SIZE)** | Baixa  | Melhora distribuição espacial          | Menos objetos por célula no grid  |
| 10    | **CCD Seletivo**                 | Média       | Só aplica CCD a objetos rápidos        | Menos chamadas a `check_continuous_collision` |

---

### **Passo a Passo Recomendado**
1. **Rode o Profiler**  
   ```python
   import cProfile
   profiler = cProfile.Profile()
   profiler.enable()
   # Seu código de simulação
   profiler.disable()
   profiler.dump_stats('perfil.colisao')
   ```
   - Use `snakeviz perfil.colisao` para visualizar.

2. **Implemente Early Exits**  
   Adicione no início de funções como `check_collision()`:
   ```python
   if not self.is_moving and not other.is_moving:
       return [False, None]
   ```

3. **Cache de Spatial Hashing**  
   Modifique `_hash_position` como no exemplo anterior.

4. **Numba para Funções Críticas**  
   Decore funções como `check_circle_collision` com `@njit`.

5. **Teste e Meça**  
   - Compare tempos antes/depois com:
     ```python
     import timeit
     timeit.timeit(lambda: manager.detect_and_resolve(objects), number=100)
     ```

---

### **Regras de Ouro**
- **Otimize apenas o que o profiler mostrar como gargalo**  
- **Mantenha um banchmarking suite** para evitar regressões  
- **Documente cada mudança** (ex: "Cache de matrizes em 15/08")  

Salve este checklist como `OPTIMIZAÇÃO_COLISÃO.md` no seu projeto e marque itens concluídos ✅.

---


# **Documentação do Sistema de Renderização SimWidget**  

## **📌 Visão Geral**  
O `SimWidget` é um widget PyQt6 que implementa um sistema avançado de **double buffering** para renderização 2D eficiente. Ele combina:  
- Um **backbuffer lógico** (`BackBuffer2D`) para armazenar comandos de desenho.  
- Um **backbuffer gráfico** (`QPixmap`) para renderização offscreen.  
- Um **frontbuffer** (`QPixmap`) para exibição controlada na tela.  

---

## **🔧 Diagrama de Funcionamento**  
```mermaid
graph TD
    A[Seu Código] -->|draw_rect, draw_img, etc.| B(BackBuffer2D)
    B -->|Lista de draw_calls| C[SimWidget.render_frame]
    C -->|QPainter| D[_back_pixmap]
    D -->|flip()| E[_front_pixmap]
    E -->|paintEvent| F((Tela))
```

### **Passo a Passo**:  
1. **Adição de Comandos**:  
   ```python
   sim_widget.back_buffer.draw_rect(...)  # Adiciona ao BackBuffer2D
   ```  
2. **Renderização Offscreen**:  
   ```python
   sim_widget.render_frame()  # Desenha no _back_pixmap (não atualiza a tela)
   ```  
3. **Atualização Controlada**:  
   ```python
   sim_widget.flip()  # Copia _back_pixmap → _front_pixmap e atualiza a tela
   ```  

---

## **🎯 Benefícios**  
| **Funcionalidade**       | **Vantagem**                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| **Controle de Atualização** | Atualiza a tela apenas quando `flip()` é chamado (evita *flickering*).     |
| **Economia de GPU**      | Nada é desenhado na tela sem necessidade (ótimo para jogos pausados).      |
| **Double Buffering**     | Renderização suave sem tearing.                                             |
| **Camadas (Layers)**     | Ordenação automática por `LAYER_BACKGROUND`, `LAYER_OBJECTS`, `LAYER_DEBUG`. |

---

## **⚙️ Métodos Principais**  
### **Controle de Renderização**  
| Método                    | Descrição                                                                 |
|---------------------------|---------------------------------------------------------------------------|
| `render_frame()`          | Renderiza tudo no `_back_pixmap` (sem atualizar a tela).                 |
| `flip()`                  | Copia o `_back_pixmap` para o `_front_pixmap` e atualiza a tela.         |
| `set_render_paused(True)` | Pausa a renderização automática (economiza recursos).                    |

### **Exemplo de Uso**  
```python
# 1. Adiciona desenhos
sim_widget.back_buffer.draw_rect(100, 100, 50, 50, color=(1, 0, 0, 1))

# 2. Renderiza offscreen
sim_widget.render_frame()

# 3. Atualiza a tela manualmente
sim_widget.flip()  # Agora o retângulo aparece!
```

---

## **🛠️ Estrutura de Arquivos**  
```
src/
├── ui/
│   ├── pages/
│   │   ├── objects/
│   │   │   ├── backbuffer2D.py   # Lógica de draw calls
│   │   │   ├── SimWidget.py      # Renderizador Qt
```

---

## **📊 Comparação com Outras Abordagens**  
| **Técnica**          | **Performance** | **Controle** | **Complexidade** |  
|----------------------|----------------|--------------|------------------|  
| **Desenho Direto**   | Baixa          | Limitado     | Simples          |  
| **OpenGL**           | Alta           | Complexo     | Alta             |  
| **SimWidget**        | **Média-Alta** | **Total**    | Moderada         |  

---

## **💡 Casos de Uso Ideais**  
- **Jogos 2D** (controle preciso de frames).  
- **Simulações** (renderização sob demanda).  
- **Aplicações com UI complexa** (menus, telas de pause).  

---

## **🚨 Notas Importantes**  
- **Sempre chame `flip()`** para exibir mudanças.  
- **Use `set_render_paused(True)`** em menus/pausa para economizar recursos.  
- **Renderize layers separadamente** para otimização (ex: só UI em `LAYER_DEBUG`).  

---

## **✅ Pronto para Uso!**  
Integre o `SimWidget` em seu projeto e controle cada frame como um profissional!  

```python
# Loop de jogo exemplo
while running:
    logica_do_jogo()
    sim_widget.render_frame()
    if frame_pronto:
        sim_widget.flip()  # Exibe quando estiver preparado
```
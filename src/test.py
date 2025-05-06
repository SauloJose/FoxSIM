from PIL import Image, ImageDraw

def gerar_robo_vss_png(cor_time, cor1, cor2, x_cm=7.5, caminho_saida="robo_vss.png"):
    """
    Gera uma imagem PNG de um robô VSS na escala correta (3.6 px = 1 cm).
    - cor_time: cor do retângulo inferior
    - cor1: cor do quadrado superior esquerdo
    - cor2: cor do quadrado superior direito
    - x_cm: lado do robô em centímetros
    """
    px_por_cm = 3.6
    lado_px = int(round(x_cm * px_por_cm))

    # Proporções fixas do desenho (referência: corpo 100x100, borda 105x105, rodas 10x40)
    prop_corpo = 1.0
    prop_borda = 1.03
    prop_roda_w = 0.15
    prop_roda_h = 0.60
    prop_sup_q = 0.5
    prop_inf_h = 0.5

    img_size = int(lado_px * prop_borda) + 2  # +2 para garantir espaço para borda
    img = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Quadrado preto maior (borda)
    borda_size = int(lado_px * prop_borda)
    borda_x = (img_size - borda_size) // 2
    borda_y = (img_size - borda_size) // 2
    draw.rectangle([borda_x, borda_y, borda_x+borda_size, borda_y+borda_size], fill="#000000")

    # Quadrado principal (corpo)
    quad_size = lado_px
    quad_x = (img_size - quad_size) // 2
    quad_y = (img_size - quad_size) // 2

    # Rodas (proporcionais ao lado)
    roda_w = int(lado_px * prop_roda_w)
    roda_h = int(lado_px * prop_roda_h)
    roda_y = quad_y + (quad_size - roda_h)//2
    # Esquerda
    draw.rectangle([quad_x-roda_w, roda_y, quad_x, roda_y+roda_h], fill="#111111")
    # Direita
    draw.rectangle([quad_x+quad_size, roda_y, quad_x+quad_size+roda_w, roda_y+roda_h], fill="#111111")

    # Quadrados superiores (proporcionais)
    sup_q = int(lado_px * prop_sup_q)
    draw.rectangle([quad_x, quad_y, quad_x+sup_q, quad_y+sup_q], fill=cor1)
    draw.rectangle([quad_x+sup_q, quad_y, quad_x+quad_size, quad_y+sup_q], fill=cor2)

    # Retângulo inferior (proporcional)
    inf_h = int(lado_px * prop_inf_h)
    draw.rectangle([quad_x, quad_y+sup_q, quad_x+quad_size, quad_y+quad_size], fill=cor_time)

    # Gira a imagem 90° no sentido horário
    img = img.rotate(-90, expand=True)
    img.save(caminho_saida)

# Exemplo de uso:
gerar_robo_vss_png("#1e90ff", "#ffcc00", "#ffffff", x_cm=7.5, caminho_saida="robo_vss.png")
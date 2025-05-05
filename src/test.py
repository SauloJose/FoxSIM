import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ui.pages.objects.SimWidget import SimulatorWidget
from ui.pages.objects.imageGL import Image

def main():
    app = QApplication(sys.argv)

    # Carrega imagem de fundo (campo)
    campo_img = Image("src/assets/field.png")
    width = campo_img.width
    height = campo_img.height

    widget = SimulatorWidget(width=width, height=height)
    widget.setWindowTitle("Teste SimulatorWidget")
    widget.set_background_image(campo_img)

    # Robô: 7 cm de lado, escala do campo: 3 px = 1 cm => 21 px de lado
    robo_tamanho_px = 7 * 3  # 21 px

    # Carrega imagens dos robôs
    robo_azul_img = Image("src/assets/ATA2.png")
    robo_vermelho_img = Image("src/assets/ATA1.png")  # ajuste o nome se necessário

    # Usa métodos da classe Image para ajustar o tamanho
    if robo_azul_img.width > 0:
        scale_azul = robo_tamanho_px / robo_azul_img.width
        robo_azul_img = robo_azul_img.set_scale(scale_azul)
    if robo_vermelho_img.width > 0:
        scale_vermelho = robo_tamanho_px / robo_vermelho_img.width
        robo_vermelho_img = robo_vermelho_img.set_scale(scale_vermelho)

    # Variáveis para animação simples
    pos_x = [200, 600]
    pos_y = [300, 300]
    angle = [0, 0]

    def animate():
        angle[0] = (angle[0] + 2) % 360
        angle[1] = (angle[1] - 2) % 360

        widget.back_buffer.clear()
        widget.back_buffer.draw_img(robo_azul_img, pos_x[0], pos_y[0], angle=angle[0], scale=1.0, alpha=1.0, layer=1)
        widget.back_buffer.draw_img(robo_vermelho_img, pos_x[1], pos_y[1], angle=angle[1], scale=1.0, alpha=1.0, layer=1)
        widget.back_buffer.draw_circle(width // 2, height // 2, 40, color=(1,0,0,0.5), layer=2)

    timer = QTimer()
    timer.timeout.connect(animate)
    timer.start(1000 // 60)  # 60 FPS

    widget.show()
    widget.start_timer()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

import time

class HighPrecisionTimer:
    def __init__(self, duration):
        """
        Inicializa o timer.
        :param duration: Duração do timer em segundos.
        """
        self.duration = duration
        self.start_time = None
        self.running = False

    def start(self):
        """Inicia o timer."""
        self.start_time = time.time()
        self.running = True

    def stop(self):
        """Para o timer."""
        self.running = False

    def get_time_left(self):
        """
        Retorna o tempo restante em segundos.
        :return: Tempo restante (float).
        """
        if not self.running or self.start_time is None:
            return self.duration
        elapsed = time.time() - self.start_time
        return max(0, self.duration - elapsed)

    def is_finished(self):
        """
        Verifica se o tempo acabou.
        :return: True se o tempo acabou, False caso contrário.
        """
        return self.get_time_left() <= 0
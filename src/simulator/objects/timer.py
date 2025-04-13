import time


class HighPrecisionTimer:
    def __init__(self, duration):
        """
        Inicializa o timer.
        :param duration: Duração do timer em segundos.
        """
        self.duration = duration           # Tempo total do cronômetro
        self.start_time = None             # Tempo de início do cronômetro
        self.running = False               # Flag indicando se o cronômetro está ativo
        self.paused = False                # Flag indicando se está pausado
        self.pause_start = None            # Armazena quando o cronômetro foi pausado
        self.total_paused_time = 0         # Tempo total acumulado em pausa

    def start(self):
        """Inicia o timer do zero."""
        self.reset()
        self.start_time = time.time()
        self.running = True

        
    def reset(self):
        """Reseta o timer para o estado inicial, sem criar uma nova instância."""
        self.start_time = None
        self.running = False
        self.paused = False
        self.pause_start = None
        self.total_paused_time = 0
        
    def pause(self):
        """Pausa o timer."""
        if self.running and not self.paused:
            self.paused = True
            self.pause_start = time.time()

    def resume(self):
        """Retoma o timer após uma pausa."""
        if self.running and self.paused:
            pause_duration = time.time() - self.pause_start
            self.total_paused_time += pause_duration
            self.paused = False
            self.pause_start = None

    def stop(self):
        """Para completamente o timer (sem considerar pausa)."""
        self.running = False
        self.paused = False
        self.pause_start = None
        self.total_paused_time = 0

    def get_time_left(self):
        """
        Retorna o tempo restante em segundos.
        :return: Tempo restante (float).
        """
        if not self.running or self.start_time is None:
            return self.duration

        if self.paused:
            elapsed = self.pause_start - self.start_time - self.total_paused_time
        else:
            elapsed = time.time() - self.start_time - self.total_paused_time

        return max(0, self.duration - elapsed)

    def is_finished(self):
        """
        Verifica se o tempo acabou.
        :return: True se o tempo acabou, False caso contrário.
        """
        return self.get_time_left() <= 0

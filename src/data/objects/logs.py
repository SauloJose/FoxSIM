import json
import time
from enum import Enum
from typing import List, Optional


class LogSystem(str, Enum):
    """
    Enumeração de sistemas de log.
    Define os sistemas que podem gerar logs.
    """
    CONTROL = "CONTROL"
    VISION = "VISION"
    SIMULATION = "SIMULATION"
    COMMUNICATION = "COMMUNICATION"
    APP = "SYSTEM APP"

    def __str__(self):
        return self



class LogType(str, Enum):
    """
    Enumeração de tipos de log.
    Define os níveis/classificações de log.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    CRITICAL = "CRITICAL" 

    def __str__(self):
        return self


class LogPriority(str, Enum):
    """
    Enumeração para prioridade dos logs.
    Pode ser usada para filtrar logs por criticidade.
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    def __str__(self):
        return self.value


class Log:
    def __init__(self, type: LogType, priority: LogPriority, message: str, system: LogSystem):
        self.timestamp = time.time()  # Tempo do evento em segundos desde epoch
        self.type = type
        self.priority = priority
        self.message = message
        self.system = system  # Nome do sistema gerador

    def to_dict(self):
        """
        Converte o log em dicionário para uso interno.
        """
        return {
            "timestamp": self.timestamp,
            "type": self.type,
            "priority": self.priority,
            "message": self.message,
            "system": self.system
        }

    def __str__(self):
        """
        Representação amigável em string do log, com data legível.
        """
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
        return f"[{ts}] [{self.system}] [{self.type}] ({self.priority}): {self.message}"

class LogManager:
    """
    Gerenciador de logs com gravação rápida em arquivos de texto plano (.log).
    Mantém um número limitado de logs em memória.
    """
    def __init__(self, auto_flush: bool = False, flush_path: Optional[str] = None, max_logs: int = 1000):
        self.logs: List[Log] = []
        self.auto_flush = auto_flush
        self.flush_path = flush_path
        self.max_logs = max_logs  # Novo: número máximo de logs mantidos na memória

    def add_log(self, log: Log):
        self.logs.append(log)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)  # Remove o log mais antigo
        if self.auto_flush and self.flush_path:
            self.flush_to_file(self.flush_path, append=True)

    def log(self, type: LogType, priority: LogPriority, message: str):
        self.add_log(Log(type, priority, message))

    def clear_logs(self):
        self.logs.clear()

    def get_logs(self) -> List[Log]:
        return self.logs

    def get_logs_by_type(self, log_type: LogType) -> List[Log]:
        return [log for log in self.logs if log.type == log_type]

    def get_logs_by_priority(self, priority: LogPriority) -> List[Log]:
        return [log for log in self.logs if log.priority == priority]

    def get_logs_by_message(self, message: str) -> List[Log]:
        return [log for log in self.logs if message in log.message]

    def flush_to_file(self, path: str, append: bool = False):
        """
        Salva os logs em um arquivo de texto simples (.log).
        Cada linha é uma string formatada com timestamp.
        """
        mode = "a" if append else "w"
        with open(path, mode, encoding="utf-8") as f:
            for log in self.logs:
                f.write(str(log) + "\n")
        if not append:
            self.clear_logs()

    def load_from_file(self, path: str) -> List[Log]:
        """
        Carrega logs de um arquivo de texto simples (.log).
        Apenas para leitura de histórico, sem recriar os objetos Log.
        """
        loaded_logs = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                loaded_logs.append(line.strip())
        return loaded_logs

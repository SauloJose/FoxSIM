import numpy as np
import subprocess 
import pkg_resources
import sys 

def get_color(name):
    colors = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
    }
    return colors.get(name.lower(), (255, 255, 255))

def calculate_distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return np.array([0.0, 0.0])
    return v / norm

def install_requirements(requirements_file='requirements.txt'):
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            required = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f" Arquivo {requirements_file} não encontrado.")
        return
    except UnicodeDecodeError:
        print(f" Erro de codificação ao ler {requirements_file}. Use UTF-8.")
        return

    installed = {pkg.key for pkg in pkg_resources.working_set}

    for requirement in required:
        pkg_name = requirement.split('==')[0].lower()
        if pkg_name not in installed:
            print(f" Instalando pacote ausente: {requirement}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            except subprocess.CalledProcessError as e:
                print(f" Erro ao instalar {requirement}: {e}")
        else:
            print(f" {pkg_name} já está instalado.")
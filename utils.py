import pygame
from settings import WHITE, screen

def read_from_arduino(serial_connection):
    if serial_connection.in_waiting > 0:
        try:
            data = serial_connection.readline().decode('utf-8').strip()
            return data
        except UnicodeDecodeError:
            print("Erro ao decodificar dados da serial")
            return None
    return None

def show_pause_menu():
    font = pygame.font.SysFont(None, 40)
    text = font.render("PAUSE", True, WHITE)
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))

def show_victory_message():
    font = pygame.font.SysFont(None, 40)
    text = font.render("Parabéns! Você completou todos os níveis!", True, WHITE)
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))

def show_failure_message(level, score, time_left):
    font = pygame.font.SysFont(None, 40)
    message = f"Você parou no nível {level}. Pontuação: {score}, Tempo restante: {time_left}s"
    text = font.render(message, True, WHITE)
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2))

def draw_level_and_time(level, time_left):
    font = pygame.font.SysFont(None, 36)
    level_text = font.render(f"Nível: {level + 1}", True, WHITE)
    screen.blit(level_text, (screen.get_width() - level_text.get_width() - 10, 10))
    time_text = font.render(f"Tempo: {time_left}s", True, WHITE)
    screen.blit(time_text, (screen.get_width() - time_text.get_width() - 10, 50))

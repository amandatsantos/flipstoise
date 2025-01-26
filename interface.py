import pygame
import random
import serial
import time

# Inicializando o Pygame
pygame.init()

# Configurações da tela
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Controle com Arduino")

# Cores
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Velocidade do jogador e dos obstáculos
player_speed = 5
bullet_speed = 7
obstacle_speed = 3

# Definir o relógio
clock = pygame.time.Clock()

# Classe do jogador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width // 2, screen_height - 50)

    def update(self, movement):
        if movement == "Esquerda" and self.rect.left > 0:
            self.rect.x -= player_speed
        elif movement == "Direita" and self.rect.right < screen_width:
            self.rect.x += player_speed

# Classe do tiro
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.y -= bullet_speed  # Movimento do tiro
        if self.rect.bottom < 0:
            self.kill()  # Remove o tiro quando sair da tela

# Classe do obstáculo
class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
    
    def update(self):
        self.rect.y += obstacle_speed
        if self.rect.top > screen_height:
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = random.randint(-100, -40)

# Função para ler dados do Arduino
def read_from_arduino(serial_connection):
    if serial_connection.in_waiting > 0:
        try:
            data = serial_connection.readline().decode('utf-8').strip()
            return data
        except UnicodeDecodeError:
            print("Erro ao decodificar dados da serial")
            return None
    return None

# Função para exibir o menu de pausa
def show_pause_menu():
    font = pygame.font.SysFont(None, 40)
    text = font.render("PAUSE", True, WHITE)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2))

# Função para exibir mensagem final de vitória
def show_victory_message():
    font = pygame.font.SysFont(None, 40)
    text = font.render("Parabéns! Você completou todos os níveis!", True, WHITE)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2))

# Função para exibir mensagem de falha
def show_failure_message(level, score, time_left):
    font = pygame.font.SysFont(None, 40)
    message = f"Você parou no nível {level}. Pontuação: {score}, Tempo restante: {time_left}s"
    text = font.render(message, True, WHITE)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2))
# Função para desenhar os níveis e o tempo restante
def draw_level_and_time(level, time_left):
    font = pygame.font.SysFont(None, 36)
    
    # Exibir o nível atual
    level_text = font.render(f"Nível: {level + 1}", True, WHITE)
    screen.blit(level_text, (screen_width - level_text.get_width() - 10, 10))

    # Exibir o tempo restante
    time_text = font.render(f"Tempo: {time_left}s", True, WHITE)
    screen.blit(time_text, (screen_width - time_text.get_width() - 10, 50))
# Função principal do jogo
# Função principal do jogo
def main():
    # Configurar a conexão serial com o Arduino (ajuste a porta conforme necessário)
    arduino = serial.Serial('COM7', 9600)  

    # Criar o jogador e o grupo de sprites
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()  # Grupo de tiros
    obstacles = pygame.sprite.Group()  # Grupo de obstáculos
    score = 0  # Pontuação do jogador

    # Criar alguns obstáculos iniciais
    for _ in range(5):  # 5 obstáculos no início
        obstacle = Obstacle()
        all_sprites.add(obstacle)
        obstacles.add(obstacle)

    movement = "Parado"  # Inicializa o jogador parado
    running = True
    game_paused = False  # Flag para controlar se o jogo está pausado
    button_press_count = 0  # Contador de pressionamentos do botão
    last_button_press_time = 0  # Tempo da última pressão
    button_press_start_time = None  # Tempo de início da pressão

    levels = [(30, 40), (20, 30), (15, 25)]  # (Tempo limite, Pontos necessários)
    current_level = 0
    level_time_limit, level_goal = levels[current_level]
    level_start_time = time.time()

    while running:
        screen.fill(BLACK)

        # Verificar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Ler os dados do Arduino e atualizar o movimento
        arduino_data = read_from_arduino(arduino)
        
        if arduino_data:
            if "Potenciômetro:" in arduino_data:
                parts = arduino_data.split(",")
                potentiometer_value = int(parts[0].split(":")[1].strip())  # Obtém o valor do potenciômetro
                button_state = int(parts[1].split(":")[1].strip())  # Obtém o estado do botão
                
                # Controlar a direção com base no valor do potenciômetro
                if potentiometer_value < 512:
                    movement = "Esquerda"
                elif potentiometer_value > 512:
                    movement = "Direita"
                else:
                    movement = "Parado"

                # Lógica de tempo de pressionamento do botão
                if button_state == 0:  # Quando o botão está pressionado (LOW)
                    if button_press_start_time is None:
                        button_press_start_time = time.time()  # Marcar o início da pressão

                else:  # Quando o botão não está pressionado
                    if button_press_start_time is not None:
                        press_duration = time.time() - button_press_start_time
                        if press_duration < 1:  # Pressionamento curto
                            if button_press_count == 0:
                                bullet = Bullet(player.rect.centerx, player.rect.top)
                                all_sprites.add(bullet)
                                bullets.add(bullet)
                        else:  # Pressionamento longo (mais de 1 segundo)
                            # Alternar entre pausa e despausa
                            game_paused = not game_paused
                        button_press_start_time = None  # Resetar o tempo de pressão

        # Se o jogo não estiver pausado, atualiza os sprites
        if not game_paused:
            player.update(movement)
            bullets.update()
            obstacles.update()

            # Verificar colisões entre tiros e obstáculos
            for bullet in bullets:
                collided_obstacles = pygame.sprite.spritecollide(bullet, obstacles, True)
                for obstacle in collided_obstacles:
                    score += 10  # Incrementa 10 pontos por cada obstáculo destruído
                    bullet.kill()  # Remove o tiro quando ele colide com o obstáculo

            # Adicionar novos obstáculos a cada nível
            if len(obstacles) < 5 + current_level * 2:  # Adiciona obstáculos a cada nível
                new_obstacle = Obstacle()
                all_sprites.add(new_obstacle)
                obstacles.add(new_obstacle)

        # Exibir a pontuação
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Pontuação: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Atualizar o tempo restante para o nível atual
        time_left = level_time_limit - int(time.time() - level_start_time)
        if time_left <= 0:  # Se o tempo se esgotou
            if score >= level_goal:  # Se o jogador atingir a meta de pontos
                current_level += 1
                if current_level < len(levels):
                    level_time_limit, level_goal = levels[current_level]
                    level_start_time = time.time()
                    score = 0  # Resetar a pontuação para o próximo nível
                else:
                    show_victory_message()
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    running = False
            else:
                show_failure_message(current_level + 1, score, time_left)
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False

        # Desenhar todos os sprites
        all_sprites.draw(screen)

        # Desenhar o nível e o tempo restante
        draw_level_and_time(current_level, time_left)

        # Atualiza a tela
        pygame.display.flip()

        # Controla o FPS
        clock.tick(60)

    pygame.quit()
    arduino.close()  # Fecha a conexão serial

# Rodar o jogo
if __name__ == "__main__":
    main()


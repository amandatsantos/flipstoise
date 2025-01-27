import pygame
import serial
import time

from entities import Bullet, Obstacle, Player
from settings import BLACK, WHITE, screen, clock
from utils import draw_level_and_time, read_from_arduino, show_failure_message, show_victory_message

def main():
    pygame.init()

    # conexão serial com o Arduino 
    arduino = serial.Serial('COM9', 9600)  

     
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()  
    obstacles = pygame.sprite.Group()  
    score = 0  # pontos do player

    for _ in range(5):  # 5 obstáculos no início
        obstacle = Obstacle()
        all_sprites.add(obstacle)
        obstacles.add(obstacle)

    movement = "Parado"  # status do start 
    running = True
    game_paused = False  #  controlar se o jogo está pausado
    button_press_count = 0  # Contador de pressionamentos do botão
    last_button_press_time = 0  # Tempo da última pressão
    button_press_start_time = None  # Tempo de início da pressão

    levels = [(30, 40), (20, 30), (15, 25)]  # (Tempo limite, Pontos necessários) em relacao as fases to-do alterar
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
                potentiometer_value = int(parts[0].split(":")[1].strip())  # valor do potenciômetro
                button_state = int(parts[1].split(":")[1].strip())  #  estado do botão
                
                #  direção com base no valor do potenciômetro
                if potentiometer_value < 512:
                    movement = "Esquerda"
                elif potentiometer_value > 512:
                    movement = "Direita"
                else:
                    movement = "Parado"

                #  tempo de pressionamento do botão
                if button_state == 0:  # Quando o botão está pressionado (LOW)
                    if button_press_start_time is None:
                        button_press_start_time = time.time()  # marcar o início da pressão

                else:  # botão não está pressionado
                    if button_press_start_time is not None:
                        press_duration = time.time() - button_press_start_time
                        if press_duration < 1:  # press curto
                            if button_press_count == 0:
                                bullet = Bullet(player.rect.centerx, player.rect.top)
                                all_sprites.add(bullet)
                                bullets.add(bullet)
                        else:  # press longo (mais de 1 segundo)
                            # pausa e despausa
                            game_paused = not game_paused
                        button_press_start_time = None  # resetar o tempo de pressão

        # caso jogo não estiver pausado, atualiza os sprites
        if not game_paused:
            player.update(movement)
            bullets.update()
            obstacles.update()

            # verificar colisões entre tiros e obstáculos
            for bullet in bullets:
                collided_obstacles = pygame.sprite.spritecollide(bullet, obstacles, True)
                for obstacle in collided_obstacles:
                    score += 10  # + 10 pontos por cada obstáculo destruído
                    bullet.kill()  # remove o tiro quando ele colide com o obstáculo

            # Adicionar novos obstáculos a cada nível
            if len(obstacles) < 5 + current_level * 2:  # add obstáculos a cada nível
                new_obstacle = Obstacle()
                all_sprites.add(new_obstacle)
                obstacles.add(new_obstacle)

        # exibir a pontuação
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Pontuação: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # att o tempo restante para o nível atual
        time_left = level_time_limit - int(time.time() - level_start_time)
        if time_left <= 0:  # caso tempo acabar
            if score >= level_goal:  # se atingir a meta de pontos
                current_level += 1
                if current_level < len(levels):
                    level_time_limit, level_goal = levels[current_level]
                    level_start_time = time.time()
                    score = 0  # rsetar a pontuação para o prx nível
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

        # desenhar todos os sprites
        all_sprites.draw(screen)

        # desenhar o nível e o tempo restante
        draw_level_and_time(current_level, time_left)

        # att a tela
        pygame.display.flip()

        # xontrola o FPS
        clock.tick(60)

    pygame.quit()
    arduino.close()  # fecha a conexão serial

if __name__ == "__main__":
    main()

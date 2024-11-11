import pygame
import sys
import time
import webbrowser

# Инициализация Pygame
pygame.init()

# Задание размеров окна
WIDTH, HEIGHT = 700, 500  # Увеличили размеры окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Markuss Simulator")

# Цвета
WHITE = (255, 255, 255)
BUTTON_COLOR = (200, 0, 0)
BUTTON_HOVER_COLOR = (255, 0, 0)

# Параметры кнопок
button_text_1 = "дахуя бан накидал"
button_text_2 = "помогите криптопиздюку максиму"
button_font = pygame.font.SysFont(None, 30)  # Увеличили размер шрифта

# Первая кнопка (закрытие игры)
button_rect_1 = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 100, 400, 80)  # Увеличили размеры кнопок

# Вторая кнопка (ссылка)
button_rect_2 = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 + 20, 400, 80)

# Флаг для отображения скримера
show_screamer = False

# Основной цикл игры
running = True
while running:
    # Заполнение экрана
    screen.fill(WHITE)

    if show_screamer:
        # Загрузка и отображение изображения скримера
        screamer_image = pygame.image.load("skrimer.png")
        screamer_image = pygame.transform.scale(screamer_image, (WIDTH, HEIGHT))
        screen.blit(screamer_image, (0, 0))

        pygame.display.flip()
        time.sleep(2)  # Показываем скример 2 секунды
        running = False  # Закрываем программу после этого
    else:
        # Получение позиции курсора
        mouse_pos = pygame.mouse.get_pos()

        # Отрисовка первой кнопки
        if button_rect_1.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect_1)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect_1)
        text_surface_1 = button_font.render(button_text_1, True, WHITE)
        text_rect_1 = text_surface_1.get_rect(center=button_rect_1.center)
        screen.blit(text_surface_1, text_rect_1)

        # Отрисовка второй кнопки
        if button_rect_2.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect_2)
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect_2)
        text_surface_2 = button_font.render(button_text_2, True, WHITE)
        text_rect_2 = text_surface_2.get_rect(center=button_rect_2.center)
        screen.blit(text_surface_2, text_rect_2)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Проверка нажатия на первую кнопку (скример)
            if button_rect_1.collidepoint(mouse_pos) and not show_screamer:
                show_screamer = True
            # Проверка нажатия на вторую кнопку (ссылка)
            elif button_rect_2.collidepoint(mouse_pos):
                webbrowser.open("https://app.getgrass.io/register?referralCode=2AmEBXJTXIEg-gh")  # Замените на нужный URL

    # Обновление экрана
    pygame.display.flip()

# Завершение Pygame
pygame.quit()
sys.exit()

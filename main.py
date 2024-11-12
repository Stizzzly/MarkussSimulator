import pygame
import sys
import webbrowser

# Инициализация Pygame
pygame.init()

# Задание размеров окна
WIDTH, HEIGHT = 700, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Markuss Simulator")

# Цвета
WHITE = (255, 255, 255)
BUTTON_COLOR = (200, 0, 0)
BUTTON_HOVER_COLOR = (255, 0, 0)
CIRCLE_COLOR = (255, 0, 0)
OUTLINE_COLOR = (255, 0, 0)

# Параметры кнопок
button_text_1 = "дахуя бан накидал"
button_text_2 = "помогите криптопиздюку максиму"
button_font = pygame.font.SysFont(None, 26)

# Первая и вторая кнопки (справа)
button_rect_1 = pygame.Rect(WIDTH - 400, HEIGHT // 2 - 100, 300, 80)
button_rect_2 = pygame.Rect(WIDTH - 400, HEIGHT // 2 + 20, 300, 80)

# Круглая кнопка слева с изображением
circle_center = (150, HEIGHT // 2)
circle_radius = 75
outline_radius = circle_radius + 15
click_count = 0

# Загрузка изображения Markuss и создание круговой маски
markus_image = pygame.image.load("markuss.png")
markus_image = pygame.transform.scale(markus_image, (circle_radius * 2, circle_radius * 2))

# Создание круглой маски
mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
pygame.draw.circle(mask, (255, 255, 255, 255), (circle_radius, circle_radius), circle_radius)
markus_image.set_colorkey((0, 0, 0))

# Применение маски к изображению
markus_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

# Текст для окна
modal_text = "Вы помогли заработать криптопиздюку максиму целых 0.00000001 евро, он вам отсыпал долю в виде 1000 маркус коинов"
modal_title = "Помощь от криптопиздюка"


# Функция для разбивки текста на несколько строк, чтобы он не выходил за пределы окна
def wrap_text(text, font, width):
    words = text.split(' ')
    lines = []
    current_line = words[0]
    for word in words[1:]:
        if font.size(current_line + ' ' + word)[0] <= width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


# Функция для отображения модального окна
def show_modal(message, title):
    font = pygame.font.SysFont(None, 30)
    title_text = font.render(title, True, WHITE)

    # Разбиваем текст на несколько строк, чтобы он не выходил за пределы окна
    message_lines = wrap_text(message, font, WIDTH // 2)

    # Отображение модального окна
    modal_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
    button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 100, 150, 40)

    # Отображаем фон модального окна
    pygame.draw.rect(screen, (0, 0, 0, 150), modal_rect)

    # Отображаем заголовок
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4 + 20))

    # Отображаем текст, разбитый на несколько строк
    y_offset = HEIGHT // 4 + 60
    for line in message_lines:
        line_text = font.render(line, True, WHITE)
        screen.blit(line_text, (WIDTH // 2 - line_text.get_width() // 2, y_offset))
        y_offset += 40

    # Кнопка закрытия окна
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
    close_button_text = font.render("Закрыть", True, WHITE)
    screen.blit(close_button_text, (button_rect.centerx - close_button_text.get_width() // 2,
                                    button_rect.centery - close_button_text.get_height() // 2))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                return True
    return False


# Загрузка изображения для скримера
screamer_image = pygame.image.load("skrimer.png")
screamer_image = pygame.transform.scale(screamer_image, (WIDTH, HEIGHT))
screen.blit(screamer_image, (0, 0))

# Основной цикл игры
running = True
showing_modal = False
showing_screamer = False

while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    # Круглая кнопка с обводкой и изображением
    pygame.draw.circle(screen, OUTLINE_COLOR, circle_center, outline_radius)
    pygame.draw.circle(screen, CIRCLE_COLOR, circle_center, circle_radius)
    screen.blit(markus_image,
                (circle_center[0] - circle_radius, circle_center[1] - circle_radius))

    # Отображение счётчика
    counter_text = button_font.render(f"Маркус коины: {click_count}", True, BUTTON_COLOR)
    screen.blit(counter_text, (10, 10))

    # Отрисовка первой кнопки
    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if button_rect_1.collidepoint(mouse_pos) else BUTTON_COLOR,
                     button_rect_1)
    text_surface_1 = button_font.render(button_text_1, True, WHITE)
    text_rect_1 = text_surface_1.get_rect(center=button_rect_1.center)
    screen.blit(text_surface_1, text_rect_1)

    # Отрисовка второй кнопки
    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if button_rect_2.collidepoint(mouse_pos) else BUTTON_COLOR,
                     button_rect_2)
    text_surface_2 = button_font.render(button_text_2, True, WHITE)
    text_rect_2 = text_surface_2.get_rect(center=button_rect_2.center)
    screen.blit(text_surface_2, text_rect_2)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if (mouse_pos[0] - circle_center[0]) ** 2 + (mouse_pos[1] - circle_center[1]) ** 2 < circle_radius ** 2:
                click_count += 1
            elif button_rect_1.collidepoint(mouse_pos):
                showing_screamer = True
            elif button_rect_2.collidepoint(mouse_pos):
                webbrowser.open("https://app.getgrass.io/register?referralCode=2AmEBXJTXIEg-gh")
                click_count += 1000
                showing_modal = True

    # Если показываем скример
    if showing_screamer:
        screen.blit(screamer_image, (0, 0)) 
        pygame.display.flip()
        pygame.time.wait(2000) 
        showing_screamer = False 

    # Если окно открыто, показываем его
    if showing_modal:
        if show_modal(modal_text, modal_title):
            showing_modal = False

    pygame.display.flip()

# Завершение игры
pygame.quit()
sys.exit()

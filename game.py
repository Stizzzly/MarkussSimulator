import pygame
import sys
import os
import webbrowser
import json


# Функция для определения пути к ресурсам
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Функции для сохранения и загрузки click_count
def save_click_count(count, bonus_claimed):
    user_name = os.getlogin()  # Получаем имя пользователя
    folder_path = f"C:\\Users\\{user_name}\\AppData\\Local\\STIZZLY\\MarkussSimulator"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, "click_count.json")

    with open(file_path, "w") as file:
        json.dump({"click_count": count, "bonus_claimed": bonus_claimed}, file)


def load_click_count():
    user_name = os.getlogin()  # Получаем имя пользователя
    folder_path = f"C:\\Users\\{user_name}\\AppData\\Local\\STIZZLY\\MarkussSimulator"
    file_path = os.path.join(folder_path, "click_count.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            return data.get("click_count", 0), data.get("bonus_claimed", False)
    return 0, False


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
click_count, bonus_claimed = load_click_count()  # Загружаем значение и состояние бонуса из файла

# Загрузка изображений
markus_image_path = resource_path("markuss.png")
markus_image = pygame.image.load(markus_image_path)
markus_image = pygame.transform.scale(markus_image, (circle_radius * 2, circle_radius * 2))

# Иконка empty_card для верхнего правого угла
empty_card_path = resource_path("empty_cart.png")
empty_card_image = pygame.image.load(empty_card_path)
empty_card_image = pygame.transform.scale(empty_card_image, (70, 50))
empty_card_rect = empty_card_image.get_rect(topright=(WIDTH - 10, 10))

# Создание круглой маски
mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
pygame.draw.circle(mask, (255, 255, 255, 255), (circle_radius, circle_radius), circle_radius)
markus_image.set_colorkey((0, 0, 0))
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
    message_lines = wrap_text(message, font, WIDTH // 2)

    modal_rect = pygame.Rect(WIDTH // 4, HEIGHT // 4, WIDTH // 2, HEIGHT // 2)
    button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 100, 150, 40)

    pygame.draw.rect(screen, (0, 0, 0, 150), modal_rect)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4 + 20))

    y_offset = HEIGHT // 4 + 60
    for line in message_lines:
        line_text = font.render(line, True, WHITE)
        screen.blit(line_text, (WIDTH // 2 - line_text.get_width() // 2, y_offset))
        y_offset += 40

    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
    close_button_text = font.render("Закрыть", True, WHITE)
    screen.blit(close_button_text, (button_rect.centerx - close_button_text.get_width() // 2,
                                    button_rect.centery - close_button_text.get_height() // 2))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                return True
    return False


# Функция для отображения интерфейса магазина
def show_shop():
    font = pygame.font.SysFont(None, 36)
    shop_text = font.render("Магазин Маркус коинов", True, WHITE)

    # Фон магазина
    pygame.draw.rect(screen, (50, 50, 50), (50, 50, WIDTH - 100, HEIGHT - 100))
    screen.blit(shop_text, (WIDTH // 2 - shop_text.get_width() // 2, 100))

    # Добавим кнопку выхода из магазина
    exit_button_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 80, 100, 40)
    pygame.draw.rect(screen, BUTTON_COLOR, exit_button_rect)
    exit_text = font.render("Назад", True, WHITE)
    screen.blit(exit_text, (exit_button_rect.centerx - exit_text.get_width() // 2,
                            exit_button_rect.centery - exit_text.get_height() // 2))

    return exit_button_rect


# Загрузка изображения для скримера
screamer_image_path = resource_path("skrimer.png")
screamer_image = pygame.image.load(screamer_image_path)
screamer_image = pygame.transform.scale(screamer_image, (WIDTH, HEIGHT))

# Основной цикл игры
running = True
showing_modal = False
showing_screamer = False
showing_shop = False

while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    if showing_shop:
        exit_button_rect = show_shop()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_click_count(click_count, bonus_claimed)  # Сохраняем состояние при выходе
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button_rect.collidepoint(mouse_pos):
                    showing_shop = False
    else:
        pygame.draw.circle(screen, OUTLINE_COLOR, circle_center, outline_radius)
        pygame.draw.circle(screen, CIRCLE_COLOR, circle_center, circle_radius)
        screen.blit(markus_image, (circle_center[0] - circle_radius, circle_center[1] - circle_radius))

        # Отображение иконки в верхнем правом углу
        screen.blit(empty_card_image, empty_card_rect)

        counter_text = button_font.render(f"Маркус коины: {click_count}", True, BUTTON_COLOR)
        screen.blit(counter_text, (10, 10))

        # Кнопка 1 (не меняется)
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if button_rect_1.collidepoint(mouse_pos) else BUTTON_COLOR,
                         button_rect_1)
        text_surface_1 = button_font.render(button_text_1, True, WHITE)
        text_rect_1 = text_surface_1.get_rect(center=button_rect_1.center)
        screen.blit(text_surface_1, text_rect_1)

        # Кнопка 2 (меняется текст, если бонус получен)
        button_text_2_display = button_text_2 if not bonus_claimed else "Ты помог криптопиздюку максу"
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if button_rect_2.collidepoint(mouse_pos) else BUTTON_COLOR,
                         button_rect_2)
        text_surface_2 = button_font.render(button_text_2_display, True, WHITE)
        text_rect_2 = text_surface_2.get_rect(center=button_rect_2.center)
        screen.blit(text_surface_2, text_rect_2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_click_count(click_count, bonus_claimed)  # Сохраняем состояние при выходе
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (mouse_pos[0] - circle_center[0]) ** 2 + (mouse_pos[1] - circle_center[1]) ** 2 < circle_radius ** 2:
                    click_count += 1
                elif button_rect_1.collidepoint(mouse_pos):
                    showing_screamer = True
                elif button_rect_2.collidepoint(mouse_pos):
                    if not bonus_claimed:
                        webbrowser.open("https://app.getgrass.io/register?referralCode=2AmEBXJTXIEg-gh")
                        click_count += 1000
                        bonus_claimed = True  # Устанавливаем флаг, что бонус получен
                        save_click_count(click_count, bonus_claimed)  # Сохраняем данные
                        showing_modal = True
                elif empty_card_rect.collidepoint(mouse_pos):
                    showing_shop = True

    if showing_screamer:
        screen.blit(screamer_image, (0, 0))
        pygame.display.update()
        pygame.time.wait(2000)
        showing_screamer = False

    if showing_modal and show_modal(modal_text, modal_title):
        showing_modal = False

    pygame.display.update()

pygame.quit()

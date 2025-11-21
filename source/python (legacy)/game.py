import pygame
import sys
import os
import webbrowser
import json
import platform
import time
import random


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def detect_os():
    os_name = platform.system()
    if os_name == "Linux":
        return "Linux"
    elif os_name == "Windows":
        return "Windows"
    else:
        return "Unknown"
        print("Операционная система не определена, сохранение невозможно, свяжитесь с разработчиком")


def get_save_path():
    os_type = detect_os()
    print(f"Операционная система: {os_type}")

    if os_type == "Linux":
        return os.path.expanduser("~/.MarkussSimulator/click_count.json")
    elif os_type == "Windows":
        user_name = os.getlogin()
        return f"C:\\Users\\{user_name}\\AppData\\Local\\STIZZLY\\MarkussSimulator\\click_count.json"
    else:
        raise Exception("Неизвестная операционная система. Сохранение невозможно.")


def load_click_count():
    save_path = get_save_path()
    folder_path = os.path.dirname(save_path)

    if folder_path and not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if os.path.exists(save_path):
        try:
            with open(save_path, "r") as file:
                data = json.load(file)
                return data.get("click_count", 0), data.get("bonus_claimed", False), data.get("mezpils_buy", False), data.get("adazu_buy", False)
        except (json.JSONDecodeError, IOError):
            print("Ошибка чтения файла. Используются значения по умолчанию.")

    print("Файл не найден. Используются значения по умолчанию.")
    return 0, False, False


def save_click_count(click_count, bonus_claimed, mezpils_buy, adazu_buy):
    save_path = get_save_path()
    folder_path = os.path.dirname(save_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    data = {
        "click_count": click_count,
        "bonus_claimed": bonus_claimed,
        "mezpils_buy": mezpils_buy,
        "adazu_buy": adazu_buy

    }

    try:
        with open(save_path, "w") as file:
            json.dump(data, file)
        print(f"Данные сохранены: {data}")
        print(f"Данные сохранены в файл: {save_path}")
    except IOError as e:
        print(f"Ошибка записи файла: {e}")


pygame.init()
if detect_os() in ["Windows", "Linux"]:
    WIDTH, HEIGHT = 700, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Markuss Simulator")
elif detect_os() in ["Android"]:
    WIDTH, HEIGHT = 360, 640
    screen = pygame.display.set_mode((HEIGHT, WIDTH), pygame.FULLSCREEN)


def draw_rotated_surface(surface):
    rotated_surface = pygame.transform.rotate(surface, -90)
    return rotated_surface


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (200, 0, 0)
BUTTON_HOVER_COLOR = (255, 0, 0)
CIRCLE_COLOR = (255, 0, 0)
OUTLINE_COLOR = (255, 0, 0)

button_text_1 = "дахуя бан накидал"
button_text_2 = "помогите криптопиздюку максиму"
button_font = pygame.font.SysFont(None, 26)

button_rect_1 = pygame.Rect(WIDTH - 400, HEIGHT // 2 - 100, 300, 80)
button_rect_2 = pygame.Rect(WIDTH - 400, HEIGHT // 2 + 20, 300, 80)

circle_center = (150, HEIGHT // 2)
circle_radius = 75
outline_radius = circle_radius + 15
click_count, bonus_claimed, mezpils_buy, adazu_buy = load_click_count()

markus_image_path = resource_path("markuss.png")
markus_image = pygame.image.load(markus_image_path)
markus_image = pygame.transform.scale(markus_image, (circle_radius * 2, circle_radius * 2))

empty_card_path = resource_path("empty_cart.png")
empty_card_image = pygame.image.load(empty_card_path)
empty_card_image = pygame.transform.scale(empty_card_image, (70, 50))
empty_card_rect = empty_card_image.get_rect(topright=(WIDTH - 10, 10))

mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
pygame.draw.circle(mask, (255, 255, 255, 255), (circle_radius, circle_radius), circle_radius)
markus_image.set_colorkey((0, 0, 0))
markus_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

modal_text = "Вы помогли заработать криптопиздюку максиму целых 0.00000001 евро, он вам отсыпал долю в виде 1000 маркус коинов"
modal_title = "Помощь от криптопиздюка"


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


# Глобальные переменные для времени отображения сообщений
purchase_time = None
purchase_message = ""
last_wallet_click_time = None


def show_shop(click_count, events):
    global purchase_time, purchase_message, mezpils_buy, last_wallet_click_time, adazu_buy

    wallet_image_path = resource_path("wallet.png")
    wallet_image = pygame.image.load(wallet_image_path)
    wallet_image = pygame.transform.scale(wallet_image, (70, 50))

    mezpils_image_path = resource_path("mezpils.png")
    mezpils_image = pygame.image.load(mezpils_image_path)
    mezpils_image = pygame.transform.scale(mezpils_image, (WIDTH // 3 - 50, HEIGHT // 3 - 10))

    adazu_image_path = resource_path("adazu.png")
    adazu_image = pygame.image.load(adazu_image_path)
    adazu_image = pygame.transform.scale(adazu_image, (WIDTH // 3 - 50, HEIGHT // 3 - 10))

    font = pygame.font.SysFont(None, 50)
    exit_button_font = pygame.font.SysFont(None, 36)
    item_font = pygame.font.SysFont(None, 36)
    description_font = pygame.font.SysFont(None, 25)
    shop_text = font.render("Магазин Маркуса", True, BLACK)

    screen.blit(shop_text, (WIDTH // 2 - shop_text.get_width() // 2, 20))

    # Отрисовка первого элемента
    screen.blit(mezpils_image, (WIDTH // 4 - 125, HEIGHT // 3 - 50))

    item_name = item_font.render("Mežpils", True, BLACK)
    item_description = description_font.render("0.5 промилле", True, BLACK)
    item_price = item_font.render("Цена: 100 МК", True, BLACK)

    screen.blit(item_name, (WIDTH // 4 - 90, HEIGHT // 3 - 50 + mezpils_image.get_height() + 10))
    screen.blit(item_description,
                (WIDTH // 4 - 100, HEIGHT // 3 - 20 + mezpils_image.get_height() + item_name.get_height() + 10))
    screen.blit(item_price, (WIDTH // 4 - 120,
                             HEIGHT // 3 - 1 + mezpils_image.get_height() + item_name.get_height() + item_description.get_height() + 20))

    # Отрисовка второго элемента рядом с первым элементом
    screen.blit(adazu_image, (WIDTH // 2 - 50, HEIGHT // 3 - 50))

    item2_name = item_font.render("Ādažu", True, BLACK)
    item2_description = description_font.render("Великие Чипсоиды", True, BLACK)
    item2_price = item_font.render("Цена: 250 МК", True, BLACK)

    screen.blit(item2_name, (WIDTH // 2 + 5, HEIGHT // 3 - 50 + adazu_image.get_height() + 10))
    screen.blit(item2_description,
                (WIDTH // 2 - 35, HEIGHT // 3 - 27 + adazu_image.get_height() + item2_name.get_height() + 10))
    screen.blit(item2_price, (WIDTH // 2 - 40,
                              HEIGHT // 3 - 1 + adazu_image.get_height() + item2_name.get_height() + item2_description.get_height() + 20))

    button_width = 150
    button_height = 40
    buy_button_rect = pygame.Rect(WIDTH // 4 - 110,
                                  HEIGHT // 3 - 1 + mezpils_image.get_height() + item_name.get_height() + item_description.get_height() + item_price.get_height() + 30,
                                  button_width, button_height)

    button2_width = 150
    button2_height = 40
    buy_button2_rect = pygame.Rect(WIDTH // 2 - 50,
                                   HEIGHT // 3 - 1 + adazu_image.get_height() + item2_name.get_height() + item2_description.get_height() + item2_price.get_height() + 30,
                                   button2_width, button2_height)

    buy_button_color = BUTTON_HOVER_COLOR if buy_button_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR
    buy_button2_color = BUTTON_HOVER_COLOR if buy_button2_rect.collidepoint(pygame.mouse.get_pos()) else BUTTON_COLOR

    if not mezpils_buy:
        pygame.draw.rect(screen, buy_button_color, buy_button_rect)
        buy_text = item_font.render("Купить", True, WHITE)
        screen.blit(buy_text, (
            buy_button_rect.centerx - buy_text.get_width() // 2, buy_button_rect.centery - buy_text.get_height() // 2))
    else:
        pygame.draw.rect(screen, buy_button_color, buy_button_rect)
        buy_text = item_font.render("Куплено", True, WHITE)
        screen.blit(buy_text, (
            buy_button_rect.centerx - buy_text.get_width() // 2, buy_button_rect.centery - buy_text.get_height() // 2))

    if not adazu_buy:
        pygame.draw.rect(screen, buy_button2_color, buy_button2_rect)
        buy2_text = item_font.render("Купить", True, WHITE)
        screen.blit(buy2_text, (
            buy_button2_rect.centerx - buy2_text.get_width() // 2,
            buy_button2_rect.centery - buy2_text.get_height() // 2))
    else:
        pygame.draw.rect(screen, buy_button2_color, buy_button2_rect)
        buy2_text = item_font.render("Куплено", True, WHITE)
        screen.blit(buy2_text, (
            buy_button2_rect.centerx - buy2_text.get_width() // 2,
            buy_button2_rect.centery - buy2_text.get_height() // 2))

    wallet_rect = pygame.Rect(10, 10, wallet_image.get_width(), wallet_image.get_height())
    screen.blit(wallet_image, wallet_rect.topleft)

    exit_button_rect = pygame.Rect(WIDTH - 100 - 20, HEIGHT - 40 - 20, 100, 40)
    pygame.draw.rect(screen, BUTTON_COLOR, exit_button_rect)
    exit_text = exit_button_font.render("Назад", True, WHITE)
    screen.blit(exit_text, (
        exit_button_rect.centerx - exit_text.get_width() // 2, exit_button_rect.centery - exit_text.get_height() // 2))

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if wallet_rect.collidepoint(mouse_pos):
                last_wallet_click_time = time.time()
            elif buy_button_rect.collidepoint(mouse_pos) and not mezpils_buy:
                if click_count >= 100:
                    click_count -= 100
                    mezpils_buy = True
                    save_click_count(click_count, bonus_claimed, mezpils_buy, adazu_buy)
                    if adazu_buy == True:
                        purchase_message = "Заебись! Теперь есть хрючево под чипсоиды! Вы купили Mežpils!"
                    else:
                        purchase_message = "Вы купили Mežpils!"
                    purchase_time = time.time()
                else:
                    purchase_message = "У вас недостаточно денег!"
                    purchase_time = time.time()
            elif buy_button2_rect.collidepoint(mouse_pos) and not adazu_buy:
                if click_count >= 250:
                    click_count -= 250
                    adazu_buy = True
                    save_click_count(click_count, bonus_claimed, mezpils_buy, adazu_buy)
                    if mezpils_buy == True:
                        purchase_message = "Заебись! Теперь есть закусон под пивас! Вы купили Ādažu!"
                    else:
                        purchase_message = "Вы купили Ādažu!"
                    purchase_time = time.time()
                else:
                    purchase_message = "У вас недостаточно денег!"
                    purchase_time = time.time()
            elif exit_button_rect.collidepoint(mouse_pos):
                return exit_button_rect, click_count

    if purchase_message and time.time() - purchase_time <= 5:
        message_text = font.render(purchase_message, True, WHITE)
        message_rect = message_text.get_rect(center=(WIDTH // 2, HEIGHT // 5))
        pygame.draw.rect(screen, (0, 0, 0), message_rect.inflate(20, 20))
        screen.blit(message_text, message_rect.topleft)

    if last_wallet_click_time and time.time() - last_wallet_click_time <= 5:
        counter_text = font.render(f"У тебя есть: {click_count} МК", True, WHITE)
        counter_rect = counter_text.get_rect(center=(WIDTH // 2, HEIGHT // 5))
        pygame.draw.rect(screen, (0, 0, 0), counter_rect.inflate(20, 20))
        screen.blit(counter_text, counter_rect.topleft)

    return exit_button_rect, click_count



screamer_images = ["skrimer.png", "sasha.png", "markus.png", "chinchin.png", "markuss2.png", "comacC919.png", "markusadazu.png" , "EC-MFE.png"]

running = True
rotated_screen = draw_rotated_surface(screen)
pygame.display.flip()
showing_modal = False
showing_screamer = False
showing_shop = False

while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    if showing_shop:
        events = pygame.event.get()
        exit_button_rect, click_count = show_shop(click_count, events)

        for event in events:
            if event.type == pygame.QUIT:
                save_click_count(click_count, bonus_claimed, mezpils_buy, adazu_buy)
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and exit_button_rect.collidepoint(mouse_pos):
                showing_shop = False
    else:
        events = pygame.event.get()
        pygame.draw.circle(screen, OUTLINE_COLOR, circle_center, outline_radius)
        pygame.draw.circle(screen, CIRCLE_COLOR, circle_center, circle_radius)
        screen.blit(markus_image, (circle_center[0] - circle_radius, circle_center[1] - circle_radius))

        screen.blit(empty_card_image, empty_card_rect)

        counter_text = button_font.render(f"Маркус коины: {click_count}", True, BUTTON_COLOR)
        screen.blit(counter_text, (10, 10))

        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if button_rect_1.collidepoint(mouse_pos) else BUTTON_COLOR,
                         button_rect_1)
        text_surface_1 = button_font.render(button_text_1, True, WHITE)
        text_rect_1 = text_surface_1.get_rect(center=button_rect_1.center)
        screen.blit(text_surface_1, text_rect_1)

        button_text_2_display = button_text_2 if not bonus_claimed else "Ты помог криптопиздюку максу"
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if button_rect_2.collidepoint(mouse_pos) else BUTTON_COLOR,
                         button_rect_2)
        text_surface_2 = button_font.render(button_text_2_display, True, WHITE)
        text_rect_2 = text_surface_2.get_rect(center=button_rect_2.center)
        screen.blit(text_surface_2, text_rect_2)

        for event in events:
            if event.type == pygame.QUIT:
                save_click_count(click_count, bonus_claimed, mezpils_buy, adazu_buy)
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if (mouse_pos[0] - circle_center[0]) ** 2 + (mouse_pos[1] - circle_center[1]) ** 2 < circle_radius ** 2:
                    if mezpils_buy and adazu_buy:
                        click_count += 5
                    elif mezpils_buy:
                        click_count += 2
                    elif adazu_buy:
                        click_count += 2

                    save_click_count(click_count, bonus_claimed, mezpils_buy, adazu_buy)
                elif button_rect_1.collidepoint(mouse_pos):
                    chosen_image_path = resource_path(random.choice(screamer_images))
                    screamer_image = pygame.image.load(chosen_image_path)
                    screamer_image = pygame.transform.scale(screamer_image, (WIDTH, HEIGHT))
                    showing_screamer = True
                elif button_rect_2.collidepoint(mouse_pos):
                    if not bonus_claimed:
                        webbrowser.open("https://app.getgrass.io/register?referralCode=2AmEBXJTXIEg-gh")
                        click_count += 1000
                        bonus_claimed = True
                        save_click_count(click_count, bonus_claimed, mezpils_buy)
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

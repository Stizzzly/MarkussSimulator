import pygame
import sys
import os
import webbrowser
import json
import platform
import time
import random


# =============================
# КЛАССЫ
# =============================

class GameState:
    """Хранит состояние игры: клики, бонусы, покупки"""
    def __init__(self):
        self.click_count = 0
        self.bonus_claimed = False
        self.mezpils_buy = False

    def save(self):
        save_path = self.get_save_path()
        folder_path = os.path.dirname(save_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        data = {
            "click_count": self.click_count,
            "bonus_claimed": self.bonus_claimed,
            "mezpils_buy": self.mezpils_buy
        }

        try:
            with open(save_path, "w") as file:
                json.dump(data, file)
            print(f"Данные сохранены: {data}")
        except IOError as e:
            print(f"Ошибка записи файла: {e}")

    def load(self):
        save_path = self.get_save_path()
        folder_path = os.path.dirname(save_path)

        if folder_path and not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if os.path.exists(save_path):
            try:
                with open(save_path, "r") as file:
                    data = json.load(file)
                    self.click_count = data.get("click_count", 0)
                    self.bonus_claimed = data.get("bonus_claimed", False)
                    self.mezpils_buy = data.get("mezpils_buy", False)
                    return
            except (json.JSONDecodeError, IOError):
                print("Ошибка чтения файла. Используются значения по умолчанию.")

        print("Файл не найден. Используются значения по умолчанию.")

    @staticmethod
    def detect_os():
        os_name = platform.system()
        if os_name == "Linux":
            return "Linux"
        elif os_name == "Windows":
            return "Windows"
        else:
            print("Операционная система не определена, сохранение невозможно, свяжитесь с разработчиком")
            return "Unknown"

    @staticmethod
    def get_save_path():
        os_type = GameState.detect_os()
        print(f"Операционная система: {os_type}")

        if os_type == "Linux":
            return os.path.expanduser("~/.MarkussSimulator/click_count.json")
        elif os_type == "Windows":
            user_name = os.getlogin()
            return f"C:\\Users\\{user_name}\\AppData\\Local\\STIZZLY\\MarkussSimulator\\click_count.json"
        else:
            raise Exception("Неизвестная операционная система. Сохранение невозможно.")


class ResourceManager:
    """Загружает и кэширует ресурсы: изображения, шрифты"""
    def __init__(self):
        self.images = {}
        self.fonts = {}

    def get_image(self, name, size=None):
        if name not in self.images:
            path = self.resource_path(name)
            image = pygame.image.load(path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            self.images[name] = image
        return self.images[name]

    def get_font(self, size):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont(None, size)
        return self.fonts[size]

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


class Button:
    """Универсальная кнопка с коллбэком при клике"""
    def __init__(self, rect, text, on_click, font_size=26, normal_color=(200, 0, 0), hover_color=(255, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.font = pygame.font.SysFont(None, font_size)
        self.normal_color = normal_color
        self.hover_color = hover_color

    def draw(self, screen, mouse_pos):
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.normal_color
        pygame.draw.rect(screen, color, self.rect)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()


class Shop:
    """Логика магазина"""
    def __init__(self, game_state, resource_manager):
        self.game_state = game_state
        self.rm = resource_manager
        self.purchase_time = None
        self.purchase_message = ""
        self.last_wallet_click_time = None
        self.showing = False

    def toggle(self):
        self.showing = not self.showing

    def update(self, events, screen, WIDTH, HEIGHT):
        if not self.showing:
            return

        # Загрузка ресурсов
        wallet_image = self.rm.get_image("wallet.png", (70, 50))
        mezpils_image = self.rm.get_image("mezpils.png", (WIDTH // 3 - 50, HEIGHT // 3 - 10))

        # Шрифты
        font = pygame.font.SysFont(None, 50)
        item_font = pygame.font.SysFont(None, 36)
        desc_font = pygame.font.SysFont(None, 25)
        exit_font = pygame.font.SysFont(None, 36)

        # Отрисовка
        shop_text = font.render("Магазин Маркуса", True, (0, 0, 0))
        screen.blit(shop_text, (WIDTH // 2 - shop_text.get_width() // 2, 20))
        screen.blit(mezpils_image, (WIDTH // 4 - 125, HEIGHT // 3 - 50))

        item_name = item_font.render("Mežpils", True, (0, 0, 0))
        item_desc = desc_font.render("0.5 промилле", True, (0, 0, 0))
        item_price = item_font.render("Цена: 100 МК", True, (0, 0, 0))

        x_offset = WIDTH // 4 - 90
        y_base = HEIGHT // 3 - 50 + mezpils_image.get_height() + 10
        screen.blit(item_name, (x_offset, y_base))
        screen.blit(item_desc, (x_offset - 10, y_base + item_name.get_height() + 10))
        screen.blit(item_price, (x_offset - 20, y_base + item_name.get_height() + item_desc.get_height() + 20))

        # Кнопка покупки
        button_rect = pygame.Rect(x_offset - 20, y_base + item_name.get_height() + item_desc.get_height() + item_price.get_height() + 30, 150, 40)
        button_color = (255, 0, 0) if button_rect.collidepoint(pygame.mouse.get_pos()) else (200, 0, 0)

        pygame.draw.rect(screen, button_color, button_rect)
        buy_text = "Куплено" if self.game_state.mezpils_buy else "Купить"
        buy_surf = item_font.render(buy_text, True, (255, 255, 255))
        screen.blit(buy_surf, (button_rect.centerx - buy_surf.get_width() // 2, button_rect.centery - buy_surf.get_height() // 2))

        # Кошелёк (показ баланса)
        wallet_rect = pygame.Rect(10, 10, 70, 50)
        screen.blit(wallet_image, wallet_rect.topleft)

        # Кнопка "Назад"
        exit_rect = pygame.Rect(WIDTH - 120, HEIGHT - 60, 100, 40)
        pygame.draw.rect(screen, (200, 0, 0), exit_rect)
        exit_text = exit_font.render("Назад", True, (255, 255, 255))
        screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width() // 2, exit_rect.centery - exit_text.get_height() // 2))

        # Обработка событий
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if wallet_rect.collidepoint(mouse_pos):
                    self.last_wallet_click_time = time.time()
                elif button_rect.collidepoint(mouse_pos) and not self.game_state.mezpils_buy:
                    if self.game_state.click_count >= 100:
                        self.game_state.click_count -= 100
                        self.game_state.mezpils_buy = True
                        self.game_state.save()
                        self.purchase_message = "Вы купили Mežpils!"
                        self.purchase_time = time.time()
                    else:
                        self.purchase_message = "У вас недостаточно денег!"
                        self.purchase_time = time.time()
                elif exit_rect.collidepoint(mouse_pos):
                    self.showing = False

        # Временные сообщения
        if self.purchase_message and time.time() - self.purchase_time <= 5:
            msg_surf = font.render(self.purchase_message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT // 5))
            pygame.draw.rect(screen, (0, 0, 0), msg_rect.inflate(20, 20))
            screen.blit(msg_surf, msg_rect.topleft)

        if self.last_wallet_click_time and time.time() - self.last_wallet_click_time <= 5:
            counter_text = font.render(f"У тебя есть: {self.game_state.click_count} МК", True, (255, 255, 255))
            counter_rect = counter_text.get_rect(center=(WIDTH // 2, HEIGHT // 5))
            pygame.draw.rect(screen, (0, 0, 0), counter_rect.inflate(20, 20))
            screen.blit(counter_text, counter_rect.topleft)


class Game:
    """Основной класс игры — управляет всем"""
    def __init__(self):
        pygame.init()

        # Определение размеров экрана
        os_type = GameState.detect_os()
        if os_type in ["Windows", "Linux"]:
            self.WIDTH, self.HEIGHT = 700, 500
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        else:
            self.WIDTH, self.HEIGHT = 640, 360
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)

        pygame.display.set_caption("Markuss Simulator")

        # Цвета
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BUTTON_COLOR = (200, 0, 0)
        self.BUTTON_HOVER_COLOR = (255, 0, 0)
        self.CIRCLE_COLOR = (255, 0, 0)
        self.OUTLINE_COLOR = (255, 0, 0)

        # Инициализация систем
        self.state = GameState()
        self.rm = ResourceManager()
        self.shop = Shop(self.state, self.rm)

        # Загрузка состояния
        self.state.load()

        # Позиции и параметры
        self.circle_center = (150, self.HEIGHT // 2)
        self.circle_radius = 75
        self.outline_radius = self.circle_radius + 15

        # Картинки
        markus_img = self.rm.get_image("markuss.png", (self.circle_radius * 2, self.circle_radius * 2))
        self.markus_image = self.create_circular_mask(markus_img, self.circle_radius)

        self.empty_card_image = self.rm.get_image("empty_cart.png", (70, 50))
        self.empty_card_rect = self.empty_card_image.get_rect(topright=(self.WIDTH - 10, 10))

        # Кнопки
        self.buttons = [
            Button(
                (self.WIDTH - 400, self.HEIGHT // 2 - 100, 300, 80),
                "дахуя бан накидал",
                self.on_screamer_click,
                26
            ),
            Button(
                (self.WIDTH - 400, self.HEIGHT // 2 + 20, 300, 80),
                "помогите криптопиздюку максиму",
                self.on_bonus_click,
                26
            )
        ]

        # Модальное окно
        self.showing_modal = False
        self.modal_text = "Вы помогли заработать криптопиздюку максиму целых 0.00000001 евро, он вам отсыпал долю в виде 1000 маркус коинов"
        self.modal_title = "Помощь от криптопиздюка"

        # Скример
        self.showing_screamer = False
        self.screamer_image = None
        self.screamer_images = ["skrimer.png", "sasha.png", "markus.png"]

    def create_circular_mask(self, image, radius):
        mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
        image.set_colorkey((0, 0, 0))
        image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return image

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + ' ' + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        return lines

    def show_modal(self, message, title):
        font = pygame.font.SysFont(None, 30)
        title_text = font.render(title, True, self.WHITE)
        message_lines = self.wrap_text(message, font, self.WIDTH // 2)

        modal_rect = pygame.Rect(self.WIDTH // 4, self.HEIGHT // 4, self.WIDTH // 2, self.HEIGHT // 2)
        button_rect = pygame.Rect(self.WIDTH // 2 - 75, self.HEIGHT // 2 + 100, 150, 40)

        pygame.draw.rect(self.screen, (0, 0, 0), modal_rect)
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, self.HEIGHT // 4 + 20))

        y_offset = self.HEIGHT // 4 + 60
        for line in message_lines:
            line_text = font.render(line, True, self.WHITE)
            self.screen.blit(line_text, (self.WIDTH // 2 - line_text.get_width() // 2, y_offset))
            y_offset += 40

        pygame.draw.rect(self.screen, self.BUTTON_COLOR, button_rect)
        close_text = font.render("Закрыть", True, self.WHITE)
        self.screen.blit(close_text, (
            button_rect.centerx - close_text.get_width() // 2,
            button_rect.centery - close_text.get_height() // 2
        ))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return True
        return False

    def on_screamer_click(self):
        chosen_image = random.choice(self.screamer_images)
        img = self.rm.get_image(chosen_image, (self.WIDTH, self.HEIGHT))
        self.screamer_image = img
        self.showing_screamer = True

    def on_bonus_click(self):
        if not self.state.bonus_claimed:
            webbrowser.open("https://app.getgrass.io/register?referralCode=2AmEBXJTXIEg-gh")
            self.state.click_count += 1000
            self.state.bonus_claimed = True
            self.state.save()
            self.showing_modal = True

    def run(self):
        clock = pygame.time.Clock()

        while True:
            events = pygame.event.get()
            mouse_pos = pygame.mouse.get_pos()

            for event in events:
                if event.type == pygame.QUIT:
                    self.state.save()
                    pygame.quit()
                    sys.exit()

            self.screen.fill(self.WHITE)

            if self.shop.showing:
                self.shop.update(events, self.screen, self.WIDTH, self.HEIGHT)
            else:
                # Основной экран
                pygame.draw.circle(self.screen, self.OUTLINE_COLOR, self.circle_center, self.outline_radius)
                pygame.draw.circle(self.screen, self.CIRCLE_COLOR, self.circle_center, self.circle_radius)
                self.screen.blit(self.markus_image, (
                    self.circle_center[0] - self.circle_radius,
                    self.circle_center[1] - self.circle_radius
                ))

                self.screen.blit(self.empty_card_image, self.empty_card_rect)

                # Счётчик
                counter_text = pygame.font.SysFont(None, 26).render(f"Маркус коины: {self.state.click_count}", True, self.BUTTON_COLOR)
                self.screen.blit(counter_text, (10, 10))

                # Кнопки
                for button in self.buttons:
                    button.draw(self.screen, mouse_pos)

                # Обработка кликов
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Клик по кругу
                        dx = mouse_pos[0] - self.circle_center[0]
                        dy = mouse_pos[1] - self.circle_center[1]
                        if dx*dx + dy*dy < self.circle_radius*self.circle_radius:
                            add = 2 if self.state.mezpils_buy else 1
                            self.state.click_count += add
                            self.state.save()

                        # Клик по карточке (магазин)
                        if self.empty_card_rect.collidepoint(mouse_pos):
                            self.shop.toggle()

                        # Клик по кнопкам
                        for button in self.buttons:
                            button.handle_event(event)

            # Отображение скримера
            if self.showing_screamer:
                self.screen.blit(self.screamer_image, (0, 0))
                pygame.display.update()
                pygame.time.wait(2000)
                self.showing_screamer = False
                continue  # Пропускаем обычный update, чтобы не мерцало

            # Отображение модального окна
            if self.showing_modal:
                if self.show_modal(self.modal_text, self.modal_title):
                    self.showing_modal = False

            pygame.display.update()
            clock.tick(60)  # 60 FPS для плавности


# =============================
# ЗАПУСК ИГРЫ
# =============================

if __name__ == "__main__":
    game = Game()
    game.run()

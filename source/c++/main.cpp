#define SDL_MAIN_USE_CALLBACKS 1
#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <SDL3_image/SDL_image.h>
#include <SDL3/SDL_ttf.h>
#include <nlohmann/json.hpp>
#include "Shop.h"
#include <string>
#include <vector>
#include <ctime>
#include <fstream>
#include <filesystem>

using json = nlohmann::json;
namespace fs = std::filesystem;

// Структура для Кнопки
struct Button {
    SDL_FRect rect;       // Позиция и размер
    std::string text;     // Текст на кнопке
    bool isHovered = false; // Наведена ли мышка
    SDL_Color colorNormal = {200, 0, 0, 255};   // Темно-красный
    SDL_Color colorHover = {255, 0, 0, 255};    // Ярко-красный (при наведении)
    SDL_Texture* textTexture = nullptr; // Текстура с текстом (кэшируем)
    int textW = 0, textH = 0;
};

class GameApp {
public:
    bool Init(const char* preferredDriver = nullptr) {
        std::srand(std::time(nullptr));
        if (SDL_Init(SDL_INIT_VIDEO) < 0) return false;
        if (TTF_Init() < 0) { // Инициализация шрифтов
             SDL_Log("TTF Init Error: %s", SDL_GetError());
             return false;
        }

        SDL_SetHint("SDL_RENDER_SCALE_QUALITY", "linear");

        if (!SDL_CreateWindowAndRenderer("Markuss Simulator 2", 800, 600, SDL_WINDOW_RESIZABLE, &window, &renderer)) return false;


        // --- ФИКС 2: Только 4 аргумента ---
        SDL_SetRenderLogicalPresentation(renderer, 800, 600,
                                         SDL_LOGICAL_PRESENTATION_LETTERBOX);
        // ----------------------------------
        // --- ЗАГРУЗКА РЕСУРСОВ ---

        if (!shop.Init(renderer, &score)) {
        }

        // 1. Картинка
        markusTexture = LoadAndMaskImage("images/markuss.png", radius);

        // 2. Шрифт (ОБЯЗАТЕЛЬНО скопируй arial.ttf или font.ttf в папку проекта)
        // Размер 26, как у тебя в Python
        font = TTF_OpenFont("font/font.ttf", 19);
        if (!font) {
            SDL_Log("НЕ НАЙДЕН ШРИФТ font.ttf! Текста не будет. %s", SDL_GetError());
        }

        // 3. Настройка кнопок (координаты из твоего Python кода)
        // Правая панель начинается с X=400. Центр правой панели = 600.
        // Кнопка шириной 300. Значит X = 600 - 150 = 450.

        // Кнопка 1: "дахуя бан накидал"
        btn1.rect = {450.0f, 200.0f, 300.0f, 80.0f};
        btn1.text = "дахуя бан накидал"; // Пока латиницей, чтобы точно работало (см. ниже про русский)
        CreateButtonTexture(btn1);

        // Кнопка 2: "помогите криптопиздюку максиму"
        btn2.rect = {450.0f, 320.0f, 300.0f, 80.0f};
        btn2.text = "помогите криптопиздюку максиму";
        CreateButtonTexture(btn2);

        // Список имен файлов (как у тебя в Python)
        std::vector<const char*> screamerFiles = {"images/skrimer.png",
            "images/sasha.png", "images/markus.png", "images/chinchin.png",
            "images/markuss2.png", "images/comacC919.png", "images/markusadazu.png"
            , "images/EC-MFE.png", "images/posuda.png" };

        texCart = IMG_LoadTexture(renderer, "images/empty_cart.png");
        if (!texCart) {
            SDL_GetError();
        } else {
            // Настраиваем позицию (справа сверху, отступ 10px)
            // 70x50 - размер из твоего Python кода
            // X = 800 (ширина экрана) - 70 (ширина иконки) - 10 (отступ) = 720
            cartRect = {720.0f, 10.0f, 70.0f, 50.0f};
        }

        for (const char* filename : screamerFiles) {
            SDL_Texture* tex = IMG_LoadTexture(renderer, filename);
            if (tex) {
                screamerTextures.push_back(tex);
            } else {
                SDL_GetError();
            }
        }
        LoadGame();
        return true;

    }

    void Render() {
        SetColor(30, 30, 30); SDL_RenderClear(renderer);

        // Панель магазина
        SetColor(45, 45, 45);
        SDL_FRect shopPanel = { 400.0f, 0.0f, 400.0f, 600.0f };
        SDL_RenderFillRect(renderer, &shopPanel);
        SetColor(100, 100, 100); SDL_RenderLine(renderer, 400.0f, 0.0f, 400.0f, 600.0f);

        // --- РИСУЕМ КНОПКИ ---
        DrawButton(btn1);
        DrawButton(btn2);

        // --- РИСУЕМ МАРКУССА ---
        float scale = isPressed ? 0.9f : 1.0f;
        float currentRadius = radius * scale;
        float currentOutline = outlineRadius * scale;

        // --- РИСУЕМ СЧЕТЧИК ---
        UpdateScoreTexture(); // Обновляем текстуру, если счет изменился

        if (scoreTexture) {
            // Рисуем в точке (10, 10)
            SDL_FRect dst = {10.0f, 10.0f, (float)scoreW, (float)scoreH};
            SDL_RenderTexture(renderer, scoreTexture, nullptr, &dst);
        }

        if (isPressed) SetColor(255, 100, 100); else SetColor(255, 0, 0);
        DrawFilledCircle(centerX, centerY, currentOutline);

        if (markusTexture) {
            SDL_FRect dst = {centerX - currentRadius, centerY - currentRadius, currentRadius*2, currentRadius*2};
            SDL_RenderTexture(renderer, markusTexture, nullptr, &dst);
        } else {
            SetColor(255, 50, 50); DrawFilledCircle(centerX, centerY, currentRadius);
        }

        if (showingScreamer) {
            Uint64 now = SDL_GetTicks();

            if (now < screamerEndTime) {
                // Рисуем на весь экран (nullptr, nullptr)
                SDL_RenderTexture(renderer, currentScreamer, nullptr, nullptr);
            } else {
                // Время вышло
                showingScreamer = false;
                currentScreamer = nullptr;
            }
        }

        if (texCart) {
            SDL_RenderTexture(renderer, texCart, nullptr, &cartRect);
        } else {
            // Если картинки нет - рисуем красный квадрат (заглушка)
            SetColor(200, 0, 0);
            SDL_RenderFillRect(renderer, &cartRect);
        }

        shop.Render();

        SDL_RenderPresent(renderer);
    }

    void UpdateScoreTexture() {
        if (!font) return;

        // Если счет не изменился с прошлого раза — выходим, не тратим ресурсы
        if (score == lastRenderedScore && scoreTexture != nullptr) return;

        lastRenderedScore = score;

        // Удаляем старую текстуру
        if (scoreTexture) {
            SDL_DestroyTexture(scoreTexture);
        }

        // Формируем строку (нужен #include <string>)
        // u8"" для русского, если шрифт поддерживает
        std::string text = "Маркус коины: " + std::to_string(score);

        SDL_Color redColor = {200, 0, 0, 255}; // Твой BUTTON_COLOR

        // Рендерим
        SDL_Surface* surf = TTF_RenderText_Blended(font, text.c_str(), 0, redColor);
        if (surf) {
            scoreTexture = SDL_CreateTextureFromSurface(renderer, surf);
            scoreW = surf->w;
            scoreH = surf->h;
            SDL_DestroySurface(surf);
        }
    }

    bool HandleEvent(SDL_Event* event) {
        if (event->type == SDL_EVENT_QUIT) return false;

        if (shop.HandleEvent(event)) {
            return true;
        }

        // --- ФИКС: Блокировка управления ---
        // Если скример сейчас на экране — игнорируем всё остальное
        if (showingScreamer) {
            // Сбрасываем нажатие, чтобы круг не "залип", если скример вылез во время клика
            isPressed = false;

            // Возвращаем true, чтобы SDL знал, что событие обработано,
            // но код ниже (клики по кнопкам) НЕ выполнялся.
            return true;
        }

        // Обработка движения мыши (для Hover эффекта)
        if (event->type == SDL_EVENT_MOUSE_MOTION) {
            float mx = event->motion.x;
            float my = event->motion.y;

            // Проверяем наведение на кнопки
            SDL_Point p = {(int)mx, (int)my}; // SDL_PointInRectFloat хочет SDL_Point
            btn1.isHovered = (mx >= btn1.rect.x && mx <= (btn1.rect.x + btn1.rect.w) &&
                              my >= btn1.rect.y && my <= (btn1.rect.y + btn1.rect.h));
            btn2.isHovered = (mx >= btn2.rect.x && mx <= (btn2.rect.x + btn2.rect.w) &&
                              my >= btn2.rect.y && my <= (btn2.rect.y + btn2.rect.h));
        }

        if (event->type == SDL_EVENT_MOUSE_BUTTON_DOWN) {
            float mx = event->button.x;
            float my = event->button.y;

            // 1. Сначала проверяем, не открыт ли магазин
            if (shop.HandleEvent(event)) return true;

            // 2. Проверка клика по КОРЗИНЕ
            if (mx >= cartRect.x && mx <= cartRect.x + cartRect.w &&
                my >= cartRect.y && my <= cartRect.y + cartRect.h)
            {
                shop.Toggle(); // Открыть/Закрыть магазин
                return true;
            }

            // Клик по Маркуссу
            if (IsPointInCircle(mx, my, outlineRadius)) {
                score++;
                isPressed = true;
                //SDL_Log("Score: %llu", score);
            }

            // Клик по кнопке 1
            if (btn1.isHovered) {
                if (!screamerTextures.empty()) {
                    // 1. Выбираем случайный индекс
                    // rand() % N дает число от 0 до N-1
                    int idx = std::rand() % screamerTextures.size();
                    currentScreamer = screamerTextures[idx];

                    // 2. Включаем режим
                    showingScreamer = true;

                    // 3. Засекаем время (Текущее + 2000мс)
                    screamerEndTime = SDL_GetTicks() + 2000;

                }
            }
             // Клик по кнопке 2
            if (btn2.isHovered) {
                if (isMaximHelped) {
                    SDL_Log("Максиму уже помогли, хватит с него.");
                } else {
                    score += 1000;
                    SDL_Log("Бонус получен! +1000");
                    const char* title = (const char*)u8"Помощь от криптопиздюка";
                    const char* message = (const char*)u8"Вы помогли заработать криптопиздюку Максиму целых 0.00000001 евро.\n\n"
                    u8"В благодарность он отсыпал вам долю:\n"
                    u8"1000 Маркус-коинов!";

                    // Аргументы: Флаг (иконка), Заголовок, Текст, Родительское окно
                    SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_INFORMATION, title, message, window);

                    // --- ФИКС: ЗАПОМИНАЕМ И МЕНЯЕМ КНОПКУ ---
                    isMaximHelped = true;

                    // Меняем текст кнопки
                    btn2.text = "Вы помогли Максиму"; // Или u8"Помощь оказана"
                    // Делаем кнопку серой (неактивной)
                    btn2.colorNormal = {100, 100, 100, 255}; // Серый
                    btn2.colorHover  = {100, 100, 100, 255}; // Тоже серый (нет реакции)

                    // Пересоздаем текстуру с новым текстом
                    CreateButtonTexture(btn2);
                }
            }
        }

        if (event->type == SDL_EVENT_MOUSE_BUTTON_UP) isPressed = false;

        return true;
    }

    void Cleanup() {
        SaveGame();
        if (scoreTexture) SDL_DestroyTexture(scoreTexture);
        // Чистим вектор скримеров
        for (auto* tex : screamerTextures) {
            SDL_DestroyTexture(tex);
        }
        screamerTextures.clear();
        if (btn1.textTexture) SDL_DestroyTexture(btn1.textTexture);
        if (btn2.textTexture) SDL_DestroyTexture(btn2.textTexture);
        if (font) TTF_CloseFont(font);
        TTF_Quit(); // Не забываем закрыть шрифты

        if (markusTexture) SDL_DestroyTexture(markusTexture);
        if (renderer) SDL_DestroyRenderer(renderer);
        if (window) SDL_DestroyWindow(window);
        if (texCart) SDL_DestroyTexture(texCart);
    }

private:
    Shop shop;
    SDL_Texture* scoreTexture = nullptr; // Текстура с текстом счета
    int scoreW = 0, scoreH = 0;          // Размеры текста
    uint64_t lastRenderedScore = -1;     // Чтобы не перерисовывать одно и то же

    SDL_Window* window = nullptr;
    SDL_Renderer* renderer = nullptr;
    SDL_Texture* markusTexture = nullptr;
    TTF_Font* font = nullptr; // Наш шрифт

    bool isMaximHelped = false; // По умолчанию: еще не помогли

    Button btn1;
    Button btn2;

    uint64_t score = 0;
    bool isPressed = false;

    SDL_Texture* texCart = nullptr; // Текстура корзины
    SDL_FRect cartRect;             // Позиция кнопки

    const float centerX = 200.0f; // Слева
    const float centerY = 300.0f;
    const float radius = 75.0f;
    const float outlineRadius = 90.0f;

     // Получение пути (AppData / .local)
    std::string GetSavePath() {
        char* basePath = SDL_GetPrefPath("StizzlyGames", "MarkussSimulator");
        if (!basePath) return "";
        std::string path = std::string(basePath) + "save.json";
        SDL_free(basePath);
        return path;
    }

    // СОХРАНЕНИЕ (Почти как в Python!)
    void SaveGame() {
        json j;

        // Просто присваиваем значения
        j["score"] = score;
        j["maxim_helped"] = isMaximHelped;
        j["mezpils_bought"] = shop.IsMezpilsBought(); // Достаем из магазина

        std::string path = GetSavePath();
        std::ofstream file(path);
        if (file.is_open()) {
            file << j.dump(4); // 4 пробела отступа (красивый вид)
            SDL_Log("Прогресс сохранен: %s", path.c_str());
        }
    }

    // ЗАГРУЗКА
    void LoadGame() {
        std::string path = GetSavePath();

        if (!fs::exists(path)) {
            SDL_Log("Нет сохранений. Новая игра.");
            return;
        }

        std::ifstream file(path);
        if (file.is_open()) {
            try {
                json j;
                file >> j; // Читаем файл в JSON

                // .value("key", default) — безопасно берет значение.
                // Если ключа нет (старый сейв), возьмет значение по умолчанию.
                score = j.value("score", (uint64_t)0);
                isMaximHelped = j.value("maxim_helped", false);

                bool bought = j.value("mezpils_bought", false);
                shop.SetMezpilsBought(bought);

                // Если Максиму помогли — обновляем кнопку визуально
                if (isMaximHelped) {
                    btn2.text = "Ты помог криптопиздюку максиму";
                    btn2.colorNormal = {100, 100, 100, 255};
                    btn2.colorHover  = {100, 100, 100, 255};
                    CreateButtonTexture(btn2);
                }


            } catch (const std::exception& e) {
                SDL_Log("Ошибка чтения JSON: %s", e.what());
            }

        }
    }

    // --- Хелпер для рисования кнопки ---
    void DrawButton(const Button& btn) {
        // 1. Выбираем цвет (Обычный или Hover)
        if (btn.isHovered) {
            SDL_SetRenderDrawColor(renderer, btn.colorHover.r, btn.colorHover.g, btn.colorHover.b, 255);
        } else {
            SDL_SetRenderDrawColor(renderer, btn.colorNormal.r, btn.colorNormal.g, btn.colorNormal.b, 255);
        }

        // 2. Рисуем прямоугольник кнопки
        SDL_RenderFillRect(renderer, &btn.rect);

        // 3. Рисуем текст по центру кнопки
        if (btn.textTexture) {
            SDL_FRect textRect;
            textRect.w = (float)btn.textW;
            textRect.h = (float)btn.textH;
            // Центрирование: X + (W_btn - W_txt)/2
            textRect.x = btn.rect.x + (btn.rect.w - btn.textW) / 2.0f;
            textRect.y = btn.rect.y + (btn.rect.h - btn.textH) / 2.0f;

            SDL_RenderTexture(renderer, btn.textTexture, nullptr, &textRect);
        }
    }

    // Создаем текстуру текста один раз (чтобы не тормозило)
    void CreateButtonTexture(Button& btn) {
        if (!font) return;

        // Белый цвет текста
        SDL_Color white = {255, 255, 255, 255};

        // Рендерим текст в Surface (Blended - сглаженный)
        // Важно: C++ может криво читать кириллицу. Используй u8"" для UTF-8 строк
        // Или пока пиши на английском, чтобы проверить.
        SDL_Surface* surf = TTF_RenderText_Blended(font, btn.text.c_str(), 0, white);

        if (surf) {
            btn.textTexture = SDL_CreateTextureFromSurface(renderer, surf);
            btn.textW = surf->w;
            btn.textH = surf->h;
            SDL_DestroySurface(surf);
        }
    }

    // ... Твои старые функции (LoadAndMaskImage, IsPointInCircle, SetColor, DrawFilledCircle) ...
    // Скопируй их сюда из прошлого кода
    SDL_Texture* LoadAndMaskImage(const char* path, float r) {
        SDL_Surface* original = IMG_Load(path);
        if (!original) return nullptr;
        int size = (int)(r * 2);
        SDL_Surface* squareSurface = SDL_CreateSurface(size, size, SDL_PIXELFORMAT_RGBA32);
        if (SDL_BlitSurfaceScaled(original, nullptr, squareSurface, nullptr, SDL_SCALEMODE_LINEAR) < 0) {}
        SDL_DestroySurface(original);
        int w = squareSurface->w; int h = squareSurface->h;
        float cx = w / 2.0f; float cy = h / 2.0f; float r_sq = r * r;
        Uint32* pixels = (Uint32*)squareSurface->pixels;
        for (int i = 0; i < w * h; i++) {
            int x = i % w; int y = i / w;
            float dx = x - cx; float dy = y - cy;
            if ((dx*dx + dy*dy) > r_sq) pixels[i] = 0x00000000;
        }
        SDL_Texture* tex = SDL_CreateTextureFromSurface(renderer, squareSurface);
        SDL_DestroySurface(squareSurface);
        SDL_SetTextureBlendMode(tex, SDL_BLENDMODE_BLEND);
        return tex;
    }

    bool IsPointInCircle(float mx, float my, float r) {
        float dx = mx - centerX; float dy = my - centerY;
        return (dx * dx + dy * dy) <= (r * r);
    }

    void SetColor(Uint8 r, Uint8 g, Uint8 b, Uint8 a = 255) {
        SDL_SetRenderDrawColor(renderer, r, g, b, a);
    }

    void DrawFilledCircle(float cx, float cy, float r) {
        float x = r; float y = 0; float err = 0;
        while (x >= y) {
            SDL_RenderLine(renderer, cx - x, cy - y, cx + x, cy - y);
            SDL_RenderLine(renderer, cx - x, cy + y, cx + x, cy + y);
            SDL_RenderLine(renderer, cx - y, cy - x, cx + y, cy - x);
            SDL_RenderLine(renderer, cx - y, cy + x, cx + y, cy + x);
            if (err <= 0) { y += 1; err += 2 * y + 1; }
            if (err > 0) { x -= 1; err -= 2 * x + 1; }
        }
    }
    // --- СКРИМЕРЫ ---
    std::vector<SDL_Texture*> screamerTextures; // Список загруженных картинок
    bool showingScreamer = false;   // Показываем ли сейчас?
    Uint64 screamerEndTime = 0;     // Когда выключать
    SDL_Texture* currentScreamer = nullptr; // Какую именно картинку показывать
};

// Callbacks... (без изменений)
SDL_AppResult SDL_AppInit(void** appstate, int argc, char* argv[]) {
    auto* app = new GameApp(); *appstate = app;
    if (!app->Init()) { delete app; return SDL_APP_FAILURE; }
    return SDL_APP_CONTINUE;
}
SDL_AppResult SDL_AppEvent(void* appstate, SDL_Event* event) {
    auto* app = static_cast<GameApp*>(appstate);
    if (!app->HandleEvent(event)) return SDL_APP_SUCCESS;
    return SDL_APP_CONTINUE;
}
SDL_AppResult SDL_AppIterate(void* appstate) {
    static_cast<GameApp*>(appstate)->Render();
    return SDL_APP_CONTINUE;
}
void SDL_AppQuit(void* appstate, SDL_AppResult result) {
    if (appstate) { auto* app = static_cast<GameApp*>(appstate); app->Cleanup(); delete app; }
}
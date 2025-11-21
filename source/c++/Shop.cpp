#include "Shop.h"
#include <filesystem>

bool Shop::Init(SDL_Renderer* r, uint64_t* sPtr) {
    renderer = r;
    scorePtr = sPtr;

    // 3. Пытаемся загрузить wallet.png
    std::string walletPath = "images/wallet.png";

    // Проверяем физическое наличие файла
    if (std::filesystem::exists(walletPath)) {
    } else {
    }

    // Пытаемся загрузить текстуру
    texWallet = IMG_LoadTexture(renderer, walletPath.c_str());
    if (!texWallet) {
        SDL_GetError();
    } else {
    }

    // 4. Пытаемся загрузить mezpils.png
    std::string mezpilsPath = "images/mezpils.png";
    if (!std::filesystem::exists(mezpilsPath)) {
    }

    texMezpils = IMG_LoadTexture(renderer, mezpilsPath.c_str());
    if (!texMezpils) {
        SDL_GetError();
    } else {

    }

    // 5. Шрифты
    fontTitle = TTF_OpenFont("font/font.ttf", 50);
    fontUI = TTF_OpenFont("font/font.ttf", 36);
    if (!fontTitle || !fontUI) {
        SDL_Log("ОШИБКА ШРИФТОВ: %s", SDL_GetError());
        // Не выходим false, чтобы хотя бы квадраты рисовались
    }
    return true;
}

void Shop::Render() {
    if (!isShowing) return;

    // 1. Рисуем фон магазина (Светло-бежевый, чтобы отличался)
    SDL_SetRenderDrawColor(renderer, 240, 240, 220, 255);
    SDL_FRect fullScreen = {0, 0, 800, 600}; // Весь экран
    SDL_RenderFillRect(renderer, &fullScreen);

    // 2. Заголовок
    SDL_Color black = {0, 0, 0, 255};
    DrawText(fontTitle, "Магазин Наркуса", 250, 20, black); // Центрируй примерно

    // 3. Картинка Mezpils
    if (texMezpils) {
        SDL_FRect dest = {100, 150, 200, 300}; // Примерные координаты
        SDL_RenderTexture(renderer, texMezpils, nullptr, &dest);
    }

    // 4. Описание товара
    float xText = 350;
    float yText = 150;
    DrawText(fontUI, "Mezpils", xText, yText, black);
    DrawText(fontUI, "0.5 промилле", xText, yText + 40, black);
    DrawText(fontUI, "Цена: 100 MK", xText, yText + 80, black);

    // 5. Кнопка Купить
    SDL_FRect btnRect = {xText, yText + 140, 150, 50};
    
    // Цвет кнопки (Зеленая если куплено, Красная если нет)
    if (isMezpilsBought) SDL_SetRenderDrawColor(renderer, 0, 200, 0, 255);
    else SDL_SetRenderDrawColor(renderer, 200, 0, 0, 255);
    
    SDL_RenderFillRect(renderer, &btnRect);

    // Текст на кнопке
    std::string btnLabel = isMezpilsBought ? "Куплено" : "Купить";
    SDL_Color white = {255, 255, 255, 255};
    DrawText(fontUI, btnLabel, btnRect.x + 20, btnRect.y + 5, white);

    // 6. Кошелек (слева сверху)
    if (texWallet) {
        SDL_FRect walletRect = {10, 10, 70, 50};
        SDL_RenderTexture(renderer, texWallet, nullptr, &walletRect);
    }

    // 7. Кнопка Выход (Назад)
    SDL_FRect exitRect = {680, 540, 100, 40};
    SDL_SetRenderDrawColor(renderer, 100, 0, 0, 255);
    SDL_RenderFillRect(renderer, &exitRect);
    DrawText(fontUI, "Назад", exitRect.x + 10, exitRect.y + 2, white);

    // 8. Всплывающее сообщение
    RenderMessage();
}

bool Shop::HandleEvent(SDL_Event* event) {
    if (!isShowing) return false; // Если магазин закрыт, события не трогаем

    if (event->type == SDL_EVENT_MOUSE_BUTTON_DOWN && event->button.button == SDL_BUTTON_LEFT) {
        float mx = event->button.x;
        float my = event->button.y;

        // 1. Кнопка КУПИТЬ (Координаты должны совпадать с Render!)
        // Лучше вынести rect в поля класса, но пока хардкод для примера
        SDL_FRect btnRect = {350, 290, 150, 50}; 
        
        if (mx >= btnRect.x && mx <= btnRect.x + btnRect.w &&
            my >= btnRect.y && my <= btnRect.y + btnRect.h) 
        {
            // Получаем окно для привязки диалога
            SDL_Window* parentWindow = SDL_GetRenderWindow(renderer);

            if (isMezpilsBought) {
                // УЖЕ КУПЛЕНО
                const char* title = (const char*)u8"Магазин";
                const char* msg = (const char*)u8"Вы уже купили это пиво!\nХватит напиваться.";

                // Желтый треугольник (Warning)
                SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_WARNING, title, msg, parentWindow);
            }
            else {
                // ПРОВЕРКА ДЕНЕГ
                if (*scorePtr >= 100) {
                    // ПОКУПКА УСПЕШНА
                    *scorePtr -= 100; // Снимаем деньги
                    isMezpilsBought = true;

                    const char* title = (const char*)u8"Успешная покупка";
                    const char* msg = (const char*)u8"Вы купили Mežpils!\n\n"
                                      u8"С вашего счета списано 100 MK.\n"
                                      u8"Теперь Ларгус бухает!.";

                    // Синий значок (Information)
                    SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_INFORMATION, title, msg, parentWindow);
                } else {
                    // НЕТ ДЕНЕГ
                    const char* title = (const char*)u8"Ошибка";
                    const char* msg = (const char*)u8"Недостаточно средств!\n\n"
                                      u8"Это элитное пиво стоит 100 MK,\n"
                                      u8"а у вас не хватает.";

                    // Красный крестик (Error)
                    SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_ERROR, title, msg, parentWindow);
                }
            }
            return true; // Клик обработан
        }

        // 2. Кнопка КОШЕЛЕК (координаты 10, 10, 70, 50)
        SDL_FRect walletRect = {10, 10, 70, 50};

        if (mx >= walletRect.x && mx <= walletRect.x + walletRect.w &&
            my <= walletRect.y + walletRect.h)
        {
            // 1. Получаем родительское окно
            SDL_Window* parentWindow = SDL_GetRenderWindow(renderer);

            // 2. Формируем сообщение (Текст + Число + Текст)
            // std::string отлично "глотает" u8 строки, если их привести к char*
            std::string msg = std::string((const char*)u8"Финансовый отчет:\n\n") +
                              std::string((const char*)u8"На вашем счету сейчас: ") +
                              std::to_string(*scorePtr) + // Вставляем число
                              std::string((const char*)u8" MK\n\n") +
                              std::string((const char*)u8"Ни в чем себе не отказывайте!");

            // 3. Заголовок
            const char* title = (const char*)u8"Кошелёк Маркусса";

            // 4. Вызываем окно
            SDL_ShowSimpleMessageBox(SDL_MESSAGEBOX_INFORMATION, title, msg.c_str(), parentWindow);

            return true;
        }

        // 3. Кнопка НАЗАД
        SDL_FRect exitRect = {680, 540, 100, 40};
        if (mx >= exitRect.x && mx <= exitRect.x + exitRect.w &&
            my >= exitRect.y && my <= exitRect.y + exitRect.h) 
        {
            Toggle(); // Закрыть
            return true;
        }
        
        // Важно: Если магазин открыт, мы "съедаем" все клики, чтобы сквозь него не кликался Маркусс
        return true;
    }
    
    // Блокируем остальные события мыши, пока магазин открыт
    if (event->type == SDL_EVENT_MOUSE_MOTION) return true;

    return false;
}

void Shop::ShowMessage(const std::string& text, int durationMs) {
    currentMsg = text;
    msgEndTime = SDL_GetTicks() + durationMs;
}

void Shop::RenderMessage() {
    if (SDL_GetTicks() < msgEndTime && !currentMsg.empty()) {
        // Рисуем черную плашку по центру
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 200);
        SDL_FRect msgBg = {200, 50, 400, 60};
        SDL_RenderFillRect(renderer, &msgBg);

        // Рисуем текст
        SDL_Color white = {255, 255, 255, 255};
        DrawText(fontUI, currentMsg, 220, 60, white);
    }
}

void Shop::DrawText(TTF_Font* font, const std::string& text, float x, float y, SDL_Color color) {
    if (!font) return;
    SDL_Surface* surf = TTF_RenderText_Blended(font, text.c_str(), 0, color);
    if (surf) {
        SDL_Texture* tex = SDL_CreateTextureFromSurface(renderer, surf);
        SDL_FRect dst = {x, y, (float)surf->w, (float)surf->h};
        SDL_RenderTexture(renderer, tex, nullptr, &dst);
        SDL_DestroyTexture(tex);
        SDL_DestroySurface(surf);
    }
}

void Shop::Cleanup() {
    if (texWallet) SDL_DestroyTexture(texWallet);
    if (texMezpils) SDL_DestroyTexture(texMezpils);
    if (fontTitle) TTF_CloseFont(fontTitle);
    if (fontUI) TTF_CloseFont(fontUI);
}
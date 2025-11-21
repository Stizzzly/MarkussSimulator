#ifndef MARKUSSSIMULATOR2_SHOP_H
#define MARKUSSSIMULATOR2_SHOP_H

#pragma once
#include <SDL3/SDL.h>
#include <SDL3_image/SDL_image.h>
#include <SDL3/SDL_ttf.h>
#include <string>
#include <iostream>

class Shop {
public:
    // Инициализация: передаем рендерер и УКАЗАТЕЛЬ на счет
    bool Init(SDL_Renderer* renderer, uint64_t* scorePtr);

    // Отрисовка
    void Render();

    // Обработка кликов
    bool HandleEvent(SDL_Event* event);

    // Открыть/Закрыть
    void Toggle() { isShowing = !isShowing; }
    bool IsVisible() const { return isShowing; }

    // Очистка памяти
    void Cleanup();

    bool IsMezpilsBought() const { return isMezpilsBought; }      // Геттер (С большой буквы I)
    void SetMezpilsBought(bool val) { isMezpilsBought = val; }    // Сеттер (С большой буквы S)

private:
    SDL_Renderer* renderer = nullptr;
    uint64_t* scorePtr = nullptr; // Ссылка на деньги в GameApp

    // Состояние
    bool isShowing = false;
    bool isMezpilsBought = false;

    // Ресурсы
    SDL_Texture* texWallet = nullptr;
    SDL_Texture* texMezpils = nullptr;
    TTF_Font* fontTitle = nullptr; // Крупный (50)
    TTF_Font* fontUI = nullptr;    // Мелкий (36)

    // Система сообщений (Toast)
    std::string currentMsg;
    Uint64 msgEndTime = 0;

    // Хелперы
    void ShowMessage(const std::string& text, int durationMs = 5000);
    void DrawText(TTF_Font* font, const std::string& text, float x, float y, SDL_Color color);
    void RenderMessage(); // Рисует всплывающее сообщение
};

#endif //MARKUSSSIMULATOR2_SHOP_H
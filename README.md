### homework_bot
# Telegram bot отслеживание статуса код-ревю Яндекс.Практикум.
Простой бот работающий с API Яндекс.Практикум. Функции отображение статуса домашней работы.

Достаточно запустить бота, прописать токены. Каждые 10 минут бот проверяет API Яндекс.Практикум. И присылает в телеграм статус. Если работа проверена вы получите сообщение о статусе вашего код ревью.

# Запуск бота
- Установите и активируйте виртуальное окружение:  
``` python -m venv venv ```
``` source venv/Scripts/activate ``` 
- Установите зависимости из файла requirements.txt:   
``` pip install -r requirements.txt ```
- Создаем .env в папке проекта:
```
PRACTICUM_ID - токен полученный с api Я.П.
BOT_ID - токен бота
CHAT_ID - id вашего телеграмма
```
- Запускаем бота
``` python homework.py ```

Автор : Вячеслав Костырка

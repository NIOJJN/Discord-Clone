# Discord Clone

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![Channels](https://img.shields.io/badge/Channels-4.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Полнофункциональный клон Discord с чатом в реальном времени, серверами, каналами, личными сообщениями и системой друзей.

## 📸 Скриншоты

*Скриншоты будут добавлены позже*

## ✨ Возможности

- 🔐 **Авторизация и регистрация** пользователей
- 💬 **Чат в реальном времени** через WebSocket
- 🏠 **Серверы** с категориями и каналами (текстовые/голосовые)
- 👥 **Система друзей** (запросы, принятие, отклонение)
- 📝 **Личные сообщения** между пользователями
- 👑 **Роли на сервере** (владелец, админ, модератор, участник)
- 🔗 **Приглашения на сервер** по коду
- 📌 **Закрепление сообщений**
- 🔍 **Поиск сообщений** в канале
- ✏️ **Редактирование и удаление** сообщений
- 🔔 **Уведомления** при упоминаниях
- 👤 **Профили пользователей** с аватарами и статусами
- 🎨 **Тёмная тема** в стиле Discord
- 📱 **Адаптивный дизайн**

## 🛠 Технологии

| Технология | Назначение |
|------------|------------|
| **Django 4.2** | Backend фреймворк |
| **Django Channels** | WebSocket для real-time чата |
| **Daphne** | ASGI сервер |
| **Redis** | Бэкенд для Channels |
| **WhiteNoise** | Раздача статических файлов |
| **Bootstrap 5** | CSS фреймворк |
| **Font Awesome** | Иконки |
| **SQLite** | База данных |

## 📥 Установка

### Предварительные требования

- Python 3.9 или выше
- Redis Server
- Git

### 1. Клонирование репозитория

git clone https://github.com/NIOJJN/discord-clone.git
cd discord-clone

2. Создание виртуального окружения
Windows:


python -m venv venv
venv\Scripts\activate
Linux/macOS:

python3 -m venv venv
source venv/bin/activate
3. Установка зависимостей

pip install -r requirements.txt
4. Запуск Redis
git clone https://github.com/NIOJJN/discord-clone.git
cd discord-clone

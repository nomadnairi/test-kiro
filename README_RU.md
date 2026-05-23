# 🔍 CyberIntel AI Platform

> **Профессиональная AI-платформа для кибер-разведки** с OSINT, анализом угроз, графовой аналитикой и автономной разведкой.

[🇬🇧 English](README.md) | 🇷🇺 Русский

## ✨ Что было создано

### 🎉 GitHub-Ready Setup - Полная настройка для публикации!

Ваш проект теперь полностью готов к публикации на GitHub с профессиональной настройкой:

#### 📦 Скрипты автоматической установки (3)
- `scripts/install.sh` - для Linux/Mac
- `scripts/install.ps1` - для Windows PowerShell  
- `scripts/install.bat` - для Windows CMD

**Пользователи смогут установить всё одной командой!**

#### 📚 Документация (10 файлов)
- `README.md` - Главная документация с badges
- `START_HERE.md` - Полное руководство для начинающих
- `CONTRIBUTING.md` - Руководство по участию в проекте
- `COMMANDS.md` - Справочник команд
- `GITHUB_SETUP.md` - Пошаговая настройка GitHub
- `PUBLISH_CHECKLIST.md` - Чеклист перед публикацией
- `RELEASE_NOTES.md` - Описание версии 1.0.0
- `SECURITY.md` - Политика безопасности
- `LICENSE` - MIT лицензия
- `GITHUB_READY_SUMMARY.md` - Полная сводка

#### 🤖 Конфигурация GitHub (6 файлов)
- `.github/workflows/pages.yml` - Автоматическое развертывание документации
- `.github/workflows/setup.yml` - CI/CD pipeline
- `.github/ISSUE_TEMPLATE/` - Шаблоны для issues (3 шаблона)
- `.github/PULL_REQUEST_TEMPLATE.md` - Шаблон для PR

#### 🔧 Файлы конфигурации (6 файлов)
- `.gitattributes` - Настройки Git
- `.editorconfig` - Единообразное форматирование
- `.prettierrc` - Форматирование кода
- `.prettierignore` - Исключения для Prettier
- `.npmrc` - Настройки npm
- `package.json` - Улучшенный с метаданными

## 🚀 Быстрый старт

### Для пользователей (после клонирования)

**Linux/Mac:**
```bash
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform
chmod +x scripts/install.sh
./scripts/install.sh
```

**Windows PowerShell:**
```powershell
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform
.\scripts\install.ps1
```

**Windows CMD:**
```cmd
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform
scripts\install.bat
```

Скрипт автоматически:
- ✅ Проверит все зависимости (Node.js, Python, Docker)
- ✅ Установит все npm пакеты
- ✅ Установит все Python зависимости
- ✅ Соберет shared библиотеки
- ✅ Создаст файл `.env`
- ✅ Скачает Docker образы

### Настройка и запуск

```bash
# 1. Добавьте API ключи в .env
nano .env

# 2. Запустите инфраструктуру
docker-compose up -d

# 3. Запустите сервисы разработки
npm run dev

# 4. Откройте в браузере
# Frontend: http://localhost:3000
# API Gateway: http://localhost:4000
# Neo4j Browser: http://localhost:7474
```

## 📋 Следующие шаги для публикации

### 1. Обновите личную информацию

Замените `YOUR_USERNAME` в файлах:
- [ ] `README.md` - все GitHub URL и badges
- [ ] `SECURITY.md` - контактный email для безопасности
- [ ] `GITHUB_SETUP.md` - примеры URL
- [ ] `package.json` - URL репозитория

### 2. Протестируйте установку

```bash
# Создайте тестовую директорию
mkdir test-install
cd test-install

# Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/cyberintel-platform.git
cd cyberintel-platform

# Запустите установку
./scripts/install.sh

# Проверьте
docker-compose up -d
npm run dev
```

### 3. Опубликуйте на GitHub

Следуйте детальному руководству в `PUBLISH_CHECKLIST.md`:

1. **Создайте репозиторий** на GitHub
2. **Загрузите код**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: CyberIntel Platform v1.0.0"
   git remote add origin https://github.com/YOUR_USERNAME/cyberintel-platform.git
   git branch -M main
   git push -u origin main
   ```
3. **Включите GitHub Pages**:
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main`, Folder: `/docs`
4. **Включите GitHub Actions**:
   - Actions → Enable workflows
5. **Настройте репозиторий**:
   - Добавьте topics: `osint`, `cybersecurity`, `threat-intelligence`, `ai`
   - Включите Issues и Discussions
6. **Создайте первый релиз**:
   - Releases → Create a new release
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - Initial Release`

## 🌟 Ключевые возможности

### 🤖 AI-разведка
- **9 специализированных AI-агентов**: Разведка, DNS, анализ угроз, IOC, граф, корреляция
- **Автономная разведка**: AI планирует и выполняет OSINT-задачи
- **Чат с данными**: Задавайте вопросы на естественном языке

### 🔍 OSINT
- **20+ интеграций**: Amass, Subfinder, Nuclei, Sherlock, TruffleHog
- **Threat Intelligence**: VirusTotal, Shodan, Censys, SecurityTrails
- **Breach Intelligence**: HaveIBeenPwned, DeHashed

### 🕸️ Графовая аналитика
- **Neo4j**: Продвинутая графовая база данных
- **Связи сущностей**: Автоматическая корреляция доменов, IP, email
- **Обнаружение цепочек атак**: Выявление многоэтапных атак

### 📊 Визуализация
- **Интерактивный граф**: Визуализация связей
- **AI-отчеты**: Автоматическая генерация PDF/HTML отчетов
- **Дашборд**: Реал-тайм лента разведданных

## 📚 Документация

| Файл | Описание |
|------|----------|
| `START_HERE.md` | **Начните отсюда!** Полное руководство |
| `COMMANDS.md` | Справочник команд |
| `GITHUB_SETUP.md` | Настройка GitHub |
| `PUBLISH_CHECKLIST.md` | Чеклист перед публикацией |
| `CONTRIBUTING.md` | Как участвовать в проекте |
| `SECURITY.md` | Политика безопасности |
| `docs/index.html` | Веб-документация |

## 🛠️ Технологии

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: Node.js 20 + Fastify + TypeScript
- **AI**: Anthropic, OpenAI, Groq, Ollama
- **Базы данных**: PostgreSQL, Neo4j, Redis, Elasticsearch
- **Инфраструктура**: Docker + Docker Compose

## 📊 Статистика проекта

- **Микросервисов**: 11
- **AI-агентов**: 9
- **OSINT интеграций**: 20+
- **Баз данных**: 4
- **AI провайдеров**: 6
- **Создано файлов**: 25+

## 🔗 Полезные команды

```bash
# Разработка
npm run dev                 # Запустить все сервисы
npm run docker:up           # Запустить инфраструктуру
npm run build               # Собрать проект
npm test                    # Запустить тесты

# Качество кода
npm run format              # Форматировать код
npm run lint                # Проверить код
npm run typecheck           # Проверить типы
npm run check               # Все проверки

# База данных
npm run migrate             # Миграции
npm run seed                # Заполнить тестовыми данными
npm run db:reset            # Сбросить БД
```

## 🤝 Участие в проекте

Мы приветствуем вклад сообщества! См. [CONTRIBUTING.md](CONTRIBUTING.md)

### Области для участия
- 🐛 Исправление багов
- ✨ Новые функции
- 📝 Улучшение документации
- 🔧 Новые OSINT интеграции
- 🤖 Новые AI-агенты

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 🙏 Благодарности

Спасибо сообществу OSINT за потрясающие инструменты и всем участникам проекта!

## 💬 Поддержка

- **Документация**: Проверьте папку `docs/`
- **Issues**: GitHub Issues (после публикации)
- **Discussions**: GitHub Discussions (после публикации)

---

<div align="center">

**Создано с ❤️ сообществом кибербезопасности**

⭐ **Поставьте звезду**, если проект полезен!

[Сообщить о баге](https://github.com/YOUR_USERNAME/cyberintel-platform/issues) • [Предложить функцию](https://github.com/YOUR_USERNAME/cyberintel-platform/issues) • [Участвовать](CONTRIBUTING.md)

</div>

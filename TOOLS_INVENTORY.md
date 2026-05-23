# 🔧 OSINT Tools Inventory

Полный список всех интегрированных OSINT инструментов в CyberIntel Platform.

## 📊 Общая статистика

- **Всего инструментов**: 33
- **Категорий**: 5
- **API интеграций**: 11
- **CLI инструментов**: 22

---

## 🔍 Reconnaissance Tools (16)

### Subdomain Enumeration
1. **Amass** ✅
   - Файл: `integrations/src/tools/recon/amass.ts`
   - Описание: Продвинутое перечисление поддоменов
   - Команда: `amass enum -d domain.com`

2. **Subfinder** ✅
   - Файл: `integrations/src/tools/recon/subfinder.ts`
   - Описание: Быстрое обнаружение поддоменов
   - Команда: `subfinder -d domain.com`

3. **Assetfinder** ✅
   - Файл: `integrations/src/tools/recon/assetfinder.ts`
   - Описание: Поиск доменов и поддоменов
   - Команда: `assetfinder domain.com`

### Port Scanning
4. **Naabu** ✅
   - Файл: `integrations/src/tools/recon/naabu.ts`
   - Описание: Быстрое сканирование портов
   - Команда: `naabu -host target.com`

5. **Masscan** ✅
   - Файл: `integrations/src/tools/recon/masscan.ts`
   - Описание: Массовое сканирование портов
   - Команда: `masscan -p1-65535 target.com`

### Web Analysis
6. **Httpx** ✅
   - Файл: `integrations/src/tools/recon/httpx.ts`
   - Описание: HTTP probe и анализ
   - Команда: `httpx -u target.com`

7. **WhatWeb** ✅
   - Файл: `integrations/src/tools/recon/whatweb.ts`
   - Описание: Определение веб-технологий
   - Команда: `whatweb target.com`

8. **Wappalyzer** ✅
   - Файл: `integrations/src/tools/recon/wappalyzer.ts`
   - Описание: Определение технологий сайта
   - Команда: `wappalyzer target.com`

9. **Aquatone** ✅
   - Файл: `integrations/src/tools/recon/aquatone.ts`
   - Описание: Визуальный анализ веб-приложений
   - Команда: `cat hosts.txt | aquatone`

### Vulnerability Scanning
10. **Nuclei** ✅
    - Файл: `integrations/src/tools/recon/nuclei.ts`
    - Описание: Сканирование уязвимостей по шаблонам
    - Команда: `nuclei -u target.com`

### DNS Analysis
11. **Dnsx** ✅
    - Файл: `integrations/src/tools/recon/dnsx.ts`
    - Описание: Быстрый DNS toolkit
    - Команда: `dnsx -d target.com`

### URL Discovery
12. **Katana** ✅
    - Файл: `integrations/src/tools/recon/katana.ts`
    - Описание: Web crawling и spidering
    - Команда: `katana -u target.com`

13. **Gau** ✅
    - Файл: `integrations/src/tools/recon/gau.ts`
    - Описание: Получение URL из архивов
    - Команда: `gau target.com`

14. **Waybackurls** ✅
    - Файл: `integrations/src/tools/recon/waybackurls.ts`
    - Описание: URL из Wayback Machine
    - Команда: `waybackurls target.com`

### Information Gathering
15. **TheHarvester** ✅
    - Файл: `integrations/src/tools/recon/theharvester.ts`
    - Описание: Email, subdomain, IP сбор
    - Команда: `theHarvester -d target.com -b all`

16. **Photon** ✅
    - Файл: `integrations/src/tools/recon/photon.ts`
    - Описание: Быстрый web crawler
    - Команда: `photon -u target.com`

---

## 👤 Social Media OSINT (4)

17. **Sherlock** ✅
    - Файл: `integrations/src/tools/social/sherlock.ts`
    - Описание: Поиск username на 300+ сайтах
    - Команда: `sherlock username`

18. **Holehe** ✅
    - Файл: `integrations/src/tools/social/holehe.ts`
    - Описание: Проверка email на 120+ сайтах
    - Команда: `holehe email@example.com`

19. **Maigret** ✅
    - Файл: `integrations/src/tools/social/maigret.ts`
    - Описание: Расширенный поиск username
    - Команда: `maigret username`

20. **Socialscan** ✅
    - Файл: `integrations/src/tools/social/socialscan.ts`
    - Описание: Проверка доступности username/email
    - Команда: `socialscan username`

---

## 💻 Code Intelligence (2)

21. **TruffleHog** ✅
    - Файл: `integrations/src/tools/code/trufflehog.ts`
    - Описание: Поиск секретов в Git репозиториях
    - Команда: `trufflehog git https://github.com/user/repo`

22. **Gitleaks** ✅
    - Файл: `integrations/src/tools/code/gitleaks.ts`
    - Описание: Обнаружение секретов в коде
    - Команда: `gitleaks detect --source .`

---

## 🌐 Threat Intelligence APIs (11)

23. **VirusTotal** ✅
    - Файл: `integrations/src/virustotal.ts`
    - Описание: Анализ файлов, URL, IP, доменов
    - API: https://www.virustotal.com/api/v3/

24. **Shodan** ✅
    - Файл: `integrations/src/shodan.ts`
    - Описание: Поиск устройств в интернете
    - API: https://api.shodan.io/

25. **URLScan** ✅
    - Файл: `integrations/src/urlscan.ts`
    - Описание: Анализ и сканирование URL
    - API: https://urlscan.io/api/v1/

26. **SecurityTrails** ✅
    - Файл: `integrations/src/securitytrails.ts`
    - Описание: DNS и domain intelligence
    - API: https://api.securitytrails.com/v1/

27. **AbuseIPDB** ✅
    - Файл: `integrations/src/abuseipdb.ts`
    - Описание: База данных вредоносных IP
    - API: https://api.abuseipdb.com/api/v2/

28. **GreyNoise** ✅
    - Файл: `integrations/src/greynoise.ts`
    - Описание: Анализ интернет-шума
    - API: https://api.greynoise.io/v3/

29. **AlienVault OTX** ✅
    - Файл: `integrations/src/alienvault.ts`
    - Описание: Open Threat Exchange
    - API: https://otx.alienvault.com/api/v1/

30. **WHOIS** ✅
    - Файл: `integrations/src/whois.ts`
    - Описание: WHOIS информация о доменах
    - Протокол: WHOIS

31. **DNS** ✅
    - Файл: `integrations/src/dns.ts`
    - Описание: DNS запросы и анализ
    - Протокол: DNS

---

## 🔐 Breach Intelligence (2)

32. **HaveIBeenPwned** ✅
    - Файл: `integrations/src/breach/haveibeenpwned.ts`
    - Описание: Проверка утечек паролей
    - API: https://haveibeenpwned.com/API/v3/

33. **DeHashed** ✅
    - Файл: `integrations/src/breach/dehashed.ts`
    - Описание: Поиск в базах утечек
    - API: https://api.dehashed.com/

---

## 📋 Категории инструментов

### По типу
- **CLI Tools**: 22 инструмента
- **API Integrations**: 11 интеграций

### По функционалу
- **Subdomain Enumeration**: 3
- **Port Scanning**: 2
- **Web Analysis**: 4
- **Vulnerability Scanning**: 1
- **DNS Analysis**: 1
- **URL Discovery**: 3
- **Information Gathering**: 2
- **Social Media OSINT**: 4
- **Code Intelligence**: 2
- **Threat Intelligence**: 9
- **Breach Intelligence**: 2

---

## 🏗️ Архитектура интеграций

### Базовые классы

**BaseTool** (`integrations/src/tools/base-tool.ts`)
- Абстрактный класс для всех CLI инструментов
- Управление процессами
- Timeout handling
- Output parsing
- Error handling

**ToolOrchestrator** (`integrations/src/tools/tool-orchestrator.ts`)
- Параллельное выполнение инструментов
- Последовательное выполнение
- Управление зависимостями
- Агрегация результатов

### API Интеграции

Все API интеграции находятся в `integrations/src/`:
- Единый интерфейс
- Rate limiting
- Error handling
- Response caching
- Retry logic

---

## 🚀 Использование

### Пример использования CLI инструмента

```typescript
import { SubfinderTool } from './tools/recon/subfinder';

const tool = new SubfinderTool();
const result = await tool.execute('example.com', {
  silent: true,
  recursive: true,
});

console.log(result.data.subdomains);
```

### Пример использования API интеграции

```typescript
import { VirusTotalClient } from './virustotal';

const vt = new VirusTotalClient(apiKey);
const report = await vt.getDomainReport('example.com');

console.log(report.reputation);
```

### Пример использования оркестратора

```typescript
import { ToolOrchestrator } from './tools/tool-orchestrator';

const orchestrator = new ToolOrchestrator();

// Параллельное выполнение
const results = await orchestrator.executeParallel(
  'example.com',
  ['amass', 'subfinder', 'assetfinder']
);

// Последовательное выполнение
const results = await orchestrator.executeSequential(
  'example.com',
  ['subfinder', 'httpx', 'nuclei']
);
```

---

## 📊 Статус реализации

| Категория | Инструментов | Статус |
|-----------|--------------|--------|
| Recon | 16 | ✅ Реализовано |
| Social Media | 4 | ✅ Реализовано |
| Code Intelligence | 2 | ✅ Реализовано |
| Threat Intel APIs | 11 | ✅ Реализовано |
| Breach Intel | 2 | ✅ Реализовано |
| **ИТОГО** | **33** | **✅ 100%** |

---

## 🔄 Планы расширения

### Дополнительные инструменты (будущие версии)

**Recon:**
- BBOT - Automated reconnaissance
- Recon-ng - Reconnaissance framework
- Osmedeus - Automated reconnaissance workflow

**Network:**
- Nmap - Network scanner
- Zmap - Fast network scanner

**Web:**
- Burp Suite API - Web vulnerability scanner
- OWASP ZAP API - Security testing

**Cloud:**
- ScoutSuite - Cloud security auditing
- Prowler - AWS security assessment

**Mobile:**
- MobSF - Mobile security framework

---

## 📝 Примечания

- Все CLI инструменты требуют установки на системе
- API интеграции требуют API ключи
- Некоторые инструменты требуют root/admin права
- Rate limiting настроен для всех API
- Все результаты нормализованы в единый формат

---

**Последнее обновление**: 2024-12-XX  
**Версия**: 1.0.0  
**Статус**: Production Ready ✅

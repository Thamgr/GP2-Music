![image](https://github.com/user-attachments/assets/16ca5d84-18c3-43bb-9371-34a54bfdc303)# Описание проекта

Этот проект направлен на анализ музыкальных данных, включающих характеристики различных жанров, количество прослушиваний и популярность исполнителей. Основная цель — выявление зависимостей между популярностью жанра и числом слушателей, а также анализ структуры данных для поиска бизнес-инсайтов.

# Описание данных
## Основные признаки датасета:
- title (object) — название трека;
- artist (object) — исполнитель;
- album (object) — альбом;
- decade (object) — десятилетие, к которому относится трек;
- genre (object) — жанр трека;
- listeners (int64) — количество слушателей;
- playcount (float64) — общее количество прослушиваний;
- genre_summary (object) — описание жанра;
- genre_popularity (float64) — уровень популярности жанра;
- world_position (float64) — позиция трека в мировом чарте;
- russia_position (float64) — позиция трека в российском чарте.
## Количество объектов
Датасет содержит 17600 записей с различными музыкальными треками.
## Пропущенные значения
Некоторые колонки содержат пропущенные значения.
- NaN может означать, что данных нет в исходном источнике;
- В столбце «album» есть пропуски, так как не все песни публикуются в альбомах или относятся к ним. В данном случае обрабатывать пропуски не стоит.
- В столбце «genre» также есть пропуски, так как не по всем трекам есть информация, к какому жанру они относятся. В данном случае решили удалить строки с пропущенными значениями в этом столбце, так как их 1990 / 17600 (на анализ особо не повлияет), заполнить значениями мы их не можем, так как жанры для анализа важны.
- В столбце «playcount» есть пропуски, так так не по всем трекам есть данные.
- genre_popularity может содержать значения, вычисленные по популярности жанра среди определенной аудитории.

# Выбор задачи и EDA
Проект направлен на анализ популярности музыкальных жанров.
## Основные этапы анализа данных:
- Нашли и удалили дубликатов - 2310 дубликатов по названию трека и исполнителю. Их обработали с помощью groupby().agg(). Строк полный дубликатов не было.
- Заполнили пропусков в genre_popularity были заменены на 0, чтобы минимизировать влияние на анализ.
- Привели названия всех жанров к нижнему регистру
- Удалили строки со значениями NaN в genre, playcount. И удалили жанры, названия которых состояли только из цифр или из одной буквы. 

## Основные выводы из Exploratory Data Analysis (EDA):
- Распределение количества прослушиваний по жанрам. Из boxplot можно заметить, что некоторые жанры имеют большое количество выбросов, что говорит о наличии супер-хитов в определенных жанрах.
- Некоторые жанры с небольшой аудиторией имеют высокий playcount/listeners, что говорит о высокой лояльности слушателей.
- Зависимость между популярностью жанра и количеством слушателей. График jointplot показывает логарифмическую зависимость между genre_popularity и listeners.
- В тепловой карте видно, что некоторые жанры популярны только в России, а другие — в мире. Например, pop и k-pop имеют разное распределение в чартах.
- Обсудим тренды по десятилетиям. Использование scraper для анализа жанров по десятилетиям показало, что популярность жанров изменяется во времени, например, synthpop возродился в 2020-х.
- Матрица корреляции показала сильную связь между playcount и listeners, но слабую связь между genre_popularity и listeners, что означает, что даже непопулярные жанры могут иметь преданную аудиторию.


# Инструменты извлечения данных
## Для автоматического сбора данных используются:
- requests – для работы с API Last.fm.
- BeautifulSoup – для парсинга жанров с Chosic.
- pandas, numpy — для обработки данных;
- plotly, matplotlib, seaborn — для визуализации данных;
- logging — для логирования процессов сбора данных;
- tqdm — для отображения прогресса выполнения операций;
- re – для работы с текстовыми тегами.
## Ключевые классы и функции:
### LastFMApi – взаимодействует с Last.fm API, получает: топовые треки и информацию о конкретных треках, альбомах и жанрах. Этот класс работает с API Last.fm и позволяет:
- Получать список самых популярных треков.
- Запрашивать популярные треки в разных странах.
- Получать информацию о конкретных треках, альбомах и жанрах.
- Использовать кэширование запросов для оптимизации.
### GenreScraper – парсит сайт Chosic, анализируя популярность жанров по десятилетиям. Этот код обогащает данные, добавляя:
- Информацию об альбоме (название, десятилетие).
- Информацию о жанре (краткое описание).
- Популярность жанра в десятилетии.
- Объединение данных в data_for_df – дополнение информации о треках и сохранение результатов. Код представляет собой аналитический инструмент, который:
- Собирает данные о популярных музыкальных треках с Last.fm (мировые чарты и чарты по странам).
- Получает дополнительную информацию о каждом треке (жанр, альбом, десятилетие, количество слушателей).
- Дополняет данные аналитикой по жанрам с Chosic (популярность жанра по десятилетиям).
- Сохраняет результаты в удобных форматах (JSON, CSV) для дальнейшего анализа.
- Готовит данные для анализа в Pandas и визуализации с помощью графиков.

# Ссылки на github-аккаунты:
- https://github.com/Anna-Troschenko : Анна Трощенко
- https://github.com/Dashkaivaa : Дарья Иванова
- https://github.com/Thamgr : Василий Виноградов





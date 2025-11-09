# Базовый образ
FROM python:3.12-slim

# Рабочая директория
# WORKDIR /app

# Копируем зависимости
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код

# Запуск бота
CMD ["python3", "main.py"]

FROM postgres:15.4
RUN localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG ru_RU.utf8
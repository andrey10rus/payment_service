# Сервис оплаты

Пример сервиса оплаты, бд payments.db создается с помощью sqlite, для тестов создается test.db

---

## Запуск

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app
```

## Тесты

```bash
python -m pytest
```
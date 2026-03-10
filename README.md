# Сервис оплаты

Пример сервиса оплаты 
БД payments.db создается с помощью sqlite 
Для тестов создается test.db

---

## Запуск

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app
```

## Тесты

```bash
python -m pytest
```
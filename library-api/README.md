# Библиотека API

Спецификация REST API сервиса «Библиотека» в формате OpenAPI 3.1: [openapi.yaml](openapi.yaml).

Ресурсы:

- `/books` — каталог книг и количество экземпляров.
- `/readers` — зарегистрированные читатели.
- `/loans` — выдачи книг; возврат через `POST /loans/{id}/return`.

Базовый адрес: `https://library.example.com/v1` (пример, сервер не развёрнут).
Авторизация всех операций — Bearer JWT.

Правила оформления — в [STYLE.md](STYLE.md), самопроверка контракта — в [REVIEW.md](REVIEW.md).

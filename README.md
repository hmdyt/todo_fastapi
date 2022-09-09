# todo_fastapi
FastAPIの練習 ([参考：FastAPI入門](https://zenn.dev/sh0nk/books/537bb028709ab9))

## 起動方法
```bash
docker-compose up -d
```
- ``localhost:8001``にアクセス

## test
```bash
docker-compose run --entrypoint "poetry run pytest -v" api
```
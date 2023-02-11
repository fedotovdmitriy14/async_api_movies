# сервис для онлайн кинотеатра на Fastapi

включает в себя эндпоинты для просмотра жанров, фильмов и персон

**Запуск:**

в корне проекта создать файл с переменными окружения на основе .env.example

docker-compose up --build -d

все данные хранятся в elasticsearch, попадают туда из postgres. Ссылка на репозеторий с etl:
https://github.com/fedotovdmitriy14/new_admin_panel_sprint_3

**Запуск тестов:**

из докера:
cd /fastapi_solution/tests/functional
docker-compose up --build -d

в докере поднимаются тестовые базы, создаются индексы и запускаются тесты
после того, как все базы поднялись, тесты можно запускать и локально:

pytest /fastapi_solution/tests/functional

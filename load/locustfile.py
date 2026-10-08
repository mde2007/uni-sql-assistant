import random

from locust import HttpUser, task, between

QUESTIONS = [
    "Сколько заявлений подано на «Экономику» в 2026 году?",
    "Как менялся набор студентов за последние пять лет?",
    "Какой средний балл по дисциплине «Базы данных»?",
    "Сколько преподавателей на каждом факультете?",
]


class UniversityUser(HttpUser):
    wait_time = between(1, 3)  # пауза между вопросами, как у живого человека

    @task(3)
    def ask_question(self):
        self.client.post(
            "/api/ask",
            json={"question": random.choice(QUESTIONS), "session_id": "load-test"},
        )

    @task(1)
    def health(self):
        self.client.get("/health")
import random
from datetime import date, timedelta

import psycopg
from faker import Faker

fake = Faker("ru_RU")
random.seed(42)  # одинаковые данные при каждом запуске

# Подключаемся как администратор: ему можно писать в базу
ADMIN_URL = "postgresql://admin:admin_password@localhost:5432/university"

FACULTIES = ["Экономический", "Информационных технологий", "Инженерный", "Гуманитарный"]

# (код, название, номер факультета, бюджетных мест)
PROGRAMS = [
    ("38.03.01", "Экономика", 1, 60),
    ("38.03.02", "Менеджмент", 1, 40),
    ("09.03.03", "Прикладная информатика", 2, 75),
    ("09.03.04", "Программная инженерия", 2, 75),
    ("15.03.01", "Машиностроение", 3, 50),
    ("21.03.01", "Нефтегазовое дело", 3, 90),
    ("40.03.01", "Юриспруденция", 4, 30),
    ("45.03.02", "Лингвистика", 4, 25),
]

DISCIPLINES = [
    "Математический анализ", "Линейная алгебра", "Физика", "Программирование",
    "Базы данных", "Микроэкономика", "Макроэкономика", "Теория вероятностей",
    "Английский язык", "История", "Философия", "Сопротивление материалов",
    "Теоретическая механика", "Гражданское право", "Маркетинг", "Статистика",
]

POSITIONS = ["Ассистент", "Старший преподаватель", "Доцент", "Профессор"]
REGIONS = ["Москва", "Московская область", "Татарстан", "Краснодарский край",
          "Свердловская область", "Новосибирская область", "Башкортостан"]

YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
YEAR_WEIGHTS = [12, 14, 16, 17, 19, 22]  # с каждым годом людей больше


def random_passport():
    return f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}"


def random_person():
    gender = random.choice(["M", "F"])
    if gender == "M":
        name = fake.name_male()
    else:
        name = fake.name_female()
    birth = fake.date_of_birth(minimum_age=17, maximum_age=24)
    return name, birth, gender


def main():
    with psycopg.connect(ADMIN_URL) as conn:
        with conn.cursor() as cur:
            # Очищаем таблицы, чтобы скрипт можно было запускать много раз
            cur.execute(
                "TRUNCATE grades, students, applications, applicants, "
                "disciplines, teachers, programs, faculties RESTART IDENTITY CASCADE"
            )

            print("Факультеты и направления...")
            for name in FACULTIES:
                cur.execute(
                    "INSERT INTO faculties (name, dean_name) VALUES (%s, %s)",
                    (name, fake.name()),
                )
            for code, name, faculty_id, places in PROGRAMS:
                cur.execute(
                    "INSERT INTO programs (code, name, faculty_id, budget_places) "
                    "VALUES (%s, %s, %s, %s)",
                    (code, name, faculty_id, places),
                )

            print("Преподаватели и дисциплины...")
            teachers = []
            for _ in range(150):
                teachers.append((
                    fake.name(), random.choice(POSITIONS),
                    random.randint(1, len(FACULTIES)),
                    fake.email(), fake.phone_number(),
                ))
            cur.executemany(
                "INSERT INTO teachers (full_name, position, faculty_id, email, phone) "
                "VALUES (%s, %s, %s, %s, %s)",
                teachers,
            )
            for name in DISCIPLINES:
                cur.execute(
                    "INSERT INTO disciplines (name, teacher_id, semester) VALUES (%s, %s, %s)",
                    (name, random.randint(1, 150), random.randint(1, 8)),
                )

            print("Абитуриенты и заявления...")
            applicants = []
            applications = []
            for i in range(30000):
                name, birth, gender = random_person()
                applicants.append((
                    name, birth, gender, random_passport(),
                    fake.phone_number(), fake.email(), random.choice(REGIONS),
                ))
                year = random.choices(YEARS, weights=YEAR_WEIGHTS)[0]
                # каждый абитуриент подаёт от 1 до 3 заявлений
                for _ in range(random.randint(1, 3)):
                    applications.append((
                        i + 1,
                        random.randint(1, len(PROGRAMS)),
                        year,
                        random.randint(150, 310),
                        random.choices(["подано", "зачислен", "отказ"], weights=[60, 25, 15])[0],
                        date(year, 6, 20) + timedelta(days=random.randint(0, 40)),
                    ))
            cur.executemany(
                "INSERT INTO applicants (full_name, birth_date, gender, passport, phone, email, region) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                applicants,
            )
            cur.executemany(
                "INSERT INTO applications (applicant_id, program_id, year, exam_score, status, submitted_at) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                applications,
            )

            print("Студенты и оценки...")
            students = []
            grades = []
            for i in range(8000):
                name, birth, gender = random_person()
                program_id = random.randint(1, len(PROGRAMS))
                year = random.choices(YEARS, weights=YEAR_WEIGHTS)[0]
                group = f"П{program_id}-{year % 100}-{random.randint(1, 3)}"
                status = random.choices(["учится", "отчислен", "выпускник"], weights=[80, 10, 10])[0]
                students.append((
                    name, birth, gender, random_passport(), fake.phone_number(),
                    fake.email(), program_id, year, group, status,
                ))
                # у каждого студента 12 оценок по разным дисциплинам
                for discipline_id in random.sample(range(1, len(DISCIPLINES) + 1), 12):
                    grades.append((
                        i + 1, discipline_id,
                        random.choices([2, 3, 4, 5], weights=[5, 25, 40, 30])[0],
                        date(year, 12, 20) + timedelta(days=random.randint(0, 200)),
                    ))
            cur.executemany(
                "INSERT INTO students (full_name, birth_date, gender, passport, phone, email, "
                "program_id, enrollment_year, group_name, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                students,
            )
            cur.executemany(
                "INSERT INTO grades (student_id, discipline_id, grade, exam_date) "
                "VALUES (%s, %s, %s, %s)",
                grades,
            )

    print(f"Готово: {len(applications)} заявлений, {len(grades)} оценок")


if __name__ == "__main__":
    main()
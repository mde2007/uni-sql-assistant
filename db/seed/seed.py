import random
from datetime import date, timedelta

import psycopg
from faker import Faker

fake = Faker("ru_RU")
Faker.seed(42)
random.seed(42)

# Подключаемся как администратор: ему можно писать в базу
ADMIN_URL = "postgresql://admin:admin_password@localhost:5432/university"

FACULTIES = [
    "Факультет геологии и геофизики нефти и газа",
    "Факультет разработки нефтяных и газовых месторождений",
    "Факультет инженерной механики",
    "Факультет автоматики и вычислительной техники",
    "Факультет экономики и управления",
    "Факультет международного энергетического бизнеса",
]

# (название кафедры, номер факультета)
DEPARTMENTS = [
    ("Кафедра поисков и разведки нефти и газа", 1),
    ("Кафедра общей и нефтегазопромысловой геологии", 1),
    ("Кафедра геофизических информационных систем", 1),
    ("Кафедра разведочной геофизики и компьютерных систем", 1),
    ("Кафедра геоэкологии", 1),
    ("Кафедра литологии", 1),

    ("Кафедра бурения нефтяных и газовых скважин", 2),
    ("Кафедра разработки и эксплуатации нефтяных месторождений", 2),
    ("Кафедра разработки и эксплуатации газовых и газоконденсатных месторождений", 2),
    ("Кафедра нефтегазовой и подземной гидромеханики", 2),
    ("Кафедра освоения морских нефтегазовых месторождений", 2),
    ("Кафедра физики", 2),
    ("Кафедра (базовая) исследования нефтегазовых пластовых систем (на базе ООО «Газпром ВНИИГАЗ»)", 2),
    ("Кафедра (базовая) моделирования физико-технологических процессов разработки месторождений", 2),
    ("Кафедра (базовая) проектирования систем обустройства месторождений углеводородов (на базе ООО «Инджиникс Груп»)", 2),
    ("Кафедра (базовая) инновационных газовых технологий (на базе ООО «Газпром ВНИИГАЗ»)", 2),

    ("Кафедра автоматизации проектирования сооружений нефтяной и газовой промышленности", 3),
    ("Кафедра трибологии, сварки, диагностики и ремонта оборудования ТЭК", 3),
    ("Кафедра машин и оборудования нефтяной и газовой промышленности", 3),
    ("Кафедра материаловедения, робототехники и инжиниринга оборудования ТЭК", 3),
    ("Кафедра оборудования нефтегазопереработки", 3),
    ("Кафедра теоретической механики", 3),
    ("Кафедра робототехники и технической механики", 3),
    ("Кафедра стандартизации, сертификации и управления качеством производства нефтегазового оборудования", 3),
    ("Кафедра промышленной безопасности и охраны окружающей среды", 3),
    ("Кафедра сварки и мониторинга нефтегазовых сооружений", 3),

    ("Кафедра высшей математики", 4),
    ("Кафедра информатики", 4),
    ("Кафедра автоматизации технологических процессов", 4),
    ("Кафедра автоматизированных систем управления", 4),
    ("Кафедра теоретической электротехники и электрификации нефтяной и газовой промышленности", 4),
    ("Кафедра информационно-измерительных систем", 4),
    ("Кафедра прикладной математики и компьютерного моделирования", 4),

    ("Кафедра экономики нефтяной и газовой промышленности", 5),
    ("Кафедра производственного менеджмента", 5),
    ("Кафедра управления трудом и персоналом", 5),
    ("Кафедра финансового менеджмента", 5),
    ("Кафедра гражданско-правовых дисциплин", 5),
    ("Кафедра горного, земельного и экологического права", 5),
    ("Кафедра (базовая) системных исследований энергетических рынков (на базе ИНЭИ РАН)", 5),
    ("Кафедра (базовая) управления системой снабжения в нефтегазовом комплексе (на базе ПАО «НК «Роснефть»)", 5),

    ("Кафедра стратегического управления топливно-энергетическим комплексом", 6),
    ("Кафедра нефтегазотрейдинга и логистики", 6),
    ("Кафедра международного нефтегазового бизнеса", 6),
    ("Кафедра экономической теории", 6),
    ("Кафедра (базовая) мировой экономики и энергетической политики (на базе ИМЭМО РАН)", 6),
    ("Кафедра (базовая) инновационного менеджмента", 6),
    ("Кафедра (базовая) маркетинга энергетических продуктов (на базе компании Uniper Global Commodities SE)", 6),
]

# (код, название, номер факультета, бюджетных мест)
PROGRAMS = [
    ("21.05.02", "Прикладная геология", 1, 40),
    ("21.05.03", "Технология геологической разведки", 1, 40),
    ("21.03.01", "Нефтегазовое дело", 2, 90),
    ("15.03.02", "Технологические машины и оборудование", 3, 50),
    ("15.03.06", "Мехатроника и робототехника", 3, 30),
    ("09.03.01", "Информатика и вычислительная техника", 4, 75),
    ("15.03.04", "Автоматизация технологических процессов и производств", 4, 50),
    ("01.03.04", "Прикладная математика", 4, 30),
    ("38.03.01", "Экономика", 5, 60),
    ("38.03.02", "Менеджмент", 5, 40),
    ("40.03.01", "Юриспруденция", 5, 25),
    ("38.03.06", "Торговое дело", 6, 30),
]

# Типичный возраст поступления на каждый факультет (номер факультета: возраст).
ENTRY_AGE = {1: 19, 2: 18, 3: 20, 4: 17, 5: 18, 6: 21}

DISCIPLINES = [
    "Математический анализ", "Линейная алгебра", "Физика", "Программирование",
    "Базы данных", "Микроэкономика", "Макроэкономика", "Теория вероятностей",
    "Английский язык", "История", "Философия", "Сопротивление материалов",
    "Теоретическая механика", "Гражданское право", "Маркетинг", "Статистика",
]

TEACHERS_COUNT = 300
POSITIONS = ["Ассистент", "Старший преподаватель", "Доцент", "Профессор"]
REGIONS = ["Москва", "Московская область", "Татарстан", "Краснодарский край",
          "Свердловская область", "Новосибирская область", "Башкортостан"]

YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
YEAR_WEIGHTS = [12, 14, 16, 17, 19, 22]


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
                "disciplines, teachers, programs, departments, faculties RESTART IDENTITY CASCADE"
            )

            print("Факультеты, кафедры и направления...")
            for name in FACULTIES:
                cur.execute(
                    "INSERT INTO faculties (name, dean_name) VALUES (%s, %s)",
                    (name, fake.name()),
                )
            for name, faculty_id in DEPARTMENTS:
                cur.execute(
                    "INSERT INTO departments (name, faculty_id) VALUES (%s, %s)",
                    (name, faculty_id),
                )
            for code, name, faculty_id, places in PROGRAMS:
                cur.execute(
                    "INSERT INTO programs (code, name, faculty_id, budget_places) "
                    "VALUES (%s, %s, %s, %s)",
                    (code, name, faculty_id, places),
                )

            print("Преподаватели и дисциплины...")
            teachers = []
            for _ in range(TEACHERS_COUNT):
                teachers.append((
                    fake.name(), random.choice(POSITIONS),
                    random.randint(1, len(DEPARTMENTS)),
                    fake.date_of_birth(minimum_age=25, maximum_age=70),
                    fake.email(), fake.phone_number(),
                ))
            cur.executemany(
                "INSERT INTO teachers (full_name, position, department_id, birth_date, email, phone) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                teachers,
            )
            for name in DISCIPLINES:
                cur.execute(
                    "INSERT INTO disciplines (name, teacher_id, semester) VALUES (%s, %s, %s)",
                    (name, random.randint(1, TEACHERS_COUNT), random.randint(1, 8)),
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
                # возраст зависит от года поступления и от факультета
                faculty_id = PROGRAMS[program_id - 1][2]
                entry_age = ENTRY_AGE[faculty_id]
                birth = fake.date_between(date(year - entry_age - 2, 9, 1), date(year - entry_age, 9, 1))
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
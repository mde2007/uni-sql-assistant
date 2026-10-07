SCHEMA_TEXT = """
База данных университета, PostgreSQL. Доступны только эти таблицы:

faculties(id, name, dean_name) — факультеты; dean_name — ФИО декана.
programs(id, code, name, faculty_id -> faculties.id, budget_places) — направления подготовки,
    name например 'Экономика', 'Программная инженерия'.
v_teachers(id, full_name, position, faculty_id -> faculties.id) — преподаватели.
disciplines(id, name, teacher_id -> v_teachers.id, semester) — дисциплины.
v_applications(application_id, program_id -> programs.id, year, exam_score, status,
    submitted_at, gender, region) — заявления абитуриентов.
    status: 'подано' | 'зачислен' | 'отказ'. gender: 'M' | 'F'. exam_score — сумма ЕГЭ.
v_students(student_code, program_id -> programs.id, enrollment_year, group_name, status, gender)
    — студенты. status: 'учится' | 'отчислен' | 'выпускник'. student_code — обезличенный код.
v_grades(student_code -> v_students.student_code, discipline_id -> disciplines.id, grade, exam_date)
    — оценки от 2 до 5.

Правила: только SELECT; всегда перечислять столбцы, без SELECT *;
не выводить student_code, только агрегаты по студентам (COUNT, AVG и т.д.).
"""
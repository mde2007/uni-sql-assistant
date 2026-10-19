-- Всё, что видит ассистент, лежит в отдельной схеме api.
-- Таблицы с личными данными остаются в public, туда у роли ассистента доступа нет.
CREATE SCHEMA IF NOT EXISTS api;

-- Старые представления из public (если база создавалась раньше)
DROP VIEW IF EXISTS public.v_applications, public.v_students, public.v_grades, public.v_teachers;

-- Справочники:
CREATE OR REPLACE VIEW api.faculties AS
SELECT id, name, dean_name FROM public.faculties;

CREATE OR REPLACE VIEW api.departments AS
SELECT id, name, faculty_id FROM public.departments;

CREATE OR REPLACE VIEW api.programs AS
SELECT id, code, name, faculty_id, budget_places FROM public.programs;

CREATE OR REPLACE VIEW api.disciplines AS
SELECT id, name, teacher_id, semester FROM public.disciplines;

-- Заявления:
CREATE OR REPLACE VIEW api.v_applications AS
SELECT a.id AS application_id, a.program_id, a.year, a.exam_score, a.status, a.submitted_at, ap.gender, ap.region
FROM
    public.applications AS a
    JOIN public.applicants AS ap ON ap.id = a.applicant_id;

-- Студенты: без кода студента, связать строку с человеком нельзя.
CREATE OR REPLACE VIEW api.v_students AS
SELECT s.program_id,
      s.enrollment_year,
      s.group_name,
      s.status,
      s.gender,
      date_part('year', age(s.birth_date))::int AS age
FROM public.students AS s;

-- Оценки: вместо кода студента — его направление и год поступления.
-- Группу и пол сюда не добавляем: по ним в маленькой группе можно узнать человека.
CREATE OR REPLACE VIEW api.v_grades AS
SELECT s.program_id,
      s.enrollment_year,
      g.discipline_id,
      g.grade,
      g.exam_date
FROM public.grades AS g
JOIN public.students AS s ON s.id = g.student_id;

-- Преподаватели:
CREATE OR REPLACE VIEW api.v_teachers AS
SELECT t.id,
      t.full_name,
      t.position,
      t.department_id,
      d.faculty_id,
      date_part('year', age(t.birth_date))::int AS age
FROM public.teachers AS t
JOIN public.departments AS d ON d.id = t.department_id;

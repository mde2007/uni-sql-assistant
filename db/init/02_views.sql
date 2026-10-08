-- Заявления:
CREATE OR REPLACE VIEW v_applications AS
SELECT a.id AS application_id, a.program_id, a.year, a.exam_score, a.status, a.submitted_at, ap.gender, ap.region
FROM
    applications AS a
    JOIN applicants AS ap ON ap.id = a.applicant_id;

-- Студенты:
CREATE OR REPLACE VIEW v_students AS
SELECT md5('salt_2026' || s.id::text) AS student_code,
      s.program_id,
      s.enrollment_year,
      s.group_name,
      s.status,
      s.gender,
      date_part('year', age(s.birth_date))::int AS age
FROM students AS s;

-- Оценки:
CREATE OR REPLACE VIEW v_grades AS
SELECT md5('salt_2026' || g.student_id::text) AS student_code,
      g.discipline_id,
      g.grade,
      g.exam_date
FROM grades AS g;

-- Преподаватели:
CREATE OR REPLACE VIEW v_teachers AS
SELECT t.id,
      t.full_name,
      t.position,
      t.department_id,
      d.faculty_id,
      date_part('year', age(t.birth_date))::int AS age
FROM teachers AS t
JOIN departments AS d ON d.id = t.department_id;
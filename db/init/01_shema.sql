CREATE TABLE faculties (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    dean_name TEXT NOT NULL
);

CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    code TEXT NOT NULL, 
    name TEXT NOT NULL, 
    faculty_id INT NOT NULL REFERENCES faculties (id),
    budget_places INT NOT NULL
);

CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    position TEXT NOT NULL,
    faculty_id INT NOT NULL REFERENCES faculties (id),
    email TEXT,
    phone TEXT
);

CREATE TABLE disciplines (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    teacher_id INT NOT NULL REFERENCES teachers (id),
    semester INT NOT NULL
);

CREATE TABLE applicants (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date DATE NOT NULL,
    gender CHAR(1) NOT NULL, -- M / F
    passport TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    region TEXT NOT NULL
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    applicant_id INT NOT NULL REFERENCES applicants (id),
    program_id INT NOT NULL REFERENCES programs (id),
    year INT NOT NULL,
    exam_score INT NOT NULL,
    status TEXT NOT NULL, -- подано / зачислен / отказ
    submitted_at DATE NOT NULL
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date DATE NOT NULL,
    gender CHAR(1) NOT NULL,
    passport TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    program_id INT NOT NULL REFERENCES programs (id),
    enrollment_year INT NOT NULL,
    group_name TEXT NOT NULL,
    status TEXT NOT NULL -- учится / отчислен / выпускник
);

CREATE TABLE grades (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students (id),
    discipline_id INT NOT NULL REFERENCES disciplines (id),
    grade INT NOT NULL CHECK (grade BETWEEN 2 AND 5),
    exam_date DATE NOT NULL
);


CREATE INDEX ON applications (program_id, year);

CREATE INDEX ON students (program_id, enrollment_year);

CREATE INDEX ON grades (discipline_id);

CREATE INDEX ON grades (student_id);
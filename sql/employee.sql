CREATE OR REPLACE FUNCTION login_employee(p_login TEXT, p_password TEXT)
RETURNS INT AS $$
DECLARE
    v_employee_id INT;
BEGIN
    SELECT
        id
    FROM
        employees
    WHERE
        login = p_login AND
        password = crypt(p_password, password)
    INTO v_employee_id;

    RETURN v_employee_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_employees()
RETURNS TABLE (
    id INT,
    login TEXT,
    surname TEXT,
    name TEXT,
    patronymic TEXT,
    sex VARCHAR(6),
    registration_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.login,
        e.surname,
        e.name,
        e.patronymic,
        e.sex,
        e.registration_date
    FROM
        employees e
    WHERE
        e.id != 1
    ORDER BY
        e.registration_date DESC,
        e.login;
END; $$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_employee(
    p_login TEXT,
    p_password TEXT,
    p_surname TEXT,
    p_name TEXT,
    p_patronymic TEXT,
    p_sex VARCHAR(6)
) RETURNS INT AS $$
DECLARE
    v_employee_id INT;
BEGIN
    INSERT INTO employees (
        login,
        password,
        surname,
        name,
        patronymic,
        sex
    )
    VALUES (
        p_login,
        crypt(p_password, gen_salt('md5')),
        p_surname,
        p_name,
        p_patronymic,
        p_sex
    )
    RETURNING id INTO v_employee_id;

    RETURN v_employee_id;
END; $$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION delete_employee(p_employee_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM edit_permissions WHERE employee_id = p_employee_id;
    DELETE FROM employees WHERE id = p_employee_id;
END;
$$ LANGUAGE plpgsql;
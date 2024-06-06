CREATE OR REPLACE FUNCTION create_project(
    p_title TEXT,
    p_deadline DATE,
    p_provider_id INT
) RETURNS INT AS $$
DECLARE
    v_project_id INT;
BEGIN
    INSERT INTO projects (
        title,
        deadline,
        provider_id
    )
    VALUES (
        p_title,
        p_deadline,
        p_provider_id
    )
    RETURNING id INTO v_project_id;

    RETURN v_project_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_projects()
RETURNS TABLE (
    id INT,
    title TEXT,
    deadline DATE,
    provider_company TEXT,
    creation_date DATE,
    employee_permissions TEXT[][]
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.title, p.deadline, providers.company, p.creation_date, ARRAY(
        SELECT
            ARRAY[employee_id::TEXT, emp.login]
        FROM
            edit_permissions, employees emp
        WHERE
            project_id = p.id AND employee_id = emp.id
    ) AS employee_permissions
    FROM
        projects p, providers
    WHERE
        p.provider_id = providers.id
    ORDER BY
        title;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_employee_projects(p_employee_id INT)
RETURNS TABLE (
    id INT,
    title TEXT,
    deadline DATE,
    provider_company TEXT,
    creation_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.title, p.deadline, providers.company, p.creation_date
    FROM
        projects p, providers
    WHERE
        p.provider_id = providers.id AND p.id IN (
            SELECT project_id
            FROM edit_permissions
            WHERE employee_id = p_employee_id
        )
    ORDER BY
        title;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION delete_project(p_project_id INT)
RETURNS VOID AS $$
BEGIN
    DELETE FROM edit_permissions WHERE project_id = p_project_id;
    DELETE FROM specifications WHERE project_id = p_project_id;
    DELETE FROM projects WHERE id = p_project_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_project_permissions(p_project_id INT)
RETURNS TABLE (
    id INT,
    login TEXT,
    full_name TEXT,
    sex VARCHAR(6),
    allowed BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        emp.id, emp.login, emp.surname || ' ' || emp.name || ' ' || emp.patronymic as full_name, emp.sex, TRUE
    FROM
        edit_permissions ep, employees emp
    WHERE
        ep.project_id = p_project_id AND emp.id = ep.employee_id
    UNION
    SELECT
        emp.id, emp.login, emp.surname || ' ' || emp.name || ' ' || emp.patronymic as full_name, emp.sex, FALSE
    FROM
        employees emp
    WHERE
        emp.id != 1 AND
        emp.id NOT IN (
            SELECT employee_id
            FROM edit_permissions
            WHERE project_id = p_project_id
        )
    ORDER BY
        full_name;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_project_permissions(p_project_id INT, p_employee_ids INT[])
RETURNS VOID AS $$
DECLARE
    p_employee_id INT;
BEGIN
    DELETE FROM edit_permissions WHERE project_id = p_project_id;
    FOREACH p_employee_id IN ARRAY p_employee_ids LOOP
        INSERT INTO edit_permissions (project_id, employee_id) VALUES (p_project_id, p_employee_id);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
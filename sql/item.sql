CREATE OR REPLACE FUNCTION get_items(p_project_id INT)
RETURNS TABLE (
    id INT,
    title TEXT,
    article INT,
    description TEXT,
    price NUMERIC(11, 2),
    amount INT
) AS $$
BEGIN
    IF p_project_id::INT = 0::INT THEN
        RETURN QUERY
        SELECT
            i.id,
            i.title,
            i.article,
            i.description,
            i.price,
            0
        FROM
            items i
        ORDER BY
            i.title;

    ELSE
        RETURN QUERY
        SELECT
            i.id,
            i.title,
            i.article,
            i.description,
            i.price,
            s.amount
        FROM
            specifications s
        JOIN
            projects ON projects.id = s.project_id
        JOIN
            items i ON i.id = s.item_id
        WHERE
            s.project_id = p_project_id
        ORDER BY
            i.title;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_specification(p_project_id INT, items INT[][])
RETURNS VOID AS $$
DECLARE
    i INT;
    item_id INT;
    amount INT;
BEGIN
    DELETE FROM
        specifications
    WHERE
        project_id = p_project_id;

    IF array_length(items, 1) IS NULL THEN
        RETURN;
    END IF;

    FOR i IN 1..array_length(items, 1) LOOP
        item_id := items[i][1];
        amount := items[i][2];
        INSERT INTO
            specifications (project_id, item_id, amount)
        VALUES
            (p_project_id, item_id, amount);
    END LOOP;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_item(p_title TEXT, p_article INT, p_description TEXT, p_price NUMERIC(11, 2))
RETURNS INT AS $$
DECLARE
    item_id INT;
BEGIN
    INSERT INTO
        items (title, article, description, price)
    VALUES
        (p_title, p_article, p_description, p_price)
    RETURNING
        id INTO item_id;

    RETURN item_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_statement_items_data(p_project_ids INT[])
RETURNS TABLE (
    title TEXT,
    amount INT,
    price NUMERIC(11, 2),
    cost NUMERIC(11, 2),
    provider_id INT
) AS $$
BEGIN
    -- Automatic statement forming
    IF ARRAY_LENGTH(p_project_ids, 1) IS NULL THEN
        RETURN QUERY
        SELECT
            i.title,
            s.amount,
            i.price,
            i.price * s.amount,
            p.provider_id
        FROM
            specifications s
        JOIN
            items i ON i.id = s.item_id
        JOIN
            projects p ON p.id = s.project_id
        WHERE
            p.deadline > CURRENT_DATE
        ORDER BY
            i.title;

    -- Selective statement forming
    ELSE
        RETURN QUERY
        SELECT
            i.title,
            s.amount,
            i.price,
            i.price * s.amount,
            p.provider_id
        FROM
            specifications s
        JOIN
            items i ON i.id = s.item_id
        JOIN
            projects p ON p.id = s.project_id
        WHERE
            s.project_id = ANY(p_project_ids)
        ORDER BY
            i.title;
    END IF;
END;
$$ LANGUAGE plpgsql;
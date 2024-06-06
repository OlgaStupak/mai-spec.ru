CREATE OR REPLACE FUNCTION get_providers()
RETURNS TABLE (
    id INT,
    company TEXT,
    address TEXT,
    inn VARCHAR(15),
    kpp VARCHAR(9),
    bank TEXT,
    payment_account VARCHAR(20),
    bik VARCHAR(9)
) AS $$
BEGIN
    RETURN QUERY SELECT * FROM providers ORDER BY company;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_provider(
    p_company TEXT,
    p_address TEXT,
    p_inn VARCHAR(15),
    p_kpp VARCHAR(9),
    p_bank TEXT,
    p_payment_account VARCHAR(20),
    p_bik VARCHAR(9)
) RETURNS TABLE(v_provider_id INT, v_provider_company TEXT) AS $$
BEGIN
    INSERT INTO providers (
        company,
        address,
        inn,
        kpp,
        bank,
        payment_account,
        bik
    )
    VALUES (
        p_company,
        p_address,
        p_inn,
        p_kpp,
        p_bank,
        p_payment_account,
        p_bik
    )
    RETURNING id, company INTO v_provider_id, v_provider_company;

    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_statement_providers_data(p_providers_ids INT[])
RETURNS TABLE (
    company TEXT,
    address TEXT,
    inn VARCHAR(15),
    kpp VARCHAR(9),
    bank TEXT,
    payment_account VARCHAR(20),
    bik VARCHAR(9)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.company,
        p.address,
        p.inn,
        p.kpp,
        p.bank,
        p.payment_account,
        p.bik
    FROM
        providers p
    WHERE
        id = ANY(p_providers_ids)
    ORDER BY
        company;
END;
$$ LANGUAGE plpgsql;
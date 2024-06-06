--
-- PostgreSQL database dump
--

-- Dumped from database version 14.11 (Debian 14.11-1.pgdg110+2)
-- Dumped by pg_dump version 14.11 (Debian 14.11-1.pgdg110+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: add_employee(text, text, text, text, text, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.add_employee(p_login text, p_password text, p_surname text, p_name text, p_patronymic text, p_sex character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
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
END; $$;


ALTER FUNCTION public.add_employee(p_login text, p_password text, p_surname text, p_name text, p_patronymic text, p_sex character varying) OWNER TO postgres;

--
-- Name: add_item(text, integer, text, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.add_item(p_title text, p_article integer, p_description text, p_price numeric) RETURNS integer
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.add_item(p_title text, p_article integer, p_description text, p_price numeric) OWNER TO postgres;

--
-- Name: add_provider(text, text, character varying, character varying, text, character varying, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.add_provider(p_company text, p_address text, p_inn character varying, p_kpp character varying, p_bank text, p_payment_account character varying, p_bik character varying) RETURNS TABLE(v_provider_id integer, v_provider_company text)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.add_provider(p_company text, p_address text, p_inn character varying, p_kpp character varying, p_bank text, p_payment_account character varying, p_bik character varying) OWNER TO postgres;

--
-- Name: create_project(text, date, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.create_project(p_title text, p_deadline date, p_provider_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.create_project(p_title text, p_deadline date, p_provider_id integer) OWNER TO postgres;

--
-- Name: delete_employee(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_employee(p_employee_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM edit_permissions WHERE employee_id = p_employee_id;
    DELETE FROM employees WHERE id = p_employee_id;
END;
$$;


ALTER FUNCTION public.delete_employee(p_employee_id integer) OWNER TO postgres;

--
-- Name: delete_project(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_project(p_project_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    DELETE FROM edit_permissions WHERE project_id = p_project_id;
    DELETE FROM specifications WHERE project_id = p_project_id;
    DELETE FROM projects WHERE id = p_project_id;
END;
$$;


ALTER FUNCTION public.delete_project(p_project_id integer) OWNER TO postgres;

--
-- Name: get_employee_projects(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_employee_projects(p_employee_id integer) RETURNS TABLE(id integer, title text, deadline date, provider_company text, creation_date date)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_employee_projects(p_employee_id integer) OWNER TO postgres;

--
-- Name: get_employees(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_employees() RETURNS TABLE(id integer, login text, surname text, name text, patronymic text, sex character varying, registration_date date)
    LANGUAGE plpgsql
    AS $$
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
END; $$;


ALTER FUNCTION public.get_employees() OWNER TO postgres;

--
-- Name: get_items(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_items(p_project_id integer) RETURNS TABLE(id integer, title text, article integer, description text, price numeric, amount integer)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_items(p_project_id integer) OWNER TO postgres;

--
-- Name: get_project_permissions(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_project_permissions(p_project_id integer) RETURNS TABLE(id integer, login text, full_name text, sex character varying, allowed boolean)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_project_permissions(p_project_id integer) OWNER TO postgres;

--
-- Name: get_projects(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_projects() RETURNS TABLE(id integer, title text, deadline date, provider_company text, creation_date date, employee_permissions text[])
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_projects() OWNER TO postgres;

--
-- Name: get_providers(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_providers() RETURNS TABLE(id integer, company text, address text, inn character varying, kpp character varying, bank text, payment_account character varying, bik character varying)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY SELECT * FROM providers ORDER BY company;
END;
$$;


ALTER FUNCTION public.get_providers() OWNER TO postgres;

--
-- Name: get_statement_items_data(integer[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_statement_items_data(p_project_ids integer[]) RETURNS TABLE(title text, amount integer, price numeric, cost numeric, provider_id integer)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_statement_items_data(p_project_ids integer[]) OWNER TO postgres;

--
-- Name: get_statement_providers_data(integer[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_statement_providers_data(p_providers_ids integer[]) RETURNS TABLE(company text, address text, inn character varying, kpp character varying, bank text, payment_account character varying, bik character varying)
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.get_statement_providers_data(p_providers_ids integer[]) OWNER TO postgres;

--
-- Name: login_employee(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.login_employee(p_login text, p_password text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.login_employee(p_login text, p_password text) OWNER TO postgres;

--
-- Name: update_project_permissions(integer, integer[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_project_permissions(p_project_id integer, p_employee_ids integer[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    p_employee_id INT;
BEGIN
    DELETE FROM edit_permissions WHERE project_id = p_project_id;
    FOREACH p_employee_id IN ARRAY p_employee_ids LOOP
        INSERT INTO edit_permissions (project_id, employee_id) VALUES (p_project_id, p_employee_id);
    END LOOP;
END;
$$;


ALTER FUNCTION public.update_project_permissions(p_project_id integer, p_employee_ids integer[]) OWNER TO postgres;

--
-- Name: update_specification(integer, integer[]); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_specification(p_project_id integer, items integer[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
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
$$;


ALTER FUNCTION public.update_specification(p_project_id integer, items integer[]) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: edit_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.edit_permissions (
    employee_id integer,
    project_id integer
);


ALTER TABLE public.edit_permissions OWNER TO postgres;

--
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    login text NOT NULL,
    password text NOT NULL,
    surname text NOT NULL,
    name text NOT NULL,
    patronymic text,
    registration_date date DEFAULT CURRENT_DATE,
    sex character varying(6) NOT NULL,
    CONSTRAINT employees_sex_check CHECK ((((sex)::text = 'male'::text) OR ((sex)::text = 'female'::text)))
);


ALTER TABLE public.employees OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employees_id_seq OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.items (
    id integer NOT NULL,
    title text NOT NULL,
    article integer NOT NULL,
    description text,
    price numeric(11,2)
);


ALTER TABLE public.items OWNER TO postgres;

--
-- Name: items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.items_id_seq OWNER TO postgres;

--
-- Name: items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.items_id_seq OWNED BY public.items.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    title text NOT NULL,
    deadline date NOT NULL,
    provider_id integer,
    creation_date date DEFAULT CURRENT_DATE,
    CONSTRAINT projects_deadline_check CHECK ((deadline > CURRENT_DATE))
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.projects_id_seq OWNER TO postgres;

--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: providers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.providers (
    id integer NOT NULL,
    company text NOT NULL,
    address text NOT NULL,
    inn character varying(15) NOT NULL,
    kpp character varying(9) NOT NULL,
    bank text NOT NULL,
    payment_account character varying(20) NOT NULL,
    bik character varying(9) NOT NULL
);


ALTER TABLE public.providers OWNER TO postgres;

--
-- Name: providers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.providers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.providers_id_seq OWNER TO postgres;

--
-- Name: providers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.providers_id_seq OWNED BY public.providers.id;


--
-- Name: specifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.specifications (
    project_id integer,
    item_id integer,
    amount integer NOT NULL,
    CONSTRAINT specifications_amount_check CHECK ((amount > 0))
);


ALTER TABLE public.specifications OWNER TO postgres;

--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.items ALTER COLUMN id SET DEFAULT nextval('public.items_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: providers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers ALTER COLUMN id SET DEFAULT nextval('public.providers_id_seq'::regclass);


--
-- Data for Name: edit_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.edit_permissions (employee_id, project_id) FROM stdin;
4	4
2	3
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employees (id, login, password, surname, name, patronymic, registration_date, sex) FROM stdin;
1	root	$1$S8d4BFrF$7uKXv8WHAZoWwx3cW3jrV.	.	.	.	2000-01-01	male
2	oroch	$1$J4nTeVk.$k1s9QP6caxvvUTGbAS0hh.	Ступак	Ольга	Алексеевна	2024-06-04	female
4	madara	$1$B5O.A.E6$ShrZFw1aRVs.kPhSzs7Ff/	Ситникова	Виктория	Андреевна	2024-06-05	female
\.


--
-- Data for Name: items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.items (id, title, article, description, price) FROM stdin;
1	Компьютер Lenovo IdeaPad 5	123456789	Персональный компьютер, с диагональю 14", темно-зеленого цвета, весом 1.5 кг, процессор intel core i3	49000.00
2	Принтер Microsoft XPS Document Writer	15263748	Принтер для цветной печати, поддерживает Bluetooth соединение, печать производится в формате А4	23990.00
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projects (id, title, deadline, provider_id, creation_date) FROM stdin;
3	Курсовая работа	2024-06-11	1	2024-06-05
4	Документация	2024-06-11	3	2024-06-05
\.


--
-- Data for Name: providers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.providers (id, company, address, inn, kpp, bank, payment_account, bik) FROM stdin;
1	oscomp	Московская область, Подольск, Кирова, 37	12345	544555	Сбер	Корпаративный	12345
3	МАИ	Москва, Волоколамское шоссе, д. 3	1234567890	123456789	Альфа-банк	12345678901234567890	544567321
\.


--
-- Data for Name: specifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.specifications (project_id, item_id, amount) FROM stdin;
4	2	2
3	1	1
3	2	2
\.


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employees_id_seq', 4, true);


--
-- Name: items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.items_id_seq', 2, true);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.projects_id_seq', 4, true);


--
-- Name: providers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.providers_id_seq', 3, true);


--
-- Name: items items_article_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_article_key UNIQUE (article);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: projects projects_title_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_title_key UNIQUE (title);


--
-- Name: providers providers_bik_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_bik_key UNIQUE (bik);


--
-- Name: providers providers_company_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_company_key UNIQUE (company);


--
-- Name: providers providers_inn_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_inn_key UNIQUE (inn);


--
-- Name: providers providers_kpp_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_kpp_key UNIQUE (kpp);


--
-- Name: providers providers_payment_account_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_payment_account_key UNIQUE (payment_account);


--
-- Name: providers providers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.providers
    ADD CONSTRAINT providers_pkey PRIMARY KEY (id);


--
-- Name: employees users_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: employees users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: edit_permissions edit_permissions_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.edit_permissions
    ADD CONSTRAINT edit_permissions_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: edit_permissions edit_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.edit_permissions
    ADD CONSTRAINT edit_permissions_user_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: projects projects_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_provider_id_fkey FOREIGN KEY (provider_id) REFERENCES public.providers(id);


--
-- Name: specifications specifications_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.specifications
    ADD CONSTRAINT specifications_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: specifications specifications_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.specifications
    ADD CONSTRAINT specifications_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- PostgreSQL database dump complete
--


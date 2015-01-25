--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = true;

--
-- Name: exemptions; Type: TABLE; Schema: public; Owner: POPM; Tablespace: 
--

CREATE TABLE exemptions (
    "ID" integer NOT NULL,
    ip text,
    whenadded integer,
    whoadded text,
    lastmodified integer,
    expires integer,
    wholast text,
    perma boolean,
    reason text,
    active boolean
);


ALTER TABLE public.exemptions OWNER TO POPM;

--
-- Name: exemptions_ID_seq; Type: SEQUENCE; Schema: public; Owner: POPM
--

CREATE SEQUENCE "exemptions_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."exemptions_ID_seq" OWNER TO POPM;

--
-- Name: exemptions_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: POPM
--

ALTER SEQUENCE "exemptions_ID_seq" OWNED BY exemptions."ID";


--
-- Name: settings; Type: TABLE; Schema: public; Owner: POPM; Tablespace: 
--

CREATE TABLE settings (
    enable_dnsbl boolean,
    enable_http boolean,
    enable_socks boolean,
    access_die integer,
    access_set integer,
    access_say integer,
    access_emote integer,
    access_joinpart integer,
    view_exempts integer,
    modify_exempts integer
);


ALTER TABLE public.settings OWNER TO POPM;

--
-- Name: users; Type: TABLE; Schema: public; Owner: POPM; Tablespace: 
--

CREATE TABLE users (
    "ID" integer NOT NULL,
    admin text NOT NULL,
    added integer NOT NULL,
    access integer NOT NULL,
    bywho text
);


ALTER TABLE public.users OWNER TO POPM;

--
-- Name: users_ID_seq; Type: SEQUENCE; Schema: public; Owner: POPM
--

CREATE SEQUENCE "users_ID_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."users_ID_seq" OWNER TO POPM;

--
-- Name: users_ID_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: POPM
--

ALTER SEQUENCE "users_ID_seq" OWNED BY users."ID";


--
-- Name: users_access_seq; Type: SEQUENCE; Schema: public; Owner: POPM
--

CREATE SEQUENCE users_access_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_access_seq OWNER TO POPM;

--
-- Name: users_access_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: POPM
--

ALTER SEQUENCE users_access_seq OWNED BY users.access;


--
-- Name: users_added_seq; Type: SEQUENCE; Schema: public; Owner: POPM
--

CREATE SEQUENCE users_added_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_added_seq OWNER TO POPM;

--
-- Name: users_added_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: POPM
--

ALTER SEQUENCE users_added_seq OWNED BY users.added;


--
-- Name: users_admin_seq; Type: SEQUENCE; Schema: public; Owner: POPM
--

CREATE SEQUENCE users_admin_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_admin_seq OWNER TO POPM;

--
-- Name: users_admin_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: POPM
--

ALTER SEQUENCE users_admin_seq OWNED BY users.admin;


--
-- Name: users_bywho_seq; Type: SEQUENCE; Schema: public; Owner: POPM
--

CREATE SEQUENCE users_bywho_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_bywho_seq OWNER TO POPM;

--
-- Name: users_bywho_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: POPM
--

ALTER SEQUENCE users_bywho_seq OWNED BY users.bywho;


--
-- Name: ID; Type: DEFAULT; Schema: public; Owner: POPM
--

ALTER TABLE ONLY exemptions ALTER COLUMN "ID" SET DEFAULT nextval('"exemptions_ID_seq"'::regclass);


--
-- Name: ID; Type: DEFAULT; Schema: public; Owner: POPM
--

ALTER TABLE ONLY users ALTER COLUMN "ID" SET DEFAULT nextval('"users_ID_seq"'::regclass);


--
-- Name: admin; Type: DEFAULT; Schema: public; Owner: POPM
--

ALTER TABLE ONLY users ALTER COLUMN admin SET DEFAULT nextval('users_admin_seq'::regclass);


--
-- Name: added; Type: DEFAULT; Schema: public; Owner: POPM
--

ALTER TABLE ONLY users ALTER COLUMN added SET DEFAULT nextval('users_added_seq'::regclass);


--
-- Name: access; Type: DEFAULT; Schema: public; Owner: POPM
--

ALTER TABLE ONLY users ALTER COLUMN access SET DEFAULT nextval('users_access_seq'::regclass);


--
-- Data for Name: exemptions; Type: TABLE DATA; Schema: public; Owner: POPM
--



--
-- Name: exemptions_ID_seq; Type: SEQUENCE SET; Schema: public; Owner: POPM
--

SELECT pg_catalog.setval('"exemptions_ID_seq"', 7, true);


--
-- Data for Name: settings; Type: TABLE DATA; Schema: public; Owner: POPM
--

INSERT INTO settings VALUES (true, true, true, 1000, 1000, 1000, 1000, 1000, 1000, 1000);


--
-- Name: users_ID_seq; Type: SEQUENCE SET; Schema: public; Owner: POPM
--

SELECT pg_catalog.setval('"users_ID_seq"', 16, true);


--
-- Name: users_access_seq; Type: SEQUENCE SET; Schema: public; Owner: POPM
--

SELECT pg_catalog.setval('users_access_seq', 1, false);


--
-- Name: users_added_seq; Type: SEQUENCE SET; Schema: public; Owner: POPM
--

SELECT pg_catalog.setval('users_added_seq', 1, false);


--
-- Name: users_admin_seq; Type: SEQUENCE SET; Schema: public; Owner: POPM
--

SELECT pg_catalog.setval('users_admin_seq', 1, false);


--
-- Name: users_bywho_seq; Type: SEQUENCE SET; Schema: public; Owner: POPM
--

SELECT pg_catalog.setval('users_bywho_seq', 1, false);


--
-- Name: exemptions_pkey; Type: CONSTRAINT; Schema: public; Owner: POPM; Tablespace: 
--

ALTER TABLE ONLY exemptions
    ADD CONSTRAINT exemptions_pkey PRIMARY KEY ("ID");


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: POPM; Tablespace: 
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY ("ID");


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;
GRANT ALL ON SCHEMA public TO popm;


--
-- Name: users; Type: ACL; Schema: public; Owner: POPM
--

REVOKE ALL ON TABLE users FROM PUBLIC;
REVOKE ALL ON TABLE users FROM POPM;
GRANT ALL ON TABLE users TO POPM;
GRANT ALL ON TABLE users TO PUBLIC;
GRANT ALL ON TABLE users TO popm;


--
-- PostgreSQL database dump complete
--


--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: fixture_markets; Type: TABLE; Schema: public; Owner: patrickmckelvy; Tablespace: 
--

CREATE TABLE fixture_markets (
    id integer NOT NULL,
    marketcurrency character varying(12) NOT NULL,
    basecurrency character varying(12) NOT NULL,
    marketcurrencylong character varying(50) NOT NULL,
    basecurrencylong character varying(50) NOT NULL,
    mintradesize double precision NOT NULL,
    marketname character varying(12) NOT NULL,
    isactive boolean DEFAULT true NOT NULL,
    logourl character varying(256) NOT NULL
);


ALTER TABLE fixture_markets OWNER TO patrickmckelvy;

--
-- Name: fixture_markets_id_seq; Type: SEQUENCE; Schema: public; Owner: patrickmckelvy
--

CREATE SEQUENCE fixture_markets_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE fixture_markets_id_seq OWNER TO patrickmckelvy;

--
-- Name: fixture_markets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: patrickmckelvy
--

ALTER SEQUENCE fixture_markets_id_seq OWNED BY fixture_markets.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: patrickmckelvy
--

ALTER TABLE ONLY fixture_markets ALTER COLUMN id SET DEFAULT nextval('fixture_markets_id_seq'::regclass);


--
-- Name: fixture_markets_pkey; Type: CONSTRAINT; Schema: public; Owner: patrickmckelvy; Tablespace: 
--

ALTER TABLE ONLY fixture_markets
    ADD CONSTRAINT fixture_markets_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


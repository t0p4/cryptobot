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
-- Name: prod_currencies; Type: TABLE; Schema: public; Owner: patrickmckelvy; Tablespace: 
--

CREATE TABLE prod_currencies (
    id integer NOT NULL,
    currency character varying(6) NOT NULL,
    currencylong character varying(50) NOT NULL,
    minconfirmation integer NOT NULL,
    txfee double precision NOT NULL,
    isactive boolean DEFAULT true NOT NULL,
    cointype character varying(256) NOT NULL,
    baseaddress character varying(256)
);


ALTER TABLE prod_currencies OWNER TO patrickmckelvy;

--
-- Name: prod_currencies_id_seq; Type: SEQUENCE; Schema: public; Owner: patrickmckelvy
--

CREATE SEQUENCE prod_currencies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE prod_currencies_id_seq OWNER TO patrickmckelvy;

--
-- Name: prod_currencies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: patrickmckelvy
--

ALTER SEQUENCE prod_currencies_id_seq OWNED BY prod_currencies.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: patrickmckelvy
--

ALTER TABLE ONLY prod_currencies ALTER COLUMN id SET DEFAULT nextval('prod_currencies_id_seq'::regclass);


--
-- Name: prod_currencies_pkey; Type: CONSTRAINT; Schema: public; Owner: patrickmckelvy; Tablespace: 
--

ALTER TABLE ONLY prod_currencies
    ADD CONSTRAINT prod_currencies_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


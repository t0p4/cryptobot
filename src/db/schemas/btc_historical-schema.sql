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
-- Name: btc_historical; Type: TABLE; Schema: public; Owner: patrickmckelvy; Tablespace: 
--

CREATE TABLE btc_historical (
    id integer NOT NULL,
    open double precision NOT NULL,
    high double precision NOT NULL,
    low double precision NOT NULL,
    close double precision NOT NULL,
    volume_btc double precision NOT NULL,
    volume_usd double precision NOT NULL,
    weighted_price double precision NOT NULL,
    "timestamp" integer NOT NULL
);


ALTER TABLE btc_historical OWNER TO patrickmckelvy;

--
-- Name: btc_historical_id_seq; Type: SEQUENCE; Schema: public; Owner: patrickmckelvy
--

CREATE SEQUENCE btc_historical_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE btc_historical_id_seq OWNER TO patrickmckelvy;

--
-- Name: btc_historical_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: patrickmckelvy
--

ALTER SEQUENCE btc_historical_id_seq OWNED BY btc_historical.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: patrickmckelvy
--

ALTER TABLE ONLY btc_historical ALTER COLUMN id SET DEFAULT nextval('btc_historical_id_seq'::regclass);


--
-- Name: btc_historical_pkey; Type: CONSTRAINT; Schema: public; Owner: patrickmckelvy; Tablespace: 
--

ALTER TABLE ONLY btc_historical
    ADD CONSTRAINT btc_historical_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


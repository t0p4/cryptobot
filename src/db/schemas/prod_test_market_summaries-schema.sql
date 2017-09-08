--
-- PostgreSQL database dump
--

-- Dumped from database version 9.4.5
-- Dumped by pg_dump version 9.6.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: prod_test_market_summaries; Type: TABLE; Schema: public; Owner: patrickmckelvy
--

CREATE TABLE prod_test_market_summaries (
    id integer NOT NULL,
    marketname character varying(12) NOT NULL,
    volume double precision NOT NULL,
    last double precision NOT NULL,
    basevolume double precision NOT NULL,
    bid double precision NOT NULL,
    ask double precision NOT NULL,
    openbuyorders integer NOT NULL,
    opensellorders integer NOT NULL,
    saved_timestamp timestamp without time zone NOT NULL,
    ticker_nonce integer NOT NULL
);


ALTER TABLE prod_test_market_summaries OWNER TO patrickmckelvy;

--
-- Name: market_summaries_id_seq; Type: SEQUENCE; Schema: public; Owner: patrickmckelvy
--

CREATE SEQUENCE market_summaries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE market_summaries_id_seq OWNER TO patrickmckelvy;

--
-- Name: market_summaries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: patrickmckelvy
--

ALTER SEQUENCE market_summaries_id_seq OWNED BY prod_test_market_summaries.id;


--
-- Name: prod_test_market_summaries id; Type: DEFAULT; Schema: public; Owner: patrickmckelvy
--

ALTER TABLE ONLY prod_test_market_summaries ALTER COLUMN id SET DEFAULT nextval('market_summaries_id_seq'::regclass);


--
-- Name: prod_test_market_summaries prod_test_market_summaries_pkey; Type: CONSTRAINT; Schema: public; Owner: patrickmckelvy
--

ALTER TABLE ONLY prod_test_market_summaries
    ADD CONSTRAINT prod_test_market_summaries_pkey PRIMARY KEY (id);


--
-- Name: prod_test_marekt_summaries_marketname_idx; Type: INDEX; Schema: public; Owner: patrickmckelvy
--

CREATE INDEX prod_test_marekt_summaries_marketname_idx ON prod_test_market_summaries USING btree (marketname);


--
-- Name: prod_test_market_summaries_ticker_nonce_idx; Type: INDEX; Schema: public; Owner: patrickmckelvy
--

CREATE INDEX prod_test_market_summaries_ticker_nonce_idx ON prod_test_market_summaries USING btree (ticker_nonce);


--
-- PostgreSQL database dump complete
--


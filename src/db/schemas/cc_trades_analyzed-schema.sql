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
-- Name: cc_trades_analyzed; Type: TABLE; Schema: public; Owner: patrickmckelvy
--

CREATE TABLE cc_trades_analyzed (
    id integer NOT NULL,
    order_type character varying(20),
    base_coin character varying(5),
    mkt_coin character varying(5),
    quantity double precision,
    rate double precision,
    trade_id character varying(50),
    exchange_id character varying(20),
    save_time timestamp without time zone,
    rate_btc double precision,
    rate_eth double precision,
    rate_usd double precision,
    trade_direction character varying(4),
    cost_avg_btc double precision,
    cost_avg_eth double precision,
    cost_avg_usd double precision,
    analyzed boolean DEFAULT false,
    pair character varying(20),
    commish double precision,
    commish_asset character varying(20),
    trade_time bigint
);


ALTER TABLE cc_trades_analyzed OWNER TO patrickmckelvy;

--
-- Name: COLUMN cc_trades_analyzed.trade_direction; Type: COMMENT; Schema: public; Owner: patrickmckelvy
--

COMMENT ON COLUMN cc_trades_analyzed.trade_direction IS 'buy or sell';


--
-- Name: cc_trades_analyzed_id_seq; Type: SEQUENCE; Schema: public; Owner: patrickmckelvy
--

CREATE SEQUENCE cc_trades_analyzed_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE cc_trades_analyzed_id_seq OWNER TO patrickmckelvy;

--
-- Name: cc_trades_analyzed_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: patrickmckelvy
--

ALTER SEQUENCE cc_trades_analyzed_id_seq OWNED BY cc_trades_analyzed.id;


--
-- Name: cc_trades_analyzed id; Type: DEFAULT; Schema: public; Owner: patrickmckelvy
--

ALTER TABLE ONLY cc_trades_analyzed ALTER COLUMN id SET DEFAULT nextval('cc_trades_analyzed_id_seq'::regclass);


--
-- Name: cc_trades_analyzed cc_trades_analyzed_pkey; Type: CONSTRAINT; Schema: public; Owner: patrickmckelvy
--

ALTER TABLE ONLY cc_trades_analyzed
    ADD CONSTRAINT cc_trades_analyzed_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


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
-- Name: backtest_orders; Type: TABLE; Schema: public; Owner: patrickmckelvy
--

CREATE TABLE backtest_orders (
    id integer NOT NULL,
    order_type character varying(256) NOT NULL,
    market character varying(256) NOT NULL,
    base_currency character varying(256) NOT NULL,
    market_currency character varying(256) NOT NULL,
    quantity character varying(256) NOT NULL,
    rate real NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    uuid character varying(256) NOT NULL
);


ALTER TABLE backtest_orders OWNER TO patrickmckelvy;

--
-- Name: backtest_orders backtest_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: patrickmckelvy
--

ALTER TABLE ONLY backtest_orders
    ADD CONSTRAINT backtest_orders_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


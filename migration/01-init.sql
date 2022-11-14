--
-- PostgreSQL database dump
--

-- Dumped from database version 15.0 (Ubuntu 15.0-1.pgdg22.10+1)
-- Dumped by pg_dump version 15.0 (Ubuntu 15.0-1.pgdg22.10+1)

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

DROP INDEX IF EXISTS public.expense_items_updated_at_idx;
DROP INDEX IF EXISTS public.expense_items_created_at_idx;
DROP INDEX IF EXISTS public.configs_path_idx;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_telegram_username_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_telegram_userid_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.expense_items DROP CONSTRAINT IF EXISTS expense_items_pkey;
ALTER TABLE IF EXISTS ONLY public.expense_category_recommendations DROP CONSTRAINT IF EXISTS expense_category_recommendations_pkey;
ALTER TABLE IF EXISTS ONLY public.expense_categories DROP CONSTRAINT IF EXISTS expense_categories_pkey;
ALTER TABLE IF EXISTS ONLY public.configs DROP CONSTRAINT IF EXISTS configs_pkey;
ALTER TABLE IF EXISTS ONLY public.bot_chatcontexts DROP CONSTRAINT IF EXISTS bot_chatcontexts_pkey;
ALTER TABLE IF EXISTS public.expense_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.expense_category_recommendations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.expense_categories ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.configs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.bot_chatcontexts ALTER COLUMN id DROP DEFAULT;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.expense_items_id_seq;
DROP TABLE IF EXISTS public.expense_items;
DROP SEQUENCE IF EXISTS public.expense_category_recommendations_id_seq;
DROP TABLE IF EXISTS public.expense_category_recommendations;
DROP SEQUENCE IF EXISTS public.expense_categories_id_seq;
DROP TABLE IF EXISTS public.expense_categories;
DROP SEQUENCE IF EXISTS public.configs_id_seq;
DROP TABLE IF EXISTS public.configs;
DROP SEQUENCE IF EXISTS public.bot_chatcontexts_id_seq;
DROP TABLE IF EXISTS public.bot_chatcontexts;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bot_chatcontexts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bot_chatcontexts ( id integer NOT NULL, user_id bigint NOT NULL, chat_id bigint NOT NULL, serialized_handler json NOT NULL, is_active boolean DEFAULT false, created_at timestamp without time zone, updated_at timestamp without time zone );


--
-- Name: bot_chatcontexts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bot_chatcontexts_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;


--
-- Name: bot_chatcontexts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bot_chatcontexts_id_seq OWNED BY public.bot_chatcontexts.id;


--
-- Name: configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.configs ( id integer NOT NULL, path character varying(255) NOT NULL, value character varying(255) NOT NULL, created_at timestamp without time zone DEFAULT now(), updated_at timestamp without time zone );


--
-- Name: configs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.configs_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;


--
-- Name: configs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.configs_id_seq OWNED BY public.configs.id;


--
-- Name: expense_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expense_categories ( id integer NOT NULL, name character varying(255) NOT NULL, created_at timestamp without time zone DEFAULT now(), updated_at timestamp without time zone DEFAULT now(), is_active boolean DEFAULT true );


--
-- Name: expense_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.expense_categories_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;


--
-- Name: expense_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.expense_categories_id_seq OWNED BY public.expense_categories.id;


--
-- Name: expense_category_recommendations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expense_category_recommendations ( id integer NOT NULL, word character varying, category_id integer, hit_count bigint, created_at timestamp without time zone DEFAULT now(), score integer DEFAULT 0 );


--
-- Name: expense_category_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.expense_category_recommendations_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;


--
-- Name: expense_category_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.expense_category_recommendations_id_seq OWNED BY public.expense_category_recommendations.id;


--
-- Name: expense_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expense_items ( subject text, amount double precision, transaction_type character varying(100), telegram_message_id bigint, created_at timestamp without time zone, updated_at timestamp without time zone, category_id integer, id integer NOT NULL );


--
-- Name: expense_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.expense_items_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;


--
-- Name: expense_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.expense_items_id_seq OWNED BY public.expense_items.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users ( telegram_username text NOT NULL, telegram_userid bigint NOT NULL, created_at timestamp without time zone DEFAULT now(), is_active boolean DEFAULT false, uuid character varying(255) NOT NULL );


--
-- Name: bot_chatcontexts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bot_chatcontexts ALTER COLUMN id SET DEFAULT nextval('public.bot_chatcontexts_id_seq'::regclass);


--
-- Name: configs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configs ALTER COLUMN id SET DEFAULT nextval('public.configs_id_seq'::regclass);


--
-- Name: expense_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_categories ALTER COLUMN id SET DEFAULT nextval('public.expense_categories_id_seq'::regclass);


--
-- Name: expense_category_recommendations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_category_recommendations ALTER COLUMN id SET DEFAULT nextval('public.expense_category_recommendations_id_seq'::regclass);


--
-- Name: expense_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_items ALTER COLUMN id SET DEFAULT nextval('public.expense_items_id_seq'::regclass);


--
-- Name: bot_chatcontexts bot_chatcontexts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bot_chatcontexts ADD CONSTRAINT bot_chatcontexts_pkey PRIMARY KEY (id);


--
-- Name: configs configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.configs ADD CONSTRAINT configs_pkey PRIMARY KEY (id);


--
-- Name: expense_categories expense_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_categories ADD CONSTRAINT expense_categories_pkey PRIMARY KEY (id);


--
-- Name: expense_category_recommendations expense_category_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_category_recommendations ADD CONSTRAINT expense_category_recommendations_pkey PRIMARY KEY (id);


--
-- Name: expense_items expense_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_items ADD CONSTRAINT expense_items_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ADD CONSTRAINT users_pkey PRIMARY KEY (uuid);


--
-- Name: users users_telegram_userid_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ADD CONSTRAINT users_telegram_userid_key UNIQUE (telegram_userid);


--
-- Name: users users_telegram_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ADD CONSTRAINT users_telegram_username_key UNIQUE (telegram_username);


--
-- Name: configs_path_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX configs_path_idx ON public.configs USING btree (path);


--
-- Name: expense_items_created_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX expense_items_created_at_idx ON public.expense_items USING btree (created_at);


--
-- Name: expense_items_updated_at_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX expense_items_updated_at_idx ON public.expense_items USING btree (updated_at);


--
-- PostgreSQL database dump complete
--


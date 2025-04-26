--
-- PostgreSQL database dump
--

-- Dumped from database version 15.11
-- Dumped by pg_dump version 15.11
-- Use the correct database
\c hems_db;

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bookings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bookings (
    id integer NOT NULL,
    room_number character varying NOT NULL,
    guest_name character varying NOT NULL,
    room_price double precision NOT NULL,
    arrival_date date NOT NULL,
    departure_date date NOT NULL,
    number_of_days integer NOT NULL,
    booking_cost double precision,
    booking_type character varying NOT NULL,
    phone_number character varying,
    status character varying,
    payment_status character varying,
    booking_date timestamp without time zone,
    is_checked_out boolean,
    cancellation_reason character varying,
    deleted boolean,
    created_by character varying NOT NULL
);


ALTER TABLE public.bookings OWNER TO postgres;

--
-- Name: bookings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bookings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bookings_id_seq OWNER TO postgres;

--
-- Name: bookings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bookings_id_seq OWNED BY public.bookings.id;


--
-- Name: event_payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_payments (
    id integer NOT NULL,
    event_id integer NOT NULL,
    organiser character varying NOT NULL,
    event_amount double precision NOT NULL,
    amount_paid double precision NOT NULL,
    discount_allowed double precision,
    balance_due double precision,
    payment_method character varying NOT NULL,
    payment_date date,
    payment_status character varying,
    created_by character varying NOT NULL
);


ALTER TABLE public.event_payments OWNER TO postgres;

--
-- Name: event_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.event_payments_id_seq OWNER TO postgres;

--
-- Name: event_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_payments_id_seq OWNED BY public.event_payments.id;


--
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    id integer NOT NULL,
    organizer character varying NOT NULL,
    title character varying NOT NULL,
    description character varying,
    start_datetime date NOT NULL,
    end_datetime date NOT NULL,
    event_amount double precision NOT NULL,
    caution_fee double precision NOT NULL,
    location character varying,
    phone_number character varying NOT NULL,
    address character varying NOT NULL,
    payment_status character varying,
    balance_due double precision NOT NULL,
    created_by character varying,
    created_at date DEFAULT now(),
    updated_at date DEFAULT now(),
    cancellation_reason character varying
);


ALTER TABLE public.events OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.events_id_seq OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- Name: license_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.license_keys (
    id integer NOT NULL,
    key character varying NOT NULL,
    is_active boolean,
    created_at timestamp without time zone,
    expiration_date timestamp without time zone NOT NULL
);


ALTER TABLE public.license_keys OWNER TO postgres;

--
-- Name: license_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.license_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.license_keys_id_seq OWNER TO postgres;

--
-- Name: license_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.license_keys_id_seq OWNED BY public.license_keys.id;


--
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    id integer NOT NULL,
    booking_id integer,
    room_number character varying,
    guest_name character varying,
    amount_paid double precision,
    discount_allowed double precision,
    balance_due double precision,
    payment_method character varying,
    payment_date timestamp without time zone,
    status character varying,
    created_by character varying NOT NULL
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.payments_id_seq OWNER TO postgres;

--
-- Name: payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_id_seq OWNED BY public.payments.id;


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    id integer NOT NULL,
    room_number character varying NOT NULL,
    room_type character varying(50),
    amount integer,
    status character varying(50)
);


ALTER TABLE public.rooms OWNER TO postgres;

--
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rooms_id_seq OWNER TO postgres;

--
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50),
    hashed_password character varying NOT NULL,
    role character varying(50)
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: bookings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings ALTER COLUMN id SET DEFAULT nextval('public.bookings_id_seq'::regclass);


--
-- Name: event_payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_payments ALTER COLUMN id SET DEFAULT nextval('public.event_payments_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- Name: license_keys id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.license_keys ALTER COLUMN id SET DEFAULT nextval('public.license_keys_id_seq'::regclass);


--
-- Name: payments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN id SET DEFAULT nextval('public.payments_id_seq'::regclass);


--
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: bookings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.bookings (id, room_number, guest_name, room_price, arrival_date, departure_date, number_of_days, booking_cost, booking_type, phone_number, status, payment_status, booking_date, is_checked_out, cancellation_reason, deleted, created_by) FROM stdin;
1	A1	John	20000	2025-02-25	2025-02-26	1	20000	checked-in	23323	checked-out	pending	2025-02-25 12:50:46.452572	f	\N	f	fcn
2	A2	Pat	20000	2025-02-25	2025-02-26	1	20000	checked-in	32323	checked-out	pending	2025-02-25 12:59:34.130536	f	\N	f	fcn
3	A3	Dan	20000	2025-02-25	2025-02-26	1	20000	checked-in	23	checked-out	pending	2025-02-25 13:05:39.508989	f	\N	f	fcn
4	A4	Fan	20000	2025-02-25	2025-02-26	1	20000	checked-in	43434	checked-out	pending	2025-02-25 13:14:10.325361	f	\N	f	fcn
5	A5	Henry	20000	2025-02-25	2025-02-26	1	20000	checked-in	32323	checked-out	pending	2025-02-25 13:14:59.741618	f	\N	f	fcn
6	A6	Stanley	20000	2025-02-25	2025-02-26	1	20000	checked-in	43434	checked-out	pending	2025-02-25 13:18:12.145556	f	\N	f	fcn
7	A7	oke	20000	2025-02-25	2025-02-26	1	20000	checked-in	434	checked-out	pending	2025-02-25 13:25:25.556399	f	\N	f	fcn
9	A2	pat	20000	2025-02-25	2025-02-26	1	20000	checked-in	34433	checked-in	pending	2025-02-25 13:28:10.976148	f	\N	f	fcn
8	A1	Dan	20000	2025-02-25	2025-02-26	1	20000	checked-in	43434	checked-in	payment completed	2025-02-25 13:27:38.964661	f	\N	f	fcn
10	A3	rerer	20000	2025-02-25	2025-02-26	1	20000	checked-in	erer	checked-in	payment completed	2025-02-25 13:41:21.690812	f	\N	f	fcn
15	A9	www	20000	2025-02-25	2025-02-26	1	20000	checked-in	wee	checked-in	pending	2025-02-25 14:51:58.028724	f	\N	f	fcn
11	A4	tytyty	20000	2025-02-25	2025-02-26	1	20000	checked-in	5334	checked-in	pending	2025-02-25 13:44:29.20279	f	\N	f	fcn
12	A5	ggg	20000	2025-02-25	2025-02-26	1	20000	checked-in	eerer	cancelled	pending	2025-02-25 13:55:55.388414	f	\N	t	fcn
13	A6	erereree	20000	2025-02-25	2025-02-26	1	20000	checked-in	33	cancelled	pending	2025-02-25 14:21:47.052467	f	\N	t	fcn
14	A8	erer	20000	2025-02-25	2025-02-26	1	20000	checked-in	ere	checked-in	payment completed	2025-02-25 14:26:41.217117	f	\N	f	fcn
16	A7	ffdd	20000	2025-02-25	2025-02-26	1	20000	checked-in	ere	checked-in	pending	2025-02-25 15:40:55.275066	f	\N	f	fcn
\.


--
-- Data for Name: event_payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_payments (id, event_id, organiser, event_amount, amount_paid, discount_allowed, balance_due, payment_method, payment_date, payment_status, created_by) FROM stdin;
1	1	oke	300000	200000	0	100000	Cash	2025-02-25	incomplete	fcn
\.


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.events (id, organizer, title, description, start_datetime, end_datetime, event_amount, caution_fee, location, phone_number, address, payment_status, balance_due, created_by, created_at, updated_at, cancellation_reason) FROM stdin;
1	oke	marriage	full time	2025-02-26	2025-02-26	300000	100000	Sapele	343434	fdfdf	cancelled	0	fcn	2025-02-25	2025-02-27	postpone
\.


--
-- Data for Name: license_keys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.license_keys (id, key, is_active, created_at, expiration_date) FROM stdin;
1	111	t	2025-02-25 12:49:00.431663	2026-02-25 12:49:00.41967
2	123	t	2025-02-26 09:31:09.931838	2026-02-26 09:31:09.927841
3	222	t	2025-02-27 08:36:31.816376	2026-02-27 08:36:31.792389
\.


--
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payments (id, booking_id, room_number, guest_name, amount_paid, discount_allowed, balance_due, payment_method, payment_date, status, created_by) FROM stdin;
1	8	A1	Dan	20000	0	0	Cash	2025-02-25 00:00:00	payment completed	fcn
2	10	A3	rerer	20000	0	0	Cash	2025-02-25 00:00:00	payment completed	fcn
4	11	A4	tytyty	20000	0	0	Cash	2025-02-25 00:00:00	voided	fcn
3	12	A5	ggg	20000	0	0	Cash	2025-02-25 00:00:00	voided	fcn
7	15	A9	www	20000	0	0	Cash	2025-02-25 00:00:00	voided	fcn
6	14	A8	erer	20000	0	0	Cash	2025-02-25 00:00:00	voided	fcn
5	11	A4	tytyty	20000	0	0	Cash	2025-02-25 00:00:00	voided	fcn
8	14	A8	erer	20000	0	0	Cash	2025-02-25 00:00:00	payment completed	fcn
\.


--
-- Data for Name: rooms; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rooms (id, room_number, room_type, amount, status) FROM stdin;
1	A1	Single	20000	checked-in
2	A2	Single	20000	checked-in
3	A3	Single	20000	checked-in
4	A4	Single	20000	checked-in
8	A8	Single	20000	checked-in
9	A9	Single	20000	checked-in
5	A5	Single	20000	available
6	A6	Single	20000	available
7	A7	Single	20000	checked-in
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, hashed_password, role) FROM stdin;
1	fcn	$2b$12$1WfW5f72lXtKxY2iXs0l7uVVYwRa5QXWVPn/K9MaY3UvQ7WjjIgES	admin
2	dan	$2b$12$SBZJOuFnyuo68gf9TSpvleS/rmV9aatFG0cWTIp8bPuAxVqjWegcO	user
\.


--
-- Name: bookings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.bookings_id_seq', 16, true);


--
-- Name: event_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_payments_id_seq', 1, true);


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.events_id_seq', 1, true);


--
-- Name: license_keys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.license_keys_id_seq', 3, true);


--
-- Name: payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_id_seq', 8, true);


--
-- Name: rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rooms_id_seq', 9, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: bookings bookings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_pkey PRIMARY KEY (id);


--
-- Name: event_payments event_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_payments
    ADD CONSTRAINT event_payments_pkey PRIMARY KEY (id);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: license_keys license_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.license_keys
    ADD CONSTRAINT license_keys_pkey PRIMARY KEY (id);


--
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (id);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- Name: rooms rooms_room_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_room_number_key UNIQUE (room_number);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_bookings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bookings_id ON public.bookings USING btree (id);


--
-- Name: ix_event_payments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_payments_id ON public.event_payments USING btree (id);


--
-- Name: ix_event_payments_organiser; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_payments_organiser ON public.event_payments USING btree (organiser);


--
-- Name: ix_events_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_id ON public.events USING btree (id);


--
-- Name: ix_license_keys_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_license_keys_id ON public.license_keys USING btree (id);


--
-- Name: ix_license_keys_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_license_keys_key ON public.license_keys USING btree (key);


--
-- Name: ix_payments_guest_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_guest_name ON public.payments USING btree (guest_name);


--
-- Name: ix_payments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_id ON public.payments USING btree (id);


--
-- Name: ix_payments_room_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_payments_room_number ON public.payments USING btree (room_number);


--
-- Name: ix_rooms_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_rooms_id ON public.rooms USING btree (id);


--
-- Name: bookings bookings_room_number_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bookings
    ADD CONSTRAINT bookings_room_number_fkey FOREIGN KEY (room_number) REFERENCES public.rooms(room_number) ON DELETE CASCADE;


--
-- Name: event_payments event_payments_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_payments
    ADD CONSTRAINT event_payments_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: payments payments_booking_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_booking_id_fkey FOREIGN KEY (booking_id) REFERENCES public.bookings(id);


--
-- PostgreSQL database dump complete
--


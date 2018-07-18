-- Adminer 4.6.3-dev PostgreSQL dump

\connect "d5g9l9blookc4p";

DROP TABLE IF EXISTS "check_ins";
CREATE TABLE "public"."check_ins" (
    "zip" character varying NOT NULL,
    "comment" character varying,
    "username" character varying NOT NULL
) WITH (oids = false);


DROP TABLE IF EXISTS "locations";
CREATE TABLE "public"."locations" (
    "zip" character varying NOT NULL,
    "city" character varying NOT NULL,
    "state" character varying NOT NULL,
    "latitude" numeric NOT NULL,
    "longitude" numeric NOT NULL,
    "population" integer NOT NULL,
    CONSTRAINT "locations_zip" PRIMARY KEY ("zip")
) WITH (oids = false);


DROP TABLE IF EXISTS "users";
CREATE TABLE "public"."users" (
    "username" character varying NOT NULL,
    "password" character varying NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("username")
) WITH (oids = false);


-- 2018-07-12 21:56:59.350369+00

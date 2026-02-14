-- =====================================================
-- EXTENSIONES POSTGRESQL
-- =====================================================
-- Ejecutar UNA VEZ al crear la base de datos

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Para UUID v7 (time-ordered)
-- https://github.com/fboulnois/pg_uuidv7
CREATE EXTENSION IF NOT EXISTS "pg_uuidv7" SCHEMA public VERSION "1.6";
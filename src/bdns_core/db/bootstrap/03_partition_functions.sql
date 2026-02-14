-- =====================================================
-- FUNCIONES DE PARTICIONADO DINÁMICO
-- =====================================================
-- Ejecutar UNA VEZ al crear la base de datos
-- Estas funciones son ESTÁTICAS, no cambian con el tiempo

CREATE OR REPLACE FUNCTION bdns.create_year_partition(year_param INTEGER)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    year_start DATE;
    year_end DATE;
    partition_name TEXT;
    subpartition_name TEXT;
    regimen TEXT;
BEGIN
    -- Calcular fechas límite
    year_start := make_date(year_param, 1, 1);
    year_end := make_date(year_param + 1, 1, 1);
    partition_name := 'concesion_' || year_param;
    
    -- Crear partición anual si no existe
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS bdns.%I PARTITION OF bdns.concesion
         FOR VALUES FROM (%L) TO (%L)
         PARTITION BY LIST (regimen_tipo_norm);',
        partition_name, year_start, year_end
    );
    
    -- Crear subparticiones por régimen
    FOR regimen IN SELECT unnest(ARRAY['minimis', 'ayuda_estado', 'ordinaria', 'desconocido'])
    LOOP
        subpartition_name := partition_name || '_' || regimen;
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS bdns.%I PARTITION OF bdns.%I
             FOR VALUES IN (%L);',
            subpartition_name, partition_name, regimen
        );
    END LOOP;
END;
$$;


CREATE OR REPLACE FUNCTION bdns.ensure_concesion_partition()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    year_val INTEGER;
BEGIN
    -- Extraer año de la fecha
    year_val := EXTRACT(YEAR FROM NEW.fecha_concesion);
    
    -- Crear partición si no existe
    PERFORM bdns.create_year_partition(year_val);
    
    RETURN NEW;
END;
$$;


CREATE OR REPLACE FUNCTION bdns.sync_regimen_tipo_norm()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    -- Sincronizar regimen_tipo_norm desde regimen_ayuda
    IF NEW.regimen_ayuda_id IS NOT NULL THEN
        SELECT descripcion_norm INTO NEW.regimen_tipo_norm
        FROM bdns.regimen_ayuda
        WHERE id = NEW.regimen_ayuda_id;
    ELSE
        NEW.regimen_tipo_norm := 'desconocido';
    END IF;
    
    RETURN NEW;
END;
$$;


-- Nota: Los triggers se aplican en la migración, no aquí
-- porque dependen de que la tabla exista
ALTER TABLE texttable ADD COLUMN path varchar;

DO $$
    DECLARE i integer;
    DECLARE pre_parent integer;
    DECLARE pre_path varchar;
    DECLARE row record;
    BEGIN
        pre_parent := -1;
        i := 1;
        pre_path := '';
        FOR row IN SELECT * FROM texttable ORDER BY parent_id NULLS FIRST, id
        LOOP
            IF row.parent_id IS NULL THEN
                UPDATE texttable SET path=i WHERE id=row.id;
                i := i + 1;
            ELSIF row.parent_id = pre_parent THEN
                UPDATE texttable SET path = CONCAT(pre_path, '.', i) WHERE id = row.id;
                i := i + 1;
            ELSE
                pre_parent := row.parent_id;
                SELECT path INTO pre_path FROM texttable WHERE id = row.parent_id;
                UPDATE texttable SET path = CONCAT(pre_path, '.', 1) WHERE id = row.id;
                i := 2;
            END IF;
        END LOOP;
    END;
$$;

ALTER TABLE texttable DROP COLUMN parent_id;
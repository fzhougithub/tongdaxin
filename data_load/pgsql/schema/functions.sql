CREATE OR REPLACE FUNCTION stock.calculate_pf_chart_pg(symbol_name text, step double precision DEFAULT NULL)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    history RECORD;
    buckets jsonb[] := '{}';
    current_mark char := 'X';  -- Start with uptrend
    current_low double precision;
    current_high double precision;
    current_volume double precision := 0;
    current_start_day date;
    price double precision;
    prev_price double precision;
    prev_high double precision;  -- Track previous bucket's high
    prev_low double precision;   -- Track previous bucket's low
    direction int := 1;  -- 1 for up, -1 for down
    box_size double precision;
    reversal_size int := 3;  -- Standard 3-box reversal
    min_steps int := 3;  -- Minimum steps for a new bar after reversal
BEGIN
    -- Determine step size if not provided
    IF step IS NULL THEN
        SELECT (MAX(c) - MIN(c)) / 50 INTO box_size
        FROM stock.stockhistory
        WHERE symbol = symbol_name;
    ELSE
        box_size := step;
    END IF;

    -- Initialize with the first record
    SELECT c, v, day INTO price, current_volume, current_start_day
    FROM stock.stockhistory
    WHERE symbol = symbol_name
    ORDER BY day ASC
    LIMIT 1;

    current_low := price;
    current_high := price;
    prev_high := price;
    prev_low := price;

    -- Process each price in history
    FOR history IN (
        SELECT c, v, day
        FROM stock.stockhistory
        WHERE symbol = symbol_name
        ORDER BY day ASC
    ) LOOP
        prev_price := price;
        price := history.c;
        current_volume := current_volume + history.v;

        -- Check if price movement continues in the same direction
        IF direction = 1 THEN  -- Uptrend
            IF price > current_high THEN
                current_high := price;
            ELSIF price < current_high - box_size * reversal_size THEN
                -- Reversal: End current bucket and start a downtrend
                buckets := array_append(buckets, jsonb_build_object(
                    'mark', 'X',
                    'low', current_low,
                    'high', current_high,
                    'volume', current_volume,
                    'start_day', current_start_day
                ));
                direction := -1;
                -- Start new O bar one step below the previous high
                current_high := current_high - box_size;  -- One step below previous high
                -- Ensure the new bar spans at least 3 steps
                current_low := current_high - box_size * min_steps;
                -- Adjust low if price is higher than the minimum required low
                IF price > current_low THEN
                    current_low := price;
                END IF;
                current_volume := history.v;
                current_start_day := history.day;
                current_mark := 'O';
                prev_high := current_high;
                prev_low := current_low;
            END IF;
        ELSE  -- Downtrend
            IF price < current_low THEN
                current_low := price;
            ELSIF price > current_low + box_size * reversal_size THEN
                -- Reversal: End current bucket and start an uptrend
                buckets := array_append(buckets, jsonb_build_object(
                    'mark', 'O',
                    'low', current_low,
                    'high', current_high,
                    'volume', current_volume,
                    'start_day', current_start_day
                ));
                direction := 1;
                -- Start new X bar one step above the previous low
                current_low := current_low + box_size;  -- One step above previous low
                -- Ensure the new bar spans at least 3 steps
                current_high := current_low + box_size * min_steps;
                -- Adjust high if price is lower than the minimum required high
                IF price < current_high THEN
                    current_high := price;
                END IF;
                current_volume := history.v;
                current_start_day := history.day;
                current_mark := 'X';
                prev_high := current_high;
                prev_low := current_low;
            END IF;
        END IF;
    END LOOP;

    -- Add the last bucket
    buckets := array_append(buckets, jsonb_build_object(
        'mark', current_mark,
        'low', current_low,
        'high', current_high,
        'volume', current_volume,
        'start_day', current_start_day
    ));

    RETURN array_to_json(buckets)::jsonb;
END;
$$;

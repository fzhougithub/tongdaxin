CREATE OR REPLACE FUNCTION calculate_pf_chart_pg(symbol_name TEXT, step FLOAT DEFAULT NULL)
RETURNS JSONB AS $$
DECLARE
    history JSONB;
    max_price FLOAT;
    min_price FLOAT;
    price_range FLOAT;
    computed_step FLOAT;
    reversal_threshold FLOAT;
    buckets JSONB DEFAULT '[]'::JSONB;
    current_bucket JSONB;
    record JSONB;
    price FLOAT;
    volume FLOAT;
    bucket_idx INT;
BEGIN
    -- Fetch stock history for the given symbol
    SELECT jsonb_agg(jsonb_build_object('day', day, 'c', c, 'v', v) order by day)
    INTO history
    FROM stock.stockhistory
    WHERE stockhistory.symbol = symbol_name;

    -- Return empty array if no history found
    IF history IS NULL THEN
        RETURN '[]'::JSONB;
    END IF;

    -- Calculate max, min prices
    SELECT MAX((r->>'c')::FLOAT), MIN((r->>'c')::FLOAT)
    INTO max_price, min_price
    FROM jsonb_array_elements(history) AS r;

    price_range := max_price - min_price;

    -- Determine step size
    IF step IS NULL OR step <= 0 THEN
        computed_step := price_range / 50;
        IF computed_step = 0 THEN
            computed_step := 1.0;
        END IF;
    ELSE
        computed_step := step;
    END IF;

    -- Define reversal threshold
    reversal_threshold := 3 * computed_step;

    -- Iterate through history and compute Point & Figure chart
    FOR record IN SELECT * FROM jsonb_array_elements(history) LOOP
        price := (record->>'c')::FLOAT;
        volume := (record->>'v')::FLOAT;

        IF jsonb_array_length(buckets) = 0 THEN
            bucket_idx := FLOOR((price - min_price) / computed_step);
            current_bucket := jsonb_build_object(
                'mark', 'X',
                'high', price,
                'low', price,
                'volume', volume,
                'start_day', record->>'day'
            );
            buckets := jsonb_insert(buckets, '{0}', current_bucket);
        ELSE
            -- Process according to last bucket mark
            IF (current_bucket->>'mark') = 'X' THEN
                IF price > (current_bucket->>'high')::FLOAT THEN
                    current_bucket := current_bucket || jsonb_build_object(
                        'high', price,
                        'volume', (current_bucket->>'volume')::FLOAT + volume
                    );
                ELSIF price <= (current_bucket->>'high')::FLOAT - reversal_threshold THEN
                    current_bucket := jsonb_build_object(
                        'mark', 'O',
                        'high', price,
                        'low', price,
                        'volume', volume,
                        'start_day', record->>'day'
                    );
                    buckets := buckets || current_bucket;
                ELSE
                    current_bucket := current_bucket || jsonb_build_object(
                        'volume', (current_bucket->>'volume')::FLOAT + volume,
                        'low', LEAST((current_bucket->>'low')::FLOAT, price)
                    );
                END IF;
            ELSIF (current_bucket->>'mark') = 'O' THEN
                IF price < (current_bucket->>'low')::FLOAT THEN
                    current_bucket := current_bucket || jsonb_build_object(
                        'low', price,
                        'volume', (current_bucket->>'volume')::FLOAT + volume
                    );
                ELSIF price >= (current_bucket->>'low')::FLOAT + reversal_threshold THEN
                    current_bucket := jsonb_build_object(
                        'mark', 'X',
                        'high', price,
                        'low', price,
                        'volume', volume,
                        'start_day', record->>'day'
                    );
                    buckets := buckets || current_bucket;
                ELSE
                    current_bucket := current_bucket || jsonb_build_object(
                        'volume', (current_bucket->>'volume')::FLOAT + volume,
                        'high', GREATEST((current_bucket->>'high')::FLOAT, price)
                    );
                END IF;
            END IF;
        END IF;
    END LOOP;

    RETURN buckets;
END;
$$ LANGUAGE plpgsql;

-- Query to generate Multi-measure TABLE
WITH pivot AS
(
	SELECT  meter_id
	       ,time
	       ,CASE WHEN measure_name = 'kwh' THEN measure_value::double END     AS kwh
	       ,CASE WHEN measure_name = 'rssi' THEN measure_value::bigint END    AS rssi
	       ,CASE WHEN measure_name = 'pf' THEN measure_value::double END      AS pf
	       ,CASE WHEN measure_name = 'voltage' THEN measure_value::double END AS voltage
	FROM "dpu"."customer-meter-data"
	-- WHERE time BETWEEN bin(now(), 5m) - 1h AND now()
	WHERE time BETWEEN ('2022-09-01 00:00:00.00000000') AND ('2022-09-30 23:00:00.00000000') 
)
SELECT  meter_id
       ,time
       ,MAX("kwh")       AS "kwh"
       ,MAX("rssi")      AS "rssi"
       ,MAX("pf")        AS "pf"
       ,MAX("voltage")   AS "voltage"
       ,'Customer-Meter' AS "measure_name"
FROM pivot
GROUP BY  meter_id
         ,time
-- Query to generate Correlation
WITH cud_result AS
(
	SELECT  meter_id
	       ,INTERPOLATE_LINEAR( CREATE_TIME_SERIES(time,kwh),SEQUENCE(MIN('2022-09-01 04:00:00.000000000'),MAX('2022-09-30 23:00:00.000000000'),10m)) AS result
	FROM "dpu"."customer-meter-data-multi"
	WHERE measure_name = 'Customer-Meter'
	AND time BETWEEN ('2022-09-01 04:00:00.000000000') AND ('2022-09-30 23:00:00.000000000')
	GROUP BY  meter_id
	         ,measure_name
), hmd_result AS
(
	SELECT  harmonic_meter_series_id
	       ,INTERPOLATE_LINEAR( CREATE_TIME_SERIES(time,measure_value::double),SEQUENCE(MIN('2022-09-01 04:00:00.000000000'),MAX('2022-09-30 23:00:00.000000000'),10m)) AS result
	FROM "dpu"."harmonic-meter-data"
	WHERE measure_name = 'harmonics_value'
	AND time BETWEEN ('2022-09-01 04:00:00.000000000') AND ('2022-09-30 23:00:00.000000000')
	GROUP BY  harmonic_meter_series_id
	         ,measure_name
)
SELECT  cud_result.meter_id
       ,hmd_result.harmonic_meter_series_id
       ,correlate_pearson(cud_result.result,hmd_result.result) AS result
FROM cud_result, hmd_result
ORDER BY 1, 2
with pivot as (
select meter_id,time,
case when measure_name = 'current' then measure_value::double end as current,
case when measure_name = 'rssi' then measure_value::double end as rssi,
case when measure_name = 'pf' then measure_value::double end as pf,
case when measure_name = 'voltage' then measure_value::double end as voltage
from "DPU"."customer_single_table"
where time between '2023-07-18 00:00:22.631000000' and '2023-07-19 22:00:00.631000000'
)
select meter_id,time,
max("current") as "current",
max("rssi") as "rssi",
max("pf") as "pf",
max("voltage") as "voltage"
from pivot
group by meter_id, time
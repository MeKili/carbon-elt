{{ config(
    materialized='table'
) }}

select
    date(valid_from) as intensity_date,
    region_code,
    round(avg(cast(actual as float)), 1) as avg_actual_intensity,
    round(avg(cast(forecast as float)), 1) as avg_forecast_intensity,
    count(*) as reading_count
from {{ ref('stg_regional_intensity') }}
where actual is not null
group by date(valid_from), region_code
order by intensity_date desc, region_code

{{ config(
    materialized='table'
) }}

select
    date(valid_from) as intensity_date,
    index,
    round(100.0 * count(*) / sum(count(*)) over (partition by date(valid_from)), 1) as share_percent
from {{ ref('stg_national_intensity') }}
where index is not null and index != 'unknown'
group by intensity_date, index
order by intensity_date desc, share_percent desc

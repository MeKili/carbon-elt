{{ config(
    materialized='view'
) }}

select
    valid_from,
    valid_to,
    fuel_type,
    percentage
from {{ source('raw', 'raw_generation') }}
order by valid_from, fuel_type

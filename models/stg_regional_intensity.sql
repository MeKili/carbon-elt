select
    valid_from,
    valid_to,
    region_code,
    forecast,
    actual,
    index
from {{ source('raw', 'raw_regional_intensity') }}

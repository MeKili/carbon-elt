-- Validate that all loaded regional data has valid UK region codes
select region_code
from {{ source('raw', 'raw_regional_intensity') }}
where region_code not in (
    'SE', 'SW', 'E', 'EM', 'WM', 'YH', 'N', 'NW', 'NE', 'EA'
)

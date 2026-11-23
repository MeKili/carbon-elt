-- Validate that carbon intensity values are within realistic ranges (gCO₂/kWh)
select *
from {{ source('raw', 'raw_national_intensity') }}
where
    actual is not null and (actual < 0 or actual > 1000)
    or forecast is not null and (forecast < 0 or forecast > 1000)

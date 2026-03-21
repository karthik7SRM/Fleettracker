CREATE TABLE trucks (
    fleet_id VARCHAR(50) PRIMARY KEY,

    truck_model VARCHAR(100),
    manufacturer VARCHAR(100),
    driver_name VARCHAR(100),

    fuel_loaded_liters FLOAT,
    fuel_consumed_liters FLOAT,

    departure_terminal VARCHAR(100),
    arrival_terminal VARCHAR(100),

    trip_duration_hrs FLOAT,
    monthly_dist_km FLOAT,
    payload_kg FLOAT,

    weather VARCHAR(50),

    avg_speed_kmh FLOAT,
    road_elevation_m FLOAT,

    engine_health VARCHAR(50),   -- e.g., Good / Warning / Critical
    last_maint DATE,
    maint_cost DECIMAL(10,2),

    co2_emissions_kg FLOAT
);

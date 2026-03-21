CREATE TABLE ships (
    FleetID VARCHAR(50) PRIMARY KEY,
    ShipModel VARCHAR(100),
    Manufacturer VARCHAR(100),
    ShipCaptain VARCHAR(100),

    FuelLoadedLiters FLOAT,
    FuelConsumedLiters FLOAT,

    DeparturePort VARCHAR(100),
    ArrivalPort VARCHAR(100),

    VoyageDuration FLOAT,
    MonthlyDistanceKM FLOAT,
    PayloadWeight FLOAT,

    WeatherCondition VARCHAR(50),

    AvgSpeed FLOAT,
    SeaLevelDepth FLOAT
);

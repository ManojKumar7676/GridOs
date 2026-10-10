"""
Accenture GridOS™ - Core Physical Portfolio & SCADA Domain Models
Production Cyber-Physical Asset Registry for Utility-Scale Balancing Authorities.
Directly implements Problem Statement 4: Utilities – Renewable Energy Orchestrator.
Compliant with IEC 61850 / IEEE 1547 / NERC BAL-001 Standards.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class AssetStatus(str, Enum):
    OPERATIONAL = "OPERATIONAL"
    DERATED = "DERATED"
    MAINTENANCE = "MAINTENANCE"
    TRIPPED = "TRIPPED"

class MaintenancePriority(str, Enum):
    NONE = "NONE"
    ROUTINE = "ROUTINE"
    URGENT = "URGENT"
    SCHEDULED_OFFPEAK = "SCHEDULED_OFFPEAK"

class SolarFarmModel(BaseModel):
    id: str = Field(..., description="SCADA Asset ID")
    name: str = Field(..., description="Plant Name")
    location: str = Field("Regional Solar Basin", description="Geographic Location")
    capacity_mw: float = Field(..., description="Nameplate Peak Capacity (MW)")
    current_output_mw: float = Field(0.0, description="Real-Time Generation (MW)")
    cloud_attenuation_factor: float = Field(1.0, description="Solar Irradiance Derate Factor (0.0 - 1.0)")
    status: AssetStatus = Field(AssetStatus.OPERATIONAL, description="Operational Health Status")
    inverter_temperature_c: float = Field(42.0, description="Inverter Core Temperature (°C)")
    coord_x: int = Field(100, description="Radar Grid Coordinate X (0-500)")
    coord_y: int = Field(150, description="Radar Grid Coordinate Y (0-380)")
    iec61850_tag: str = Field("SOL_MMXU1", description="IEC 61850 Logical Node Tag")
    power_factor: float = Field(0.98, description="Inverter AC Power Factor")
    is_available: bool = Field(True, description="Online Availability Flag")
    maintenance_status: MaintenancePriority = Field(MaintenancePriority.NONE, description="Maintenance Schedule")

class WindFarmModel(BaseModel):
    id: str = Field(..., description="SCADA Asset ID")
    name: str = Field(..., description="Plant Name")
    location: str = Field("Coastal & Highland Ridge", description="Geographic Location")
    capacity_mw: float = Field(..., description="Nameplate Peak Capacity (MW)")
    current_output_mw: float = Field(0.0, description="Real-Time Generation (MW)")
    wind_speed_mps: float = Field(8.5, description="Anemometer Wind Speed (m/s)")
    gust_speed_mps: float = Field(11.0, description="Peak Gust Speed (m/s)")
    cut_in_speed: float = Field(3.0, description="Cut-In Speed (m/s)")
    cut_out_speed: float = Field(25.0, description="Storm Safety Cut-Out Speed (m/s)")
    status: AssetStatus = Field(AssetStatus.OPERATIONAL, description="Operational Health Status")
    turbine_vibration_mm_s: float = Field(1.8, description="Drivetrain Vibration Telemetry (mm/s)")
    coord_x: int = Field(380, description="Radar Grid Coordinate X (0-500)")
    coord_y: int = Field(200, description="Radar Grid Coordinate Y (0-380)")
    iec61850_tag: str = Field("WND_MMXU1", description="IEC 61850 Logical Node Tag")
    power_factor: float = Field(0.95, description="Turbine Converter Power Factor")
    is_available: bool = Field(True, description="Online Availability Flag")
    maintenance_status: MaintenancePriority = Field(MaintenancePriority.NONE, description="Maintenance Schedule")

class BESSModel(BaseModel):
    id: str = Field(..., description="SCADA Asset ID")
    name: str = Field(..., description="Battery Facility Name")
    power_rating_mw: float = Field(..., description="Continuous Power Rating (MW)")
    energy_capacity_mwh: float = Field(..., description="Total Energy Storage Capacity (MWh)")
    current_soc_pct: float = Field(..., description="State of Charge (0 - 100%)")
    min_soc_pct: float = Field(10.0, description="Minimum Safety Reserve Threshold (%)")
    max_soc_pct: float = Field(95.0, description="Maximum Charge Buffer Ceiling (%)")
    roundtrip_efficiency: float = Field(0.92, description="Roundtrip AC-to-AC Efficiency")
    degradation_cost_per_mwh: float = Field(14.0, description="Cell Degradation Wear Cost ($/MWh)")
    status: AssetStatus = Field(AssetStatus.OPERATIONAL, description="Operational Health Status")
    current_flow_mw: float = Field(0.0, description="Current Power Flow (+Discharge / -Charge)")
    chemistry: str = Field("LFP (Lithium Iron Phosphate)", description="Cell Chemistry")
    c_rate: float = Field(0.25, description="Continuous C-Rate")
    cell_temperature_c: float = Field(28.5, description="Battery Pack Temperature (°C)")
    iec61850_tag: str = Field("BAT_ZBAT1", description="IEC 61850 Logical Node Tag")
    is_available: bool = Field(True, description="Online Availability Flag")
    maintenance_status: MaintenancePriority = Field(MaintenancePriority.NONE, description="Maintenance Schedule")

    @property
    def current_energy_mwh(self) -> float:
        return (self.current_soc_pct / 100.0) * self.energy_capacity_mwh

class IndustrialConsumerModel(BaseModel):
    id: str = Field(..., description="Consumer SCADA ID")
    name: str = Field(..., description="Facility Descriptor")
    facility_type: str = Field("Heavy Industry", description="Category")
    base_load_mw: float = Field(..., description="Non-Curtailable Baseload (MW)")
    flexible_shiftable_mw: float = Field(..., description="Deferrable Process Load (MW)")
    interruptible_mw: float = Field(..., description="Curtailable Demand Response Block (MW)")
    dr_incentive_rate_mwh: float = Field(..., description="Contracted DR Compensation Rate ($/MWh)")
    current_demand_mw: float = Field(0.0, description="Current Demand (MW)")
    is_dr_triggered: bool = Field(False, description="Whether DR Curtailment Is Active")
    iec61850_tag: str = Field("IND_MMXU1", description="IEC 61850 Logical Node Tag")

class GridIntertieModel(BaseModel):
    intertie_id: str = Field("TIE-REGIONAL-500KV", description="Interconnection Identifier")
    substation_name: str = Field("Northwest 500kV Bulk Transmission Intertie", description="Substation Name")
    max_export_mw: float = Field(200.0, description="Maximum Transmission Export Flow (MW)")
    max_import_mw: float = Field(150.0, description="Maximum Transmission Import Flow (MW)")
    current_frequency_hz: float = Field(50.00, description="Grid Operating Frequency (Hz)")
    grid_carbon_intensity_kg_per_mwh: float = Field(480.0, description="Marginal Fossil Carbon Factor (kg CO2/MWh)")
    transmission_congested: bool = Field(False, description="Thermal Line Congestion Flag")
    line_utilization_pct: float = Field(42.5, description="Thermal Loading (%)")
    voltage_kv: float = Field(500.0, description="Busbar Voltage (kV)")
    iec61850_tag: str = Field("TIE_MMXU1", description="IEC 61850 Logical Node Tag")

class MarketStateModel(BaseModel):
    spot_price_per_mwh: float = Field(45.0, description="Real-Time Wholesale Spot LMP ($/MWh)")
    projected_price_next_hour: float = Field(52.0, description="Day-Ahead / Forward Projected Price ($/MWh)")
    carbon_credit_price_per_ton: float = Field(40.0, description="Carbon Offset Credit Price ($/ton CO2)")
    dr_penalty_rate_mwh: float = Field(20.0, description="Unserved Energy Penalty Rate ($/MWh)")
    market_operator: str = Field("Regional Transmission Organization (RTO/ISO)", description="Market Authority")

class UtilityPortfolioState(BaseModel):
    solar_farms: List[SolarFarmModel] = Field(default_factory=lambda: [
        SolarFarmModel(id="SOL-01", name="Solar Alpha (Desert Plains)", capacity_mw=50.0, coord_x=90, coord_y=100, iec61850_tag="SOL_01_MMXU1"),
        SolarFarmModel(id="SOL-02", name="Solar Beta (Sun Valley)", capacity_mw=40.0, coord_x=140, coord_y=180, iec61850_tag="SOL_02_MMXU1"),
        SolarFarmModel(id="SOL-03", name="Solar Gamma (Highland Ridge)", capacity_mw=60.0, coord_x=210, coord_y=110, iec61850_tag="SOL_03_MMXU1"),
        SolarFarmModel(id="SOL-04", name="Solar Delta (Golden Fields)", capacity_mw=35.0, coord_x=110, coord_y=270, iec61850_tag="SOL_04_MMXU1"),
        SolarFarmModel(id="SOL-05", name="Solar Epsilon (Coastal Basin)", capacity_mw=45.0, coord_x=180, coord_y=310, iec61850_tag="SOL_05_MMXU1"),
    ])
    wind_farms: List[WindFarmModel] = Field(default_factory=lambda: [
        WindFarmModel(id="WND-01", name="Wind North (Breeze Pass)", capacity_mw=80.0, coord_x=370, coord_y=90, iec61850_tag="WND_01_MMXU1"),
        WindFarmModel(id="WND-02", name="Wind Coastal (Ocean View)", capacity_mw=100.0, coord_x=420, coord_y=210, iec61850_tag="WND_02_MMXU1"),
        WindFarmModel(id="WND-03", name="Wind Highland (Gale Crest)", capacity_mw=70.0, coord_x=340, coord_y=300, iec61850_tag="WND_03_MMXU1"),
    ])
    bess_systems: List[BESSModel] = Field(default_factory=lambda: [
        BESSModel(
            id="BESS-01",
            name="Iron-Phosphate Bulk Storage",
            power_rating_mw=100.0,
            energy_capacity_mwh=400.0,
            current_soc_pct=65.0,
            roundtrip_efficiency=0.92,
            degradation_cost_per_mwh=12.0,
            chemistry="LFP (Lithium Iron Phosphate)",
            c_rate=0.25,
            iec61850_tag="BESS_01_ZBAT1"
        ),
        BESSModel(
            id="BESS-02",
            name="Lithium-Titanate Peaker Unit",
            power_rating_mw=50.0,
            energy_capacity_mwh=100.0,
            current_soc_pct=80.0,
            roundtrip_efficiency=0.96,
            degradation_cost_per_mwh=18.0,
            chemistry="LTO (Lithium Titanate Fast Peaker)",
            c_rate=0.50,
            iec61850_tag="BESS_02_ZBAT1"
        ),
    ])
    industrial_consumers: List[IndustrialConsumerModel] = Field(default_factory=lambda: [
        IndustrialConsumerModel(id="IND-01", name="MegaTech Electric Smelter", facility_type="Metallurgical Smelter", base_load_mw=70.0, flexible_shiftable_mw=15.0, interruptible_mw=25.0, dr_incentive_rate_mwh=65.0, iec61850_tag="IND_01_MMXU1"),
        IndustrialConsumerModel(id="IND-02", name="Apex Clean Hydrogen Facility", facility_type="PEM Electrolyzer", base_load_mw=45.0, flexible_shiftable_mw=25.0, interruptible_mw=10.0, dr_incentive_rate_mwh=50.0, iec61850_tag="IND_02_MMXU1"),
        IndustrialConsumerModel(id="IND-03", name="Metro Cold Chain Terminal", facility_type="Refrigerated Logistics", base_load_mw=35.0, flexible_shiftable_mw=10.0, interruptible_mw=15.0, dr_incentive_rate_mwh=70.0, iec61850_tag="IND_03_MMXU1"),
    ])
    grid: GridIntertieModel = Field(default_factory=GridIntertieModel)
    market: MarketStateModel = Field(default_factory=MarketStateModel)

    @property
    def total_solar_capacity_mw(self) -> float:
        return sum(s.capacity_mw for s in self.solar_farms)

    @property
    def total_wind_capacity_mw(self) -> float:
        return sum(w.capacity_mw for w in self.wind_farms)

    @property
    def total_bess_power_capacity_mw(self) -> float:
        return sum(b.power_rating_mw for b in self.bess_systems)

    @property
    def total_bess_energy_capacity_mwh(self) -> float:
        return sum(b.energy_capacity_mwh for b in self.bess_systems)

    @property
    def total_industrial_baseload_mw(self) -> float:
        return sum(ind.base_load_mw for ind in self.industrial_consumers)

import time
import random
from typing import Dict, Any

class TelemetryManager:
    def __init__(self):
        self.last_update = time.time()
        self._initialize_metrics()

    def _initialize_metrics(self):
        self.metrics = {
            "brewing": {
                "active_fermenters": 12,
                "current_batch": "EVR-2026-0814-A",
                "avg_fermentation_temp_c": 10.5,
                "target_temp_c": 10.5,
                "diacetyl_ppm": 0.018,
                "lager_spec_status": "Optimal",
                "bright_beer_dissolved_o2_ppb": 13.8
            },
            "production": {
                "line_1_can_hl_shift": 2000,
                "line_1_can_target_hl": 2000,
                "line_3_can_hl_shift": 1800,
                "line_3_can_target_hl": 1800,
                "line_4_bottle_bpm": 1000,
                "line_4_bottle_target_bpm": 1000,
                "line_4_bottle_hl_shift": 1020,
                "line_4_target_range_hl": "800 - 1,200 hL",
                "total_shift_volume_hl": 4820,
                "overall_oee_percent": 87.2,
                "active_shift": "Shift 1 - Day (8 hrs)",
                "micro_stoppages_last_24h": 1,
                "line_status": "RUNNING_OPTIMAL"
            },
            "quality": {
                "finished_abv_percent": 5.02,
                "target_abv": 5.0,
                "bitterness_ibu": 12.1,
                "bright_beer_do_ppb": 13.8,
                "micro_cfu_count": 0,
                "can_seam_overlap_percent": 58.4,
                "can_seam_tightness_percent": 96.5,
                "ebi_optical_rejections_24h": 4,
                "active_qa_holds": 1,
                "sensory_panel_status": "Passed (Zero Off-Flavor)"
            },
            "logistics": {
                "active_fleet_trucks": 42,
                "cold_chain_compliance_rate": 99.4,
                "avg_transit_temp_c": 0.8,
                "on_time_in_full_otif_percent": 98.6,
                "keg_recycling_turnaround_days": 19.8,
                "active_weather_alerts": 0
            },
            "administration": {
                "water_to_beer_ratio_l_l": 2.08,
                "renewable_power_percent": 94.5,
                "landfill_diversion_percent": 99.3,
                "active_sap_pos_pending": 14,
                "ytd_esg_scorecard": "Tier 1 - On Track"
            },
            "hr_compliance": {
                "days_without_lost_time_injury": 412,
                "whmis_compliance_audit_score": 99.1,
                "active_plant_headcount": 348,
                "active_shift_name": "Shift 1 - Day (07:00 - 15:00)"
            }
        }

    def get_live_telemetry(self) -> Dict[str, Any]:
        # Micro-fluctuations simulating real SCADA streaming
        self.metrics["brewing"]["avg_fermentation_temp_c"] = round(10.5 + random.uniform(-0.2, 0.3), 2)
        self.metrics["brewing"]["bright_beer_dissolved_o2_ppb"] = round(13.8 + random.uniform(-0.6, 0.8), 1)

        # Line 1: Can ~2,000 hL / 8hrs
        l1 = int(2000 + random.randint(-40, 45))
        # Line 3: Can ~1,800 hL / 8hrs
        l3 = int(1800 + random.randint(-35, 40))
        # Line 4: Bottle ~1,000 bpm & 800-1,200 hL / 8hrs
        l4_bpm = int(1000 + random.randint(-25, 20))
        l4_hl = int(1020 + random.randint(-50, 60))

        self.metrics["production"]["line_1_can_hl_shift"] = l1
        self.metrics["production"]["line_3_can_hl_shift"] = l3
        self.metrics["production"]["line_4_bottle_bpm"] = l4_bpm
        self.metrics["production"]["line_4_bottle_hl_shift"] = l4_hl
        self.metrics["production"]["total_shift_volume_hl"] = l1 + l3 + l4_hl
        self.metrics["production"]["overall_oee_percent"] = round(87.0 + random.uniform(-0.6, 1.0), 1)

        # Quality metrics
        self.metrics["quality"]["finished_abv_percent"] = round(5.0 + random.uniform(-0.04, 0.05), 2)
        self.metrics["quality"]["bitterness_ibu"] = round(12.0 + random.uniform(-0.3, 0.4), 1)
        self.metrics["quality"]["bright_beer_do_ppb"] = self.metrics["brewing"]["bright_beer_dissolved_o2_ppb"]
        self.metrics["quality"]["can_seam_overlap_percent"] = round(58.0 + random.uniform(-1.0, 1.5), 1)

        self.metrics["logistics"]["avg_transit_temp_c"] = round(0.6 + random.uniform(-0.3, 0.4), 1)
        
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S EST"),
            "data": self.metrics
        }

    def update_telemetry_metric(self, department: str, key: str, value: Any) -> bool:
        dept = department.lower()
        if dept in self.metrics:
            self.metrics[dept][key] = value
            return True
        return False

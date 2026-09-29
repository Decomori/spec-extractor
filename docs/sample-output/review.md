# Specification review

**Structure validated; source truth still requires human/agent review.**

| Product / variant | Field | Status | Raw | Value | Unit | Evidence |
|---|---|---|---|---|---|---|
| EXAMPLE-ADAPTER-01 / EU | input_voltage | sourced | 100–240 V AC, 50/60 Hz | 100–240 V AC, 50/60 Hz |  | [{"source_id": "s1", "locator": "line 4", "quote": "Input: 100–240 V AC, 50/60 Hz"}] |
| EXAMPLE-ADAPTER-01 / EU | rated_power | conflict | 65 W max / 60 W max |  | W | [] |
| EXAMPLE-ADAPTER-01 / EU | dimensions | sourced | 30 × 45 × 60 mm | 30 × 45 × 60 | mm | [{"source_id": "s1", "locator": "line 6", "quote": "Dimensions: 30 × 45 × 60 mm (axis order not stated)"}] |
| EXAMPLE-ADAPTER-01 / EU | weight | missing |  |  |  | [] |

## Needs review

- EXAMPLE-ADAPTER-01 / EU / rated_power: conflict; Do not select a candidate without verifying the applicable revision.
  Candidates: [{"raw_value": "65 W max", "value": "65 max", "unit": "W", "evidence": [{"source_id": "s1", "locator": "line 5", "quote": "Output power: 65 W max"}]}, {"raw_value": "60 W max", "value": "60 max", "unit": "W", "evidence": [{"source_id": "s1", "locator": "line 7", "quote": "output power as 60 W max"}]}]
- EXAMPLE-ADAPTER-01 / EU / weight: missing; No weight value in inspected source.

## Source inventory

- s1: sample-source.txt (text)

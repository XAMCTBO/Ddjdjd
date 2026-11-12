"""OBD Reader agent - turns raw ELM327 responses into structured values.

Deliberately deterministic (no LLM): byte decoding must be exact. Handles
  * spaces on/off (ATS0/ATS1) and headers off (ATH0)
  * ISO-TP multi-frame CAN responses ("014" length line + "0:" "1:" frames)
  * responses from several ECUs at once
  * Mode 01 live PIDs + supported-PID bitmaps, Mode 01 PID 01 readiness monitors
  * Mode 02 freeze frames, Mode 03/07/0A DTC lists, Mode 09 VIN
  * ELM327 protocol numbers (ATDPN) and adapter identification (ATI)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

HEX = re.compile(r"^[0-9A-Fa-f]+$")
ELM_NOISE = ("SEARCHING", "BUS INIT", "OK", "STOPPED", "CAN ERROR", "BUFFER FULL",
             "?", "ELM327", "BUS BUSY", "FB ERROR", "DATA ERROR")
ELM_NO_DATA = ("NO DATA", "UNABLE TO CONNECT", "ERROR", "<RX ERROR")

PROTOCOLS = {
    "0": "Automatic", "1": "SAE J1850 PWM (41.6 kbaud)", "2": "SAE J1850 VPW (10.4 kbaud)",
    "3": "ISO 9141-2 (5 baud init)", "4": "ISO 14230-4 KWP (5 baud init)",
    "5": "ISO 14230-4 KWP (fast init)", "6": "ISO 15765-4 CAN (11 bit, 500 kbaud)",
    "7": "ISO 15765-4 CAN (29 bit, 500 kbaud)", "8": "ISO 15765-4 CAN (11 bit, 250 kbaud)",
    "9": "ISO 15765-4 CAN (29 bit, 250 kbaud)", "A": "SAE J1939 CAN (29 bit, 250 kbaud)",
}


# ---------------------------------------------------------------- raw parsing
def frames(raw: str) -> list[list[int]]:
    """Split one ELM response into per-message byte lists.

    Multi-frame (ISO-TP) messages are reassembled into a single list.
    """
    if raw is None:
        return []
    text = raw.replace(">", "\n").replace("\r", "\n")
    out: list[list[int]] = []
    current_mf: list[int] | None = None
    mf_len = 0
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        up = line.upper()
        if any(up.startswith(n) for n in ELM_NO_DATA):
            continue
        if any(up.startswith(n) for n in ELM_NOISE):
            # "SEARCHING..." can be glued to data on some clones
            up = re.sub(r"^(SEARCHING\.\.\.|BUS INIT:?\s*\.*(OK)?)", "", up).strip()
            if not up:
                continue
        compact = up.replace(" ", "")
        # ISO-TP length header line, e.g. "014"
        if re.fullmatch(r"[0-9A-F]{3}", compact):
            if current_mf:
                out.append(current_mf[:mf_len] if mf_len else current_mf)
            current_mf, mf_len = [], int(compact, 16)
            continue
        m = re.match(r"^([0-9A-F]):\s*(.*)$", up)
        if m and current_mf is not None:
            data = m.group(2).replace(" ", "")
            if HEX.match(data):
                current_mf.extend(_bytes(data))
            continue
        if not HEX.match(compact) or len(compact) % 2:
            continue
        out.append(_bytes(compact))
    if current_mf:
        out.append(current_mf[:mf_len] if mf_len else current_mf)
    return out


def _bytes(compact: str) -> list[int]:
    return [int(compact[i:i + 2], 16) for i in range(0, len(compact), 2)]


# ---------------------------------------------------------------- PID table
@dataclass(frozen=True)
class Pid:
    pid: int
    key: str
    name: str
    unit: str
    nbytes: int
    calc: Callable[[list[int]], float | int | str]


def _u16(b):
    return b[0] * 256 + b[1]


def _trim(x):
    return round((x - 128) * 100 / 128, 1)


def _pct(x):
    return round(x * 100 / 255, 1)


FUEL_STATUS = {1: "open loop (cold)", 2: "closed loop", 4: "open loop (load/decel)",
               8: "open loop (fault)", 16: "closed loop (O2 fault)"}

PID_LIST = [
    Pid(0x04, "load", "Calculated engine load", "%", 1, lambda b: _pct(b[0])),
    Pid(0x05, "coolant", "Coolant temperature", "°C", 1, lambda b: b[0] - 40),
    Pid(0x06, "stft1", "Short term fuel trim B1", "%", 1, lambda b: _trim(b[0])),
    Pid(0x07, "ltft1", "Long term fuel trim B1", "%", 1, lambda b: _trim(b[0])),
    Pid(0x08, "stft2", "Short term fuel trim B2", "%", 1, lambda b: _trim(b[0])),
    Pid(0x09, "ltft2", "Long term fuel trim B2", "%", 1, lambda b: _trim(b[0])),
    Pid(0x0A, "fuel_pressure", "Fuel pressure (gauge)", "kPa", 1, lambda b: b[0] * 3),
    Pid(0x0B, "map", "Intake manifold pressure", "kPa", 1, lambda b: b[0]),
    Pid(0x0C, "rpm", "Engine speed", "rpm", 2, lambda b: round(_u16(b) / 4)),
    Pid(0x0D, "speed", "Vehicle speed", "km/h", 1, lambda b: b[0]),
    Pid(0x0E, "timing", "Timing advance", "°", 1, lambda b: b[0] / 2 - 64),
    Pid(0x0F, "iat", "Intake air temperature", "°C", 1, lambda b: b[0] - 40),
    Pid(0x10, "maf", "MAF air flow rate", "g/s", 2, lambda b: round(_u16(b) / 100, 2)),
    Pid(0x11, "throttle", "Throttle position", "%", 1, lambda b: _pct(b[0])),
    Pid(0x14, "o2_b1s1", "O2 sensor B1S1 voltage", "V", 2, lambda b: round(b[0] / 200, 3)),
    Pid(0x15, "o2_b1s2", "O2 sensor B1S2 voltage", "V", 2, lambda b: round(b[0] / 200, 3)),
    Pid(0x16, "o2_b1s3", "O2 sensor B1S3 voltage", "V", 2, lambda b: round(b[0] / 200, 3)),
    Pid(0x18, "o2_b2s1", "O2 sensor B2S1 voltage", "V", 2, lambda b: round(b[0] / 200, 3)),
    Pid(0x19, "o2_b2s2", "O2 sensor B2S2 voltage", "V", 2, lambda b: round(b[0] / 200, 3)),
    Pid(0x1F, "run_time", "Run time since start", "s", 2, _u16),
    Pid(0x21, "dist_mil", "Distance with MIL on", "km", 2, _u16),
    Pid(0x22, "fuel_rail_rel", "Fuel rail pressure (rel. manifold)", "kPa", 2,
        lambda b: round(_u16(b) * 0.079, 1)),
    Pid(0x23, "fuel_rail", "Fuel rail gauge pressure", "kPa", 2, lambda b: _u16(b) * 10),
    Pid(0x24, "lambda_b1s1", "O2 B1S1 equivalence ratio", "λ", 4, lambda b: round(_u16(b) * 2 / 65536, 3)),
    Pid(0x2C, "egr_cmd", "Commanded EGR", "%", 1, lambda b: _pct(b[0])),
    Pid(0x2D, "egr_err", "EGR error", "%", 1, lambda b: _trim(b[0])),
    Pid(0x2E, "evap_purge", "Commanded evaporative purge", "%", 1, lambda b: _pct(b[0])),
    Pid(0x2F, "fuel_level", "Fuel tank level", "%", 1, lambda b: _pct(b[0])),
    Pid(0x30, "warmups", "Warm-ups since codes cleared", "", 1, lambda b: b[0]),
    Pid(0x31, "dist_clear", "Distance since codes cleared", "km", 2, _u16),
    Pid(0x33, "baro", "Barometric pressure", "kPa", 1, lambda b: b[0]),
    Pid(0x34, "lambda_b1s1_wide", "O2 B1S1 λ (wideband)", "λ", 4, lambda b: round(_u16(b) * 2 / 65536, 3)),
    Pid(0x3C, "cat_temp_b1s1", "Catalyst temperature B1S1", "°C", 2, lambda b: round(_u16(b) / 10 - 40, 1)),
    Pid(0x3E, "cat_temp_b2s1", "Catalyst temperature B2S1", "°C", 2, lambda b: round(_u16(b) / 10 - 40, 1)),
    Pid(0x42, "voltage", "Control module voltage", "V", 2, lambda b: round(_u16(b) / 1000, 2)),
    Pid(0x43, "abs_load", "Absolute load value", "%", 2, lambda b: round(_u16(b) * 100 / 255, 1)),
    Pid(0x44, "lambda_cmd", "Commanded equivalence ratio", "λ", 2, lambda b: round(_u16(b) * 2 / 65536, 3)),
    Pid(0x45, "throttle_rel", "Relative throttle position", "%", 1, lambda b: _pct(b[0])),
    Pid(0x46, "ambient", "Ambient air temperature", "°C", 1, lambda b: b[0] - 40),
    Pid(0x49, "pedal_d", "Accelerator pedal position D", "%", 1, lambda b: _pct(b[0])),
    Pid(0x4C, "throttle_cmd", "Commanded throttle actuator", "%", 1, lambda b: _pct(b[0])),
    Pid(0x4D, "time_mil", "Time run with MIL on", "min", 2, _u16),
    Pid(0x4E, "time_clear", "Time since codes cleared", "min", 2, _u16),
    Pid(0x51, "fuel_type", "Fuel type", "", 1, lambda b: FUEL_TYPES.get(b[0], f"type {b[0]}")),
    Pid(0x52, "ethanol", "Ethanol fuel", "%", 1, lambda b: _pct(b[0])),
    Pid(0x5A, "pedal_rel", "Relative accelerator pedal", "%", 1, lambda b: _pct(b[0])),
    Pid(0x5B, "hybrid_soc", "Hybrid battery remaining life", "%", 1, lambda b: _pct(b[0])),
    Pid(0x5C, "oil_temp", "Engine oil temperature", "°C", 1, lambda b: b[0] - 40),
    Pid(0x5E, "fuel_rate", "Engine fuel rate", "L/h", 2, lambda b: round(_u16(b) / 20, 2)),
    Pid(0x62, "torque_pct", "Actual engine torque", "%", 1, lambda b: b[0] - 125),
    Pid(0x63, "torque_ref", "Engine reference torque", "Nm", 2, _u16),
    Pid(0xA6, "odometer", "Odometer", "km", 4,
        lambda b: round(((b[0] << 24) + (b[1] << 16) + (b[2] << 8) + b[3]) / 10, 1)),
]
FUEL_TYPES = {1: "Gasoline", 2: "Methanol", 3: "Ethanol", 4: "Diesel", 5: "LPG", 6: "CNG",
              8: "Electric", 17: "Hybrid gasoline", 19: "Hybrid diesel", 20: "Hybrid electric"}
PIDS = {p.pid: p for p in PID_LIST}
PIDS_BY_KEY = {p.key: p for p in PID_LIST}


def decode_pid(pid: int, data: list[int]) -> dict | None:
    if pid == 0x03:
        return {"key": "fuel_system", "name": "Fuel system status", "unit": "",
                "value": FUEL_STATUS.get(data[0], f"0x{data[0]:02X}") if data else None}
    p = PIDS.get(pid)
    if not p or len(data) < p.nbytes:
        return None
    try:
        value = p.calc(data[:p.nbytes])
    except (IndexError, ZeroDivisionError):
        return None
    return {"key": p.key, "name": p.name, "unit": p.unit, "value": value}


def _payloads(raw: str, service: int, pid: int | None = None) -> list[list[int]]:
    """Payload bytes after the service echo (and PID echo, when given), per ECU."""
    resp_sid = service + 0x40
    out = []
    for f in frames(raw):
        try:
            i = f.index(resp_sid)
        except ValueError:
            continue
        rest = f[i + 1:]
        if pid is not None:
            if not rest or rest[0] != pid:
                continue
            rest = rest[1:]
        out.append(rest)
    return out


def parse_mode01(raw: str, pid: int) -> dict | None:
    for data in _payloads(raw, 0x01, pid):
        val = decode_pid(pid, data)
        if val:
            return val
    return None


def parse_supported(raw: str, base_pid: int) -> list[int]:
    """Mode 01 PID 00/20/40/... bitmap -> list of supported PIDs (union over ECUs)."""
    supported: set[int] = set()
    for data in _payloads(raw, 0x01, base_pid):
        if len(data) < 4:
            continue
        bits = (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3]
        for i in range(32):
            if bits & (1 << (31 - i)):
                supported.add(base_pid + i + 1)
    return sorted(supported)


# ---------------------------------------------------------------- DTCs
def decode_dtc(b1: int, b2: int) -> str:
    letter = "PCBU"[(b1 >> 6) & 0x3]
    return f"{letter}{(b1 >> 4) & 0x3}{b1 & 0xF:X}{b2:02X}"


def parse_dtcs(raw: str, service: int = 0x03, can: bool | None = None) -> list[str]:
    """Mode 03 (stored), 07 (pending) or 0A (permanent) -> ['P0420', ...]."""
    codes: list[str] = []
    for data in _payloads(raw, service):
        if not data:
            continue
        is_can = can
        if is_can is None:  # CAN responses carry a count byte first
            is_can = len(data) % 2 == 1 and data[0] * 2 == len(data) - 1
        if is_can:
            data = data[1:]
        for i in range(0, len(data) - 1, 2):
            if data[i] == 0 and data[i + 1] == 0:
                continue
            code = decode_dtc(data[i], data[i + 1])
            if code not in codes:
                codes.append(code)
    return codes


# ---------------------------------------------------------------- readiness
SPARK_MONITORS = ["Catalyst", "Heated catalyst", "Evaporative system", "Secondary air system",
                  "A/C refrigerant", "Oxygen sensor", "Oxygen sensor heater", "EGR / VVT system"]
COMPRESSION_MONITORS = ["NMHC catalyst", "NOx/SCR aftertreatment", None, "Boost pressure",
                        None, "Exhaust gas sensor", "PM filter", "EGR / VVT system"]


def parse_status(raw: str) -> dict | None:
    """Mode 01 PID 01 -> MIL state, DTC count and readiness monitors."""
    for data in _payloads(raw, 0x01, 0x01):
        if len(data) < 4:
            continue
        a, b, c, d = data[:4]
        compression = bool(b & 0x08)
        monitors = []
        for i, name in enumerate(["Misfire", "Fuel system", "Comprehensive components"]):
            if b & (1 << i):
                monitors.append({"name": name, "complete": not (b & (1 << (i + 4))), "continuous": True})
        names = COMPRESSION_MONITORS if compression else SPARK_MONITORS
        for i, name in enumerate(names):
            if name and c & (1 << i):
                monitors.append({"name": name, "complete": not (d & (1 << i)), "continuous": False})
        return {
            "mil_on": bool(a & 0x80),
            "dtc_count": a & 0x7F,
            "ignition": "compression (diesel)" if compression else "spark (petrol)",
            "monitors": monitors,
            "incomplete": [m["name"] for m in monitors if not m["complete"]],
        }
    return None


# ---------------------------------------------------------------- freeze frame / VIN
def parse_freeze_frame(raw: str, pid: int) -> dict | None:
    """Mode 02 '02 PID 00' response (frame 0)."""
    for data in _payloads(raw, 0x02, pid):
        if not data:
            continue
        data = data[1:]  # skip frame number
        if pid == 0x02:
            if len(data) >= 2 and (data[0] or data[1]):
                return {"key": "trigger_dtc", "name": "DTC that stored the freeze frame",
                        "unit": "", "value": decode_dtc(data[0], data[1])}
            return None
        val = decode_pid(pid, data)
        if val:
            return val
    return None


def parse_vin(raw: str) -> str | None:
    chars: list[int] = []
    for f in frames(raw):
        if 0x49 in f:
            i = f.index(0x49)
            rest = f[i + 2:] if len(f) > i + 1 and f[i + 1] == 0x02 else f[i + 1:]
            if rest and rest[0] <= 0x05:  # message count / sequence number
                rest = rest[1:]
            chars.extend(rest)
        else:
            chars.extend(f)
    text = "".join(chr(c) for c in chars if 0x30 <= c <= 0x5A)
    return text[-17:] if len(text) >= 17 else (text or None)


def describe_vin(vin: str | None) -> dict:
    if not vin or len(vin) != 17:
        return {}
    year_codes = "ABCDEFGHJKLMNPRSTVWXY123456789"
    yc = vin[9]
    years = []
    if yc in year_codes:
        idx = year_codes.index(yc)
        years = [1980 + idx, 2010 + idx]
    region = {"1": "USA", "4": "USA", "5": "USA", "2": "Canada", "3": "Mexico", "J": "Japan",
              "K": "Korea", "L": "China", "S": "UK", "V": "France/Spain", "W": "Germany",
              "Y": "Sweden/Finland", "Z": "Italy", "T": "Czechia/Switzerland/Hungary",
              "U": "Romania/Denmark", "X": "Russia/Netherlands"}.get(vin[0], "unknown")
    return {"wmi": vin[:3], "region": region, "model_year_candidates": years, "serial": vin[11:]}


def protocol_name(raw: str) -> str | None:
    txt = (raw or "").replace(">", "").strip().upper()
    auto = txt.startswith("A")
    num = txt[-1:] if txt else ""
    name = PROTOCOLS.get(num)
    if not name:
        return None
    return name + (" (auto-detected)" if auto else "")


def adapter_info(ati: str) -> dict:
    txt = (ati or "").replace(">", "").strip()
    m = re.search(r"(ELM327|STN\d+|OBDLink)\s*v?([\d.]+)?", txt, re.I)
    info = {"raw": txt, "chip": m.group(1) if m else None, "version": m.group(2) if m else None}
    if m and m.group(1).upper() == "ELM327" and m.group(2) in ("2.1", "2.2"):
        info["warning"] = ("Reports ELM327 v2.1 - almost always a clone. Expect slower polling and "
                           "occasional missing multi-frame responses.")
    return info


# ---------------------------------------------------------------- full scan
class OBDReaderAgent:
    """Decodes a whole scan bundle sent by the phone.

    Bundle format (all values are the raw ELM text, including the '>' prompt):
      {"ati": "...", "dpn": "...", "status": raw(0101), "vin": raw(0902),
       "stored": raw(03), "pending": raw(07), "permanent": raw(0A),
       "supported": {"00": raw, "20": raw, ...},
       "freeze": {"02": raw(020200), "05": raw(020500), ...},
       "live": {"0C": raw(010C), ...}}
    """

    name = "obd_reader"

    def decode(self, bundle: dict) -> dict:
        proto = protocol_name(bundle.get("dpn", ""))
        can = ("CAN" in proto) if proto else None
        result: dict = {
            "adapter": adapter_info(bundle.get("ati", "")),
            "protocol": proto,
            "status": parse_status(bundle.get("status", "")),
            "dtcs": {
                "stored": parse_dtcs(bundle.get("stored", ""), 0x03, can),
                "pending": parse_dtcs(bundle.get("pending", ""), 0x07, can),
                "permanent": parse_dtcs(bundle.get("permanent", ""), 0x0A, can),
            },
            "freeze_frame": {},
            "live": {},
            "supported_pids": [],
        }
        vin = parse_vin(bundle["vin"]) if bundle.get("vin") else None
        result["vin"] = vin
        result["vin_info"] = describe_vin(vin)
        for base, raw in (bundle.get("supported") or {}).items():
            result["supported_pids"].extend(parse_supported(raw, int(base, 16)))
        for pid_hex, raw in (bundle.get("freeze") or {}).items():
            v = parse_freeze_frame(raw, int(pid_hex, 16))
            if v:
                result["freeze_frame"][v["key"]] = v
        for pid_hex, raw in (bundle.get("live") or {}).items():
            v = parse_mode01(raw, int(pid_hex, 16))
            if v:
                result["live"][v["key"]] = v
        # values provided already-decoded (e.g. from the phone's recorder) pass through
        for k, v in (bundle.get("decoded_live") or {}).items():
            if k not in result["live"] and isinstance(v, (int, float)):
                p = PIDS_BY_KEY.get(k)
                result["live"][k] = {"key": k, "name": p.name if p else k,
                                     "unit": p.unit if p else "", "value": v}
        result["all_codes"] = sorted(set(sum(result["dtcs"].values(), [])))
        return result

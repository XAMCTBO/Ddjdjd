"""The "check bulletins" step - points the user (or Claude, via computer use) at the
right manufacturer service bulletins / recalls for a diagnosis.

This module holds NO bulletin content. Bulletins live in the user's own paid
subscriptions (ALLDATA Europe, Autodata, HaynesPro), whose terms forbid bulk
copying. What we do:
  * build a ready-to-paste search for each code and vehicle,
  * explain why a bulletin is likely to exist for this case,
  * list the user's sources and how to reach them (bulletin_sources.json),
  * link the free DVSA recall check (UK),
  * store the user's own short notes about bulletins they checked, so later
    diagnoses, chat and reports can take them into account.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import dtc_catalog

SOURCES_FILE = Path(os.environ.get("OBDAI_BULLETIN_SOURCES",
                                   Path(__file__).resolve().parent / "bulletin_sources.json"))

DVSA = {
    "id": "dvsa",
    "name": "DVSA vehicle recall check (UK, free)",
    "by_registration": "https://www.check-mot.service.gov.uk/",
    "by_make_model": "https://www.check-vehicle-recalls.service.gov.uk/recall-type/vehicle/make",
    "how": ["With a registration number: MOT history service shows outstanding recalls.",
            "Without one: choose make, model and year of manufacture."],
}

# Codes where manufacturer bulletins (software updates, revised parts, known
# pattern faults) are common. Used only to raise the priority of the check.
BULLETIN_PRONE = {
    "P0011", "P0012", "P0014", "P0016", "P0299", "P0234", "P2263", "P0087", "P0093",
    "P2463", "P242F", "P2002", "P20EE", "P0401", "P0420", "P0430", "P0300", "P0171",
    "P0174", "P0700", "P0730", "P0740", "P0606", "P0600", "P0562", "P0128",
}
SOFTWARE_HINT = {"P0606", "P0600", "P0700"}

NOTE_FIELDS = ("source", "reference", "title", "codes", "summary", "applies", "action")
MAX_SUMMARY = 1200  # keep notes short and in the user's own words


def load_sources() -> list[dict]:
    try:
        data = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
        return [s for s in data.get("sources", []) if s.get("enabled", True)]
    except (OSError, ValueError):
        return []


def vehicle_label(info: dict) -> str:
    parts = [str(info.get(k)) for k in ("make", "model", "year", "engine") if info.get(k)]
    return " ".join(parts) or "this vehicle"


def build_check(codes: list[str], vehicle: dict | None, history_counts: dict[str, int] | None = None,
                notes: list[dict] | None = None) -> dict:
    info = (vehicle or {}).get("info", {})
    history_counts = history_counts or {}
    notes = notes or []
    label = vehicle_label(info)
    reasons: list[str] = []
    high = False
    searches = []
    for code in codes:
        entry = dtc_catalog.lookup(code)
        searches.append({"code": code, "query": f"{label} {code} {entry['description']}".strip()})
        if history_counts.get(code):
            high = True
            reasons.append(f"{code} has come back before ({history_counts[code]} earlier session(s)) - "
                           "recurring faults are often covered by a revised part or software update.")
        if entry["manufacturer_specific"]:
            reasons.append(f"{code} is manufacturer-specific - its exact meaning and fixes are in "
                           "manufacturer information, not generic OBD data.")
        if code in SOFTWARE_HINT:
            high = True
            reasons.append(f"{code} points at a control module - check for a software/calibration update.")
        elif code in BULLETIN_PRONE:
            reasons.append(f"{code} is a code manufacturers frequently issue bulletins for "
                           "(known faults, revised parts, software updates).")
    checked = {c for n in notes for c in n.get("codes", [])}
    unchecked = [c for c in codes if c not in checked]
    if not info.get("make"):
        reasons.append("Add the make, model, year and engine to the vehicle so the searches are specific.")
    return {
        "recommended": bool(unchecked),
        "priority": "high" if high else "normal",
        "vehicle": label,
        "reasons": reasons,
        "searches": searches,
        "already_checked": sorted(checked & set(codes)),
        "unchecked": unchecked,
        "sources": load_sources(),
        "recall_check": {**DVSA, "registration": info.get("reg")},
        "notes": [n for n in notes if set(n.get("codes", [])) & set(codes)] or notes[-5:],
        "reminder": "Record what you find in your own words (reference, what it says, whether it applies). "
                    "Don't paste the full bulletin text - it belongs to the information provider.",
    }


def clean_note(payload: dict) -> dict:
    note = {k: payload.get(k) for k in NOTE_FIELDS}
    note["source"] = str(note["source"] or "").strip()[:60]
    if not note["source"]:
        raise ValueError("source is required (e.g. alldata_eu, autodata, haynespro, dvsa, dealer)")
    note["reference"] = str(note["reference"] or "").strip()[:80]
    note["title"] = str(note["title"] or "").strip()[:200]
    codes = note["codes"] or []
    if isinstance(codes, str):
        codes = codes.replace(",", " ").split()
    note["codes"] = sorted({str(c).strip().upper() for c in codes if str(c).strip()})[:20]
    summary = str(note["summary"] or "").strip()
    if len(summary) > MAX_SUMMARY:
        raise ValueError(f"summary too long ({len(summary)} chars) - keep it under {MAX_SUMMARY} "
                         "characters, in your own words")
    note["summary"] = summary
    note["applies"] = note["applies"] if note["applies"] in (True, False) else None
    note["action"] = str(note["action"] or "").strip()[:300]
    if not (note["title"] or note["summary"] or note["reference"]):
        raise ValueError("give at least a reference, title or summary")
    return note

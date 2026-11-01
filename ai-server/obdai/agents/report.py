"""Report Generator agent - printable diagnostic report (HTML -> "Save as PDF").

Modes:  owner (plain language) | mechanic (raw values, protocol, PIDs)
        sale  (used-car buyer template: readiness, codes-cleared check, VIN)
Languages: en, uk.
Charts are inline SVG so the report is one self-contained file.
"""
from __future__ import annotations

import html
import time

from . import evidence

T = {
    "en": {"title": "Vehicle diagnostic report", "vehicle": "Vehicle", "summary": "Summary", "codes": "Trouble codes",
           "none": "No trouble codes found.", "code": "Code", "status": "Status", "desc": "Description", "sev": "Severity",
           "causes": "Likely causes", "plan": "Recommended actions", "readiness": "Readiness monitors",
           "complete": "complete", "incomplete": "INCOMPLETE", "freeze": "Freeze frame", "live": "Live data snapshot",
           "trends": "Health trends", "predictions": "Predictions", "charts": "Session charts", "safe": "Safe to drive",
           "yes": "Yes", "with_caution": "With caution", "no": "No - stop and get help", "generated": "Generated",
           "disclaimer": "Generated with the help of AI from OBD-II data. It doesn't replace an inspection by a qualified mechanic.",
           "sale": "Pre-purchase check", "cleared": "Signs that codes were cleared recently",
           "cleared_yes": "Yes: codes appear to have been cleared recently. Ask the seller why.", "cleared_no": "No signs of a recent code clear.",
           "mil": "Check-engine light", "on": "ON", "off": "off", "protocol": "Protocol", "adapter": "Adapter",
           "interactions": "How the codes relate", "notes": "Notes", "cost": "Est. cost", "mechanic": "When to see a mechanic"},
    "uk": {"title": "Звіт діагностики автомобіля", "vehicle": "Автомобіль", "summary": "Підсумок", "codes": "Коди несправностей",
           "none": "Кодів несправностей не знайдено.", "code": "Код", "status": "Статус", "desc": "Опис", "sev": "Серйозність",
           "causes": "Ймовірні причини", "plan": "Рекомендовані дії", "readiness": "Монітори готовності",
           "complete": "готово", "incomplete": "НЕ ГОТОВО", "freeze": "Стоп-кадр (freeze frame)", "live": "Поточні дані",
           "trends": "Тренди стану", "predictions": "Прогнози", "charts": "Графіки сесії", "safe": "Чи можна їхати",
           "yes": "Так", "with_caution": "Обережно", "no": "Ні - зупиніться та зверніться по допомогу", "generated": "Створено",
           "disclaimer": "Створено за допомогою ШІ на основі даних OBD-II. Звіт не замінює огляд кваліфікованим механіком.",
           "sale": "Перевірка перед купівлею", "cleared": "Ознаки нещодавнього стирання кодів",
           "cleared_yes": "Так: коди, схоже, нещодавно стирали. Запитайте продавця чому.", "cleared_no": "Ознак нещодавнього стирання кодів немає.",
           "mil": "Лампа Check Engine", "on": "УВІМК.", "off": "вимк.", "protocol": "Протокол", "adapter": "Адаптер",
           "interactions": "Зв'язок між кодами", "notes": "Примітки", "cost": "Орієнт. вартість", "mechanic": "Коли до механіка"},
}
SEV_COLOR = {"low": "#2e7d32", "medium": "#ef8f00", "high": "#d84315", "critical": "#b71c1c"}

CSS = """
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1d232a;max-width:860px;margin:24px auto;padding:0 18px;font-size:14px;line-height:1.45}
h1{font-size:22px;margin:0}h2{font-size:16px;border-bottom:2px solid #1d232a;padding-bottom:4px;margin-top:26px}
.meta{color:#5b6670;font-size:12px}table{border-collapse:collapse;width:100%;margin:6px 0}
td,th{border:1px solid #d5dbe0;padding:5px 7px;text-align:left;vertical-align:top;font-size:13px}th{background:#f1f4f6}
.sev{color:#fff;border-radius:4px;padding:1px 6px;font-size:12px;font-weight:600}
.box{border:1px solid #d5dbe0;border-radius:8px;padding:10px 12px;background:#fafbfc}
.bad{color:#b71c1c;font-weight:600}.ok{color:#2e7d32}.small{font-size:12px;color:#5b6670}
svg{width:100%;height:auto;border:1px solid #e3e7ea;border-radius:6px;background:#fff}
@media print{body{margin:0}h2{break-after:avoid}table,svg{break-inside:avoid}.noprint{display:none}}
"""


def _e(x) -> str:
    return html.escape(str(x if x is not None else "—"))


def svg_chart(series: dict[str, list[tuple[float, float]]], title: str, unit: str = "",
              ref_lines: list[float] | None = None, w: int = 760, h: int = 180) -> str:
    pts = [p for s in series.values() for p in s]
    if len(pts) < 2:
        return ""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts] + (ref_lines or [])
    x0, x1 = min(xs), max(xs) or 1
    y0, y1 = min(ys), max(ys)
    if y0 == y1:
        y0, y1 = y0 - 1, y1 + 1
    pad = (y1 - y0) * 0.1
    y0, y1 = y0 - pad, y1 + pad
    L, R, Tp, B = 46, 10, 22, 24

    def sx(x):
        return L + (x - x0) / ((x1 - x0) or 1) * (w - L - R)

    def sy(y):
        return Tp + (1 - (y - y0) / (y1 - y0)) * (h - Tp - B)

    colors = ["#1565c0", "#ef6c00", "#2e7d32", "#6a1b9a"]
    parts = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-size="11" font-family="sans-serif">',
             f'<text x="{L}" y="14" font-weight="600">{_e(title)}</text>']
    for i in range(5):
        yv = y0 + (y1 - y0) * i / 4
        parts.append(f'<line x1="{L}" x2="{w - R}" y1="{sy(yv):.1f}" y2="{sy(yv):.1f}" stroke="#eceff1"/>'
                     f'<text x="{L - 4}" y="{sy(yv) + 4:.1f}" text-anchor="end" fill="#78909c">{yv:.0f}{unit}</text>')
    for rl in ref_lines or []:
        parts.append(f'<line x1="{L}" x2="{w - R}" y1="{sy(rl):.1f}" y2="{sy(rl):.1f}" stroke="#d84315" stroke-dasharray="4 3"/>')
    for i, (name, s) in enumerate(series.items()):
        if len(s) < 2:
            continue
        d = " ".join(f"{'M' if j == 0 else 'L'}{sx(x):.1f},{sy(y):.1f}" for j, (x, y) in enumerate(s))
        c = colors[i % len(colors)]
        parts.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="1.8"/>'
                     f'<text x="{w - R - 4 - 110 * i}" y="14" text-anchor="end" fill="{c}">{_e(name)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def codes_recently_cleared(scan: dict) -> bool | None:
    live = evidence.values(scan.get("live"))
    dist, warm = live.get("dist_clear"), live.get("warmups")
    status = scan.get("status") or {}
    signals = []
    if isinstance(dist, (int, float)):
        signals.append(dist < 160)
    if isinstance(warm, (int, float)):
        signals.append(warm < 10)
    if status.get("monitors"):
        signals.append(len(status.get("incomplete", [])) >= 2)
    return any(signals) if signals else None


class ReportAgent:
    name = "report"

    def render(self, vehicle: dict, session: dict, diagnosis: dict | None, recommendations: dict | None,
               prediction: dict | None, history: list[dict] | None = None,
               mode: str = "owner", lang: str = "en") -> str:
        t = T.get(lang, T["en"])
        scan = session.get("scan", {})
        info = (vehicle or {}).get("info", {})
        mech = mode == "mechanic"
        out = [f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><title>{_e(t["title"])}</title>'
               f'<style>{CSS}</style></head><body>',
               f'<button class="noprint" onclick="window.AndroidPrint ? AndroidPrint.print() : print()" style="float:right">PDF / Print</button>',
               f'<h1>{_e(t["sale"] if mode == "sale" else t["title"])}</h1>',
               f'<div class="meta">{_e(t["generated"])}: {time.strftime("%Y-%m-%d %H:%M", time.localtime())}'
               f' · session #{_e(session.get("id"))}</div>']
        # vehicle
        rows = [("VIN", vehicle.get("vin") or scan.get("vin")),
                (t["vehicle"], " ".join(str(info.get(k, "")) for k in ("year", "make", "model", "engine")).strip() or None),
                ("Odometer", info.get("odometer_km") and f'{info["odometer_km"]} km')]
        status = scan.get("status") or {}
        if status:
            rows.append((t["mil"], t["on"] if status.get("mil_on") else t["off"]))
        if mech:
            rows += [(t["protocol"], scan.get("protocol")), (t["adapter"], (scan.get("adapter") or {}).get("raw"))]
        out.append("<h2>" + _e(t["vehicle"]) + "</h2><table>" +
                   "".join(f"<tr><th style='width:30%'>{_e(k)}</th><td>{_e(v)}</td></tr>" for k, v in rows if v) + "</table>")
        # summary
        if diagnosis:
            safe = diagnosis.get("safe_to_drive", "yes")
            out.append(f'<h2>{_e(t["summary"])}</h2><div class="box">{_e(diagnosis.get("summary"))}<br>'
                       f'<b>{_e(t["safe"])}:</b> <span class="{"bad" if safe != "yes" else "ok"}">{_e(t.get(safe, safe))}</span></div>')
        # sale check
        if mode == "sale":
            cleared = codes_recently_cleared(scan)
            if cleared is not None:
                out.append(f'<h2>{_e(t["cleared"])}</h2><div class="box {"bad" if cleared else "ok"}">'
                           f'{_e(t["cleared_yes"] if cleared else t["cleared_no"])}</div>')
        # codes
        out.append(f'<h2>{_e(t["codes"])}</h2>')
        codes = (diagnosis or {}).get("codes") or []
        if not codes:
            out.append(f"<p>{_e(t['none'])}</p>")
        else:
            out.append(f"<table><tr><th>{_e(t['code'])}</th><th>{_e(t['status'])}</th><th>{_e(t['desc'])}</th>"
                       f"<th>{_e(t['sev'])}</th><th>{_e(t['causes'])}</th></tr>")
            for c in codes:
                causes = "<br>".join(_e(x["cause"]) + (f' <span class="small">({_e(x["why"])})</span>' if mech else "")
                                     for x in c.get("likely_causes", [])[:4])
                out.append(f"<tr><td><b>{_e(c['code'])}</b></td><td>{_e(c['status'])}</td><td>{_e(c['description'])}</td>"
                           f"<td><span class='sev' style='background:{SEV_COLOR.get(c['severity'], '#555')}'>{_e(c['severity'])}</span></td>"
                           f"<td>{causes}</td></tr>")
            out.append("</table>")
            if diagnosis.get("interactions"):
                out.append(f"<p><b>{_e(t['interactions'])}:</b></p><ul>" +
                           "".join(f"<li>{_e(x)}</li>" for x in diagnosis["interactions"]) + "</ul>")
        # recommendations
        if recommendations and recommendations.get("steps"):
            out.append(f"<h2>{_e(t['plan'])}</h2><ol>")
            for s in recommendations["steps"]:
                extra = f' <span class="small">[{_e(s.get("difficulty"))}, {_e(t["cost"])} {_e(s.get("est_cost_usd"))}]</span>'
                out.append(f"<li><b>{_e(s['title'])}</b>{extra}<br>{_e(s.get('detail'))}"
                           + (f"<br><span class='small'>{_e(s.get('confirms'))}</span>" if mech else "") + "</li>")
            out.append("</ol>")
            if recommendations.get("when_to_see_mechanic"):
                out.append(f"<p><b>{_e(t['mechanic'])}:</b> {_e(recommendations['when_to_see_mechanic'])}</p>")
        # readiness
        if status.get("monitors"):
            out.append(f"<h2>{_e(t['readiness'])}</h2><table>" + "".join(
                f"<tr><td>{_e(m['name'])}</td><td class='{'ok' if m['complete'] else 'bad'}'>"
                f"{_e(t['complete'] if m['complete'] else t['incomplete'])}</td></tr>" for m in status["monitors"]) + "</table>")
        # freeze frame / live
        for key, label in (("freeze_frame", t["freeze"]), ("live", t["live"])):
            block = scan.get(key) or {}
            if block and (mech or key == "freeze_frame"):
                out.append(f"<h2>{_e(label)}</h2><table>" + "".join(
                    f"<tr><td>{_e(v.get('name', k))}</td><td>{_e(v.get('value'))} {_e(v.get('unit', ''))}</td></tr>"
                    for k, v in block.items() if isinstance(v, dict)) + "</table>")
        # charts from this session's samples
        samples = session.get("samples") or []
        if len(samples) > 3:
            rows = [{evidence.ALIASES.get(k, k): v for k, v in r.items()} for r in samples]

            def ser(key):
                return [(r.get("t", 0) / 1000, r[key]) for r in rows if isinstance(r.get(key), (int, float))]
            out.append(f"<h2>{_e(t['charts'])}</h2>")
            out.append(svg_chart({"STFT B1": ser("stft1"), "LTFT B1": ser("ltft1")}, "Fuel trims (%) vs time (s)", "%", [10, -10]))
            out.append(svg_chart({"Coolant": ser("coolant")}, "Coolant temperature (°C) vs time (s)", "°"))
            if ser("o2_b1s1"):
                out.append(svg_chart({"O2 B1S1": ser("o2_b1s1"), "O2 B1S2": ser("o2_b1s2")}, "O2 sensors (V)", ""))
        # trends across sessions
        if history and len(history) >= 2:
            hs = [(i + 1, s["summary"]) for i, s in enumerate(history) if s.get("summary")]
            ch = svg_chart({"Total trim (warm)": [(i, s["trim_warm_b1"]) for i, s in hs if "trim_warm_b1" in s]},
                           "Fuel trim per session (%)", "%", [20])
            if ch:
                out.append(f"<h2>{_e(t['trends'])}</h2>{ch}")
        if prediction and prediction.get("ready") and prediction.get("components"):
            out.append(f"<h2>{_e(t['predictions'])}</h2><p>{_e(prediction.get('summary'))}</p><table>" + "".join(
                f"<tr><td>{_e(c['component'])}</td><td><span class='sev' style='background:{SEV_COLOR.get(c['level'], '#555')}'>"
                f"{_e(c['level'])}</span></td><td>{_e(c['advice'])}</td></tr>" for c in prediction["components"]) + "</table>")
        out.append(f'<p class="small" style="margin-top:30px">{_e(t["disclaimer"])}</p></body></html>')
        return "".join(out)

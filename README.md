# OBD Logger — Android app

Thin native shell + the same web page used in plain Chrome. Most of the
app (gauges, parsing, recording, CSV/JSON export) lives in one HTML file
hosted outside the app, so updating it does **not** need a new APK build —
the WebView just loads the latest version next time it opens. The native
Kotlin code only supplies what a browser can't: classic Bluetooth (SPP)
and a BLE path that isn't limited by Chrome's Web Bluetooth restrictions.

## AI diagnostics (new)

The app can now explain codes, plan repairs, predict failures, generate PDF reports and chat, backed by a
self-hosted multi-agent server in [`ai-server/`](ai-server/README.md):

- **Diagnostics panel** - *Scan codes* reads stored, pending and permanent codes, freeze frame, readiness
  monitors and VIN; *Clear codes* is behind two explicit warnings.
- **AI diagnostics panel** - set the server address and token once. Scans are explained by the DTC Analyzer and
  Recommendation agents, finished recordings are uploaded automatically for the Prediction agent, and there's a
  chat with the AI mechanic. *Report (PDF)* opens a native screen with Print / Save as PDF.
- Live data now also shows battery voltage and MAF (and records O2 sensors), and only polls PIDs the car
  actually supports.

Two bugs in the original page were fixed along the way: responses with spaces turned off (`ATS0`, which the page
itself sets) were never parsed, so the gauges stayed at `--` on most adapters; and a stale command timeout could
hand a later command an empty reply, shifting every response by one.

## Why this exists

The Kingbolen Ediag Elite's own app is closed — it won't share live data
with other software, and its own protocol is authenticated/licensed, which
is not something this project touches. This app instead talks to the
**dongle's hardware directly** over Bluetooth, the same way any generic
ELM327-clone OBD adapter is read. It tries three widely-used BLE chipset
profiles (Nordic UART, TI CC254x, Microchip ISSC) and falls back to classic
Bluetooth SPP, covering the great majority of cheap/generic OBD dongles —
branded or not.

## Build status

The project compiles: the GitHub Actions workflow builds a debug APK and uploads it as the
`obd-logger-debug-apk` artifact. It runs on every push to `main`, or on demand from the Actions tab (*Run
workflow*). It hasn't been tested on a phone with a real adapter yet. If something misbehaves, send the
`adb logcat` output (see below).

## Getting an actual installable APK

I can't produce an APK file directly, since I have no Android SDK to build
one with. Two realistic paths:

1. **GitHub Actions (recommended)** — `.github/workflows/android-build.yml`
   builds a debug APK on every push, using Google's own servers instead of
   mine, and uploads it as a downloadable build artifact. This needs the
   project pushed to a GitHub repo you control. Tell me the repo (new or
   existing) and I'll push it and trigger the build.
2. **Your own computer, with Android Studio** — open this folder as a
   project and hit Run, or Build > Build APK(s). Gives you the fastest
   iteration loop if you have a computer free for it.

## Debugging after it's installed

True "live" viewing of your phone's screen isn't something I can do from
here. The closest practical equivalent:

- Connect the phone to a computer by USB, turn on Developer Options → USB
  debugging, and run `adb logcat | grep BtBridge` there. Send me that
  output (or paste the relevant lines) and I can read exactly what the app
  saw on the Bluetooth link.
- Any crash shows a stack trace in the same logcat output — paste it to me
  directly.
- If your computer is linked to this Claude session (Claude desktop app),
  I can run `adb logcat` myself once the phone is plugged into that
  computer, which is the nearest thing to live debugging available here.

## Updating the app later

- **Gauges, parsing, recording, UI** — edit `obd-logger.html` (the file I
  already gave you) and republish it at the same URL. The app picks it up
  the next time it's opened. No rebuild, no reinstall.
- **Bluetooth bridge itself** (`BtBridge.kt`) — this only needs touching if
  we add a new chipset profile or fix a connection bug. That does need a
  new APK build via the path above.

## Project layout

```
app/src/main/java/com/newbodymechanics/obdlogger/
  MainActivity.kt   — WebView shell, loads the hosted page, wires up the bridges
  BtBridge.kt       — classic (RFCOMM/SPP) + BLE (GATT) Bluetooth, exposed to JS as `AndroidBT`
  ReportActivity.kt — shows AI reports with Print / Save as PDF
ai-server/          — multi-agent AI diagnostics backend (Python), see ai-server/README.md
app/src/main/AndroidManifest.xml
app/src/main/res/   — minimal layout, launcher icon, theme
.github/workflows/android-build.yml  — CI build (needs a GitHub repo)
```

Before the first build, open `MainActivity.kt` and set `LOGGER_URL` to
wherever `obd-logger.html` actually ends up hosted.

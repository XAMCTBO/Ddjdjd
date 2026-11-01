# Samsung UE65CU7100K (2023, 65" CU7100) that will not turn on: official and general diagnosis resources

> **SAFETY WARNING. Read this first.** The power supply board in an LED TV runs from mains voltage. Its primary ("HOT") side, with the bridge rectifier, PFC stage and the large main filter/bulk capacitor (typically around 400 V DC when charged), can stay charged to a lethal voltage **after the TV is unplugged**. Live voltage checks (standby rail, 13 V rail) are made with the TV **plugged in and the back cover off**. Only probe the low-voltage output ("cold") side, use one hand, and use insulated probes. Before touching the board, discharge the main capacitor through a resistor (not a screwdriver) and confirm with the multimeter that it reads 10 V or less. LED backlight testers put out up to 300 V or more DC. Opening the TV also voids any remaining Samsung warranty, so check warranty status first. Sources for these points are cited in section (c) below.

## Q1. Which official Samsung pages exist for UE65CU7100K (manuals, support, firmware, service request)?

### Takeaway
Samsung UK has a model support page for UE65CU7100KXXU. It holds the user manual, the e-Manual, USB firmware and OS-upgrade files, and links to warranty, repair booking and troubleshooting pages. The standard UK manufacturer's warranty on TVs is 12 months. Selected retailers ran a free 5-year promotional warranty that has to be registered.

### Cited Findings
- **Main model support page (UK):** https://www.samsung.com/uk/support/model/UE65CU7100KXXU/. It covers the 2023 65" CU7100 UHD 4K HDR Smart TV, model UE65CU7100K. [Samsung UK](https://www.samsung.com/uk/support/model/UE65CU7100KXXU/)
- **Manuals listed on that page:** User Manual BN68-17064A-02 (v2507040, 25.07.2025); e-Manual BN81-27185C-680 (v1.0, 18.11.2025); Quick Guide BN68-15966A-01 (23.03.2023); remote control leaflet BN68-15698F-00; Statement of Compliance BN68-19211B-00. [Samsung UK](https://www.samsung.com/uk/support/model/UE65CU7100KXXU/)
- **Firmware and software files listed on that page** (downloads come from org.downloadcenter.samsung.com):
  - Main USB upgrade file T-KSU2ECDEUC.zip, version 2000.2 (1378 MB, 04.09.2024)
  - OS Upgrade file T-KSU2ECDEUC_OSU_0080.zip, version 0080-2032.8 (23.07.2025)
  - OS Upgrade file T-KSU2ECDEUC_OS_0090.zip, version 0090-2230.0 (21.07.2026), listed for specific European and other regional areas
  - OS Upgrade USB user manual, plus release notes for 0080 and 0090
  [Samsung UK](https://www.samsung.com/uk/support/model/UE65CU7100KXXU/)
- **Repair and service links (UK):**
  - Troubleshoot & Book a Repair: https://www.samsung.com/uk/support/repair/
  - Track My Repair: https://www.samsung.com/uk/support/repair/track-my-repair/
  - Repair costs and times: https://www.samsung.com/uk/support/repair/why-repair-with-us/
  - Contact (chat or phone): https://www.samsung.com/uk/support/contact/
  [Samsung UK model page](https://www.samsung.com/uk/support/model/UE65CU7100KXXU/)
- **Troubleshooting articles linked from the model page:**
  - "My TV won't turn on": https://www.samsung.com/uk/support/tv-audio-video/my-tv-wont-turn-on/
  - "My TV switches itself off": https://www.samsung.com/uk/support/tv-audio-video/my-tv-switches-itself-off/
  - Remote not working: https://www.samsung.com/uk/support/tv-audio-video/my-tv-remote-isnt-working/
  - Picture test (self-diagnosis): https://www.samsung.com/uk/support/tv-audio-video/how-do-i-run-a-picture-test-self-diagnosis-on-my-tv/
  - Cold boot, reboot or reset: https://www.samsung.com/uk/support/tv-audio-video/how-to-cold-boot-reboot-restart-or-reset-your-samsung-smart-tv/
  [Samsung UK](https://www.samsung.com/uk/support/model/UE65CU7100KXXU/)
- When fetched, the UK "my TV won't turn on" URL showed only a notice that the repair booking service was "currently offline for essential maintenance", with no troubleshooting text. Treat that as a temporary page state. [Samsung UK](https://www.samsung.com/uk/support/tv-audio-video/my-tv-wont-turn-on/)
- A mirror of the UK article also exists at https://ushl.samsung.com/uk/support/tv-audio-video/my-tv-wont-turn-on. There is an Irish equivalent at https://www.samsung.com/ie/support/tv-audio-video/my-tv-wont-turn-on/, but it fetched as an index page only. [Search results](https://www.samsung.com/ie/support/tv-audio-video/my-tv-wont-turn-on/)
- **What other regional Samsung pages say about a TV that won't turn on:**
  - A lit red standby light means the TV is getting power. Try the physical power button on the TV. If the TV is powered but won't respond to either the remote or the button, "service is needed".
  - No standby light: test a known-working wall socket and bypass any surge protector.
  - A blinking standby light suggests a hardware issue, so contact support.
  [Samsung Lebanon](https://www.samsung.com/lb/support/tv-audio-video/how-to-troubleshoot-samsung-tv-that-will-not-turn-on/); [Samsung UAE](https://www.samsung.com/ae/support/tv-audio-video/what-to-do-if-your-samsung-tv-wont-turn-on)
- **UK warranty:**
  - Samsung TVs carry a 12-month standard manufacturer's warranty from the date of purchase, "in addition to, and does not affect statutory rights".
  - A free promotional 5-year TV warranty applies to selected TVs bought from selected retailers, and must be registered and claimed.
  - A claim needs the original proof of purchase and an intact serial number label.
  - TVs are repaired in the home or collected, depending on screen size.
  [Samsung UK Warranty](https://www.samsung.com/uk/support/warranty/)
- The retailer Euronics lists UE65CU7100KXXU with a "5 Year Promotional Warranty (Redemption Required)" that must be registered within 90 days. [Euronics UK](https://www.euronics.co.uk/p/SAMUE65CU7100KXXU)

### Inferences
- The CU7100 has a 5-year promotional warranty in the UK, so a 2023 set could still be covered if it was registered. Check this before opening the TV, because opening it may void the warranty.
- "UE" model codes are used across the UK and EU, with country-specific suffixes (KXXU = UK). For EU readers, the same model page should exist under other country paths, for example samsung.com/de/support/model/UE65CU7100KXZG/. That URL pattern and suffix were not verified.
- Firmware cannot fix a TV that will not power on at all. It is only relevant if the set boots partway or reboot-loops.

### Gaps
- EU-country model page URLs (DE, FR, NL and others) were not verified.
- No source was found for the EU 2-year legal guarantee as it applies to this specific case.
- No public service manual or schematic for the CU7100 chassis was found on official channels.
- The BN44 power board part number for UE65CU7100K was not found. Search results only showed boards for other series, such as BN44-01055A for UN65TU7000 ([ShopJimmy](https://shopjimmy.com/samsung-bn44-01055a-bn96-50313a-bn96-50314a-power-supply-backlight-strips-combo)). Read the part number from the sticker on the board itself.

## Q2. Is there a Samsung service-mode procedure for the CU series, and what does it help diagnose?

### Takeaway
Samsung officially documents only the user-facing **Self Diagnosis** menu (2022 and later models). It is only useful if the TV boots. The hidden service menu (Mute, 1, 8, 2, Power from standby) is community knowledge only and is unreliable. Neither helps with a TV that is completely dead.

### Cited Findings
- **Official Self Diagnosis** (2022 and later TVs and Smart Monitors): Settings > All Settings > Support > Device Care > Self Diagnosis. [Samsung Singapore](https://www.samsung.com/sg/support/tv-audio-video/self-diagnosis-options-on-your-samsung-tv-and-smart-monitor/)
- **Tests offered:**
  - Power (shows power history)
  - SW version
  - Video Test and Picture Test
  - Sound Test
  - Remote Control key test
  - HDMI Troubleshooting, HDMI Signal and HDMI-CEC Check
  - Smart Hub connection
  - Wi-Fi, Bluetooth and IoT module checks
  - Accelerometer, light sensor and mic checks
  - Broadcast signal
  - Reset Smart Hub (PIN 0000)
  A green tick means no issue was found. A red exclamation mark means an issue was found, and the TV may suggest contacting Samsung with the model code, software version and serial number. The page does not mention a service mode. [Samsung Singapore](https://www.samsung.com/sg/support/tv-audio-video/self-diagnosis-options-on-your-samsung-tv-and-smart-monitor/); same article for other regions: [Samsung Australia](https://www.samsung.com/au/support/tv-audio-video/self-diagnosis-options-on-your-samsung-tv-and-smart-monitor/), [Samsung Canada](https://www.samsung.com/ca/support/tv-audio-video/self-diagnosis-options-on-your-samsung-tv-and-smart-monitor/)
- **Hidden service menu, community sources:**
  - With the TV off or in standby, press Mute, 1, 8, 2, Power slowly on the remote.
  - One user reports it works only about 50% of the time, and only on an input with no signal.
  - Codes vary by model.
  [SamyGO forum](https://forum.samygo.tv/viewtopic.php?p=109534); [Samsung EU Community thread](https://eu.community.samsung.com/t5/tv/how-to-enter-service-menu-un65au8000/td-p/5091748); [Xataka Home (ES)](https://www.xatakahome.com/tutoriales/asi-menu-super-secreto-smart-tv-samsung-apto-solo-para-expertos-esto-que-esconde-asi-puedes-acceder)
- Some blogs mix up the Mute-1-8-2 menu with the official Self Diagnosis menu. Samsung sources do not support that link. [Search summary of Samsung pages](https://www.samsung.com/sg/support/tv-audio-video/self-diagnosis-options-on-your-samsung-tv-and-smart-monitor/)

### Inferences
- If the TV is dead with no picture, neither menu can be reached. The "Power" history in Self Diagnosis may be useful only if the fault is intermittent and the TV still turns on sometimes.
- Changing settings in the hidden service menu, such as panel or option bytes, can damage the TV's configuration. A hobbyist should only read values there, never change them.

### Gaps
- No official Samsung documentation of the service menu for the 2023 CU series was found.
- No source documents error codes or blink codes for the CU7100. Samsung's pages only say that a blinking light means a hardware fault.

## Q3. Which tutorial pages and videos clearly explain step-by-step dead-TV diagnosis for Samsung LED TVs?

### Takeaway
iFixit's "Samsung TV Will Not Turn On" wiki and TVPartsToday's Samsung no-power article give the clearest beginner-level sequence:

1. Check the socket, cable and reset.
2. Read the standby light.
3. Do the flashlight test for a dead backlight.
4. Inspect the power board visually and check the fuse.
5. Measure the output rails.
6. Unplug the main board to isolate it.

The 8 V standby / 13 V on figures come from iFixit community answers, not from Samsung. Check them against the labels printed on your own board.

### Cited Findings
- **iFixit wiki "Samsung TV Will Not Turn On"** ([link](https://www.ifixit.com/Wiki/Samsung_TV_Will_Not_Turn_On)):
  - Standby light solid: the TV has power, so reset the TV or remote. Light off: check the supply. Light blinking: often the power supply board.
  - Soft reset: unplug for 60 seconds and hold the power button for 30 seconds.
  - Bypass surge protectors and power strips.
  - A connected HDMI device can stop the TV starting.
  - **Flashlight test:** shine a torch close to the screen. A faint picture means a backlight fault, caused either by the power board or the LEDs.
  - Inspect the power board for burn marks and swollen capacitors, and check the fuse for continuity. A blown fuse often means other parts have failed too.
  - **Main board isolation:** unplug the power board to main board cable, power on, and look through the holes in the back plate to see whether the backlight comes on. If it does, the main board is suspect.
  - Warning: take care around the power board's "HOT" section.
  [iFixit](https://www.ifixit.com/Wiki/Samsung_TV_Will_Not_Turn_On)
- **TVPartsToday, "Samsung TV No Power Repair: Which Circuit Board Is Faulty"** ([link](https://tvpartstoday.com/blogs/blog/samsung-tv-no-power-repair-which-circuit-board-is-faulty)):
  - Check the socket and cord. Unplug, hold the power button for 30–60 seconds and wait.
  - With the TV face-down, inspect for swollen or leaking capacitors, burn marks and cracked solder.
  - Use a multimeter on the labelled output rails (5 V, 12 V or 24 V). No output points to a faulty power board.
  - Disconnect the main board. If the standby light then appears or the backlight flashes, the main board is dragging the supply down.
  - Samsung part number prefixes: BN44 = power board, BN94 = main board, BN96 = T-con (per the article).
  - Video playlist ("Troubleshooting 101"): https://www.youtube.com/watch?v=0kyA_PHJx5g&list=PLc3yCKcEGD_qbxKxSgI44MyvUk2gcLStg
  - YouTube channel: https://www.youtube.com/channel/UCLxjTbUfqel8LSoJIYjwA-Q
  [TVPartsToday](https://tvpartstoday.com/blogs/blog/samsung-tv-no-power-repair-which-circuit-board-is-faulty)
- **iFixit Answers, standby and 13 V checks** ([link](https://proxy.ifixit.com/Answers/View/776153/TV+will+not+power+up)):
  - If the fuse is OK, measure the STB (standby) reference point on the power board. It should read about 8 V DC in standby and 13 V DC when the TV is on.
  - With only the main board cable unplugged, the 13 V rail should be present, because the power board is then effectively told to turn on.
  - If there is no 13 V, check the marked rectifier diodes on the cold side for shorts or opens.
  - Another user reports 13 V even in standby, which conflicts with the 8 V figure. The voltages vary by board.
  [iFixit Answers](https://proxy.ifixit.com/Answers/View/776153/TV+will+not+power+up)
- **ShopJimmy blog, "Samsung TV Won't Turn On – Which Part Should You Replace?"** ([link](https://blog.shopjimmy.com/samsung-tv-wont-turn-on-which-part-should-you-replace)). It returned HTTP 503 when fetched, so its content was not verified.
- **Elektroda Q&A (BN44 boards):** typical no-start causes include a high-ESR start-up capacitor (for example CM802, 47 µF/50 V) starving the PWM IC, a failed start-up IC, the fuse, and shorted transistors or diodes. The part designators are board-specific. [Elektroda](https://www.elektroda.com/qa,samsung-bn44-00339a-issues-fixes.html)
- **Samsung EU Community:** a UE65TU7100 owner reports the standby light flashing intermittently for months before the TV stopped turning on. This is the earlier 7100 series, not the CU. [Samsung EU Community](https://eu.community.samsung.com/t5/televisie/standby-lampje-samsung-58tu7100/td-p/2086104)
- **YouTube channels named in search results:** Mr Carlson's Lab ("Power Supply Troubleshooting and Repair Tips") and Michael Dranfield ("TV repair") appeared in results. Their suitability for Samsung sets and for beginners was not verified. [Search context, TVPartsToday](https://tvpartstoday.com/blogs/blog/my-tv-has-no-power-signs-of-a-faulty-power-supply-board)

### Inferences
- **Suggested hobbyist sequence for a 2023 Samsung edge-lit/direct-lit set,** combining the sources above:
  1. Check the socket, cable and soft reset.
  2. Read the standby LED: off, solid or blinking.
  3. Do the flashlight test. A picture with no light means the backlight or LED driver.
  4. Inspect the board with the TV unplugged and the main capacitor discharged.
  5. Do a cold-side DC check of the standby and 13 V rails, measured against chassis ground.
  6. Unplug the main board to separate a power board fault from a main board fault.
  7. Test the LED strips.
- On many recent 65" Samsung TVs the power supply and LED driver are on one board, "BN44 Power/LED". A "no backlight" fault can therefore be the strips, or the driver section of the same board.
- In Samsung "no picture, sound works" cases a common real-world cause is failed backlight LEDs, which then shut down the LED driver. This is general community knowledge, not sourced here.

### Gaps
- No beginner tutorial or video specific to the CU7100 was found.
- ElektroTanya (which hosts service manuals) and Shib's TV repair pages were not reached in searches.
- No URLs for specific YouTube videos were verified beyond the TVPartsToday playlist.

## Q4. What do sources say about testing LED backlights with a multimeter vs an LED tester, and which LED tester products are typical?

### Takeaway
Multimeter diode mode, such as the DM303's, only gives rough per-LED spot checks. In-circuit readings are often ambiguous, and a typical meter's roughly 3 V test voltage may not light TV LEDs, which are often around 6 V each. A dedicated current-limited 0–300 V LED backlight tester can light a whole strip, or one LED, to find the dead one. A current-limited bench supply is an alternative.

### Cited Findings
- **Multimeter diode mode:**
  - It passes a small current through the LED and reads the voltage drop. "OL" means open or reversed.
  - Never use diode or resistance mode on a powered circuit.
  [Search summary, OAK LED](https://www.oakled.com/blogs/how-to-use-a-multimeter-to-detect-damaged-led/)
- **In-circuit readings are ambiguous:**
  - One forum user measured 0.724 V on known-good LEDs and 0.312 V on others in a 4-LED TV strip.
  - Another responder said ~0.73 V is "suspect for an LED too unless they have a reverse diode across them".
  [All About Circuits forum](https://forum.allaboutcircuits.com/threads/testing-leds-back-light-on-a-tv.185038/)
- **Current-limited bench supply:** one user lit a strip using a bench supply set to about 13.6 V with a 0.02 A (20 mA) current limit. [All About Circuits forum](https://forum.allaboutcircuits.com/threads/testing-leds-back-light-on-a-tv.185038/)
- **DIY and kit tester:** the Tindie "Tester for LED TV Backlight strips and Zener diodes" is a current-limited kit tester. Search snippets also describe a low 5–10 mA current source used to test strips. [Tindie](https://www.tindie.com/products/jasonkits/led-tv-backlight-and-zener-tester); [New Screwdriver blog](https://newscrewdriver.com/2021/07/04/backlight-led-tester/)
- **Typical commercial testers:** generic "0–300 V / 0–320 V LED TV backlight tester" boxes, often sold with a capacitance and diode function and an on/off switch, are sold in the UK and EU, for example on ManoMano UK. One example is the Heayzoki KT4H: it has voltage and current displays, and its manual describes connecting driver boards through constant-current cables. [ManoMano UK](https://www.manomano.co.uk/p/ca-300v-portable-led-lamp-beads-light-bar-tv-backlight-tester-led-strip-beads-lamp-panel-test-tool-capacitance-diode-voltage-test-with-switch-by-debuns-86282165); [manuals.plus, Heayzoki KT4H](https://manuals.plus/asin/B0B3Y96PJ5)
- **Strip vs driver diagnosis:** if the strips light on a tester but not in the TV, the LED driver or power board is more likely at fault. [Elektroda Q&A](https://www.elektroda.com/qa,tv-backlight-not-working.html)
- **Field example:** Jestine Yong used an LED tester to find one LED that would not light. The strip had previously been "repaired" with a short across one LED. Commenters mention using a bench power supply or stacked 9 V batteries instead of a tester. [Jestine Yong](https://jestineyong.com/a-tv-with-faulty-backlight-repaired-and-maintained/)
- iFixit Answers notes that many YouTube videos demonstrate TV LED backlight testers. [iFixit Answers](https://ts.ifixit.com/Answers/History/623477)
- A Technibble guide, "How to Test and Use an LCD's LED Backlights", exists, but the full text sits behind a forum login. [Technibble](https://www.technibble.com/forums/resources/how-to-test-and-use-an-lcds-led-backlights.7)
- **Safety (tester):** a generic 0–320 V tester listing says to disconnect the tested object from its power first. That listing is on a dubious reseller domain. [Reseller listing](https://plastiquealaloupe.fondationtaraocean.org/products/multipurpose-led-tv-backlight-tester-for-all-led-lights-repa/210251425/)

### Inferences
- A DM303-type meter's diode test is useful for checking rectifier diodes and fuses on the power board. It is a weak tool for TV LEDs.
- An LED tester costs roughly EUR 15–30 (price not sourced) and is the practical choice for testing strips. Never apply a tester's full-string voltage across a single LED.
- The 13.6 V at 20 mA bench-supply approach only works on short strings. A 65" set usually has several strips in series, and the string voltage can exceed 100 V.

### Gaps
- No verified per-LED forward voltage or strip configuration (BN96 part numbers) for the UE65CU7100K was found.
- The "GJ2C" tester could not be verified.

## (c) Safety guidance for mains-powered TV boards (supporting material for all questions)

### Cited Findings
- **Restarters wiki, "How to safely discharge capacitors":**
  - Power supplies can hold a dangerous charge long after the mains is disconnected.
  - Disconnect the mains, then find all reservoir capacitors on the high-voltage side and assume each one is charged.
  - Discharge each one through a high-power resistor with well-insulated leads (example given: 10 kΩ), without touching the connections.
  - Check with a multimeter, and repeat until the reading is 10 V or less.
  - Rule of thumb: t ≈ R(kΩ) × C(µF) / 330 seconds to fall to one twentieth of the starting voltage. Example: 100 µF at 300 V through 10 kΩ reaches about 15 V in roughly 3 seconds.
  - Shorting with a screwdriver causes a crack and a spark, draws many amps, and can damage the capacitor.
  [Restarters wiki](https://wiki.restarters.net/How_to_safely_discharge_capacitors)
- **Resistor values from other guides:**
  - 1 kΩ–100 kΩ, rated 2–5 W ([LCSC](https://www.lcsc.com/blog/?p=2601))
  - 4.7 kΩ, 10 W for up to 600 V DC ([Electronics For You](https://www.electronicsforu.com/?p=185416))
  - Forum users use a 150 Ω 2 W clip lead. 1 MΩ can take over a minute on large capacitors. ([AudioKarma](https://audiokarma.org/forums/threads/how-to-discharge-caps.212805/))
  - An iFixit-style discharge tool build: [Instructables](https://instructables.com/Safe-Capacitor-Discharge-Tool)
  - DigiKey's guide to discharging capacitors: [DigiKey](https://www.digikey.com/en/blog/how-to-safely-discharge-a-capacitor)
- **Classic TV safety and discharge FAQ** (from the CRT era, but the discharge principles are general): [Sci.Electronics.Repair FAQ, repairfaq.org](https://repairfaq.org/samnew/tvfaq/tvsafdis.htm)
- **HOT section warning:** voltages on the power board's HOT section are much higher, so proceed only if comfortable. [iFixit](https://www.ifixit.com/Wiki/Samsung_TV_Will_Not_Turn_On)
- **TVPartsToday safety notes:** unplug before opening, some parts hold a charge after unplugging, work face-down on a soft surface, and consult a professional if unsure. [TVPartsToday](https://tvpartstoday.com/blogs/blog/samsung-tv-no-power-repair-which-circuit-board-is-faulty)
- **Elektroda caution:** dangerous voltages are present on the power board even when the TV is unplugged. [Elektroda](https://www.elektroda.com/qa,samsung-bn44-00339a-issues-fixes.html)

### Inferences
- **Practical rules for a hobbyist with a DM303-class meter** (inferred from the sources above, not from one authoritative source):
  - Check the meter's CAT rating and the condition of its leads.
  - Measure live voltages only on the cold-side output connector, referenced to the cold ground or chassis. Never mix hot-side and cold-side grounds.
  - Use one hand, keep a clear bench, and plug the TV in through a switched RCD-protected strip.
  - Use a resistor tool rated at least 2–5 W, never a screwdriver.
  - Re-verify that the capacitor is discharged after every power-up.
- **The 65" panel itself is a physical hazard:** it can crack if flexed, so lay it face-down on a soft, flat surface. The ShopJimmy/TVPartsToday face-down advice is consistent with this.

### Gaps
- No official Samsung safety document for consumer self-repair of TVs was found. Samsung offers no DIY repair programme for TVs. The Samsung self-repair programme covers phones and laptops, which was not verified in this research.
- No isolation-transformer guidance specific to a hobbyist working on TVs was sourced.

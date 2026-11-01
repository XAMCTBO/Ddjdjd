# Samsung CU-series (2023, UE65CU7100K and siblings): no power / dead / blinking standby / sound-no-picture fault reports

Research date: 2026-11-01. Method: about 15 web searches and fetches. **Limitations:** eu.community.samsung.com, justanswer.co.uk and badcaps.net returned HTTP 403 to the fetch tool, and elektroda.com/.pl returned 503 or HTTP/2 errors. Thread bodies on those sites could not be read. Where a finding comes only from a search-result snippet or title, it is marked "(snippet only)". No Reddit thread or YouTube video specific to CU7100/CU7000 turned up in search. That doesn't prove none exist, only that the search engine didn't surface them.

## What are the most common causes of "TV won't turn on" on Samsung CU7100/CU7xxx 65" TVs?

### Takeaway
No CU7100-specific repair thread with a confirmed root cause could be read in full. The sources that were readable, mostly for older Samsung edge/direct-LED series, point to three cause groups, in order of how often they are reported:
1. LED backlight failure. The TV is actually "on": sound plays, or the image shows under a torch, and a shorted backlight can also make the standby LED blink.
2. Power supply failure: blown fuse with shorted MOSFETs, or bad capacitors.
3. Main board failure.
Basic checks (outlet, remote, power cycle) come first.

### Cited Findings
- **CU7100 65" case (UK, JustAnswer, snippet only, date not visible):** the title reads "My Samsung Series 7 CU7100 65" 4K Ultra HD Smart TV has no backlight, ive had the tv for 2 weeks and its was working". The expert advice in the snippet: the picture is visible under a torch, so inspect the LED strips for damage or disconnection, and the fix is usually replacing the LED strips or the "inverter"/power board. This is the closest exact-model report found. — [JustAnswer UK](https://www.justanswer.co.uk/tv-repair/pa7ys-samsung-series-cu7100-65-4k-ultra-hd-smart-tv-no.html)
- **UE65CU7100 "TV not turning on" thread** on the Samsung EU community: URL found, content blocked (403). — [Samsung EU Community](https://eu.community.samsung.com/t5/tv/tv-not-turning-on/td-p/7301064)
- **UE50CU7100KXXU "backlight not working"** thread on the Samsung EU community (thread id 12233357, so likely 2024-2025): URL found, content blocked. This is a second exact-series backlight report. — [Samsung EU Community](https://eu.community.samsung.com/t5/tv/led-uhd-ue50cu7100kxxu-backlight-not-working/td-p/12233357)
- **CU7000 (US twin of the CU7100) sound-no-picture reports:** several user Q&A posts on asktech.support (UN43CU7000D, 43CU7000FXZA, UN43CU7000B). The advice in them points to a backlight or power supply fault. These are low-quality Q&A sources. — [asktech UN43CU7000D](https://www.asktech.support/tv-repair/tmqfu-tv-model-un43cu7000d-no-picture.html), [asktech 43CU7000FXZA](https://www.asktech.support/tv-repair/sg55d-sound-no-pictures-tv-samsung-43cu7000fxza.html), [asktech UN43CU7000B](https://www.asktech.support/tv-repair/uf8t0-samsung-tv-sound-no-picture-fix.html)
- **Analogous older model (UE65TU7100, 2020):** the standby LED flashed intermittently and the TV would not turn on, getting worse over months. Resets and a new plug didn't help. No resolution in the snippet. — [Samsung EU Community](https://eu.community.samsung.com/t5/tv/ue65tu7100kxxu-goes-completely-dead-for-several-days-days/td-p/4332540)
- **What the standby LED means:** Samsung support says LED off means no power, or the set is on with a black screen. A flashing LED means a power problem or an internal component fault. If it keeps blinking after a power cycle, Samsung treats it as a hardware fault. — [Samsung Levant](https://www.samsung.com/levant/support/tv-audio-video/how-to-troubleshoot-samsung-tv-that-will-not-turn-on/), [Samsung AE](https://www.samsung.com/ae/support/tv-audio-video/how-to-fix-a-samsung-tv-that-wont-power-on/)
- **iFixit Samsung troubleshooting:** a blinking standby is most likely the power supply board, "but there are a significant number of other potential causes". It also says a blinking standby light can indicate a shorted backlight. — [iFixit Samsung TV Won't Turn On](https://www.ifixit.com/Troubleshooting/Samsung_Television/Samsung+TV+Will+Not+Turn+On/482914)
- **Capacitors:** older Samsung generations shipped with under-rated capacitors on the power board, and bulged caps are a classic no-power cause (older series, analogous only). — [Instructables](https://www.instructables.com/Samsung-TV-OnOff-Issue-Repair/), [AVForums (older LCD)](https://www.avforums.com/threads/cheap-and-easy-repair-to-samsung-lcd-tv-power-supply.1142142/)
- **Elektroda (Polish), older Samsung UE55MU6172 (2017), red LED blinking about once a second, won't start.** Rule of thumb from members: if the LED lights, suspect the main board; if it stays dark, suspect the LEDs or the power supply. Also try disconnecting the main-board-to-panel ribbon cables. — [elektroda.pl topic3953468](https://www.elektroda.pl/rtvforum/topic3953468.html)
- **Elektroda (snippet only, unspecified Samsung models):** one fix was replacing punctured MOSFETs and checking capacitors. In another, replacing swollen capacitor CB852 plus six larger capacitors fixed a no-start, although the set still did not start on the first press. — elektroda search results: [topic4076003](https://www.elektroda.pl/rtvforum/topic4076003.html), [topic4125626](https://www.elektroda.pl/rtvforum/topic4125626.html), [topic4177128](https://www.elektroda.pl/rtvforum/topic4177128.html). Which snippet belongs to which topic could not be verified because the pages wouldn't load.

### Inferences
- The CU7100 is a low-cost direct-LED set. The pattern seen across 2018-2023 Samsung 7-series models (NU/RU/TU/AU/CU7100) is that "dead" sets with sound, or with a faint image under a torch, are most often LED strip failures. True no-standby faults point to the PSU (fuse, MOSFET, caps). The two exact-model reports found (CU7100 65" and UE50CU7100) both concern the backlight, which fits this pattern but is too small a sample to call a statistic.
- Separately, the tab-tv model guide says CU7100/CU7170/CU7179 etc. are regional variants of the same set. Findings for the CU7000 (US) and CU7172 (EU) are therefore likely transferable to the UE65CU7100K. — [tab-tv](https://en.tab-tv.com/samsung-crystal-uhd-2023-series-tvs-explanation-of-the-differences/)

### Gaps
- No full, readable CU7100/CU7000 thread with a confirmed root cause and fix was retrieved, because the forums were blocked.
- No failure-rate data exists for this series.
- No CU7100-specific Reddit thread was found.

## Which specific components fail on the power board or main board (BN94-18054A), and how were they found?

### Takeaway
No source found discusses component-level failures on BN94-18054A specifically. That exact suffix doesn't appear in any indexed listing. Sibling boards BN94-18054L and BN94-18054D are main boards on PCB **BN41-02992A**, sold for UN70/75/85CU7000. On the 65" US CU7000, the part sold as the "power supply" (BN96-56550K) carries the main-board chassis label **KANTSU2E_CU7000**. This suggests the 2023 CU7000/CU7100 uses a combined main + power board on at least some sizes. Component-level failure reports found are all from older Samsung PSUs: fuse, primary MOSFETs, and capacitors.

### Cited Findings
- BN94-18054L main board = BN97-20449D / PCB BN41-02992A, sold for UN85CU7000DX. — [TV Parts Today](https://tvpartstoday.com/products/bn94-18054l-samsung-main-board-bn97-20449d-bn41-02992a-un85cu7000dxza), [TvPartsGuy](https://www.tvpartsguy.com/bn94-18054l-samsung-main-board-bn41-02992a-bn97-20449d/)
- BN94-18054D = BN97-20671D / BN41-02992A, for UN85CU7000F. — [TV Parts Today](https://tvpartstoday.com/products/bn94-18054d-samsung-main-bn94-18054d-bn97-20671d-bn41-02992a-un85cu7000fxza)
- BN94-18054L is listed for UN70CU7000 (panel CY-BC070HGSV5H) and UN75CU7000 (panel CY-BC075HGHV2H, version CF02). — [eBay 70"](https://www.ebay.com/itm/126699371608), [eBay 75"](https://www.ebay.com/p/5062341728), [TV Parts Canada](https://tvpartscanada.ca/tv-parts/boards/main-boards/samsung-bn94-18054l-main-board-for-un75cu7000f-version-cf02/)
- **UN65CU7000 (version CA04):** "power supply" BN96-56550K plus LED strips BN96-50313A / BN96-50314A. Labels visible on the original parts include KANTSU2E_CU7000C0B, BA65FA210 and SVC650AG6_R / SVC650AG6_L (strip labels). — [ShopJimmy bundle](https://www.shopjimmy.com/samsung-un65cu7000-power-supply-led-backlight-strips-bundle/)
- A second ShopJimmy bundle is named "Main/Power Supply/LED Backlight Strips", with power supply BN96-57056A for the UE01 version. That name supports the combined main/power board reading. — [ShopJimmy bundle 1](https://www.shopjimmy.com/samsung-un65cu7000-power-supply-led-backlight-strips-bundle-1/)
- An eBay listing names **BN96-57056L "Main Power Supply"** for UN65CU7000FXZA, panel CY-BC065HGSV9H. — [eBay](https://ebay.com/itm/135255364107)
- On UN50CU7000, a "BN96-57568C-COMBO Main Board / Power Supply" is labeled KANTSU2E with BA55FA160. — [TV Parts Today collection](https://tvpartstoday.com/collections/samsung?page=165)
- The 65" CU8000 uses a separate PSU, BN44-01111E/D (L65E6N_BHS). — [TV Parts Today](https://tvpartstoday.com/products/bn44-01111e-samsung-power-supply-bn44-01111d-un65cu8000f-un65cu8000fxza)
- **Analogous older series, component level.** On Samsung PSU BN44-00874C (UN75NU7100, 2018), the main fuse and two primary MOSFETs QP801CS/QP802CS were burnt. A replacement fuse and MOSFETs blew again on power-up. The advice given: also replace the related ceramic caps and test under load. — [Badcaps](https://www.badcaps.net/forum/troubleshooting-hardware-devices-and-electronics-theory/troubleshooting-tvs-and-video-sources/3632743-samsung-tv-un75nu7100-power-board-bn44-00874c), [AllAboutCircuits](https://forum.allaboutcircuits.com/threads/samsung-tv-powerboard-blown-mosfets.205783/)
- **Repairer advice:** a blown fuse is a symptom. Find the shorted MOSFET (and, for example, a zener it took out) before fitting a new fuse. — [EEVblog](https://www.eevblog.com/forum/repair/samsung-monitor-doesn_t-work-fuse-blow-up/), [iFixit fuse blows instantly](https://www.ifixit.com/Answers/View/714284/Power+board+faulty,+fuse+blows+immediately+when+plugged+in)

### Inferences
- The UE65CU7100K's main board is probably part of the BN94-18054x / BN41-02992A (KANT-SU2E) family. On 65" units the power stage may sit on the same board, sold as BN96-56550K / BN96-57056x assemblies. That would make "PSU vs main board" one assignment, and a no-power fault often a single-board swap. This needs confirming against the actual board label in the user's set.
- On 2023 KANT-SU2E boards, typical PSU failure points would by analogy be the mains fuse, bridge, primary MOSFET(s), bulk/secondary capacitors and the backlight boost stage. There is no direct evidence for this chassis.

### Gaps
- No source names BN94-18054A or gives its component-level fault history.
- No schematic or service-manual excerpt for KANT-SU2E (CU7xxx) was found.
- It isn't confirmed whether the EU UE65CU7100K uses a combined board or a separate BN44 PSU.

## Are LED backlight strip failures common on this series, and how do people test them?

### Takeaway
Backlight failures are the most frequently reported "dead with sound" symptom in what was found for CU7000/CU7100. Two exact-series threads and several CU7000 Q&As describe it, and parts sellers bundle PSU and strips together for the UN65CU7000. The standard tests are: torch test for a faint image, a backlight tester on each strip or LED, and measuring backlight output at the PSU connector. A failed strip can also make the standby LED blink or the set cycle.

### Cited Findings
- Exact-series reports: CU7100 65" no backlight after 2 weeks ([JustAnswer UK](https://www.justanswer.co.uk/tv-repair/pa7ys-samsung-series-cu7100-65-4k-ultra-hd-smart-tv-no.html)), UE50CU7100KXXU backlight not working ([Samsung EU](https://eu.community.samsung.com/t5/tv/led-uhd-ue50cu7100kxxu-backlight-not-working/td-p/12233357)), UN43CU7000 sound-no-picture ([asktech](https://www.asktech.support/tv-repair/sg55d-sound-no-pictures-tv-samsung-43cu7000fxza.html)).
- ShopJimmy sells a PSU plus BN96-50313A/50314A strip bundle for the UN65CU7000. This suggests sellers expect strip faults to take the PSU with them, or the reverse, though the page doesn't say so. — [ShopJimmy](https://www.shopjimmy.com/samsung-un65cu7000-power-supply-led-backlight-strips-bundle/)
- Aftermarket strip kits are sold for UE50CU7172U / UE50CU7170U / UE50CU71A0K and for 70"/75" CU7000/CU8000 (seller compatibility claims, unverified). — [AliExpress](https://www.aliexpress.us/item/3256810202021071.html), [eBay 75"](https://www.ebay.com/itm/205863153995)
- **Torch/flashlight test:** if the image is visible under a light, the panel and main board are working and the backlight has failed. — [iFixit](https://www.ifixit.com/Answers/View/371960/Why+tv+is+on,+volume+works+and+can+see+a+picture+if+you+shine+light+on)
- **Strips are wired in series,** so one failed LED darkens everything. Test each strip with an LED backlight tester. — [TV Parts Today guide](https://tvpartstoday.com/blogs/blog/diagnosing-and-fixing-your-tv-symptoms-of-backlight-failure-and-replacement-guide)
- **Measuring backlight output at the PSU connector.** UN65TU700DF (2020, analogous) has picture and sound but no backlight. The member reports "BL tests ok", yet replacing the PSU didn't fix it. A related snippet reports roughly 100V and 64V on the backlight connector pins. — [Badcaps UN65TU700DF](https://www.badcaps.net/forum/troubleshooting-hardware-devices-and-electronics-theory/troubleshooting-tvs-and-video-sources/108262-un65tu700df-picture-and-sound-but-no-backlight-bl-tests-ok-but-repl-psu-didnt-fix) (snippet only; thread blocked)
- **Interpreting the readings:** if the backlight never lights, replace the strips. Less voltage than expected, or none, at the backlight array points to the power board. — [iFixit un65h6203 SOLVED](https://www.ifixit.com/Answers/View/651982/Samsung+tv+has+sound+and+picture+no+backlight.+(backlight+can+flash))
- **Buy strips by the panel/strip part number, not the TV model.** The same model can use different strips. — [Tech Junctions](https://techjunctions.com/how-to-fix-backlight-on-samsung-tv/)
- **Video (older model, analogous):** "How to Fix a Samsung TV Blinking Red Light (Backlight Repair)". — [YouTube lz0oBoUv4BM](https://www.youtube.com/watch?v=lz0oBoUv4BM)

### Inferences
- For a UE65CU7100K that shows standby but no picture, or blinks, the backlight is the first suspect. Do the torch test, then test the strips (SVC650AG6-type 65" strips on the US twin) before replacing boards.

### Gaps
- No CU7100-specific strip voltage spec (Vf per strip / total string voltage) was found.
- No CU7100-specific YouTube teardown was found.

## Which threads/videos give step-by-step measurements (voltages at connectors) for this chassis?

### Takeaway
None were found for the CU7100/KANT-SU2E chassis. The only measured-voltage material comes from older Samsung series: the TU7000 badcaps thread and NU7100 PSU threads. These give an analogous procedure, but the values are not this chassis's.

### Cited Findings
- **Isolation procedure:** unplug the main board from the PSU and power the PSU alone. If no light shows through the screw holes, suspect the PSU. If light appears, move on to the main board. — [iFixit](https://www.ifixit.com/Answers/View/389926/Power+light+and+screen+blinking)
- **Fuse-blow procedure** (older PSU): check the MOSFETs, diodes and nearby caps in diode mode, check for a short after the fuse, and test with a series lamp or load before fitting a new fuse. — [Badcaps BN44-00874C](https://www.badcaps.net/forum/troubleshooting-hardware-devices-and-electronics-theory/troubleshooting-tvs-and-video-sources/3632743-samsung-tv-un75nu7100-power-board-bn44-00874c)
- **Backlight connector readings** of about 100V/64V on an older Samsung set (snippet only). — [Badcaps UN65TU700DF](https://www.badcaps.net/forum/troubleshooting-hardware-devices-and-electronics-theory/troubleshooting-tvs-and-video-sources/108262-un65tu700df-picture-and-sound-but-no-backlight-bl-tests-ok-but-repl-psu-didnt-fix)
- **Standby rail check:** confirm the standby voltage reaches the main board. Without it the TV will not respond; with it, the main board or remote/IR board is suspect. — [Tom's Guide](https://forums.tomsguide.com/threads/samsung-tv-will-not-come-out-of-standby.117690/latest), [TV Parts Today no-power guide](https://tvpartstoday.com/blogs/blog/samsung-tv-no-power-repair-which-circuit-board-is-faulty)
- An elektroda English-section CU-era thread (topic4160277) appeared in "Samsung CU7000 no picture" results, but the page could not be loaded (503). — [elektroda.com topic4160277](https://www.elektroda.com/rtvforum/topic4160277.html)

### Inferences
- A practical sequence for the UE65CU7100K, built from these analogous sources:
  1. Do a power cycle and check the outlet and remote.
  2. Note the standby LED state: off, steady or blinking.
  3. Do the torch test.
  4. Open the back, look for a blown fuse or bulged caps, and check for a short across the MOSFETs.
  5. Check the standby/12V rail to the main section.
  6. Measure the backlight output, or test each strip with an LED tester.
  7. Swap the main/power assembly only after the strips test good.

### Gaps
- No CU7100/KANT-SU2E connector pinout, rail voltages (e.g. 12V/13V main, standby) or backlight string voltage was found in any accessible source.
- The service manual and a dedicated measurement thread remain unfound. Elektroda (Polish section, search "UE65CU7100" / "BN41-02992A") and badcaps are the most promising places to retry from an unblocked browser.

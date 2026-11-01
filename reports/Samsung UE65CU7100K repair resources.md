# Find the power board, then test it

No public page gives a step-by-step repair for the Samsung UE65CU7100K. There is no free service manual, schematic or power-board pinout. The best pages are general Samsung "no power" guides (iFixit, TVPartsToday), parts listings that help identify your boards, and a small number of reports for this exact model, which all describe **backlight failure**. Your main board, **BN94-18054A** (assembly BN96-57053E), is confirmed by UK sellers as the main board for the UE65CU7100KXXU ([eBay UK](https://www.ebay.co.uk/b/bn_7022856865)). Because it takes 13 V on CN201, your TV has a separate power/LED-driver board. The most likely power board is **BN44-01055A (code L65S6N_TDY)**. This is inferred, not confirmed: read the sticker on your board. The most useful next step is to photograph that sticker. After that, check the 13 V output and test the LED strips. Your DM303 is good for fuses, diodes and DC voltages, but weak for testing TV LEDs.

**How to read the labels below.** **Read** = the page was opened and checked. **Snippet** = only the search-result text was seen, not the full page. **Blocked** = the page exists but could not be opened (HTTP 403/503), so its content is unknown. **Inferred** = a conclusion drawn from several sources, not stated by any of them.

## Safety comes first: the power board can kill after unplugging

The "HOT" (primary) side of the power board has a large capacitor of about **400 V DC** that can stay charged after you unplug the TV. Discharge it through a resistor (for example 10 kΩ, 2–5 W, with insulated leads), never with a screwdriver. Then measure it, and repeat until it reads **10 V or less** ([Restarters wiki](https://wiki.restarters.net/How_to_safely_discharge_capacitors)). With the TV plugged in, measure only on the low-voltage "cold" side, such as the 13 V output connector, and use the cold ground. Never mix hot and cold grounds (inferred from several guides). Note that LED backlight testers also produce up to 300 V. Lay the 65" panel face-down on a soft, flat surface ([TVPartsToday](https://tvpartstoday.com/blogs/blog/samsung-tv-no-power-repair-which-circuit-board-is-faulty)).

| Page | What it gives you | Status |
|---|---|---|
| [Restarters: safely discharge capacitors](https://wiki.restarters.net/How_to_safely_discharge_capacitors) | Clear method, resistor value, timing rule | Read |
| [DigiKey: discharge a capacitor](https://www.digikey.com/en/blog/how-to-safely-discharge-a-capacitor) | Second guide | Read (search) |
| [Instructables: discharge tool](https://instructables.com/Safe-Capacitor-Discharge-Tool) | Build a simple tool | Read (search) |
| [repairfaq.org TV safety FAQ](https://repairfaq.org/samnew/tvfaq/tvsafdis.htm) | Classic safety rules (old CRT era, principles still apply) | Read (search) |

## Official Samsung pages: useful for warranty and manuals, not for board repair

Samsung publishes only user manuals, firmware and consumer troubleshooting. There is no service manual (it is behind the dealer-only GSPN portal). **Check your warranty before you continue.** Some UK retailers sold this model with a **free 5-year promotional warranty** that had to be registered ([Euronics UK](https://www.euronics.co.uk/p/SAMUE65CU7100KXXU)), and opening the TV may void it ([Samsung UK warranty](https://www.samsung.com/uk/support/warranty/)). Firmware cannot fix a TV that does not power on at all.

| Page | What it gives you | Status |
|---|---|---|
| [Samsung UK model page UE65CU7100KXXU](https://www.samsung.com/uk/support/model/UE65CU7100KXXU/) | User manual, e-Manual, firmware, links to repair | Read |
| [Samsung UK: book a repair](https://www.samsung.com/uk/support/repair/) | Official repair booking | Read (link) |
| [Samsung UK warranty](https://www.samsung.com/uk/support/warranty/) | 12-month standard warranty, 5-year promo rules | Read |
| [Samsung UK: my TV won't turn on](https://www.samsung.com/uk/support/tv-audio-video/my-tv-wont-turn-on/) | Showed only a "maintenance" notice | Read, but empty |
| [Samsung Lebanon: TV will not turn on](https://www.samsung.com/lb/support/tv-audio-video/how-to-troubleshoot-samsung-tv-that-will-not-turn-on/) | What the standby light means: solid = power OK, off = no power, blinking = hardware fault | Read |
| [Samsung Singapore: Self Diagnosis](https://www.samsung.com/sg/support/tv-audio-video/self-diagnosis-options-on-your-samsung-tv-and-smart-monitor/) | Built-in tests. Works only if the TV boots | Read |

## Step-by-step diagnosis guides: iFixit and TVPartsToday are the best two

These two pages give the clearest sequence: check the socket and do a reset, read the standby LED, do a **torch test** (shine a light on the screen; a faint picture means the backlight has failed), inspect the power board and fuse, measure the outputs, then unplug the main board to see which board is faulty ([iFixit wiki](https://www.ifixit.com/Wiki/Samsung_TV_Will_Not_Turn_On); [TVPartsToday](https://tvpartstoday.com/blogs/blog/samsung-tv-no-power-repair-which-circuit-board-is-faulty)). One iFixit answer says the standby point reads about **8 V in standby and 13 V when on**. With only the main board cable unplugged, 13 V should be present. Another user reports different values, so the numbers vary by board ([iFixit Answers](https://proxy.ifixit.com/Answers/View/776153/TV+will+not+power+up)). A blown fuse is a symptom: find the shorted MOSFET before you fit a new fuse ([iFixit](https://www.ifixit.com/Answers/View/714284/Power+board+faulty,+fuse+blows+immediately+when+plugged+in); [EEVblog](https://www.eevblog.com/forum/repair/samsung-monitor-doesn_t-work-fuse-blow-up/)).

| Page | What it gives you | Status |
|---|---|---|
| [iFixit wiki: Samsung TV Will Not Turn On](https://www.ifixit.com/Wiki/Samsung_TV_Will_Not_Turn_On) | Full beginner sequence, torch test, board isolation | Read |
| [iFixit troubleshooting page](https://www.ifixit.com/Troubleshooting/Samsung_Television/Samsung+TV+Will+Not+Turn+On/482914) | A blinking standby light can mean a shorted backlight | Read |
| [TVPartsToday: which board is faulty](https://tvpartstoday.com/blogs/blog/samsung-tv-no-power-repair-which-circuit-board-is-faulty) | Visual checks, rail measurements, BN44/BN94/BN96 meaning | Read |
| [TVPartsToday video playlist](https://www.youtube.com/watch?v=0kyA_PHJx5g&list=PLc3yCKcEGD_qbxKxSgI44MyvUk2gcLStg) | "Troubleshooting 101" videos | Link only, not watched |
| [iFixit Answers: 8 V / 13 V checks](https://proxy.ifixit.com/Answers/View/776153/TV+will+not+power+up) | Standby and 13 V test, diode checks | Read |
| [iFixit: isolate PSU from main board](https://www.ifixit.com/Answers/View/389926/Power+light+and+screen+blinking) | Run the PSU alone and look for backlight | Read |
| [Badcaps: BN44-00874C blown MOSFETs](https://www.badcaps.net/forum/troubleshooting-hardware-devices-and-electronics-theory/troubleshooting-tvs-and-video-sources/3632743-samsung-tv-un75nu7100-power-board-bn44-00874c) | Fuse and MOSFET repair on an older Samsung PSU | Snippet (blocked) |
| [Elektroda: BN44 no-start causes](https://www.elektroda.com/qa,samsung-bn44-00339a-issues-fixes.html) | Start-up capacitor, fuse, transistors | Read |
| [ShopJimmy: which part to replace](https://blog.shopjimmy.com/samsung-tv-wont-turn-on-which-part-should-you-replace) | Board-choice guide | Blocked (503) |

**What this means for your CN201 (inferred, not from a CU7100 source).** With the power board connected to mains and the main board removed, measure DC between pins 4–6 (A13V) and pin 1, 3, 7 or 10 (GND) of the cable that goes to CN201. If you see 13 V, the power board's main rail works. If you see nothing, some Samsung boards need the power-on pin (pin 2) pulled high before they turn on. Check the silkscreen on your power board before you bridge anything. Note also that pins 8 and 9 (dimming) control the backlight, so the backlight may stay off when the main board is not connected.

## Reports for this exact model all point to the backlight

Only a few exact-series reports exist, and most could not be read in full. All of them describe **backlight failure** (sound plays or a picture shows under a torch, but the screen is dark). This is a small sample, not a statistic ([JustAnswer UK](https://www.justanswer.co.uk/tv-repair/pa7ys-samsung-series-cu7100-65-4k-ultra-hd-smart-tv-no.html)). The CU7000 (US) and CU7170/CU7172 (EU) are regional versions of the same set, so their reports are likely relevant ([tab-tv](https://en.tab-tv.com/samsung-crystal-uhd-2023-series-tvs-explanation-of-the-differences/)).

| Page | What it gives you | Status |
|---|---|---|
| [JustAnswer UK: CU7100 65" no backlight](https://www.justanswer.co.uk/tv-repair/pa7ys-samsung-series-cu7100-65-4k-ultra-hd-smart-tv-no.html) | Closest exact-model case: strips or power board | Snippet (blocked) |
| [Samsung EU Community: UE65CU7100 not turning on](https://eu.community.samsung.com/t5/tv/tv-not-turning-on/td-p/7301064) | Exact model thread | Blocked (403) |
| [Samsung EU Community: UE50CU7100 backlight](https://eu.community.samsung.com/t5/tv/led-uhd-ue50cu7100kxxu-backlight-not-working/td-p/12233357) | Same series, backlight fault | Blocked (403) |
| [asktech: 43CU7000 sound, no picture](https://www.asktech.support/tv-repair/sg55d-sound-no-pictures-tv-samsung-43cu7000fxza.html) | US twin, backlight/PSU advice (low quality) | Read |
| [Samsung EU: UE65TU7100 goes dead](https://eu.community.samsung.com/t5/tv/ue65tu7100kxxu-goes-completely-dead-for-several-days-days/td-p/4332540) | Older 65" 7100, blinking standby | Snippet |
| [Elektroda: CU7000 no picture](https://www.elektroda.com/rtvforum/topic4160277.html) | CU-era thread | Blocked (503) |
| [elektroda.pl: UE55MU6172 blinking LED](https://www.elektroda.pl/rtvforum/topic3953468.html) | Rule of thumb for PSU vs main board (older model) | Read |

## Board identification: the sticker on your power board decides everything

**Your main board is confirmed:** BN94-18054A is sold as the main AV board for UE65CU7100KXXU ([eBay UK](https://www.ebay.co.uk/b/bn_7022856865), snippet), sometimes as a "main and power board set" ([eBay.ie](https://www.ebay.ie/sch/i.html?_nkw=bn94-), snippet). Another UK site lists **BN94-18053B** for UE65CU7100KXXU version 02, so the board differs by version. Always match the BN number on the sticker, not just the model name ([tvparts.co.uk](https://www.tvparts.co.uk/lcd-tv-spares/main-pcb-lcd/samsung-2?sort=p.model&order=DESC&limit=75&page=6), snippet). **The power board is not confirmed.** BN44-01055A (L65S6N_TDY) is the best guess, because a UK seller lists a "UE65CU7100K Power Supply 65S6" ([SJS TV](https://www.sjstv.co.uk/parts-shop/all-categories/power-supplies), snippet) and a Russian seller groups BN44-01055A with UE65CU7100 (no URL captured). BN44-01056C is for the **75"** model, not yours ([ShopJimmy](https://www.shopjimmy.com/samsung-bn44-01056c-power-supply-led-board/)). Be careful with US pages: the US 65" CU7000 uses a combined main + power board (BN96-56550K), which is different from your set ([ShopJimmy](https://www.shopjimmy.com/samsung-bn96-56550k-main-board-power-supply-for-un65cu7000dxza-ca04)).

| Page | What it gives you | Status |
|---|---|---|
| [ShopJimmy BN44-01055A + strips combo](https://www.shopjimmy.com/samsung-bn44-01055a-bn96-50313a-bn96-50314a-power-supply-backlight-strips-combo) | Likely power board, photos, code L65S6N_TDY | Read |
| [SJS TV power supplies (UK)](https://www.sjstv.co.uk/parts-shop/all-categories/power-supplies) | "UE65CU7100K Power Supply 65S6" listing | Snippet |
| [tvparts.co.uk UE65TU7100 ver:01](https://www.tvparts.co.uk/TV-parts-for-Samsung-Ue65tu7100kxxu+ver:01) | BN44-01055A in the older 65" 7100 | Snippet |
| [eBay UK main AV boards](https://www.ebay.co.uk/b/bn_7022856865) | BN94-18054A for UE65CU7100KXXU | Snippet |
| [tvparts.co.uk main PCB list](https://www.tvparts.co.uk/lcd-tv-spares/main-pcb-lcd/samsung-2?sort=p.model&order=DESC&limit=75&page=6) | Board numbers by version | Snippet |
| [TVPartsToday BN94-18054L](https://tvpartstoday.com/products/bn94-18054l-samsung-main-board-bn97-20449d-bn41-02992a-un85cu7000dxza) | Sibling board, PCB BN41-02992A | Read |
| [tvspareparts.co.uk UE55CU7100K PSU](https://tvspareparts.co.uk/product/power-supply-psu-samsung-ue55cu7100k-led-tv-3in1-kant-su2e-50-55-inch-rev-1-4/) | 55" sibling PSU (KANT-SU2E) | Blocked |

## Backlight testing: your DM303 is not enough for the LED strips

The likely strip set is **BN96-50313A + BN96-50314A (10 strips, marked SVC650AG6_R / _L)**. This is confirmed for the US 65" CU7000 ([ShopJimmy](https://www.shopjimmy.com/samsung-bn96-50313a-bn96-50314a-led-backlight-bars-strips-10-strips)) and only inferred for your EU set. Buy strips by the code printed on the strip, not by the TV model ([Tech Junctions](https://techjunctions.com/how-to-fix-backlight-on-samsung-tv/)). A multimeter's diode test uses about 3 V, and TV LEDs often need about 6 V each, so in-circuit readings are confusing ([All About Circuits](https://forum.allaboutcircuits.com/threads/testing-leds-back-light-on-a-tv.185038/)). A cheap **0–300 V LED backlight tester** lights each LED or strip and shows the dead one ([Jestine Yong](https://jestineyong.com/a-tv-with-faulty-backlight-repaired-and-maintained/)). If the strips light on the tester but not in the TV, the LED driver on the power board is the likely fault ([Elektroda Q&A](https://www.elektroda.com/qa,tv-backlight-not-working.html)). No source gives the LED voltage for this model.

| Page | What it gives you | Status |
|---|---|---|
| [TVPartsToday: backlight failure guide](https://tvpartstoday.com/blogs/blog/diagnosing-and-fixing-your-tv-symptoms-of-backlight-failure-and-replacement-guide) | Strips are in series; one bad LED darkens all | Read |
| [iFixit: torch test](https://www.ifixit.com/Answers/View/371960/Why+tv+is+on,+volume+works+and+can+see+a+picture+if+you+shine+light+on) | Confirms a backlight fault | Read |
| [iFixit: no backlight SOLVED](https://www.ifixit.com/Answers/View/651982/Samsung+tv+has+sound+and+picture+no+backlight.+(backlight+can+flash)) | How to read the backlight voltage results | Read |
| [All About Circuits: testing TV LEDs](https://forum.allaboutcircuits.com/threads/testing-leds-back-light-on-a-tv.185038/) | Multimeter limits; bench supply 13.6 V / 20 mA method | Read |
| [Jestine Yong: faulty backlight repair](https://jestineyong.com/a-tv-with-faulty-backlight-repaired-and-maintained/) | Real repair using an LED tester | Read |
| [ManoMano UK: 0–300 V LED tester](https://www.manomano.co.uk/p/ca-300v-portable-led-lamp-beads-light-bar-tv-backlight-tester-led-strip-beads-lamp-panel-test-tool-capacitance-diode-voltage-test-with-switch-by-debuns-86282165) | Typical tester you can buy in Europe | Read |
| [Tindie: LED backlight tester kit](https://www.tindie.com/products/jasonkits/led-tv-backlight-and-zener-tester) | Current-limited kit tester | Read |
| [YouTube: Samsung blinking red light, backlight repair](https://www.youtube.com/watch?v=lz0oBoUv4BM) | Video for an older model | Link only, not watched |
| [Badcaps: UN65TU700DF no backlight](https://www.badcaps.net/forum/troubleshooting-hardware-devices-and-electronics-theory/troubleshooting-tvs-and-video-sources/108262-un65tu700df-picture-and-sound-but-no-backlight-bl-tests-ok-but-repl-psu-didnt-fix) | About 100 V / 64 V on the backlight connector (older 65") | Snippet (blocked) |

## Conclusion

The missing piece is not on the web. It is the sticker on your power board. Once you have the BN44 number and the L65S… code, the ShopJimmy and SJS listings will either confirm BN44-01055A or point to the right variant, and you can match photos and connector labels. The evidence suggests the backlight is the first suspect. A cheap LED tester (about EUR 15–30, price not sourced) will probably tell you more than any page here, and it costs less than a guessed board swap.

If you want to search further, the most promising places are the blocked ones: Samsung EU Community, Elektroda (search "UE65CU7100" or "BN44-01055A") and Badcaps. Open them in a normal browser. No source found gives the CN201 pinout, standby voltage or LED driver voltage for this chassis, so treat any number you find online as belonging to a similar board, not to your exact board.

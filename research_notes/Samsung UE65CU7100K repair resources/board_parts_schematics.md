# Samsung UE65CU7100K: boards, part numbers, schematics and voltages

Context from the user: main board BN94-18054A (assembly BN96-57053E, label "3IN1-C T2C 65 SESK"). The power input connector CN201 is pin 1 DGND, 2 power-on, 3 DGND, 4-6 A13V, 7 DGND, 8 ANA_DIM, 9 PWM_DIM, 10 DGND. This pinout came from the user and was not found online.

Research limits: elektroda.pl and elektroda.com threads, sjstv.co.uk detail pages and ebay.co.uk item pages returned HTTP 503 or 403 to the fetch tool. tvspareparts.co.uk is blocked by the session network allowlist. Several findings below therefore rest on search-engine snippets rather than full page reads, and are marked "(snippet only)".

## Q1: Which BN44 power board does UE65CU7100K use (and variants)? Pinout or output voltages?

### Takeaway
No source confirms a BN44 number for the 65" UE65CU7100K. The best lead is BN44-01055A (PSU code L65S6N_TDY), the 65" TU7000/TU7100 power and LED board. A Russian seller groups it with UE65AU7100 and UE65CU7100, and a UK seller names a "UE65CU7100K Power Supply 65S6", which fits the L65S6 code. BN44-01056C belongs to the 70/75" sets, not the 65". I found no published pinout or output voltages for any of these boards.

### Cited Findings
- BN44-01055A is a 65" power supply/LED board, internal code **L65S6N_TDY**, used with LED strips BN96-50313A/BN96-50314A. Listed models: UN65TU7000F, UN65TU700DF, UN65TU8000F, UN65TU8200F, LH65BETHLGFXGO. No CU7100 is listed. Refurbished price $69.99, out of stock. No voltage or connector info. — [ShopJimmy BN44-01055A combo](https://www.shopjimmy.com/samsung-bn44-01055a-bn96-50313a-bn96-50314a-power-supply-backlight-strips-combo)
- A Russian parts seller (zipzonaspb.com) lists "BN44-01055A / BN4401055A / UE65AU7100 / UE65CU7100 NEW" at 2,000 RUB, article 1122533. (snippet only; I did not capture the exact product URL. The site's similar listings follow the pattern https://zipzonaspb.com/products/bn44-00807a-bn4400807a-ue49ku6300-ue55mu7100) — seller listing, not Samsung data
- tvparts.co.uk lists BN44-01055A as the PSU for the earlier UE65TU7100KXXU ver:01 (snippet only) — [tvparts.co.uk UE65TU7100KXXU ver:01](https://www.tvparts.co.uk/TV-parts-for-Samsung-Ue65tu7100kxxu+ver:01); also [ver:02](https://www.tvparts.co.uk/TV-parts-for-Samsung-Ue65tu7100kxxu+ver:02)
- SJS TV (UK) has a listing titled "Samsung UE65CU7100K Power Supply 65S6". The snippet showed no part number or price. — [SJS TV power supplies category](https://www.sjstv.co.uk/parts-shop/all-categories/power-supplies)
- BN44-01056C is the power board for the **75"** UE75CU7100K (eBay listing "Samsung UE75CU7100K Power Board - BN44-01056C") — [eBay 396776367682](https://www.ebay.com/itm/396776367682) (snippet only, 403 on fetch)
- BN44-01056C cross-references list 70" and 75" sets: UN70/75CU7000, UN75TU7000, UA75CU7100, UE75CU7100. It replaces BN44-01056A. — [ShopJimmy BN44-01056C](https://www.shopjimmy.com/samsung-bn44-01056c-power-supply-led-board/); [huoltopalvelu.com BN44-01056C](https://www.huoltopalvelu.com/Samsung-television-power-supply-BN44-01056C); [Paul's TV](https://paulstv.com/products/samsung-bn44-01056c-power-supply-for-un70tu7000-un70tu7000fxza-un75tu8000f-un75cu7000fxza); [iFixit](https://www.ifixit.com/products/bn44-01056c-samsung-power-supply-board); [PartSelect](https://www.partselect.com/PS16898519-Samsung-BN44-01056C-Power-Supply-Board.htm)
- BN44-01056A is listed for UE70TU7100 (SJS TV) — [sjstv UE70TU7100 BN44-01056A](https://sjstv.co.uk/all-categories/4589/samsung-ue70tu7100-power-supply-bn44-01056a-detail)
- The 65" CU8000 (US) uses BN44-01111E / BN44-01111D — [TVPartsToday BN44-01111E](https://tvpartstoday.com/products/bn44-01111e-samsung-power-supply-bn44-01111d-un65cu8000f-un65cu8000fxza); also sold on [Allegro Lokalnie "zasilacz BN4401111E Samsung 65"](https://allegrolokalnie.pl/oferta/zasilacz-bn4401111e-samsung-65)
- US 65" CU7000 sets use a single main+power board (BN96-56550K, board code KANTSU2E_CU7000C0B), with no separate BN44 — [ShopJimmy UN65CU7000 bundle](https://shopjimmy.com/samsung-un65cu7000-power-supply-led-backlight-strips-bundle); [ShopJimmy BN96-56550K](https://www.shopjimmy.com/samsung-bn96-56550k-main-board-power-supply-for-un65cu7000dxza-ca04); [eBay BN96-57056L for UN65CU7000FXZA](https://ebay.com/itm/135255364107)
- A 55" sibling PSU is sold as "POWER SUPPLY PSU SAMSUNG UE55CU7100K LED TV 3IN1 KANT-Su2e 50/55 INCH REV 1.4" (could not fetch, host blocked) — [tvspareparts.co.uk](https://tvspareparts.co.uk/product/power-supply-psu-samsung-ue55cu7100k-led-tv-3in1-kant-su2e-50-55-inch-rev-1-4/)
- The TV's mains input is AC 220-240 V, 50/60 Hz (Samsung spec, via search snippet) — [Samsung UK UE65CU7100KXXU](https://www.samsung.com/uk/business/tvs/uhd-4k-tv/cu7100-65-inch-ue65cu7100kxxu/)

### Inferences
- The user's main board takes 13 V (A13V) plus power-on and dimming signals on CN201. That means the EU 65" set has a separate PSU/LED-driver board, unlike the US UN65CU7000, where power and main are combined on BN96-56550K. Sources call the EU main board "3IN1" and "main AV board", and the US unit "main board power supply".
- BN44-01055A (L65S6N_TDY) is the most probable PSU. Three things point to it: the "65S6" naming on SJS, the Russian listing that groups it with UE65CU7100, and the fact that the 65" CU7000 reuses the TU7000's LED strips (BN96-50313A/50314A). **This is inferred, not confirmed.** A later suffix variant (e.g. BN44-01055B/C/D) is also possible. The user should read the sticker on the PSU, which shows the BN44 number and L65S6N code.
- On Samsung PSUs of this family, the 10-pin output to the main board typically matches CN201: 13 V on three pins, a power-on (PS_ON) input, and dimming lines. The LED driver sits on the same PSU board. This is general knowledge, not taken from a source, and should be verified on the board's silkscreen.

### Gaps
- No page found that confirms the BN44 number for UE65CU7100K (any version code).
- No page found with the PSU's output-connector pinout, standby voltage, 13 V tolerance, or LED driver open-circuit or operating voltage.
- The exact zipzonaspb product URL for BN44-01055A / UE65CU7100 was not captured.

## Q2: Is a service manual or schematic for the CU7000/CU7100 2023 chassis (or the power board) publicly available?

### Takeaway
I found no public service manual, schematic or PSU diagram for the 2023 CU7000/CU7100 chassis (KANT-SU2e) or for BN44-01055A/01056C. Samsung only publishes user manuals and e-manuals. Service manuals sit behind Samsung's GSPN dealer portal.

### Cited Findings
- Samsung support pages for CU7100 models list only user-facing downloads (e-Manual, user manual) and no service documentation — [Samsung MN UE65CU7100UXRU](https://www.samsung.com/mn/support/model/UE65CU7100UXRU/); [UE55CU7100UXCE](https://www.samsung.com/mn/support/model/UE55CU7100UXCE); [UE43CU7100UXCE](https://www.samsung.com/mn/support/model/UE43CU7100UXCE/); [n_africa UE43CU7100UXTK](https://samsung.com/n_africa/support/model/UE43CU7100UXTK)
- The Samsung MN support page for UE65CU7100U has a "TV won't turn on" troubleshooting article (consumer level only) — [Samsung MN UE65CU7100UXRU](https://www.samsung.com/mn/support/model/UE65CU7100UXRU/)
- Consumer-level troubleshooting FAQ for the exact model — [tvsfaq UE65CU7100K troubleshooting](https://www.tvsfaq.com/en/faq/samsung-ue65cu7100k); spec sheet: [tvsfaq specifications](https://www.tvsfaq.com/en/specifications/samsung-ue65cu7100k); panel spec (64.5" VA, 3840x2160): [displayspecifications](https://www.displayspecifications.com/fr/model/2e4c325f)
- Photofact sells paid OEM-derived service data for some Samsung models. I found no CU7100 entry, and US-model coverage is unconfirmed — e.g. [photofactonline example](https://photofactonline.com/en/photofact/details/index/id/80880)
- Elektroda search results showed generic Samsung "won't turn on" threads (blinking standby, PSU vs main-board isolation), but none specific to UE65CU7100. The two newest hits returned 503: [elektroda.pl topic4125626](https://www.elektroda.pl/rtvforum/topic4125626.html), [elektroda.com topic4125413](https://www.elektroda.com/rtvforum/topic4125413.html). One thread's snippet describes a common test: unplug the PSU-to-main cable and see whether the backlight comes on. If it does, the fault is likely on the main board.

### Inferences
- Without a schematic, the practical route is the standard Samsung PSU test. Disconnect CN201, pull the power-on pin up to the PSU's standby or 3.3-5 V rail through a resistor (or bridge it as shown on the PSU silkscreen), then check for 13 V output and whether the backlight lights. This is a common forum practice, not sourced to a CU7100 document here.

### Gaps
- No free or paid service manual located for UE65CU7100K / KANT-SU2e 2023. ElektroTanya, eserviceinfo and badcaps were not reached in this pass, because the fetch budget went to part-number confirmation.

## Q3: Pages selling/listing BN94-18054A or the power board, with photos or pinouts useful for diagnosis

### Takeaway
BN94-18054A with BN96-57053E is confirmed on UK eBay and parts sites as the main AV board for the UE65CU7100KXXU and UE65CU71A0KXXU. Some sellers also offer it as a "main and power board set". The 18054 suffix family covers other CU7000 sizes (D = 85" US, L = 70/75/85" US). No listing shows a pinout.

### Cited Findings
- eBay UK listing "MAIN AV BOARD FOR SAMSUNG UE65CU7100KXXU 65" TV BN94-18054A BN96-57053E", £89.99 (snippet only) — [eBay UK Samsung AV board category](https://www.ebay.co.uk/b/bn_7022856865)
- eBay listing "SAMSUNG UE65CU7100KXXU main and power board set / combo - BN94-18054A", EUR 89.73 plus EUR 9.57 postage from the UK (snippet only) — [eBay.ie search "bn94-"](https://www.ebay.ie/sch/i.html?_nkw=bn94-)
- lcd-tv-parts.com lists the same combo at £74.99, out of stock (snippet only) — [lcd-tv-parts.com BN94 search](https://www.lcd-tv-parts.com/catalogsearch/result/index/?aa_condition=32&mode=grid&q=BN94)
- tvparts.co.uk lists BN94-18054A as the main PCB for UE65CU71A0KXXU (versions 02 and 04). It also lists **BN94-18053B** as the main PCB for UE65CU7100KXXU VER:02, so the board differs by version (snippet only) — [tvparts.co.uk Samsung main PCB list, page 6](https://www.tvparts.co.uk/lcd-tv-spares/main-pcb-lcd/samsung-2?sort=p.model&order=DESC&limit=75&page=6)
- Sibling boards: BN94-18054L for UN75CU7000FXZA / UN70CU7000FXZA / UN85CU7000DXZA (BN97-20449D, BN41-02992A) — [TVPartsToday BN94-18054L](https://tvpartstoday.com/products/bn94-18054l-samsung-main-board-bn97-20449d-bn41-02992a-un85cu7000dxza); [Short Circuit Solution](https://shortcircuitsolution.com/products/samsung-bn94-18054l-main-board-for-un75cu7000fxza-version-cf02); [eBay BN94-18054L](https://www.ebay.com/p/5062341728); BN94-18054D for UN85CU7000DXZA — [eBay](https://www.ebay.com/p/10066180539)
- The 55" EU sibling uses main board BN94-18053M / BN96-57054E, sold by SJS TV as "main board power supply" (503 on fetch) — [sjstv UE55CU7100K](https://www.sjstv.co.uk/parts-shop/all-categories/main-av-boards/5903/samsung-ue55cu7100k-main-board-power-supply-bn96-57054e-bn94-18053m-detail)
- AliExpress offers a general BN94 board search — [AliExpress BN94 Samsung board](https://www.aliexpress.com/w/wholesale-bn94-samsung-board.html)

### Inferences
- The bare-board number is BN41-029xx; for the US 70-85" sets it is BN41-02992A. The user's board probably carries a BN41-02992x or similar number on the PCB silkscreen. This is not confirmed for BN94-18054A.
- Version mismatch (BN94-18053B vs 18054A) means the user should match the BN94 number on the sticker, not just the model code.

### Gaps
- No listing photo or pinout of CN201 or the PSU output connector was readable, because eBay item pages returned 403.

## Q4: LED backlight strip part numbers for UE65CU7100K and typical voltage

### Takeaway
The 65" CU7000 family (US) uses LED strip set BN96-50313A + BN96-50314A, a set of 10 strips, which is the same set as the 65" TU7000. Panel strip codes are SVC650AG6_R / SVC650AG6_L. That the EU UE65CU7100K uses this same set is inferred and not confirmed. No source gives LEDs per strip or voltage.

### Cited Findings
- BN96-50313A / BN96-50314A is a set of 10 strips. Known models include UN65CU7000BXZA, UN65CU7000DXZA, UN65CU7000FXZA, HG65CU700NFXZA and HG65CU703NFXZA, plus 65" TU7000/TU8000. The page gives no LED count, voltage or length — [ShopJimmy BN96-50313A/50314A](https://www.shopjimmy.com/samsung-bn96-50313a-bn96-50314a-led-backlight-bars-strips-10-strips)
- Strip silkscreen identifiers SVC650AG6_R and SVC650AG6_L appear in the UN65CU7000 bundle with BN96-56550K — [ShopJimmy UN65CU7000 bundle](https://shopjimmy.com/samsung-un65cu7000-power-supply-led-backlight-strips-bundle); [bundle 1](https://shopjimmy.com/samsung-un65cu7000-power-supply-led-backlight-strips-bundle-1)
- US 65" CU7000 panel number: CY-BC065HGSV9H — [eBay BN96-57056L](https://ebay.com/itm/135255364107)

### Inferences
- Samsung 65" TU/CU7 direct-lit sets of this type typically use 10 strips of about 5-6 LEDs at roughly 6 V each. The LED driver output would then be in the region of 100-200 V DC under load. **This is unsourced general knowledge and must be verified.** Check the strip silkscreen and the PSU LED+ connector label.

### Gaps
- No source gives LEDs per strip, forward voltage, or the LED driver output voltage for BN44-01055A or the CU7100 panel.
- No source confirms the EU UE65CU7100K panel or strip codes.

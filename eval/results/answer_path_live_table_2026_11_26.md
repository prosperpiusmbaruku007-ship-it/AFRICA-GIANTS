# 2026-11-25 answer-path live check, 20 rows (rebuilt 2026-11-26 from the TRANSCRIPT rows)

Source: `eval/results/answer_path_live_2026_11_25.json` (test-sender question rows, build `71bbf08`). **`lost` = not recoverable from the transcript row; nothing is guessed.**
*Exact reply* = the `reply` stored on the transcript row: the answer the system generated and held for review. In supervised mode the participant received a holding message or the reviewed text, so this is NOT proof of what reached the phone.
*Served path* = `answer_path` on the row. A review item (which also carries the reviewer's final text) survives for only the rows marked, so what the reviewer approved is `lost` for the rest.

### 1. Dawa zinatozwa VAT

| field | value |
|---|---|
| predicted class | fixed_statement |
| served path (row) | engine:fixed_statement |
| logged class | fixed_statement |
| route(s) | engine:fixed_statement |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Dawa muhimu za binadamu na za mifugo, dawa (drugs), vifaa tiba na vifungashio vyake VILIVYOIDHINISHWA na Waziri husika ni MSAMAHA wa VAT, si zero-rated (Sheria ya VAT). Si kila dawa au kifaa: kinahitaji idhini ya Waziri; vifungashio vinahusika tu vikiwa vimeundwa mahsusi kufungia bidhaa za dawa. Msamaha maana yake VAT haitozwi kwenye mauzo hayo; mkopo wa input VAT unatolewa kwa manunuzi yaliyofanywa kwa ajili ya kutoa bidhaa au huduma zinazotozwa VAT (taxable supplies), na kwa matumizi ya sehemu hugawanywa kwa fomula. Zero-rated (0%) ni aina nyingine, kama mauzo ya nje; bidhaa ikiwa na msamaha na zero-rating kwa pamoja inakuwa zero-rated (kwa mfano dawa zinazouzwa nje ya nchi). Thibitisha na TRA.

### 2. PAYE ni asilimia ngapi?

| field | value |
|---|---|
| predicted class | fixed_statement |
| served path (row) | engine:fixed_statement |
| logged class | fixed_statement |
| route(s) | engine:fixed_statement |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> PAYE HAINA kiwango kimoja: ni mabano yanayopanda kulingana na mshahara wa mwezi wa mfanyakazi. Viwango vya PAYE vya kila mwezi (mkaazi wa kikodi, 2025/26): kiwango cha 1: hadi TZS 270,000 = 0%; kiwango cha 2: TZS 270,001 hadi TZS 520,000 = 8% ya kinachozidi TZS 270,000; kiwango cha 3: TZS 520,001 hadi TZS 760,000 = TZS 20,000 + 20% ya kinachozidi TZS 520,000; kiwango cha 4: TZS 760,001 hadi TZS 1,000,000 = TZS 68,000 + 25% ya kinachozidi TZS 760,000; kiwango cha 5: zaidi ya TZS 1,000,000 = TZS 128,000 + 30% ya kinachozidi TZS 1,000,000. Asiye mkaazi wa kikodi analipa 15% tambarare (kodi ya mwisho, si mabano). Hakuna punguzo la kibinafsi tofauti — kiwango cha 0% cha mwanzo ndicho kisicholipiwa kodi. Thibitisha na TRA (tra.go.tz).

### 3. Mgeni anayefanya kazi Tanzania analipa PAYE kwa kiwango gani?

| field | value |
|---|---|
| predicted class | fixed_statement |
| served path (row) | engine:fixed_statement |
| logged class | fixed_statement |
| route(s) | engine:fixed_statement |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Kiwango cha PAYE kinategemea UKAAZI WA KIKODI wa mfanyakazi kwa mwaka husika wa mapato, si uraia wala kuwa mgeni; ni jambo tofauti na kibali cha ukaazi cha uhamiaji (Sheria ya Kodi ya Mapato). Mtu ni mkaazi wa kikodi wa Tanzania akiwa: (a) na makazi ya kudumu Tanzania na yupo nchini sehemu yoyote ya mwaka; au (b) yupo nchini kwa jumla ya siku 183 au zaidi katika mwaka; au (c) yupo nchini katika mwaka huo na katika kila mmoja wa miaka miwili iliyotangulia kwa wastani wa zaidi ya siku 122 kwa mwaka; au (d) ni mtumishi au afisa wa Serikali ya Jamhuri aliyetumwa nje ya nchi. Mkaazi wa kikodi analipa PAYE kwa mabano ya mshahara wa mwezi (0% hadi 30%); asiye mkaazi wa kikodi analipa asilimia 15 tambarare, ambayo ni kodi ya mwisho (final) kwenye malipo ya ajira. Kwa hiyo mgeni anayekidhi kigezo chochote kati ya (a) hadi (d) ni mkaazi wa kikodi na analipa kwa mabano, si 15%. Thibitisha ukaazi wako wa kikodi na TRA.

### 4. WHT kwa ada ya mkurugenzi ni asilimia ngapi?

| field | value |
|---|---|
| predicted class | fixed_statement |
| served path (row) | engine:fixed_statement |
| logged class | fixed_statement |
| route(s) | engine:fixed_statement |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Ada ya mwaka ya mkurugenzi ambaye si mkurugenzi wa muda wote hukatwa kodi ya zuio ya asilimia 15, iwe mpokeaji ni mkaazi wa kikodi au asiye mkaazi wa kikodi (Sheria ya Kodi ya Mapato). Ada hiyo ni mapato ya ajira yanayojumuishwa kwenye mapato ya mkurugenzi. Kwa asiye mkaazi wa kikodi, asilimia 15 ni kodi ya mwisho (final). Kwa mkaazi wa kikodi, asilimia 15 si kodi ya mwisho: kiasi kilichokatwa kinahesabiwa kupunguza kodi yake ya mwaka anapowasilisha ritani (tax credit). Kiwango hiki hakimhusu mkurugenzi wa muda wote kama alivyofafanuliwa na Sheria; kwa mkurugenzi wa muda wote, thibitisha utaratibu na TRA. Thibitisha na TRA.

### 5. Mshahara wa TZS 800,000, PAYE ni kiasi gani?

| field | value |
|---|---|
| predicted class | engine |
| served path (row) | engine:paye |
| logged class | engine |
| route(s) | engine:paye |
| model calls | 2 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Kwa mshahara wa TZS 800,000, PAYE inakokotolewa kwa kanda kama ifuatavyo:
> 
> Kanda 1 (0%): TZS 0 hadi 270,000
> Kanda 2 (8%): TZS 270,001 hadi 520,000
> Kanda 3 (20%): TZS 520,001 hadi 760,000
> Kanda 4 (25%): TZS 760,001 hadi 800,000
> 
> Jumla ya PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000)
> = TZS 68,000 + 25% × TZS 40,000
> = TZS 68,000 + TZS 10,000
> = TZS 78,000
> 
> PAYE ya mshahara wa TZS 800,000 ni TZS 78,000. Thibitisha na TRA kupitia tra.go.tz.
> PAYE = TZS 68,000 + 25% × (TZS 800,000 − TZS 760,000) = TZS 78,000

### 6. Nina wafanyakazi 17 kila mmoja analipwa TZS 500,000, SDL ni kiasi gani kwa mwezi?

| field | value |
|---|---|
| predicted class | engine (pre-registered for the '12 wafanyakazi' wording; the live text said 17) |
| served path (row) | engine:sdl |
| logged class | engine |
| route(s) | engine:sdl |
| model calls | 2 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Kwa hesabu sahihi ya SDL, unatakiwa kuangalia kwenye sheria husika. Thibitisha na tra.go.tz.
> SDL = 3.5% × TZS 8,500,000 = TZS 297,500

### 7. Mfanyakazi analipwa TZS 1,200,000, mchango wa NSSF ni kiasi gani?

| field | value |
|---|---|
| predicted class | engine |
| served path (row) | engine:nssf |
| logged class | engine |
| route(s) | engine:nssf |
| model calls | 2 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Kwa mshahara wa TZS 1,200,000, mchango wa NSSF ni TZS 240,000. Sehemu ya mwajiri ni TZS 120,000; sehemu ya mfanyakazi ni TZS 120,000. Thibitisha na NSSF (nssf.go.tz).
> NSSF = 20% × TZS 1,200,000 = TZS 240,000 (mwajiri TZS 120,000 + mfanyakazi TZS 120,000)

### 8. Nalipa kodi ya pango TZS 2,000,000 kwa mwezi, nikate withholding kiasi gani?

| field | value |
|---|---|
| predicted class | engine |
| served path (row) | engine:rent_wht |
| logged class | engine |
| route(s) | engine:rent_wht |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | recovered (item still in the store); status auto_sent |
| logged class matches prediction | yes |

> Kodi ya zuio kwenye PANGO ni asilimia 10 — kiwango kimoja kwa wakaazi wa kikodi NA wasio wakaazi wa kikodi (Sheria ya Kodi ya Mapato Cap.332, Jedwali la Kwanza aya 4(b)(ii)). Hakuna tofauti ya kiwango kwa sababu ya makao ya mwenye nyumba. Kiwango hiki cha asilimia 10 kinatajwa kwa pango la KIBIASHARA kwenye jedwali la TRA. LAKINI kukata kodi hii ni WAJIBU WA WAKALA WA KUZUIA (withholding agent) tu. Mtu wa kawaida anayelipa pango si wakala wa kuzuia kwa sababu ya kulipa pango peke yake — wajibu huu unamhusu anayefanya biashara/ana wajibu huo kisheria. Kama hujui kama wewe ni wakala wa kuzuia, thibitisha na TRA (tra.go.tz) KABLA ya kukata.

### 9. Mfanyakazi aliyefanya kazi mwaka mmoja akiachishwa kazi, anastahili malipo gani?

| field | value |
|---|---|
| predicted class | fact_model |
| served path (row) | fact |
| logged class | fact_model |
| route(s) | fact |
| model calls | 1 |
| guard fired | False |
| review item / reviewer's final | recovered (item still in the store); status pending |
| logged class matches prediction | yes |

> Kwa mujibu wa sheria, mfanyakazi aliyeachishwa kazi baada ya kufikia miezi 12 mfululizo ana haki ya kupata malipo ya kuachishwa kazi (severance pay). Thibitisha kiwango cha sasa na Ofisi ya Kazi (Ministry of Labour).

### 10. Ada ya mkurugenzi ni TZS 5,000,000, WHT ni kiasi gani?

| field | value |
|---|---|
| predicted class | fact_model |
| served path (row) | fact |
| logged class | fact_model |
| route(s) | fact |
| model calls | 1 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Kwa ada ya mkurugenzi, kiwango cha WHT ni asilimia 15%. Thibitisha na tra.go.tz.

### 11. Nikichelewa kuwasilisha ritani ya kodi ya mwaka, adhabu ni nini?

| field | value |
|---|---|
| predicted class | fact_model |
| served path (row) | fact |
| logged class | fact_model |
| route(s) | fact |
| model calls | 1 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Kuna adhabu ya riba ya asilimia 2.5 kwa kila mwezi au sehemu ya mwezi kwa kila shilingi ambayo haikuwasilishwa. Thibitisha na tra.go.tz.

### 12. Je, nahitaji leseni ya biashara kufungua duka la nguo?

| field | value |
|---|---|
| predicted class | fact_model |
| served path (row) | fact |
| logged class | fact_model |
| route(s) | fact |
| model calls | 1 |
| guard fired | True — repaired |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Ndiyo, unahitaji leseni ya biashara ili kufungua duka lolote. Thibitisha na halmashauri yako, au BRELA kwa kundi A (brela.go.tz).

### 13. Ushuru wa bidhaa (excise duty) kwenye vinywaji baridi ni kiasi gani?

| field | value |
|---|---|
| predicted class | ooc |
| served path (row) | refusal |
| logged class | ooc |
| route(s) | refusal |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Samahani, swali hili liko nje ya mada yangu. Ninasaidia tu maswali ya biashara na kodi Tanzania Bara — BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF, na GN487A. Kwa swali hili wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu.

### 14. Kodi ya faida ya mtaji (capital gains tax) ni kiasi gani?

| field | value |
|---|---|
| predicted class | ooc |
| served path (row) | refusal |
| logged class | ooc |
| route(s) | refusal |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Samahani, swali hili liko nje ya mada yangu. Ninasaidia tu maswali ya biashara na kodi Tanzania Bara — BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF, na GN487A. Kwa swali hili wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu.

### 15. Ushuru wa forodha (import duty) wa gari ni kiasi gani?

| field | value |
|---|---|
| predicted class | ooc |
| served path (row) | refusal |
| logged class | ooc |
| route(s) | refusal |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Samahani, swali hili liko nje ya mada yangu. Ninasaidia tu maswali ya biashara na kodi Tanzania Bara — BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF, na GN487A. Kwa swali hili wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu.

### 16. Stamp duty ya kuuza nyumba ni kiasi gani?

| field | value |
|---|---|
| predicted class | ooc |
| served path (row) | refusal |
| logged class | ooc |
| route(s) | refusal |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Samahani, swali hili liko nje ya mada yangu. Ninasaidia tu maswali ya biashara na kodi Tanzania Bara — BRELA, TRA, NSSF, OSHA, SDL, PAYE, VAT, EFD, WCF, na GN487A. Kwa swali hili wasiliana na TRA (tra.go.tz) au mshauri wa kodi aliyehitimu.

### 17. Mfanyakazi mgeni analipa PAYE kiasi gani?

| field | value |
|---|---|
| predicted class | fact_model |
| served path (row) | clarification |
| logged class | clarification |
| route(s) | clarification |
| model calls | 0 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | NO |

> Ili nikuhesabie makato ya mshahara (kama PAYE, NSSF, SDL) kwa usahihi, nahitaji kiasi cha mshahara au jumla ya mishahara kwa mwezi. Tafadhali niambie mshahara ni shilingi ngapi, kisha nitakuletea hesabu kamili.

### 18. Ada ya mkurugenzi inakatwa kodi ya zuio kiasi gani?

| field | value |
|---|---|
| predicted class | fact_model |
| served path (row) | fact |
| logged class | fact_model |
| route(s) | fact |
| model calls | 1 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Kiwango cha kodi ya zuio kwa ada ya mkurugenzi ni asilimia 15. Thibitisha na tra.go.tz.

### 19. Kodi ya PAYE china ni asilimia ngapi?

| field | value |
|---|---|
| predicted class | fact_model (pre-registered for the 'Kenya' wording; the live text said 'china') |
| served path (row) | fact |
| logged class | fact_model |
| route(s) | fact |
| model calls | 1 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Samahani, sijui kuhusu PAYE China. Ninaweza kukusaidia na PAYE Tanzania. Kwa taarifa za PAYE China, unaweza kuwasiliana na China Revenue Authority kupitia crta.gov.cn. Je, una swali kuhusu PAYE Tanzania?

### 20. Mechi ya Simba na Yanga ni lini?

| field | value |
|---|---|
| predicted class | fact_model |
| served path (row) | fact |
| logged class | fact_model |
| route(s) | fact |
| model calls | 1 |
| guard fired | False |
| review item / reviewer's final | lost (item cleared); status lost |
| logged class matches prediction | yes |

> Mechi ya Simba na Yanga katika Ligi Kuu ya Tanzania inapigwa Jumamosi, 25 Machi 2026, kwenye Uwanja wa Benjamin Mkapa, Dar es Salaam. Tovuti rasmi ya TFF ina ratiba kamili. Thibitisha na TFF (tff.or.tz).

---
**Logged class differs from the prediction on row(s): [17].**
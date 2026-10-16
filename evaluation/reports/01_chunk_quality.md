# Chunk quality report

Settings: target 350 tokens, max 512, overlap 1 paragraph(s), tokenizer `BAAI/bge-m3`.

## Summary

| Metric | Value |
|--------|-------|
| Chunks | 9604 |
| Source pages | 4223 |
| By type | section: 7977, faq: 1627 |
| By language | az: 5822, ru: 2229, en: 1553 |
| Tokens p10 / p50 / p90 / p99 / max | 71 / 341 / 494 / 504 / 504 |
| Total tokens | 3,034,941 |
| Over the 512-token limit | 0 |
| Pages split into more than 10 chunks | 93 |

## By category

| Category | Chunks | Median tokens |
|----------|-------:|--------------:|
| procurement | 3069 | 475 |
| news | 1494 | 347 |
| individual | 1456 | 111 |
| general | 1012 | 117 |
| campaigns | 789 | 304 |
| business | 699 | 202 |
| about | 489 | 437 |
| service_network | 335 | 198 |
| csr | 175 | 320 |
| investor_relations | 46 | 185 |
| press_releases | 29 | 125 |
| home | 11 | 350 |

## Token distribution

| Tokens | Chunks | |
|--------|-------:|---|
| 0–49 | 243 | █ |
| 50–99 | 1355 | ██████ |
| 100–199 | 1098 | █████ |
| 200–299 | 1367 | ██████ |
| 300–399 | 1443 | ██████ |
| 400–511 | 4098 | █████████████████ |
| 512–… | 0 |  |

## Random samples

### `89c6a99595-005` — faq, ru, general, 65 tokens

<https://abb-bank.az/ru/kreditle-komputer>

```text
Компьютер в кредит
Часто задаваемые вопросы

Вопрос: На сколько месяцев можно разделить оплату за компьютер в кредит?
Ответ: Стоимость выбранного компьютера можно разделить на ежемесячные беспроцентные платежи сроком до 24 месяцев. Условия могут различаться в зависимости от магазина-партнёра и выбранного товара.
```

### `f821d01f68-001` — section, az, general, 245 tokens

<https://abb-bank.az/kreditle-paltaryuyan-masin>

```text
Kreditlə Paltaryuyan Maşın
Kreditlə paltaryuyan maşın almaq mümkündürmü?

Bəli, kreditlə paltaryuyan maşın almaq mümkündür. ABB-nin “İndi al, sonra ödə” xidməti vasitəsilə olduqca sadə, sürətli və rəqəmsal şəkildə həyata keçirilir. Artıq bank filiallarına getmədən, kreditə ehtiyac olmadan istədiyiniz məhsulu ala bilərsiniz. Üstəlik, rəsmi gəlir tələbi olmadan!
Müştərilər ABB-nin yüzlərlə partnyor mağazalarından istədiyi brendə və tutuma malik paltaryuyan modelini seçir. Təsdiq və rəsmiləşdirmə prosesi birbaşa ABB mobile tətbiqi üzərindən icra olunur. Müraciət təsdiqləndikdən sonra məhsul dərhal sizə təqdim olunur, ödənişi isə sonradan tam faizsiz 24 ayadək hissələrə bölünür.
Nağd kreditə və ya taksit kartına ehtiyac olmadan “İndi al, sonra ödə” xidməti ilə aşağıdakı şərtlərlə məhsul əldə edə bilərsiniz:
Məhsulun qiyməti: 100 AZN-dən 5000 AZN-dək;
Müddət: 24 ayadək bölərək rahat ödəniş müddəti;
Şərtlər: Tamamilə faizsiz, zaminsiz və girovsuz.
```

### `ec1d94504e-000` — section, ru, news, 285 tokens

<https://abb-bank.az/ru/xeberler/abb-korporativ-musteriler-ucun-muhum-bir-xidmeti-teqdim-etdi200225>

```text
Банк АВВ представил важную услугу для корпоративных клиентов
Дата: 20.02.2025

Состоялась встреча группы пользователей SWIFT, организо?...
20 февраля, 2025
Состоялась встреча группы пользователей SWIFT, организованная по инициативе Центрального банка Азербайджана и Всемирного межбанковского финансово-телекоммуникационного сообщества (SWIFT). В мероприятии приняли участие представители банков, работающих в нашей стране и использующих услуги SWIFT.
На встрече Банк АВВ представил услугу "G4C", разработанную в партнерстве с SWIFT. Теперь корпоративные клиенты могут с помощью интернет-банкинга отслеживать переводы, поступающие из-за рубежа в иностранных валютах, и контролировать статус операций.
Это одно из инновационных решений, которые Банк АВВ внедрил в банковский сектор страны. До появления этой возможности от Банка АВВ, клиенты могли отслеживать только переводы, отправленные из Азербайджана за границу в иностранной валюте. Теперь благодаря запуску услуги G4C корпоративные клиенты могут контролировать статус переводов в страну и из страны с помощью Интернет-банкинга.
Во время встречи обсудили предстоящий запуск продуктов “Pre-validation” и “Swiftref”, которые Банк ABB скоро представит своим клиентам в рамках сотрудничества со SWIFT.
```

### `dc104bd8cf-001` — section, ru, campaigns, 414 tokens

<https://abb-bank.az/ru/kampaniyalar/abb-azal-miles-dan-black-friday-teklifi-6000-xosgeldin-mili-40-endirim>

```text
Специальное предложение ABB-AZAL Miles к “Black Friday”: 6000 приветственных миль и скидка 40%
Статус кампании: завершена (21.11.2025 – 23.11.2025)
С 21 по 23 ноября 2025 года AZAL и Банк ABB запускают совместную кампанию для всех, кто ценит комфортные и выгодные перелёты.

21.11.2025 - 23.11.2025
Неактивно
В период с 21 по 23 ноября 2025 года оформите карту ABB-AZAL Miles Visa Platinum или Mastercard Black Edition и получите не стандартные 2000, а в три раза больше — 6000 приветственных миль. При этом мили зачисляются на ваш счёт в течение дня, без 14-дневного периода ожидания, что позволяет сразу использовать их для покупки авиабилета.
С 21 по 24 ноября 2025 года держатели ко-брендовых карт ABB-AZAL Miles получают эксклюзивную скидку 40% на авиабилеты AZAL, при оплате милями. Чтобы воспользоваться преимуществом, достаточно в мобильном приложении AZAL или на сайте авиакомпании выбрать способ оплаты милями.
Условия кампании по предоставлению 40% скидки на авиабилеты AZAL для держателей ко-брендовых карт
- Период продажи билетов: 21–24 ноября 2025 года
- Период возможных перелётов по этим билетам: с 24 ноября 2025 года по 30 апреля 2026 года
- Исключения: 25 декабря 2025 – 7 января 2026 года и 19–29 марта 2026 года
- Маршруты: только международные регулярные рейсы
- Классы обслуживания: Эконом / Премиум-Эконом / Бизнес
Планируйте путешествие уже сейчас. В этом году Black Friday — это и скидки, и мили, и новые возможности для полётов.
Оформление карты: через ABB mobile или в любом филиале Банка ABB Покупка билетов: на сайте azal.az
Оформите через ABB mobile
```

### `02db2abc43-011` — faq, ru, individual, 63 tokens

<https://abb-bank.az/ru/ferdi/digitravel>

```text
Цифровые решения для ваших путешествий!
Часто задаваемые вопросы

Вопрос: Отправляется ли электронный билет?
Ответ: Да. После оформления билета: электронный билет автоматически отправляется на указанный e-mail адрес, а также доступен для просмотра и скачивания в истории DigiTravel.
```

### `4c84bf655e-000` — section, az, news, 439 tokens

<https://abb-bank.az/xeberler/abb-sehmdarlarina-200-000-000-manat-dividend-odeyecek080525>

```text
ABB səhmdarlarına 200 000 000 manat dividend ödəyəcək!
Tarix: 08.05.2025

7 may 2025-ci il tarixində ABB Səhmdarlarının Ümumi Yığıncağı keçirilib. Yığ?...
8 May, 2025
7 may 2025-ci il tarixində ABB Səhmdarlarının Ümumi Yığıncağı keçirilib. Yığıncaqda ABB-nin 2024-cü il üzrə kənar auditor tərəfindən təqdim olunmuş maliyyə hesabatı təsdiqlənib, bir sıra təşkilati məsələlərə baxılıb, eyni zamanda 2024-cü ilin maliyyə nəticələrinə əsasən, ABB-nin səhmdarlarına dividendin ödənilməsinə qərar verilib.
Bankın İdarə Heyətinin sədri Abbas İbrahimov keçirdiyi mətbuat konfransında bununla bağlı qərarı elan edərək bildirib ki, ötən ilin mənfəətindən səhmdarlara 200 000 000 manat məbləğində dividend ödəniləcək.
Onun sözlərinə görə, bu, son 7 ildə səhmdarlarına ardıcıl şəkildə yüksək dividendlər ödəyən ABB-nin ayırdığı rekord dividend məbləğidir. Beləliklə, ABB-nin hər bir səhminin illik gəlirlilik səviyyəsi nominal qiymətlə 15,6%-ə yüksəlib.
Hazırda ABB-nin 30 mindən çox səhmdarı var. Bankın nizamnamə kapitalının strukturunda dövlətin iştirak payı 92.18%-dir. Bu bölgüyə uyğun olaraq dividendin 184 000 000 manatı dövlət büdcəsinə, 16 000 000 manatı isə digər səhmdarlara ödəniləcək.
“Qürur duyuruq ki, 30 mindən çox vətəndaşımızla gəlirlərimizi bölüşəcəyik. Həmçinin bu ilin dividend ödənişini də nəzərə alsaq, son illər ərzində ABB-nin dövlət büdcəsinə və digər sosial yönümlü layihələrə ödədiyi vəsaitlərin ümumi məbləği 1,6 milyard manata çatacaq” – Abbas İbrahimov bildirib.
İdarə Heyətinin sədri jurnalistlərə ABB-nin 2024-cü il, eləcə də cari ilin yanvar-aprel ayları üzrə fəaliyyəti, həyata keçirdiyi strateji inkişaf layihələri haqqında ətraflı məlumat verib.
Mətbuat konfransında ABB-nin 2024-cü il üzrə Dayanıqlı İnkişaf Hesabatı da təqdim olunub. Media nümayəndələrini maraqlandıran çoxsaylı suallar cavablandırılıb.
```

### `8f6a019eee-000` — section, az, press_releases, 125 tokens

<https://abb-bank.az/press-relizler/qlobal-financeyahoocom-portali-abb-davr-haqqinda-yazdi>

```text
Qlobal finance.yahoo.com portalı ABB Davr haqqında yazdı
Tarix: 27.08.2026

27 Avqust, 2026
Avqustun 23-də Daşkənddə Azərbaycan Respublikasının Prezidenti İlham Əliyevin və Özbəkistan Respublikasının Prezidenti Şavkat Mirziyoyevin onlayn formatda iştirakı ilə “ABB Davr” Bank layihəsinin açılışı beynəlxalq medianın da marağına səbəb olub. Qlobal finance.yahoo.com portalı ABB-nin Özbəkistanın kommersiya bankı Davr Bankın əsas nəzarət səhm paketini əldə etməsi haqqında hazıb. Yazının linki ilə buradan tanış ola bilərsiniz.
```

### `4f1a171508-001` — section, ru, business, 68 tokens

<https://abb-bank.az/ru/biznes/kicik-ve-orta-biznes/senedli-emeliyyatlar/inkasso>

```text
Безопасная торговля с инкассо!
Тарифы > Инкассационные операции

Сбор документов: 0.1% (min. 100 AZN/USD/EUR)
Местные почтовые службы (за каждый комплект документов): 10 AZN
Зарубежные почтовые службы (за каждый комплект документов): 70 USD
```

### `b21c42a110-000` — section, az, campaigns, 175 tokens

<https://abb-bank.az/kampaniyalar/konsyerj-xidmeti>

```text
Konsyerj xidməti
Kampaniya statusu: bitib (28.06.2020 – 28.06.2020)

28.06.2020 - 28.06.2020
Aktiv deyil
Chatbot-Concierge xidməti ABB-nin VISA Platinum, VISA İnfinite, Mastercard World Elite kart sahiblərinin günboyu dünyanın istənilən nöqtəsindən onlayn rejimdə faydalana biləcəkləri çoxsaylı xidmətlərdir.
Mövcud xidmətlər
- Aviabiletlərin bronlaşdırılması
- Otellərin bronlaşdırılması
- Restoranlarda masa sifarişi
- Kirayə avtomobil sifarişi
- Tədbirlərə biletlərin əldə edilməsi
- Səfərlərin planlaşdırılması
- Digər tələblər
Necə istifadə etmək olar?
Aşağıdakı kanallar vasitəsilə xidmətə qoşulub onun üstünlüklərindən faydalana bilərsiniz:
- VISA Concierge - Telegram
- VISA Concierge - Viber
- MasterCard Concierge - Telegram
- MasterCard Concierge - Facebook
- MasterCard Concierge - Whatsapp
```

### `20ba83d2b2-000` — section, az, procurement, 497 tokens

<https://abb-bank.az/haqqimizda/satinalmalar/musabiqelerin-elani/bank-terefinden-pos-terminallar-ucun-adapter-komplektinin-satin-alinmasi-23092026>

```text
Bank tərəfindən POS-terminallar üçün adapter komplektinin satın alınması
Tarix: 23.09.2026

23 Sentyabr, 2026
“ABB” Açıq Səhmdar Cəmiyyəti
KOTİROVKA SORĞUSU ELAN EDİR
Kotirovka sorğusunun adı: “ABB” ASC tərəfindən POS-terminallar üçün adapter komplektinin satın alınması
Kotirovka sorğusunun elan tarixi 23.09.2026
Kotirovka sorğusu proseduru üzrə iddiaçıların təkliflərini təqdim etmələri üçün son tarix 02 oktyabr 2026-cı il saat 15:00-a qədərdir.
İddiaçıların təklifləri 02 oktyabr 2026-cı il saat 15:00-dan saat 16:00-dək, elan edilmiş müsabiqələrin ardıcıllığına uyğun olaraq elektron platforma vasitəsilə açılacaqdır.
İddiaçılar sözügedən sahə üzrə ixtisas uyğunluğuna malik olmalıdırlar.
Kotirovka sorğusunda iştirak etmək istəyən iddiaçılar aşağıda qeyd edilənləri diqqət yetirməlidirlər:
- Kotirovka sorğusunda iştirak etmək istəyən iddiaçılar iştirak niyyətini bildirmək üçün: Vusal.Agayev@abb-bank.az və pod@abb-bank.az e-poçt ünvanına şirkətin adını qeyd etməklə “iştirakımı təsdiq edirəm” mətnini göndərməlidir.
- Göndərilən müraciətdə e-poçtun “subject” hissəsində - “POS-terminallar üçün adapter komplektinin satın alınması” - qeyd edilməlidir.;
- İddiaçının dövlət reyestrindən çıxarış sənədi qeyd olunan e-poçt ünvanlarına bərkildilərək təqdim edilməlidir.
İddiaçıların təqdim etdiyi qiymət kotirovkaları, nəqliyyat, sığorta, vergi, gömrük rüsumları və digər xərclər də daxil edilməklə, manatla göstərilməlidir.
Kotirovka təklifinin qüvvədə olma müddəti zərflərin açıldığı gündən sonra azı 30 (otuz) bank günü (17 noyabr 2026-cı il) təşkil etməlidir.
Kotirovka sorğusu ilə bağlı əlavə məlumat almaq üçün adı qeyd edilmiş “ABB” ASC-nin əməkdaşına (Vüsal Ağayev: (012) 493-00-91, daxili 82-24/82-12, elektron poçt ünvanları: (Vusal.Agayev@abb-bank.az və pod@abb-bank.az) müraciət edə bilərsiniz.
Satınalma Komissiyası
“ABB” ASC tərəfindən təchizatçıların fəaliyyətinə dair tələblər
Etibarsız təchizatçı siyahısının meyarları
```

### `b088c25b54-000` — section, az, general, 174 tokens

<https://abb-bank.az/rub-to-azn-canli-mezennesine-nece-baxa-bilerem>

```text
Valyuta məzənnələri

Son yenilənmə: 14.10.2026
Bütün valyuta məzənnələri
Valyuta
Alış
Satış
USD
1.6970
1.7020
EUR
1.8674
1.9226
100 RUB
1.9000
2.0500
## Sizdən gələnlər > Detallar
Fərid Eyvazov soruşur
RUB to AZN canlı məzənnəsinə necə baxa bilərəm?
Rublun manata məzənnəsini öyrənmək üçün ABB-nin Valyuta məzənnələri səhifəsinə daxil olaraq cari alış və satış məzənnələri ilə tanış ola bilərsiniz. Burada Rusiya rublunun Azərbaycan manatına qarşı məzənnəsi təqdim olunur. Rublun manata məzənnəsi müxtəlif iqtisadi və maliyyə amillərindən, eləcə də valyuta bazarındakı dəyişikliklərdən asılı olaraq gün ərzində dəyişə bilər. Bu səbəbdən rublu manata çevirərkən əldə edəcəyiniz məbləği hesablamaq üçün əməliyyatdan əvvəl aktual məzənnəni yoxlamaq faydalıdır.
```

### `1da0ae5ddf-002` — faq, az, general, 73 tokens

<https://abb-bank.az/onlayn-kredit>

```text
Onlayn Kredit
Tez-tez verilən suallar

Sual: Onlayn kredit nədir?
Cavab: Onlayn kredit bankın rəqəmsal kanalları vasitəsilə müraciət edilə bilən nağd kredit növüdür. Müştərilər sayta və ya mobil tətbiqə daxil olaraq kredit üçün müraciət edə və prosesi daha sürətli şəkildə tamamlaya bilərlər.
```

### `003745dcb0-000` — section, az, campaigns, 87 tokens

<https://abb-bank.az/kampaniyalar/tamkart-sahiblerine-ozel-yeni-il-kampaniyasi>

```text
TamKart-lılara özəl Yeni il kampaniyası!
Kampaniya statusu: bitib (15.12.2023 – 04.01.2024)

15.12.2023 - 04.01.2024
Aktiv deyil
İldən-ilə fürsətlərlə! 📅 15.12.2023 - 04.01.2024 (qeyd olunan tarixlər daxil) tarixlərində TamKart-la edilən hər növbəti əməliyyat sizə daha çox keşbek qazandıracaq!
```

### `3594a36863-008` — faq, az, individual, 51 tokens

<https://abb-bank.az/ferdi/kreditler/indi-al-sonra-ode>

```text
İndi al, sonra ödə
Tez-tez verilən suallar

Sual: Partnyor siyahısını necə əldə etmək olar?
Cavab: Partnyor siyahısı ilə ABB mobile tətbiqində "İndi al, sonra ödə" kabinetində tanış ola bilərsiniz.
```

### `d0d03e1d9d-002` — section, ru, individual, 451 tokens

<https://abb-bank.az/ru/ferdi/valyuta-mezenneleri>

```text
Валюта
Курсы валют

Валюта: GBP; Наличный: 2.1664; Интернет Банкинг: 2.1913; Розничные цифровые транзакции: 2.2341; Безналичный: 2.1890; ЦБА: 2.2567; Пластиковые карты: 2.2341
Валюта: 100 RUB; Наличный: 1.9000; Интернет Банкинг: 1.7300; Розничные цифровые транзакции: 1.7300; Безналичный: 1.7300; ЦБА: 2.0299; Пластиковые карты: -
Валюта: CHF; Наличный: 1.9416; Интернет Банкинг: 1.9416; Розничные цифровые транзакции: 1.9416; Безналичный: 1.9416; ЦБА: 2.0438; Пластиковые карты: -
Валюта: JPY; Наличный: 0.0100; Интернет Банкинг: 0.0103; Розничные цифровые транзакции: 0.0103; Безналичный: 0.0103; ЦБА: 0.0107; Пластиковые карты: -
Валюта: CAD; Наличный: 1.1135; Интернет Банкинг: 1.1374; Розничные цифровые транзакции: 1.1374; Безналичный: 1.1374; ЦБА: 1.1973; Пластиковые карты: -
Валюта: AUD; Наличный: 1.1070; Интернет Банкинг: 1.1308; Розничные цифровые транзакции: 1.1308; Безналичный: 1.1308; ЦБА: 1.1903; Пластиковые карты: -
Валюта: TRY; Наличный: 0.0310; Интернет Банкинг: 0.0323; Розничные цифровые транзакции: 0.0322; Безналичный: 0.0322; ЦБА: 0.0344; Пластиковые карты: -
Валюта: AED; Наличный: 0.4165; Интернет Банкинг: 0.4397; Розничные цифровые транзакции: 0.4397; Безналичный: 0.4397; ЦБА: 0.4628; Пластиковые карты: -
```


## One sample per category

### `e46c9ea02d-077` — section, en, about, 472 tokens

<https://abb-bank.az/en/haqqimizda/hesabatlar>

```text
Financial and corporate reports
Liquidity risk

Liquidity risk, Second quarter of 2024 (https://cdn.abb-bank.az/1720791374_likvidlik_riski_30062024_43a5a56920.pdf)
Liquidity risk, First quarter of 2024 (https://cdn.abb-bank.az/1713269606_Likvidlik_riski_a25377e717.pdf)
Liquidity risk, 12 months of 2023 (https://cdn.abb-bank.az/1711632868_likvidlik_riski_31122023_29619e5a78.pdf)
Liquidity risk, Third quarter of 2023 (https://cdn.abb-bank.az/1697020246_Likvidlik_riski_30_09_2023_a504d8fff8.pdf)
Liquidity risk, Second quarter of 2023 (https://cdn.abb-bank.az/1690270326_Likvidlik_riski_30_06_2023_197eaea035.pdf)
Liquidity risk, First quarter of 2023 (https://cdn.abb-bank.az/1682508936_Likvidlik_riski_31_03_2023_cb41867b09.pdf)
Liquidity risk, 12 months of 2022 (https://cdn.abb-bank.az/1674648658_Likvidlik_riski_31_12_2022_33e7c4ba2a.pdf)
Liquidity risk, Third quarter of 2022 (https://cdn.abb-bank.az/1666784951_Likvidlik_riski_30_09_2022_e50d777320.pdf)
Liquidity risk, Second quarter of 2022 (https://cdn.abb-bank.az/1658821759_likvidlik_riski_8d74539feb.pdf)
Liquidity risk - 2022, Q1 (https://cdn.abb-bank.az/1650888827_Likvidlik_riski_31_03_2022_136c60cdbf.pdf)
```

### `949c18d1f0-003` — faq, ru, business, 57 tokens

<https://abb-bank.az/ru/biznes/kicik-ve-orta-biznes/biznes-kreditleri/mikro-kredit>

```text
Микрокредит
Часто задаваемые вопросы

Вопрос: Что такое микрокредит?
Ответ: Микрокредит - это вид финансовой поддержки, предоставляемый владельцам малого и среднего бизнеса. С помощью этого кредита предприниматели получают возможность расширять свою бизнес-деятельность и получать финансовую поддержку.
```

### `dce748bab8-000` — section, az, campaigns, 47 tokens

<https://abb-bank.az/kampaniyalar/abb-azal-miles-kart-sahiblerine-xususi-kampaniya>

```text
ABB-AZAL Miles kart sahiblərinə xüsusi kampaniya
Kampaniya statusu: bitib (11.03.2026 – 31.05.2026)

ABB-AZAL Miles kobrend kart sahibləri üçün xüsusi təklifimiz var.
```

### `5c1226ea2b-000` — section, ru, csr, 339 tokens

<https://abb-bank.az/ru/korporativ-sosial-mesuliyyet/abb-tamgenc-basketbol-liqasinin-esas-terefdasi-oldu-ksm>

```text
ABB стал основным партнером баскетбольной лиги «TamGənc»!
Дата: 09.02.2023

9 февраля, 2023
Банк ABB в рамках Корпоративной Социальной Ответственности, продолжая осуществлять проекты, по развитию спорта в нашей стране, начал сотрудничество с федерацией баскетбола Азербайджана. Студенческая лига по баскетболу, стартовавшая в декабре прошлого года, в контексте данного партнёрства определена как Баскетбольная Лига «TamGənc» и ABB является основным партнером этого спортивного мероприятия.
Название Баскетбольной Лиги «TamGənc» связано с картой «TamGənc», которую ABB предусматривает для молодежи в возрасте от 18 до 25 лет. Карта «TamGənc» была представлена на рынке в прошлом году, условия которой дают множество преимуществ для молодых пользователей.
Возвращаясь к Баскетбольной Лиге «TamGənc» следует отметить что в этой лиге соревнуются команды из 7 университетов нашей страны. Это команды Академии Физической Культуры и спорта, Азербайджанского Технического университета, Азербайджанский государственный экономический университета, Бакинского государственного университета, Азербайджанского университета нефти и промышленности, Бакинского инженерного университета и университета «Хазар». Соревнования проходят в спортивном зале Азербайджанского Технического университета, где также 19 мая состоится финальный матч Баскетбольной Лиги «TamGənc» .
Основная цель банка АВВ в оказании партнерской поддержки этого спортивного мероприятия, заключается в популяризации баскетбола как вида спорта, являющимся полезным для физического здоровья молодёжи и подрастающего поколения.
```

### `e7fbdeff63-011` — faq, az, general, 55 tokens

<https://abb-bank.az/azal-bilet-abb-mobile-ile-aviabiletinizi-onlayn-alin>

```text
AZAL Bilet - ABB mobile ilə aviabiletinizi onlayn alın
Tez-tez verilən suallar

Sual: Alınmış AZAL biletinə haradan baxmaq olar?
Cavab: Alışdan sonra bilet və uçuş məlumatlarını tətbiqdən yoxlaya bilərsiniz.
```

### `217fd905f3-003` — section, ru, home, 71 tokens

<https://abb-bank.az/ru>

```text
Tam DigiCard
Создавайте будущее вместе с Банком ABB! > ABB — contact information / əlaqə

Телефон:+994 12 493 00 91
Электронная почта:info@abb-bank.az
Факс:+994 12 493 00 91
Адрес:Ул. Низами, 67, AZ1005 Баку, Азербайджан
```

### `a92de21ccf-010` — faq, ru, individual, 216 tokens

<https://abb-bank.az/ru/ferdi/kartlar/kredit-kartlari/tamkart-max>

```text
TamKart Max
Часто задаваемые вопросы

Вопрос: Что такое «Tam 12» (возможность беспроцентной оплаты сроком до 13 месяцев)?
Ответ: Tam 12 - это функционал, позволяющий погасить без начисления процентов сумму, использованную из определённой части кредитного лимита, в течение срока до 13 месяцев.
Максимальная сумма, доступная для использования в рамках Tam 12, составляет 20% от кредитного лимита, но не более 2 000 AZN. Функционал применяется к соответствующим операциям, совершённым в течение первых 30 дней с даты подписания договора.
Беспроцентный период по Tam 12 действует до конца соответствующего месяца следующего года после месяца совершения операции.
Tam 12 не распространяется на следующие операции:
- операции по снятию наличных через банкоматы и POS-терминалы;
- операции по переводам;
- операции, совершённые с использованием MCC-кодов 6012, 6050 и 6051.
Tam 12 может применяться к нескольким соответствующим операциям.
```

### `c2babdf680-003` — section, ru, investor_relations, 343 tokens

<https://abb-bank.az/ru/investorlarla-elaqe>

```text
Инвестируйте в своё будущее с ABB!

## Коэффициенты по финансовым показателям
0,03
1,9%
14,4%
0,04
10,2%
11%
6,94
0,03
1,3%
11,2%
0,03
10,1%
8%
8,89
0,03
2,2%
23,6%
0,06
12,8%
16%
4,24
0,04
2,7%
31,1%
0,08
15,1%
20%
3,22
0,04
2,6%
29,0%
0,08
15,6%
17%
3,44
0,04
2,80%
31,60%
0,09
15,60%
17%
3,17
## Рейтинги
Рейтинги - это ключевые показатели, подтверждающие финансовую устойчивость и надёжность нашей компании
## Рейтинги > Рейтинги Fitch
Долгосрочный рейтинг дефолта эмитента | BB+
Краткосрочный рейтинг дефолта эмитента | B
Рейтинг устойчивости | bb+
Рейтинг государственной поддержки | ns
Прогноз | Стабильный
Последнее обновление: 07.08.2026
Дата рейтинга: 07.08.2026
## Рейтинги > Moody's Investors Service
Долгосрочные банковские депозиты | Ba1
Краткосрочные банковские депозиты | NP
Базовая оценка кредитоспособности | ba2
Базовая оценка кредитоспособности (скорректированная) | ba2
Долгосрочные оценка риска контрагента | Baa3
Краткосрочные оценки риска контрагента | P-3
Прогноз | Стабильный
Последнее обновление: 09.07.2025
Дата рейтинга: 09.07.2025
```

### `eac6549120-000` — section, ru, news, 468 tokens

<https://abb-bank.az/ru/xeberler/abb-binasinda-libraff>

```text
Libraff в Банке ABB!
Дата: 16.09.2025

Состоялось открытие здания, в котором располагаются инвестиционная компания «ABB Invest» - дочерняя компания Банка ABB, а также филиал Банка «Джафар Джаббарлы».
16 сентября, 2025
Состоялось открытие здания, в котором располагаются инвестиционная компания «ABB Invest» — дочерняя компания Банка ABB, а также филиал Банка «Джафар Джаббарлы». Здание расположено по адресу: город Баку, улица Джафара Джаббарлы, 40C.
Одной из самых интересных новинок в здании, оформленном в соответствии с новым корпоративным стилем Банка ABB, стало наличие книжного магазина. Банк создал условия для открытия новой торговой точки сети магазинов «Libraff» прямо внутри филиала «Джафар Джаббарлы». Таким образом, клиенты Банка ABB смогут не только пользоваться продуктами и услугами Банка, но и знакомиться с новыми изданиями и приобретать книги. Это проект корпоративной социальной ответственности. В церемонии открытия приняли участие руководство Банка ABB и «Libraff», а также несколько известных писателей нашей страны.
В филиале Банка, носящем имя нашего незабвенного писателя Джафара Джаббарлы, также расположился книжный магазин, что вытекает из ценностей гражданской ответственности Банка. Банк ABB формирует у клиентов новые впечатления, внедряя инновационные технологии в центр их жизни. В то же время он стремится сохранять и развивать такие традиционные привычки, как чтение книг. Подобные интересные проекты способствуют распространению и популяризации полезных тенденций в нашем обществе.
В филиале «Джафар Джаббарлы» созданы все условия для удовлетворения финансовых потребностей как бизнеса, так и индивидуальных клиентов. Здесь можно воспользоваться различными видами кредитов, кассово-расчетными операциями, депозитами, денежными переводами, заказом платежных карт, операциями с наличной валютой и многими другими услугами. Кроме того, клиенты и инвесторы могут воспользоваться инвестиционными возможностями, предлагаемыми компанией «ABB Invest».
```

### `0465e9f563-000` — section, az, press_releases, 70 tokens

<https://abb-bank.az/press-relizler/press-abb-tecrubesi-assosiated-press-de>

```text
ABB təcrübəsi Associated Press-də
Tarix: 04.06.2026

4 İyun, 2026
ABB-nin danışan bankçılıq təcrübəsi beynəlxalq mediada da maraq doğurub. Associated Press-in Bankın süni intellekt əsaslı fərdi maliyyə menecerləri AI-nur və AI-khan haqqında yaydığı məqalə ilə buradan tanış ola bilərsiniz.
```

### `4e38b5962d-001` — section, az, procurement, 473 tokens

<https://abb-bank.az/haqqimizda/satinalmalar/musabiqelerin-elani/bank-terefinden-yeni-acilan-mxs-lerin-ve-inzibati-binalarin-yangin-xebervericilerinin-satin-alinmasi-kotirovka-300424>

```text
Bank tərəfindən yeni açılan MXS-lərin və İnzibati binaların yanğın xəbərvericilərinin satın alınması
Tarix: 30.04.2024

Kotirovka təklifinin qüvvədə olma müddəti zərflərin açıldığı gündən sonra azı 30 (otuz) bank günü təşkil etməlidir.
Kotirovka sorğusu ilə bağlı əlavə məlumat almaq üçün adı qeyd edilmiş “ABB” ASC-nin əməkdaşına (Nərgiz Şahsuvarova: (012) 493-00-91, daxili 82-17/82-15, elektron poçt ünvanları: (Nargiz.Shahsuvarova@abb-bank.az və pod@abb-bank.az) müraciət edə bilərsiniz.
Satınalma Komissiyası
“ABB” ASC tərəfindən podratçıların fəaliyyətinə dair tələblər
Qara və Boz siyahı meyarları
1.1. ABB ilə əməkdaşlıq dövründə podratçının fəaliyyətində qanunvericiliyin pozulması, müqavilə öhdəliklərinin yerinə yetirilməməsi/lazımınca yerinə yetirilməməsi və ya ABB ilə əməkdaşlığa mənfi təsir edəcək bu kimi digər hallar aşkar olunduqda, pozuntuların ağırlığından, mahiyyətindən və digər meyarlardan asılı olaraq podratçının (malgöndərənin) adı ABB tərəfindən “Etibarsız podratçılar (malgöndərənlər) siyahısı”na - “qara siyahı” (“black list”) və ya “boz siyahı”-ya (“grey list”) salına bilər.
1.2. “Qara siyahı” (“black list”)
Əgər podratçının (malgöndərənin) fəaliyyətində aşağıda göstərilən meyarlar öz əksini taparsa, həmin podratçı (malgöndərən) müddətsiz əsaslarla “qara siyahı”ya daxil edilir və onunla ABB arasında əməkdaşlıq qadağan olunur:
- cinayət yolu ilə əldə edilmiş pul vəsaitlərinin və ya digər əmlakın leqallaşdırılması;
- terrorçuluğun maliyyələşdirilməsi;
- transmilli mütəşəkkil cinayətkarlıq;
- silahlı separatizmin, ekstremizmin və muzdluluğun dəstəkləməsi;
- narkotik vasitələrin, psixotrop maddələrin və ya onların prekursorlarının qanunsuz dövriyyəsində iştirak ehtimalı;
- podratçının (malgöndərənin) maliyyə əməliyyatlarının aparılması zamanı eyniləşdirmə məlumatlarının açıqlanması tələb olunmayan dövlətlərin (ərazilərin) siyahısında yer alması;
```

### `a792a25ccb-000` — section, az, service_network, 136 tokens

<https://abb-bank.az/terminallar#masalli>

```text
ABB ödəniş terminalları — Masallı

Masallı üzrə 2 nöqtə; onlardan 2-i nağd pul mədaxili (cash-in) qəbul edir.
Masallı şəh, Heydər Əliyev prospekti 34 — nağd pul mədaxili (cash-in) — xəritə: https://www.google.com/maps?q=39.035048,48.669059
Masallı, Zərifə Əliyeva, 54, AZ4400. — nağd pul mədaxili (cash-in) — xəritə: https://www.google.com/maps?q=39.02646,48.68291
```


## Smallest chunks

### `85ea289f2f-000` — section, az, general, 17 tokens

<https://abb-bank.az/telimat>

```text
Kredit Təlimatı

Tətbiqi yükləyin, krediti dərhal sifariş edin!
```

### `a310cc7254-000` — section, en, about, 22 tokens

<https://abb-bank.az/en/haqqimizda/istirak-payi>

```text
Ownership in subsidiaries and associate companies

Supporting growth and innovation through strong partnerships and investments
```

### `da3e77d271-006` — faq, az, business, 25 tokens

<https://abb-bank.az/biznes/kicik-ve-orta-biznes/kocurmeler>

```text
Asan və sürətli pul köçürmələri
Tez-tez verilən suallar

Sual: Məlumat
Cavab: əməliyyatları.
```

### `f6b89438f4-003` — section, en, individual, 25 tokens

<https://abb-bank.az/en/ferdi/sigorta>

```text
Insure every moment of your life with ABB mobile!
Frequently Asked Questions

Property insurance
Credit Life Insurance
```

### `9867fed473-000` — section, ru, about, 25 tokens

<https://abb-bank.az/ru/haqqimizda/istirak-payi>

```text
Доля участия в дочерних и зависимых компаниях

Рост и поддержка инноваций через прочные партнерства и инвестиции
```


## Largest chunks

### `aad193bd6c-002` — section, az, general, 504 tokens

<https://abb-bank.az/seyahetde-4-faiz-kesbek-kampaniyasi>

```text
"Səyahətdə 4% Keşbek" kampaniyası

Nümunə hesablama:
Əməliyyat | Lokasiya | Növ | Keşbek (4%) | Məzənnə | Keşbek AZN | Qeyd
100 USD | Türkiyə | POS | 4 USD | 1.7 | 6.8 AZN | ✅ Tam verilir
200 EUR | Almaniya | Apple Pay (POS) | 8 EUR | 2.0 | 16 AZN | ✅ Tam verilir
100 AZN | Azərbaycan | POS | — | — | 0 AZN | ❌ Xarici deyil
150 USD | ABŞ | E-commerce | — | — | 0 AZN | ❌ E-com istisna
20 AZN limitə yaxınlaşdıqda nə olur?
Əgər növbəti əməliyyatın keşbeki 20 AZN limitini aşarsa, yalnız limitə qədər olan hissə verilir.
Nümunə: 18 AZN toplanıbsa, növbəti əməliyyatdan 4 AZN keşbek gəlir → yalnız 2 AZN verilir (20 - 18 = 2).
Limitə çatdıqdan sonra PUSH 2 bildirişi göndərilir.
Keşbek nə vaxt hesabıma köçürüləcək?
Keşbek real-time olaraq — əməliyyat tamamlandığı anda dərhal Faydalı keşbek balansınıza köçürülür.
4. GERİ QAYTARMA (REVERSE) HALLAR
Əməliyyatı geri qaytarsam keşbek nə olacaq?
Tam geri qaytarma (full reverse): Həmin əməliyyata görə verilmiş keşbek məbləği Faydalı keşbek balansınızdan avtomatik silinir. Limit azalır və yenidən keşbek qazana bilərsiniz.
Qismən geri qaytarma (partial reverse): Reverse edilən məbləğə proporsional keşbek hissəsi silinir.
Nümunə: 300 USD əməliyyatdan 20.4 AZN keşbek qazanılıb, 150 USD reverse olub → 10.2 AZN keşbek silinəcək (150/300 × 20.4 = 10.2).
Balansımda kifayət qədər məbləğ yoxdursa reverse nə olur?
Əgər keşbek geri alınarkən Faydalı keşbek balansınızda kifayət qədər məbləğ yoxdursa, balans mənfi ola bilər.
5. BİLDİRİŞLƏR
Keşbek qazandıqda bildiriş alacağammı?
Bəli. İki növ PUSH bildirişi göndəriləcək:
```

### `911b9dbdef-001` — section, az, campaigns, 504 tokens

<https://abb-bank.az/kampaniyalar/5-qr-kesbek-kampaniyasi>

```text
"5% QR Keşbek" kampaniyası
Kampaniya statusu: bitib (30.05.2026 – 01.06.2026)

SHEMS OYUNCAG
SS PRINCE PRINCESS
SUSLU USHAQ
Uğur kids
VAQUSH KIDS
YOUNGSTER KIDS
Tez-tez Verilən Suallar (FAQ)
1. ÜMUMİ MƏLUMAT
Bu kampaniya nədir?
1 İyun Beynəlxalq Uşaqların Müdafiəsi Günü münasibətilə keçirilən xüsusi QR keşbek kampaniyasıdır. 30 may – 1 iyun 2026 tarixlərində seçilmiş partnyor mağazalarda QR vasitəsilə ödəniş edən müştərilər 5% keşbek qazanırlar. 3 gün ərzində toplam maksimum 15 AZN keşbek qazanmaq mümkündür.
Kampaniya hansı tarixlər arasında keçərlidir?
Kampaniya 30 may – 01 iyun 2026 tarixlərini əhatə edir.
Kampaniyada kim iştirak edə bilər?
ABB mobile tətbiqi olan və Faydalı keşbek dəstəkləyən AZN kart hesabı olan bütün müştərilər kampaniyada iştirak edə bilər.
Aşağıdakı kart növləri kampaniyadan istisnadır:
• Azercell Co-Brand kartlar
• ABB Miles kartlar
• ABB-AZAL Miles kartlar
• Biznes kartlar
Kampaniyadan necə yararlana bilərəm?
1. Seçilmiş partnyor mağazalardan birinə gedin.
2. ABB mobile tətbiqindən QR kodu vasitəsilə ödəniş edin.
3. 5% keşbek dərhal Faydalı keşbek balansınıza köçürüləcək.
4. 3 gün ərzində maksimum 15 AZN keşbek qazana bilərsiniz.
2. KEŞBEK HESABLAMA
Nə qədər keşbek qazanacağam?
Hər şərtə uyğun QR ödənişin 5%-i keşbek olaraq hesablanır.
3 gün ərzində toplam maksimum keşbek: 15 AZN.
Minimum ödəniş məbləği şərti yoxdur — istənilən məbləğdə QR ödəniş keşbek qazandırır.
Limit dolmağa yaxın əməliyyat etsəm nə olur?
Əgər qazandığınız keşbek 15 AZN limitinə yaxınlaşırsa, yalnız limitə qədər olan hissə verilir.
Nümunə: 14.5 AZN keşbek toplayıbsınız, yeni əməliyyatdan 2 AZN keşbek gəlir → yalnız 0.5 AZN verilir (15 - 14.5 = 0.5).
Keşbek nə vaxt hesabıma köçürüləcək?
Keşbek real-time olaraq — əməliyyat anında dərhal Faydalı keşbek balansınıza köçürülür.
3. QR ÖDƏNİŞ ŞƏRTLƏRİ
Yalnız QR ilə ödəniş keşbek qazandırır?
```

### `851979b108-004` — section, az, campaigns, 504 tokens

<https://abb-bank.az/kampaniyalar/abb-play-master-liqa-il-futbol-h-y-cani-qayidir>

```text
"ABB Play - Master Liqa" ilə futbol həyəcanı qayıdır!
Kampaniya statusu: aktivdir (09.09.2026 – 05.06.2027)

Sea Breeze üzrə ev ipotekası əldə edən müştərilər kampaniya boyu 1 dəfə 100 000 qol qazanır.
Müştəri kampaniyaya qoşuldu → Sea Breeze ipotekası rəsmiləşdirdi → 100 000 qol
Kampaniyadan əvvəl rəsmiləşdirilmiş kreditlərə qol verilmir.
Müştəri Sea Breeze ipotekası ilə 100 000 qol qazandı → kampaniyada ikinci ipoteka götürdü → 0 qol
Kampaniya ərzində yalnız 1 dəfə qol hesablanır.
2. Dövlət və daxili ipoteka nə qədər qol qazandırır?
Dövlət və ya daxili ipoteka krediti əldə edən müştərilər kampaniya boyu 1 dəfə 50 000 qol qazanır.
Qeyd: Sea Breeze – ev ipotekası bu bənddən istisnadır.
Müştəri kampaniyaya qoşuldu → daxili ipoteka rəsmiləşdirdi → 50 000 qol
Kampaniyadan əvvəl rəsmiləşdirilmiş ipoteka üzrə qol verilmir.
3. TamKart Kredit kartı limit açmaq nə qədər qol qazandırır?
Kampaniyaya qoşulduqdan sonra TamKart kredit kartlarında yeni kredit limiti açıldıqda 20 000 qol qazanılır.
Nümunə 1: Müştərinin kredit kartı yoxdur → kampaniyaya qoşulur → TamKart limiti açır → 20 000 qol
Nümunə 2: Müştərinin 1 000 AZN limiti var → kampaniya zamanı limiti 2 000 AZN edir → 0 qol (limit artımı qol vermir)
Nümunə 3: Müştəri mövcud TamKart limitini bağlayıb yenidən TamKart limiti açır → 0 qol (eyni məhsul təkrar qol vermir)
Qol müraciət anında deyil, limitin faktiki aktivləşdiyi anda hesablanır.
Qeyd: Kampaniya ərzində Bank tərəfindən yeni kredit kartı məhsulu yaradılarsa, mövcud kartını həmin yeni məhsula dəyişən (yeni limit açan) müştərilərə 20 000 qol təqdim ediləcəkdir.
4. Fayda Max abunəliyi nə qədər qol qazandırır?
Kampaniyaya qoşulduqdan sonra ilk dəfə Fayda Max abunəliyi aktiv edən müştərilər 5 000 qol qazanır.
Müştəri qoşulduqdan sonra Fayda Max abunəliyi aktiv etdi → 5 000 qol
Müştərinin kampaniyaya qoşulmazdan əvvəl aktiv Fayda Max abunəliyi var idi → 0 qol
Kampaniya ərzində yalnız 1 dəfə qol verilir. Abunəliyin səviyyəsindən asılı olmayaraq eyni qol hesablanır.
```


# Chunk quality report

Settings: target 350 tokens, max 512, overlap 1 paragraph(s), tokenizer `BAAI/bge-m3`.

## Summary

| Metric | Value |
|--------|-------|
| Chunks | 8044 |
| Source pages | 4223 |
| By type | section: 6431, faq: 1613 |
| By language | az: 4282, ru: 2220, en: 1542 |
| Tokens p10 / p50 / p90 / p99 / max | 66 / 293 / 472 / 502 / 504 |
| Total tokens | 2,206,865 |
| Over the 512-token limit | 0 |
| Pages split into more than 10 chunks | 93 |

## By category

| Category | Chunks | Median tokens |
|----------|-------:|--------------:|
| procurement | 1523 | 374 |
| news | 1494 | 347 |
| individual | 1446 | 108 |
| general | 1012 | 117 |
| campaigns | 789 | 304 |
| business | 695 | 201 |
| about | 489 | 437 |
| service_network | 335 | 198 |
| csr | 175 | 320 |
| investor_relations | 46 | 185 |
| press_releases | 29 | 125 |
| home | 11 | 350 |

## Token distribution

| Tokens | Chunks | |
|--------|-------:|---|
| 0–49 | 249 | █ |
| 50–99 | 1356 | ███████ |
| 100–199 | 1099 | █████ |
| 200–299 | 1431 | ███████ |
| 300–399 | 2008 | ██████████ |
| 400–511 | 1901 | █████████ |
| 512–… | 0 |  |

## Random samples

### `89504f47e9-001` — section, en, individual, 272 tokens

<https://abb-bank.az/en/ferdi/kartlar/kredit-kartlari>

```text
TamKart Credit Card

## Credit card application terms
To apply for a credit card, it is sufficient to fill out the online application form and provide the required information. After the application is reviewed, the approved credit card becomes ready for use within a short period of time. Since the credit card application process is simple and convenient, it can be completed without visiting a bank branch. This approach allows users to obtain their card quickly and efficiently, without wasting time.
## Credit cards > TamKart > TamKart Max
Get the maximum benefit out of your credit card with TamKart Max! 12-month interest-free payments with TAM 12, “Convert to installments” up to 24 months, and many more.
Credit limit: Up to 30 000 ₼
Grace period: Up to 60 months
Interest-free payments: TAM 12
Installment: Up to 24 months
## Credit cards > TamKart > TamKart Classic
You will earn more cashback from your payments with Faydali Cashback, partner stores, and Fayda Max. Make your purchases with TamKart and enjoy interest-free installments for up to 24 months.
Credit limit: Up to 30,000 ₼
Installment: Up to 24 months, no interest rate
Grace period: Up to 60 days
Price: Free
```

### `37992897cc-023` — faq, az, individual, 462 tokens

<https://abb-bank.az/ferdi/investisiya>

```text
ABB mobile ilə qiymətli kağızlara investisiya!
Tez-tez verilən suallar

Sual: SELL LIMIT sifarişi nədir?
Cavab: SELL LIMIT – bu sifarişini yerləşdirmək üçün iki parametri müəyyən etməlisiz: satmaq istədiyiniz qiymətli kağızın miqdarı və satışın minimal qiyməti (bu qiymət limit qiyməti olaraq qəbul edilir). Sifarişiniz sistemə yerləşdirildikdən sonra sifarişin icra alqoritmi satmaq istədiyiniz qiymətli kağızın bazar qiyməti ilə müəyyən etdiyiniz limit qiymətini müqayisə edir. Əgər bazarda olan alış sifarişlərinin qiyməti sizin limit qiymətinizə bərabər və ya bu qiymətdən çox olarsa, sifarişiniz “ən yaxşı qiymət prinsipi” ilə icra ediləcək. Satış sifarişlərinə nisbətdə “ən yaxşı qiymət prinsipi” satış sifarişlərinizin qiymət baxımından bazarda mövcud olan ən yaxşı alış qiyməti ilə uzlaşdırılması (müvafiq qiymətlə əqdin bağlanması) prinsipidir. Nəzərə almalısınız ki, SELL LIMIT sifarişi tam və qismən icra edilə və ya ümumiyyətlə icra edilməyə bilər. Sifarişinizin icrası bazarda uyğun qiymətli əks sifarişlərin, yəni alış sifarişlərin olması ilə yanaşı bu əks sifarişlər ilə alınan qiymətli kağızların həcmindən (miqdarından) də asılıdır. Əgər qiymət üzrə uyğun gələn əks sifarişlərin həcmi sizin satmaq istədiyiniz həcmdən azdırsa, o zaman satış sifarişiniz natamam icra olunacaq və müvafiq həcmdə və qiymətdə əks sifarişlər əmələ gələnədək gözləmə rejimində qalacaqdır. Misal 1: SELL LIMIT sifarişinin tam icrası
İnvestisiya portfelinizdə 16 ədəd Apple Inc. (ticarət simvolu: AAPL) şirkətinin səhmi mövcuddur. Sizin bu səhmlərdən 10 ədədini ən azı $180-a satmaq niyyətiniz var. Bu halda, siz miqdar olaraq 10 ədəd, limit qiyməti olaraq $180 müəyyən edib sistemə SELL LIMIT sifarişi yerləşdirirsiniz. Həmin an bazarda olan alış sifarişləri aşağıdakılardır:
· $179-a 1 ədəd AAPL səhmləri alınır;
· $180-a 3 ədəd AAPL səhmləri alınır;
· $181,50-a 8 ədəd AAPL səhmləri alınır.
```

### `e7fbdeff63-008` — faq, az, general, 56 tokens

<https://abb-bank.az/azal-bilet-abb-mobile-ile-aviabiletinizi-onlayn-alin>

```text
AZAL Bilet - ABB mobile ilə aviabiletinizi onlayn alın
Tez-tez verilən suallar

Sual: AZAL biletinin qiymətini necə yoxlamaq olar?
Cavab: İstiqamət və tarix seçərək mövcud uçuşların qiymətlərini müqayisə edə bilərsiniz.
```

### `e29ded27cf-000` — section, az, procurement, 358 tokens

<https://abb-bank.az/haqqimizda/satinalmalar/musabiqelerin-elani/bank-terefinden-oracle-sistemleri-ucun-yeni-lisenziyalarin-satin-alinmasi-iyun-2023>

```text
Bank tərəfindən Oracle sistemləri üçün yeni lisenziyaların satın alınması
Tarix: 07.06.2023

7 İyun, 2023
Tenderin adı: “ABB” ASC tərəfindən Oracle sistemləri üçün yeni lisenziyaların satın alınması
Tenderin elan tarixi: 07.06.2023
İştirak haqqı:
BANKIN ADI: ABB
VÖEN : 9900001881
KOD: 805250
SWIFT: IBAZAZ2X
M/h: AZ03NABZ01350100000000002944
H/h: AZ12IBAZ34501019440000100100 AZN
H/h: AZ33IBAZ34511018400000100100 USD
- tender təklifi (tender zərflərinin açıldığı tarixdən (22 iyun 2023-cü il) sonra azı 30 (otuz) bank günü (yəni ən azı 08 avqust 2023-cü il tarixinədək) qüvvədə olmalıdır;
- tender təklifi dəyərinin 1 (bir) faizi həcmində bank təminatı (tender təklifinin qüvvədə olma müddətinin sonuncu günündən azı 30 bank günü çox olmalıdır (yəni ən azı 18 sentyabr 2023-cü il tarixinədək qüvvədə olmalıdır);
İddiaçılar tenderdə iştirak etmək üçün yuxarıda göstərilən sənədləri (tender təklifi və bank təminatı istisna olmaqla) 14 iyun 2023-cü il saat 17:00-a qədər, tender təklifi və bank təminatını isə möhürlənmiş ikiqat zərflərdə 21 iyun 2023-cü il saat 17:00-a qədər Bakı şəhəri, Nəsimi rayonu, Nizami küçəsi, 67 nömrəli ünvana təqdim etməlidirlər.
İddiaçıların təklifləri 22 iyun 2023-cü il saat 16:00-da Bakı şəhəri, Nəsimi rayonu, Nizami küçəsi, 67 nömrəli ünvanda açılacaqdır.
Tender Komissiyası
```

### `754876f930-002` — section, az, news, 342 tokens

<https://abb-bank.az/xeberler/abb-nin-yeni-sehmdarlari-da-2024-ci-ilin-neticeleri-uzre-dividendler-alacaqlar>

```text
ABB-nin yeni səhmdarları da 2024-cü ilin nəticələri üzrə dividendlər alacaqlar
Tarix: 01.08.2024

- Bəli, səhmlərə ABB mobile tətbiqi, ölkəmizdəki əksər bankların filialları, eləcə də Azərbaycanda fəaliyyət göstərən investisiya şirkətləri vasitəsilə abunə yazılmaq mümkündür. Səhm almaq niyyətində olan investorlara tövsiyəmiz bu olardı ki, qərarlarını sürətləndirib sifarişlərini vaxtında etsinlər. Çünki müddət azalır, hazırki proses sentyabrın 10-da tamamlanacaq.
Digər tərəfdən, səhm sifariş etmiş investorlar 10 sentyabr tarixinə qədər ABB-də ödədikləri sifariş məbləğinə görə 7% illik gəlirliliklə faiz qazancı əldə edirlər. Bu faiz gəliri investorlara əvvəlcədən, yəni sifariş verilən gün ödənilir. Səhmlərə daha tez abunə yazılanlar bu imkandan da faydalanmış olurlar.
Bundan başqa, avqustun 1-dən etibarən ABB səhmi sifariş verən investorlar üçün lotereya kampaniyasına da start verdik. İnvestorlar avqust və sentyabr aylarındakı səhm sifarişlərinə görə 5000 manatadək uduş şansı qazanacaqlar.
- ABB səhmlərini təkrar bazarda satmaq olacaqmı?
- Yerləşdirmə bitdikdən sonra hər bir səhmdar öz səhmlərini “ABB-İnvest” şirkəti və ya digər investisiya şirkətləri vasitəsilə sata bilər. Bununla yanaşı, sentyabrın sonunadək səhmləri ABB mobile vasitəsilə də satmaq mümkün olacaq. Yəni səhmdar malik olduğu səhmləri istədiyi zaman ən rahat şəkildə sata biləcək. ABB səhmlərinin alqı-satqısında yüksək likvidliyin təmin olunması üçün hazırda Bank aidiyyəti qurumlarla müvafiq tədbirlər həyata keçirir.
```

### `f39ca662a9-000` — section, az, news, 417 tokens

<https://abb-bank.az/xeberler/abb-de-sansli-2026-lotereya-kampaniyasi-baslandi>

```text
ABB-də “Şanslı 2026” lotereya kampaniyası başlandı!
Tarix: 15.11.2025

15 Noyabr, 2025
Müştərilərini daim xoş sürprizlərlə sevindirən ABB “Şanslı 2026” lotereya kampaniyasına start verib. Bu kampaniya müştərilərə avtomobil də daxil olmaqla qiymətli hədiyyələr qazandırır.
Şərtlərə görə, 15.11.2025-ci tarixindən 15.01.2026-cı il tarixinə qədər ABB-nin kartları ilə aparılan hər 20 AZN ödəniş müştəriyə 1 şans qazandırır. ABB-nin yeni məhsullarından istifadə edən müştərilər isə əlavə şanslar da əldə edirlər.
Belə ki, nağd kredit və depozit məhsullarından istifadə birdəfəlik 100 şans, kredit kartının sifarişi 100 şans, debet kartı sifarişi 20 şans gətirir. Bu imkan əməkhaqqı, təqaüd, biznes və sahibkar kartlarına aid deyil.
Şans qazanmaq istəyən istifadəçilər ABB mobile tətbiqinin “Lotereya” bölməsinə keçid edib, “Aktiv et” düyməsini sıxıb iştiraklarını aktivləşdirməlidirlər. Eyni müştəri yalnız 1 dəfə qalib ola bilər.
Birinci yerin qalibi “Li Auto L6 Pro” avtomobili qazanacaq. Digər yerlərin qaliblərinə isə, “MacBook Air 13 M4” kompüterləri, “İphone 16 Pro” telefonları, “Apple Watch Series 11” saatları, 1000 AZN-lik səyahət kartları, “AirPods 4” qulaqlıqları və “Faydalı Keşbek”lər veriləcək. Kampaniya zamanı oynanılacaq hədiyyə sayı ümumən 2026-dır.
Qaliblər 03 fevral 2026-cı il tarixində ABB-nin rəsmi Facebook səhifəsində canlı yayımda elan olunacaqlar.
ABB-nin müasir, faydalı və universal məhsul və xidmətləri barədə məlumatları Bankın filial və şöbələrindən, https://abb-bank.az/ rəsmi internet səhifəsindən və ya 937 nömrəli Məlumat Mərkəzindən, həmçinin sosial şəbəkələrdəki rəsmi korporativ səhifələrindən əldə etmək olar.
```

### `89c6a99595-009` — faq, ru, general, 71 tokens

<https://abb-bank.az/ru/kreditle-komputer>

```text
Компьютер в кредит
Часто задаваемые вопросы

Вопрос: Можно ли оформить компьютер в кредит только по удостоверению личности?
Ответ: Да, оформить компьютер в кредит только по удостоверению личности возможно. После выбора товара в магазине-партнёре необходимо ознакомиться с условиями в приложении ABB Mobile и после подтверждения оплачивать покупку по частям.
```

### `5df4451210-088` — section, az, about, 433 tokens

<https://abb-bank.az/haqqimizda/hesabatlar>

```text
Maliyyə və korporativ hesabatlar
İnvestisiya portfeli

Son yenilənmə - 23.01.2026
Depozitlər və Qiymətli Kağızlar portfeli (investisiya portfeli daxil) 2025, 12 ay üzrə (https://cdn.abb-bank.az/Depozitler_ve_Qiymetli_Kagizlar_98657973c4.pdf)
Depozitlər və Qiymətli Kağızlar portfeli (investisiya portfeli daxil) 2024, 12 ay üzrə (https://cdn.abb-bank.az/1737551832_Depoz_Itl_r_v_Q_Iym_tl_I_Kagizlar_portfel_I_Invest_Is_Iya_portfel_I_dax_Il_31_683c18b457.pdf)
Depozitlər və Qiymətli Kağızlar portfeli (investisiya portfeli daxil) 2023, 12 ay üzrə (https://cdn.abb-bank.az/1706248276_depozitler_ve_qiymetli_kagizlar_portfeli_investisiya_portfeli_daxil_31122023_92d72b279c.pdf)
Depozitlər və Qiymətli Kağızlar portfeli (investisiya portfeli daxil) 2022, 12 ay üzrə (https://cdn.abb-bank.az/1674829870_depozitler_ve_qiymetli_kagizlar_portfeli_investisiya_portfeli_daxil_31122022_8f59191630.pdf)
Depozitlər və Qiymətli Kağızlar portfeli (investisiya portfeli daxil) 2021, 12 ay üzrə (https://cdn.abb-bank.az/1651065419_depozitler_ve_qiymetli_kagizlar_portfeli_investisiya_portfeli_daxil_31122021_5ad217bf0d.pdf)
```

### `9d248b0890-000` — section, az, procurement, 385 tokens

<https://abb-bank.az/haqqimizda/satinalmalar/musabiqelerin-elani/bank-terefinden-mobilelron-proqram-teminati-ucun-yeni-lisenziyalarin-ve-texniki-destek-xidmetlerinin-satin-alinmasi-kotirovka-190424>

```text
Bank tərəfindən “Mobilelron” proqram təminatı üçün yeni lisenziyaların və texniki dəstək xidmətlərinin satın alınması
Tarix: 19.04.2024

19 Aprel, 2024
Kotirovka sorğusunun adı: "ABB" ASC tərəfindən “Mobilelron” proqram təminatı üçün yeni lisenziyaların və texniki dəstək xidmətlərinin satın alınması
Kotirovka sorğusunun elan tarixi: 19.04.2024
Kotirovka sorğusunda iştirak etmək istəyən iddiaçılar öz qiymət kotirovkalarını qapalı zərfdə imzalanmış və ya möhürlənmiş şəkildə Bakı şəhəri, Nəsimi rayonu, Nizami küçəsi 67 ünvanında yerləşən “ABB” ASC-nin Baş ofisinə 29 aprel 2024-cü il saat 17:00-a qədər təqdim etməlidirlər.
Kotirovka sorğusu proseduru üzrə zərflərin açılışı 30 aprel 2024-cü il saat 15:00-da keçiriləcəkdir.
- Kotirovka sorğusunda iştirak etmək istəyən iddiaçılar iştirak niyyətini bildirmək üçün Orkhan.Taghiyev@abb-bank.az və pod@abb-bank.az e-poçt ünvanına şirkətin adını qeyd etməklə “iştirakımı təsdiq edirəm” mətnini göndərməlidir.
- Göndərilən müraciətdə e-poçtun “subject” hissəsində - "ABB" ASC tərəfindən “Mobilelron” proqram təminatı üçün yeni lisenziyaların və texniki dəstək xidmətlərinin satın alınması - qeyd edilməlidir.
Kotirovka sorğusu ilə bağlı əlavə məlumat almaq üçün adı qeyd edilmiş “ABB” ASC-nin əməkdaşına (Orxan Tağıyevə: (012) 493-00-91, daxili 82-16/82-20, elektron poçt ünvanları: (Orkhan.Taghiyev@abb-bank.az və pod@abb-bank.az) müraciət edə bilərsiniz.
Satınalma Komissiyası
- terrorçuluğun maliyyələşdirilməsi;
Performans dəyərləndirilməsi prosesi
- Ödəniş şərtləri
```

### `c1c24ba28c-000` — section, en, general, 100 tokens

<https://abb-bank.az/en/yol-hereketi-cerimelerimi-nece-odeye-bilerem>

```text
Pay Fines Online | ABB ✅
Your questions > Detallar

Rashad Aliyev asks
How can I pay my traffic fines?
You can easily and securely pay traffic violation fines using the ABB mobile application. To do so, simply go to the Payments section, enter your fine details, and confirm the payment. This allows you to pay your fines conveniently at any time and from anywhere.
For more detailed information, please visit the ABB mobile Payments page.
```

### `7f15ea468d-000` — section, az, procurement, 361 tokens

<https://abb-bank.az/haqqimizda/satinalmalar/musabiqelerin-elani/atm-sebekesi-ucun-gprs-modemlerin-satin-alinmasi>

```text
ATM şəbəkəsi üçün GPRS modemlərin satın alınması
Tarix: 26.10.2020

26 Oktyabr, 2020
Tenderin adı: “ABB” Açıq Səhmdar Cəmiyyətinin mövcud ATM şəbəkəsi üçün GPRS modemlərin satın alınması.
Tenderin elan tarixi: 26.10.2020
İştirak haqqı:
BANKIN ADI: ABB
VÖEN : 9900001881
KOD: 805250
SWIFT: IBAZAZ2X
M/h: AZ03NABZ01350100000000002944
H/h: AZ12IBAZ34501019440000100100 AZN
H/h: AZ33IBAZ34511018400000100100 USD
- tender təklifi (tender zərflərinin açıldığı tarixdən (17 noyabr 2020-ci il) sonra azı 30 (otuz) bank günü (yəni ən azı 29 dekabr 2020-ci il tarixinədək) qüvvədə olmalıdır;
- tender təklifi dəyərinin 1 (bir) faizi həcmində bank təminatı (tender təklifinin qüvvədə olma müddətinin sonuncu günündən azı 30 bank günü çox olmalıdır (yəni ən azı 15 fevral 2021-ci il tarixinədək qüvvədə olmalıdır);
İddiaçılar tenderdə iştirak etmək üçün yuxarıda göstərilən sənədləri (tender təklifi və bank təminatı istisna olmaqla) 10 noyabr 2020-cı il saat 17:00-a qədər, tender təklifi və bank təminatını isə möhürlənmiş ikiqat zərflərdə 16 noyabr 2020-cı il saat 17.00-a qədər Bakı şəhəri, Nəsimi rayonu, Nizami küçəsi, 67 nömrəli ünvana təqdim etməlidirlər.
İddiaçıların təklifləri 17 noyabr 2020-cı il saat 16.00-da Bakı şəhəri, Nəsimi rayonu, Nizami küçəsi, 67 nömrəli ünvanda açılacaqdır.
Tender komissiyası
```

### `ac5be36d3e-000` — section, az, procurement, 482 tokens

<https://abb-bank.az/haqqimizda/satinalmalar/musabiqelerin-elani/bank-terefinden-oracle-exadata-engineering-system-avadanliginin-satin-alinmasi>

```text
Bank tərəfindən “Oracle Exadata Engineering System” avadanlığının satın alınması
Tarix: 24.10.2025

24 Oktyabr, 2025
lot - 1 Lot üzrə 500 (beş yüz) manat
Tenderin adı: “ABB” ASC tərəfindən “Oracle Exadata Engineering System” avadanlığının satın alınması
Tenderin elan tarixi: 24.10.2025
İştirak haqqı:
Lot – 1 üzrə 500 (beş yüz) manat
BANKIN ADI: ABB
VÖEN: 9900001881
KOD: 805250
SWIFT: IBAZAZ2X
M/h: AZ03NABZ01350100000000002944
H/h: AZ12IBAZ34501019440000100100 AZN
H/h: AZ33IBAZ34511018400000100100 USD
· tenderdə iştirak haqqının ödənilməsi barədə bank sənədi;
· tender təklifi (tender zərflərinin açıldığı tarixdən (18 noyabr 2025-ci il) sonra azı 30 (otuz) bank günü (yəni ən azı 08 yanvar 2026-cı il tarixinədək) qüvvədə olmalıdır;
· Tender təklifinin 1%-i dəyərində bank təminatı (tender təklifinin qüvvədə olma müddətinin sonuncu günündən azı 30 bank günü çox olmalıdır (yəni ən azı 19 fevral 2026-cı il tarixinədək qüvvədə olmalıdır);
· iddiaçının Azərbaycan Respublikasında vergilərə və digər icbari ödənişlərə dair yerinə yetirilməsi vaxtı keçmiş öhdəliklərinin olmaması haqqında müvafiq vergi orqanından arayış; rəsmi formada təqdim edilməlidir (imzalı, möhürlü və ya notarial qaydada təsdiq edilmiş)
· iddiaçının son bir ildəki fəaliyyəti haqqında vergi orqanları tərəfindən təsdiq olunmuş maliyyə hesabatının surəti; rəsmi formada təqdim edilməlidir (imzalı, möhürlü və ya notarial qaydada təsdiq edilmiş)
· iddiaçının son bir ildəki maliyyə vəziyyəti haqqında bank arayışı;
· iddiaçının tam adı, hüquqi statusu, nizamnaməsi, qeydiyyatdan keçdiyi ölkə (notarial qaydada təsdiq edilmiş) və bank rekvizitləri;
· iddiaçının öz mülahizəsinə uyğun digər sənədlər;
· iddiaçı qeyri-rezident olduğu halda qeyri-rezident hesab edilən iddiaçının vergi rezidentliyini müəyyən etmək məqsədi ilə həmin şəxslər vergi rezidentliyini təsdiq edən sənədi (sertifikatı) təqdim etməlidir.
```

### `1b19228e29-001` — section, en, procurement, 364 tokens

<https://abb-bank.az/en/haqqimizda/satinalmalar/musabiqelerin-elani/ehtimal-olunan-deleduzluq-fraud-hallarinin-ve-insidentlerin-mueyyen-olunmus-indikatorlar-uzerinden-askarlanmasi-ucun-proqram-teminatinin-satin-alinmasi2104>

```text
Procurement of software for detection of possible fraud and incidents on the basis of certain indicators
Date: 21.04.2021

Required documents for participation in the tender:
- A copy of the financial report of the bidder on its activity for the last year, approved by the tax authorities;
- Bank statement on the financial condition of the bidder for the last year (if the operations period is shorter, for the whole activity period);
- Full name, legal status, charter, country of registration and bank details of the bidder;
- Other documents at the discretion of the bidder;
- If the bidder is a non-resident, these persons must submit a document (certificate) confirming the tax residency in order to determine the tax residency of the bidder who is considered a non-resident.
Documents must be prepared in 2 copies (original and copy), in the Azerbaijani language (tender proposals in a foreign language must be translated into Azerbaijani).
To participate in the tender, bidders must submit the above documents (excluding the tender proposal and bank guarantee) until May 05, 2021, at 17:00, and the tender proposal and bank guarantee in sealed double envelopes until May 16, 2021, at 17:00, to the following address: Baku city, Nasimi district, Nizami street, 67.
Submitted envelopes after the deadline will be returned unopened.
Bidders' proposals will be opened on May 17, 2021, at 15:50 at the address: 67, Nizami Street, Nasimi district, Baku.
Authorized representatives of the bidders may attend. The participating representatives must submit a document (power of attorney) confirming their authority.
Tender committee
```

### `02505efa9c-000` — section, ru, news, 384 tokens

<https://abb-bank.az/ru/xeberler/abb-en-yaxsi-isegoturen-beynelxalq-sertifikatina-layiq-goruldu>

```text
Банк ABB удостоен международного сертификата «Лучший работодатель»!
Дата: 13.06.2024

13 июня, 2024
Банк ABB стремится стать лучшим работодателем в банковском секторе нашей страны и последовательно движется к этой цели. В результате своих усилий Банк получил сертификат международной организации "Top Employers Institute" («Институт лучших работодателей»).
Аудиторы организации проводили сертификационный процесс в течение трех месяцев, оценивая Банк ABB по 255 международным стандартам. Эти стандарты проверялись на соответствие в Банке ABB. Анализ включал такие аспекты, как рабочая среда, привлечение талантов, обучение, разнообразие, равенство и инклюзивность, благополучие, развитие и другие.
Банк ABB выполнил 88% критериев и получил сертификат «Лучший работодатель». Минимальное требование для получения этого сертификата составляет 60%. Согласно мировому опыту, в среднем компании, получившие этот сертификат, соответствуют 85% критериев. Банк ABB превзошел этот показатель, что подчеркивает его превосходство в применении международных практик управления персоналом и создании достойных условий труда для сотрудников.
"Top Employers Institute" до сих пор сертифицировал более 2300 организаций в 121 стране и регионе. Процессы сертификации, проводимые институтом, оказывают положительное влияние на жизнь более 12 миллионов сотрудников по всему миру. Среди компаний, получивших сертификат «Лучший работодатель», такие мировые бренды, как BP, Coca-Cola, HSBC, Unicredit, BMW, Puma, Pepsico, Toyota, Walmart, Philip Morris International, Ferrari, Mercedes, Marriott International, Bosch, HUAWEI, Vodafone, EY.
Подробнее о "Top Employers Institute" можно узнать здесь.
```

### `56b0110462-013` — faq, en, general, 66 tokens

<https://abb-bank.az/en/krediti-olanlara-kredit>

```text
Loans for Existing Borrowers
Frequently asked questions

Question: What Are the Loan Terms for Customers with Existing Credit?
Answer: The loan amount, term, interest rate, and monthly payment may be determined based on the terms of the selected loan product and the outcome of the application assessment.
```


## One sample per category

### `d6e47f9e75-005` — section, en, about, 328 tokens

<https://abb-bank.az/en/haqqimizda/senedler>

```text
Documents and resources
AML/CFT

AML Questionnaire (https://cdn.abb-bank.az/1639461324_aml_questionnaire_eng_53ec628c06.pdf)
Policy of “ABB” OJSC with regard to actions against anti-money laundering and combating the financing of terrorism (https://cdn.abb-bank.az/1744373112_aml_policy_e3e0a95932.pdf)
“Know the Client Policy” of the “ABB” OJSC in its activity in the field of fight against legalization of monetary funds or other property obtained through the crime and financing of terrorism (https://cdn.abb-bank.az/1680678979_kyc_2023_866d09ddc8.pdf)
Certification Regarding Correspondent Accounts for Foreign Banks (https://cdn.abb-bank.az/IBA_Patriot_Act_July_2025_stamped_2e273d18aa.pdf)
Wolfsberg Questionnaire (https://cdn.abb-bank.az/IBA_Wolfsberg_CBDDQ_v1_4_20_04_2026_2ba83c56f1.pdf)
FinTech Questionnaire (https://cdn.abb-bank.az/Fin_Tech_Questionnaire_09_09_2025_2_c07392940b.docx)
```

### `4f9638e7db-002` — faq, ru, business, 120 tokens

<https://abb-bank.az/ru/biznes/korporativ/kocurmeler-1>

```text
Быстрые денежные переводы
Часто задаваемые вопросы

Вопрос: Для других целей:
Ответ: - Плата за участие в международных организациях, конференциях, выставках;
- Плата за подписку на периодические издания зарубежных стран; плата за размещение объявлений;
- Переводы для оплаты за образование, лечение и для материальной помощи, оказываемой гражданам республики с такими целями;
- Переводы для оплаты за использование авторских прав и франчайзинга;
- Возмещение командировочных расходов туристов лицами, осуществляющими туристическую деятельность.
```

### `bdb9165a2b-000` — section, az, campaigns, 173 tokens

<https://abb-bank.az/kampaniyalar/abb-azal-miles-kartlarindan-bayram-teklifleri>

```text
ABB-AZAL Miles kartlarından bayram təklifləri
Kampaniya statusu: bitib (17.03.2025 – 19.03.2025)

17.03.2025 - 19.03.2025
Aktiv deyil
17-19 mart 2025-ci il tarixlərində ABB-AZAL Miles kartı sifariş edən müştərilər eksklüziv üstünlüklərdən faydalanacaqlar!
Bu müddət ərzində:
ABB-AZAL Miles Visa Platinum və ya Mastercard World Black Edition kartlarını əldə edən müştərilər 4500 mil “Xoşgəldin mili” qazanacaqlar. Bu, İstanbul uçuş biletinin 50%-nə bərabərdir və heç bir əlavə dövriyyə şərti tələb olunmur!
ABB-AZAL Miles Visa Infinite və ya Mastercard World Elite kartlarını əldə etmək istəyən müştərilər isə 50% endirim qazanaraq bu premium kartları 1000 AZN əvəzinə, 500 AZN-ə əldə edə biləcəklər.
```

### `cb1aaf9201-001` — section, az, csr, 138 tokens

<https://abb-bank.az/korporativ-sosial-mesuliyyet/4-cu-reqemsal-jurnalistikaya-dogru-proqramina-start-verilir-ksm>

```text
4-cü “Rəqəmsal Jurnalistikaya doğru” proqramına start verilir
Tarix: 04.10.2022

Layihə ilə bağlı ətraflı məlumat əldə etmək üçün:
https://www.digital.gov.az/digitalazerbaijan/webinars/6/reqemsal-jurnalistikaya-dogru-proqrami-4
Əlavə suallar üçün digicom@asan.gov.az
İndiyədək sayca 3 “Rəqəmsal Jurnalistikaya doğru” proqramı keçirilib. Layihə çərçivəsində 100-dən çox media nümayəndəsinə təlimlər verilib, sertifikatlar təqdim edilib.
Proqramın media tərəfdaşı “ASAN Radio”dur.
Rəqəmsal sahədə bizimlə inkişaf edin!
```

### `038bb7c59a-001` — faq, az, general, 59 tokens

<https://abb-bank.az/aciq-bankciliq-kesbek-kampaniyasi>

```text
ABB - Müasir, Faydalı, Universal
Tez-tez verilən suallar

Sual: Açıq Bankçılıq nədir?
Cavab: Açıq Bankçılıq - ABB mobile tətbiqindən istifadə edərək digər banklara məxsus kartlarınızı bir yerdə idarə etməyə imkan verən müasir bankçılıq funksiyasıdır.
```

### `47eb7de06e-003` — section, az, home, 66 tokens

<https://abb-bank.az/>

```text
Tam DigiCard
Gələcəyinizi ABB ilə qurun! > ABB — contact information / əlaqə

Tel:+994 12 493 00 91
E-poçt:info@abb-bank.az
Faks:+994 12 493 00 91
Ünvan:67, Nizami küç., AZ1005 Bakı, Azərbaycan
```

### `f2dbcc1d06-000` — section, az, individual, 348 tokens

<https://abb-bank.az/ferdi/kartlar/kredit-kartlari>

```text
TamKart Kredit Kartı

Məişət əşyaları, səyahət, elektronika və daha bir çox alış-verişlərinizdə TamKart yanınızdadır. TAM alın, 24 ayadək hissə-hissə ödəyin. FİFD: min.18.40% - maks.41.60%
## Kredit kartı nədir?
Kredit kartı sizə əvvəlcədən müəyyən edilmiş limit çərçivəsində alış-veriş etmək və ödənişləri sonradan həyata keçirmək imkanı yaradır. Bu vasitə həm gündəlik xərclər, həm də planlaşdırılmış alışlar üçün rahat həll sayılır. Kredit kartı ilə ödəniş edərkən nağd pula ehtiyac qalmır və bütün əməliyyatları izləmək daha asan olur. Müxtəlif bonus və kampaniyalar da kredit kartı istifadəsini daha sərfəli edir. Sərfəli kredit kartları gündəlik xərclərinizi rahat idarə etmək və alış-verişlərdə əlavə üstünlüklər qazanmaq üçün ideal maliyyə alətidir. Bu kartlar vasitəsilə nağdsız ödənişlər edə, kampaniyalardan yararlana və büdcənizi daha planlı şəkildə idarə edə bilərsiniz.
## Kredit kartları harda istifadə etmək olar?
Kredit kartları fərqli ehtiyaclara uyğun olaraq müxtəlif limit, güzəşt müddəti və əlavə imkanlarla təqdim olunur. İstifadəçilər öz xərcləmə vərdişlərinə uyğun kredit kartları seçərək ödənişlərini daha səmərəli şəkildə idarə edə bilərlər. Bu kartlar onlayn ödənişlərdə, səyahətlərdə və gündəlik alışlarda geniş istifadə olunur. Kredit kartları büdcə planlamasını asanlaşdıraraq maliyyə çevikliyini artırır. Sərfəli kredit kartları həm onlayn, həm də fiziki mağazalarda rahat istifadə imkanı təqdim edir və müxtəlif güzəştli şərtlərlə seçilir. Doğru kart seçimi ilə ödənişlərinizi daha çevik və rahat şəkildə həyata keçirmək mümkündür.
```

### `c2babdf680-001` — section, ru, investor_relations, 494 tokens

<https://abb-bank.az/ru/investorlarla-elaqe>

```text
Инвестируйте в своё будущее с ABB!
200 mln. AZN

Выплаченные дивиденды
Коэффициенты по финансовым показателям: Дивиденд на акцию (DPS); 2020: 0,03; 2021: 0,03; 2022: 0,03; 2023: 0,04; 2024: 0,04; 2025: 0,04
Коэффициенты по финансовым показателям: Доходность активов (ROA); 2020: 1,9%; 2021: 1,3%; 2022: 2,2%; 2023: 2,7%; 2024: 2,6%; 2025: 2,80%
Коэффициенты по финансовым показателям: Доходность акций (Earnings Yield)*; 2020: 14,4%; 2021: 11,2%; 2022: 23,6%; 2023: 31,1%; 2024: 29,0%; 2025: 31,60%
Коэффициенты по финансовым показателям: Чистая прибыль на акцию (EPS); 2020: 0,04; 2021: 0,03; 2022: 0,06; 2023: 0,08; 2024: 0,08; 2025: 0,09
Коэффициенты по финансовым показателям: Дивидендная доходность (Dividend Yield)*; 2020: 10,2%; 2021: 10,1%; 2022: 12,8%; 2023: 15,1%; 2024: 15,6%; 2025: 15,60%
Коэффициенты по финансовым показателям: Доходность собственного капитала (ROE); 2020: 11%; 2021: 8%; 2022: 16%; 2023: 20%; 2024: 17%; 2025: 17%
Коэффициенты по финансовым показателям: Соотношение цены акции к прибыли (P/E ratio)*; 2020: 6,94; 2021: 8,89; 2022: 4,24; 2023: 3,22; 2024: 3,44; 2025: 3,17
Коэффициенты по финансовым показателям: Дивиденд на акцию (DPS); 2020: 0,03
Коэффициенты по финансовым показателям: Доходность активов (ROA); 2020: 1,9%
Коэффициенты по финансовым показателям: Доходность акций (Earnings Yield)*; 2020: 14,4%
```

### `a48148c8e7-006` — section, ru, news, 492 tokens

<https://abb-bank.az/ru/xeberler/abb-yeni-strateji-dovre-daxil-olub-musahibimiz-bankin-idare-heyeti-sedri-abbas-ibrahimovdur>

```text
«ABB вступает в новый стратегический этап»
Дата: 15.11.2023

- Как крупнейший банк страны, мы внимательно следим за всеми тенденциями современного банковского сектора, стремимся быть среди первых в применении решений, соответствующих нашим потребностям и бизнес-стратегии. Мы оцениваем инициативы открытого банкинга (open banking) в контексте новых возможностей, поддерживаемые новым законом о платежных услугах и платежных системах и другими новыми нормами в нашей стране. Эти инициативы запустят новый период изменений в секторе, что приведет к созданию новых ценностей для наших клиентов. Представьте, что после внедрения подхода открытого банкинга отдельные банки с согласия клиента будут открывать его данные конкурирующим банкам, а также новым инновационным игрокам в финансовой экосистеме - финтехам и стартапам. Это создаст более динамичную и конкурентную среду для клиентов. В результате клиент сможет выбрать финансового поставщика, который предлагает наиболее подходящие ему продукты и услуги наилучшего качества. Опыт показывает, что современные банки и инновационные финтехи, готовые к этим процессам, будут победителями. Мы в ABB уже некоторое время работаем над технологической и цифровой инфраструктурой, подготавливаем API - набор протоколов и инструментов для взаимодействия между различными информационными системами, которые являются основой для перехода к открытому банкингу. Наша технологическая инфраструктура полностью готова для взаимодействия с информационными системами внешних организаций или компаний. Мы уже применили некоторые из этих интеграций. В прошлом периоде, будучи одним из двух операторских банков услуги «Возврат НДС», мы обеспечили доступность этой услуги для клиентов нескольких других коммерческих банков. Как я уже упоминал, в начале года мы завершили интеграцию в реальном времени с брокерской компанией в США для предоставления клиентам ABB mobile прямого и моментального доступа к американским биржам, именно опираясь на наше технологическое преимущество. Недавно благодаря взаимной интеграции с системами страховой компаний мы предоставили клиентам полный цифровой процесс покупки страховых продуктов . Клиенты также могут отслеживать все свои активные продукты в данной страховой компании через ABB mobile. В настоящее время мы также обсуждаем процессы интеграции с несколькими финтех-игроками.
```

### `527c38891d-000` — section, az, press_releases, 449 tokens

<https://abb-bank.az/press-relizler/abb-asc-nin-sehmdarlarinin-umumi-yigincaginda-onlayn-qaydada-istirak-edin>

```text
"ABB" ASC-nin Səhmdarlarının Ümumi Yığıncağında onlayn qaydada iştirak edin
Tarix: 19.03.2026

19 Mart, 2026
Hörmətli səhmdar!
“Banklar haqqında” Azərbaycan Respublikası Qanununun 24.5-ci maddəsini rəhbər tutaraq, “Azərbaycan Beynəlxalq Bankı” Açıq Səhmdar Cəmiyyətinin (bundan sonra - “ABB” ASC) İdarə Heyəti Sizin nəzərinizə çatdırır ki, 07.05.2026-cı il tarixində Bankın səhmdarlarının növbəti ümumi yığıncağı (bundan sonra – Ümumi Yığıncaq) keçiriləcəkdir.
Bununla yanaşı bildiririk ki, “ABB” ASC-nin Nizamnaməsinin 8.10-cu maddəsinə əsasən səsvermənin qiyabi şəkildə, Azərbaycan Respublikasının Milli Depozit Mərkəzi tərəfindən İnvestor Portalında (invp.e-mdm.gov.az) yaradılmış şəxsi kabinet vasitəsilə həyata keçirilməsi nəzərdə tutulmuşdur. Ümumi yığıncağın gündəliyinə aşağıdakı məsələlər daxil edilir:
1. “ABB” ASC-nin kənar auditor tərəfindən yoxlanılmış 2025-ci ilin maliyyə hesabatları və idarəetmə hesabatının təsdiq edilməsi; 2. 2025-ci ilin maliyyə nəticələrinə əsasən “ABB” ASC-nin səhmdarlarına dividendin ödənilməsi; 3. “ABB” ASC-nin aktivlərin idarə edilməsi üzrə törəmə şirkətinin yaradılması; 4. Xarici bankda iştirak payının (nəzarət səhm paketinin) alınması; 5. “ABB” ASC-nin Müşahidə Şurasının tərkibinə dəyişiklik edilməsi
Ümumi yığıncağın gündəliyinə çıxarılan məsələlər üzrə müvafiq materiallar və səsvermə bülleteni 15.04.2026-cı il tarixindən hər bir səhmdar üçün Azərbaycan Respublikasının Milli Depozit Mərkəzi tərəfindən İnvestor Portalında yaradılmış şəxsi kabinetində yerləşdiriləcəkdir (invp.e-mdm.gov.az).
Gündəlikdə olan məsələlərə dair münasibətinizi şəxsi kabinet vasitəsilə 15.04.2026-cı il tarixindən 06.05.2026-cı il tarixinədək elektron qaydada bildirməklə səsvermədə qiyabi iştirak edə bilərsiniz.
Yuxarıda qeyd olunan şəkildə elektron qaydada verilmiş səslərin sayılması ümumi yığıncağın keçirildiyi gün həyata keçiriləcəkdir.
“Azərbaycan Beynəlxalq Bankı” ASC-nin İdarə Heyəti
```

### `722eae8e42-000` — section, az, procurement, 354 tokens

<https://abb-bank.az/haqqimizda/satinalmalar/musabiqelerin-elani/pesekar-yukdasima-xidmetlerinin-satin-alinmasi-12>

```text
Peşəkar yükdaşıma xidmətlərinin satın alınması
Tarix: 22.12.2022

22 Dekabr, 2022
Tenderin adı: “ABB” ASC tərəfindən peşəkar yükdaşıma xidmətlərinin satın alınması
Tenderin elan tarixi: 22.12.2022
İştirak haqqı:
BANKIN ADI: ABB
VÖEN : 9900001881
KOD: 805250
SWIFT: IBAZAZ2X
M/h: AZ03NABZ01350100000000002944
H/h: AZ12IBAZ34501019440000100100 AZN
H/h: AZ33IBAZ34511018400000100100 USD
- tender təklifi (tender zərflərinin açıldığı tarixdən (17 yanvar 2023-cü il) sonra azı 30 (otuz) bank günü (yəni ən azı 01 mart 2023-cü il tarixinədək) qüvvədə olmalıdır;
- 900.00 (doqquz yüz) manat dəyərində bank təminatı (tender təklifinin qüvvədə olma müddətinin sonuncu günündən azı 30 bank günü çox olmalıdır (yəni ən azı 19 aprel 2023-cü il tarixinədək qüvvədə olmalıdır);
İddiaçılar tenderdə iştirak etmək üçün yuxarıda göstərilən sənədləri (tender təklifi və bank təminatı istisna olmaqla) 10 yanvar 2023-cü il saat 17:00-a qədər, tender təklifi və bank təminatını isə möhürlənmiş ikiqat zərflərdə 16 yanvar 2023-cü il saat 17:00-a qədər Bakı şəhəri, Nəsimi rayonu, Nizami küçəsi, 67 nömrəli ünvana təqdim etməlidirlər.
İddiaçıların təklifləri 17 yanvar 2023-cü il saat 16:45-də Bakı şəhəri, Nəsimi rayonu, Nizami küçəsi, 67 nömrəli ünvanda açılacaqdır.
Tender Komissiyası
```

### `1bbb47e073-000` — section, az, service_network, 497 tokens

<https://abb-bank.az/atm#agdas>

```text
ABB bankomatları (ATM) — Ağdaş

Ağdaş üzrə 9 nöqtə; onlardan 2-i nağd pul mədaxili (cash-in) qəbul edir.
Agdash rayonu, Leki qesebesi, Sabir k. 1 (Nur market) — xəritə: https://www.google.com/maps?q=40.5593118849288,47.428207445752946
Ağdaş r., Məşəd kəndi (1inci market) — xəritə: https://www.google.com/maps?q=40.63019365175335,47.46457721515742
Ağdaş rayon,Yuxarı Ləki kəndi (Halal Super market) — xəritə: https://www.google.com/maps?q=40.548661,47.42294
Ağdaş rayonu, Ağdaş-Qəbələ yolunun üzərində (Ağdaş ticarət mərkəzi) — 24/7 — xəritə: https://www.google.com/maps?q=40.648466045400845,47.497024988075616
Ağdaş rayonu, Xosrov kəndi (Store market) — xəritə: https://www.google.com/maps?q=40.63277,47.572907
Ağdaş ş., M.İsayev küç. "Ağdaş" market (Beş mərtəbəli binanın birinci mərtəbəsi) — xəritə: https://www.google.com/maps?q=40.648036,47.471287
Ağdaş, H.Əliyev prospekti, 96 (ABB-nin Ağdaş filialı 24/7 sahə) — nağd pul mədaxili (cash-in), həftə sonu işləyir — xəritə: https://www.google.com/maps?q=40.64464509611075,47.47541481995137
Ağdaş, H.Əliyev prospekti, 96 (ABB-nin Ağdaş filialı 24/7 sahə) — nağd pul mədaxili (cash-in), həftə sonu işləyir — xəritə: https://www.google.com/maps?q=40.64464509611075,47.47541481995137
H.Əliyev pr., 73A — xəritə: https://www.google.com/maps?q=40.640642,47.470164
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

### `a7025f445b-000` — section, en, about, 26 tokens

<https://abb-bank.az/en/haqqimizda/siyasetlerimiz>

```text
Our policies

Key principles and governance rules applied in Bank ABB’s operations - Last updated: 13.10.2026
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


# ABB — Kaynaklı 100 Soruluk Değerlendirme Seti

Hazırlanma tarihi: **15 Ekim 2026** (Europe/Istanbul).

Bu set, ABB web scraping çıktısından hazırlanmıştır. Her soru için beklenen cevap, resmî sayfanın bağlantısı ve yerel veriden alınan destekleyici alıntı verilmiştir. Cevaplar 14 Ekim 2026 tarihinde toplanmış içerikleri esas alır.

| Soru tipi | Sayı | Amaç |
| --- | ---: | --- |
| Basit, doğrudan bilgi | 25 | Tek kaynak bölümü veya FAQ kaydından cevap bulma |
| Anlamsal/parafraz soru | 20 | Bilgiyi farklı ve doğal ifadelerle arama |
| Ürün adı ve teknik terim | 15 | Ürün adlarını, kısaltmaları ve teknik kavramları eşleştirme |
| Sayısal bilgiler | 15 | Faiz, ücret, vade ve limitleri koşullarıyla bulma |
| Çoklu chunk gerektiren | 15 | En az iki ayrı belgedeki bilgiyi birleştirme |
| Çok dilli sorular | 10 | Azerbaycanca kaynakları Rusça ve İngilizce sorgularla bulma |
| **Toplam** | **100** | |

**Dil dağılımı:** 90 Azerbaycanca, 3 Rusça, 7 İngilizce. Beklenen cevaplar soru ile aynı dildedir; bütün kaynak alıntıları Azerbaycancadır. Her soru tek bir ana kategoriye atanmıştır.

**Kaynak korpus:** `data/abb_pages.jsonl` — 4.420 kayıt. Bu sette 36 farklı kaynak belge kullanılmıştır. Kullanılan belgelerin toplanma tarihleri: 2026-10-14 (UTC).

**Korpus SHA-256:** `042c420d56a8e62278fd280ee9452339a06fd5d67e455474dc8497a71c48a94a`

**Kaynak konumları:** Satır numaraları 1’den, `sections`, `paragraphs` ve `faq` indeksleri 0’dan başlar. Konumlar yukarıdaki korpus sürümüne aittir. Şube belgelerindeki URL parçaları (`#filial-...`) yerel çıkarımın belge kimliğidir; resmî kaynak sayfası ilgili şube listesidir.

**Chunk eşleştirmesi:** Korpusta henüz hazırlanmış chunk kimlikleri bulunmadığı için bölüm/FAQ konumları kullanılmıştır. İlk kategorideki 25 sorunun her biri tek bölüm veya tek FAQ kaydından cevaplanabilir. Çoklu chunk kategorisindeki 15 soru ise iki ayrı kaynak belgeden bilgi gerektirir. Chunking uygulandığında bu konumlar gerçek chunk kimlikleriyle eşleştirilmelidir.

**Sayısal değerlendirme:** Cevaplarda para birimi, vade, limit ve ödeme seçeneği korunmuştur. Faiz sorularında ilgili para birimine ait tablo satırları esas alınır; nominal faiz ile FİFD ayrı değerlendirilir. Alıntılar kaynak yazımıyla korunmuştur.

**Kullanım:** Arama sistemine yalnızca “Soru” metnini sorgu olarak verin. Beklenen cevapları ve alıntıları değerlendirme referansı olarak tutun; bunları aranan korpusa eklemeyin. Çoklu kaynak sorularında cevabın her iki kaynağı da kapsaması beklenir.

## 1. Basit, doğrudan bilgi — 25 soru

### ABB-Q001

**Soru (az):** Alpha Card sifarişini kim həyata keçirir?

**Beklenen cevap:** Alpha Card sifarişi valideyn tərəfindən həyata keçirilir.

**Kaynak 1:** [Alpha Card](https://abb-bank.az/ferdi/kartlar/debet-kartlari/alpha-card)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2468**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** Alpha Card

**Kanıt:**

> 7–17 yaşlı uşaqlar üçün – sifariş valideyn tərəfindən həyata keçirilir.

### ABB-Q002

**Soru (az):** Tam DigiCard ilə keşbek qazanmaq üçün hansı paketlərdən yararlanmaq olar?

**Beklenen cevap:** “Faydalı keşbek” paketlərindən və partnyor təkliflərindən yararlanmaq olar.

**Kaynak 1:** [Tam DigiCard Tam Rəqəmsal, Tam Real](https://abb-bank.az/ferdi/kartlar/debet-kartlari/tam-digicard)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2476**; `sections[1].paragraphs[0]`.

**Bölüm / FAQ:** Tam DigiCard Tam Rəqəmsal, Tam Real > Hər cəhətdən sərfəli > 10%-dək keşbek!

**Kanıt:**

> "Faydalı keşbek" paketləri və partnyorlarla daha yüksək keşbekdən yararlanın.

### ABB-Q003

**Soru (az):** TamGənc Debet kartının yeni sifarişi qəbul olunurmu?

**Beklenen cevap:** Mənbədə kartın sifarişinin hazırda dayandırıldığı göstərilir.

**Kaynak 1:** [TamGənc Debet](https://abb-bank.az/ferdi/kartlar/debet-kartlari/tamgenc-debet)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2478**; `sections[5].paragraphs[0]; sections[5].paragraphs[1]`.

**Bölüm / FAQ:** TamGənc Debet

**Kanıt:**

> TamGənc - gənclər üçün debet kartıdır.
> *Qeyd edək ki, kartın sifarişi hazırda dayandırılıb.

### ABB-Q004

**Soru (az):** Travel Card bonus balansını ABB mobile-da haradan yoxlamaq olar?

**Beklenen cevap:** Bonus kabinetindən mövcud bonus sayını, aktiv bonusları və bonusların tarixçəsini yoxlamaq olar.

**Kaynak 1:** [Travel Card Visa Signature](https://abb-bank.az/ferdi/kartlar/debet-kartlari/travel-card-visa-signature)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2481**; `faq[12]`.

**Bölüm / FAQ:** Bonus balansımı necə yoxlaya bilərəm?

**Kanıt:**

> Bonus balansınızı ABB mobile tətbiqindəki Bonus kabinetinə daxil olaraq yoxlaya bilərsiniz. Burada mövcud bonus sayı, istifadə üçün aktiv bonuslar və bonusların tarixçəsi də əks edilir.

### ABB-Q005

**Soru (az):** TamKart Max borcunu başqa bankın kartı ilə ödəmək mümkündürmü?

**Beklenen cevap:** Bəli, borcu digər banklara məxsus ödəniş kartları ilə də ödəmək mümkündür.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `faq[5]`.

**Bölüm / FAQ:** Borcu başqa bankın kartı ilə ödəyə bilərəm?

**Kanıt:**

> Bəli, borcunuzu digər banklara məxsus ödəniş kartları vasitəsilə də ödəyə bilərsiniz.

### ABB-Q006

**Soru (az):** DigiHesab hansı valyutalarda açıla bilər?

**Beklenen cevap:** DigiHesab AZN, USD və EUR valyutalarında açıla bilər.

**Kaynak 1:** [DigiHesab - Etibarlı və rəqəmsal](https://abb-bank.az/ferdi/butun-hesablar/digihesab)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1528**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** DigiHesab - Etibarlı və rəqəmsal

**Kanıt:**

> ABB mobile tətbiqi vasitəsilə tam onlayn şəkildə AZN, USD və EUR hesabları aça bilərsiniz.

### ABB-Q007

**Soru (az):** DigiHesabdakı vəsaiti nağd şəkildə haradan götürə bilərəm?

**Beklenen cevap:** Vəsaiti istənilən ABB filialından məxaric etmək olar.

**Kaynak 1:** [DigiHesab - Etibarlı və rəqəmsal](https://abb-bank.az/ferdi/butun-hesablar/digihesab)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1528**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** DigiHesab - Etibarlı və rəqəmsal > 3 valyutada hesab > İstənilən ABB filialından nağd vəsaitin əldə edilməsi

**Kanıt:**

> Hesabınızda olan nağd pul vəsaitinizi istənilən filialımızdan məxaric edə bilərsiniz.

### ABB-Q008

**Soru (az):** ABB mobile-da Dama-dama yığım hesabı açmaq üçün hansı addımları atmalıyam?

**Beklenen cevap:** ABB mobile-a daxil olun, “+” ikonuna toxunaraq “Dama-dama yığım hesabı”nı seçin və açılan pəncərədə hədəfinizi yaradın.

**Kaynak 1:** [Dama-dama hədəflərinizə çatın!](https://abb-bank.az/ferdi/butun-hesablar/dama-dama)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1527**; `sections[4].paragraphs[0]; sections[4].paragraphs[1]; sections[4].paragraphs[2]`.

**Bölüm / FAQ:** Dama-dama hədəflərinizə çatın! > 3 addıma Dama-Dama yığım hesabı açın!

**Kanıt:**

> ABB mobile-a daxil olun
> “+” ikonuna toxunub “Dama-dama yığım hesabı”nı seçin
> Açılan pəncərədə hədəfinizi yaradın

### ABB-Q009

**Soru (az):** DigiHesab Max hesabından filialda pul çıxaranda həmin günə qədər qazandığım faiz itirilirmi?

**Beklenen cevap:** Xeyr. İstənilən ABB filialından komissiyasız məxaric etmək və həmin günə qədər qazanılmış faizləri saxlamaq olar.

**Kaynak 1:** [DigiHesab Max - hesab qalığından qazanın](https://abb-bank.az/ferdi/butun-hesablar/digihesab-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1529**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** DigiHesab Max - hesab qalığından qazanın > Yığın, idarə edin, qazanın! > İstənilən ABB filialından nağd vəsaitin əldə edilməsi

**Kanıt:**

> Hesabınızda olan nağd pul vəsaitini istənilən filialımızdan komissiyasız məxaric edə bilərsiniz. Üstəlik, həmin günə qədər qazandığınız faizləri itirmirsiniz.

### ABB-Q010

**Soru (az):** ABB-də əmanət seyfi icarəyə götürmək üçün nə təqdim etməliyəm?

**Beklenen cevap:** İcarə müqaviləsi üçün ərizə doldurmaq və şəxsiyyət vəsiqəsini təqdim etmək kifayətdir.

**Kaynak 1:** [Depozit və əmanət seyfləri](https://abb-bank.az/ferdi/emanetler/depozit-seyfi)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1530**; `sections[2].paragraphs[1]`.

**Bölüm / FAQ:** Depozit və əmanət seyfləri > Əmanət qutusunu necə sifariş etmək olar? > Depozit və əmanət seyfləri

**Kanıt:**

> Əmanət seyfi üçün müraciət edin: İcarə müqaviləsini bağlamaq üçün ərizə doldurmaq və şəxsiyyət vəsiqəsini təqdim etmək kifayətdir.

### ABB-Q011

**Soru (az):** ABB filialında cari hesab açmaq üçün hansı sənəd tələb olunur?

**Beklenen cevap:** Ərizə doldurmaq və şəxsiyyəti təsdiq edən sənədi təqdim etmək lazımdır.

**Kaynak 1:** [Bir neçə valyutada cari hesab](https://abb-bank.az/ferdi/butun-hesablar/cari-hesab)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1526**; `sections[6].paragraphs[1]`.

**Bölüm / FAQ:** Bir neçə valyutada cari hesab > Cari hesab necə açılır?

**Kanıt:**

> Hesab üçün müraciət və sənədlərin imzalanması: Müqavilə bağlamaq üçün ərizə doldurmaq və şəxsiyyəti təsdiq edən sənədi təqdim etmək kifayətdir.

### ABB-Q012

**Soru (az):** ABB mobile-da onlayn kredit müraciəti imkanını necə söndürmək olar?

**Beklenen cevap:** “Təhlükəsizlik” bölməsində onlayn kredit icazəsini deaktiv etmək lazımdır.

**Kaynak 1:** [Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit](https://abb-bank.az/ferdi/kreditler/nagd-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1547**; `faq[7]`.

**Bölüm / FAQ:** Onlayn kredit müraciətimi necə məhdudlaşdıra bilərəm?

**Kanıt:**

> ABB mobile tətbiqindəki "Təhlükəsizlik" bölməsinə daxil olaraq onlayn kredit icazəsini deaktiv etməklə müraciət seçimini məhdudlaşdıra bilərsiniz.

### ABB-Q013

**Soru (az):** Nağd kredit müraciətinin nəticəsi müştəriyə necə bildirilir?

**Beklenen cevap:** Nəticə barədə təsdiq SMS-i göndərilir; əlavə sual olduqda bank əməkdaşları müştəri ilə əlaqə saxlayır.

**Kaynak 1:** [Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit](https://abb-bank.az/ferdi/kreditler/nagd-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1547**; `faq[9]`.

**Bölüm / FAQ:** Kredit müraciətimlə bağlı qərar hansı müddətə veriləcək?

**Kanıt:**

> Kredit müraciətinizlə bağlı qərar bir neçə dəqiqə ərzində veriləcək və Sizə müraciətin nəticəsi barədə təsdiq SMS-i göndəriləcək. Əlavə sual olduğu halda isə əməkdaşlarımız Sizinlə əlaqə saxlayacaq.

### ABB-Q014

**Soru (az):** Avans kreditinin avtomatik ödənişi nə zaman həyata keçirilir?

**Beklenen cevap:** Avtomatik ödəniş əməkhaqqı köçürülən tarixdə həyata keçirilir.

**Kaynak 1:** [1000 AZN-dək Avans Krediti](https://abb-bank.az/ferdi/kreditler/avans-kredit-xetti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1541**; `sections[8].paragraphs[2]`.

**Bölüm / FAQ:** 1000 AZN-dək Avans Krediti > Avans krediti haqqında > Ödəniş

**Kanıt:**

> Avtomatik ödəniş: Kredit ödənişi əməkhaqqı köçürülən tarixdə avtomatik ödənilir.

### ABB-Q015

**Soru (az):** “İndi al, sonra ödə” xidmətinin partnyor mağazalarının siyahısını haradan görə bilərəm?

**Beklenen cevap:** Siyahı ABB mobile tətbiqində “İndi al, sonra ödə” kabinetində göstərilir.

**Kaynak 1:** [İndi al, sonra ödə](https://abb-bank.az/ferdi/kreditler/indi-al-sonra-ode)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1545**; `faq[3]`.

**Bölüm / FAQ:** Partnyor siyahısını necə əldə etmək olar?

**Kanıt:**

> Partnyor siyahısı ilə ABB mobile tətbiqində "İndi al, sonra ödə" kabinetində tanış ola bilərsiniz.

### ABB-Q016

**Soru (az):** “İndi al, sonra ödə” borcunu vaxtından əvvəl ödəsəm, məbləğ necə nəzərə alınır?

**Beklenen cevap:** Vaxtından əvvəl edilən ödəniş növbəti dövrün borc məbləğindən çıxılır.

**Kaynak 1:** [İndi al, sonra ödə](https://abb-bank.az/ferdi/kreditler/indi-al-sonra-ode)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1545**; `faq[6]`.

**Bölüm / FAQ:** “İndi al, sonra ödə” vaxtından öncə ödəniş etsəm, nə baş verəcək?

**Kanıt:**

> "İndi al, sonra ödə" xidməti üzrə vaxtından öncə edilən ödənişlər növbəti dövr üçün olan borc məbləğindən çıxılır.

### ABB-Q017

**Soru (az):** Faydalı Klub keşbeklərini harada görə bilərəm?

**Beklenen cevap:** Tətbiqin “Faydalı keşbek” bölməsində; bu bölmə kart balansından ayrıdır.

**Kaynak 1:** [Faydalı Klub - 20%-dək keşbek](https://abb-bank.az/ferdi/kesbek/faydali-klub)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1540**; `faq[3]`.

**Bölüm / FAQ:** Faydali klub keşbeklərimi harada görə bilərəm?

**Kanıt:**

> Faydalı klub keşbeklərinizi tətbiqdəki Faydalı keşbek bölməsində görə bilərsiniz, bu bölmə kart balansınızdan ayrıdır.

### ABB-Q018

**Soru (az):** ABB-nin ePOS xidmətində veb-sayt kart ödənişləri hansı təhlükəsizlik protokolu ilə qorunur?

**Beklenen cevap:** 3D Secure protokolundan istifadə olunur.

**Kaynak 1:** [Elektron ticarət (ePOS)](https://abb-bank.az/biznes/korporativ/online-xidmetler-korporativ/elektron-ticaret)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2399**; `sections[3].paragraphs[2]`.

**Bölüm / FAQ:** Elektron ticarət (ePOS) > Qəbul edilə bilən kart növləri:

**Kanıt:**

> * Veb-saytınızda kart ödənişlərinin təhlükəsizliyini təmin etmək üçün 3D Secure protokolundan istifadə olunur.

### ABB-Q019

**Soru (az):** Mobil POS üçün yaradılmış müqaviləni imzalamaq üçün filiala getməliyəmmi?

**Beklenen cevap:** Xeyr. Müqaviləni filiala getmədən rəqəmsal şəkildə imzalamaq olar.

**Kaynak 1:** [Mobil POS](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/mobil-pos)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2407**; `sections[7].paragraphs[0]`.

**Bölüm / FAQ:** Mobil POS > Necə MPOS sifariş etmək olar? > Yaradılmış müqaviləni imzalayın

**Kanıt:**

> Müraciətə əsasən yaradılan müqaviləni filiala getmədən rəqəmsal olaraq imzalayın.

### ABB-Q020

**Soru (az):** QR kodla qəbul edilmiş ödənişi ABB Biz-də geri qaytarmaq olar?

**Beklenen cevap:** Bəli, əməliyyat məlumatlarını yoxlayaraq ABB Biz üzərindən geri qaytarmaq mümkündür.

**Kaynak 1:** [QR kod](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/qr-kod)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2408**; `faq[2]`.

**Bölüm / FAQ:** QR kodla qəbul edilmiş ödənişi geri qaytarmaq mümkündürmü?

**Kanıt:**

> Bəli, zərurət yarandıqda QR kodla qəbul edilmiş ödənişi ABB Biz üzərindən geri qaytarmaq mümkündür. Sahibkar əməliyyat məlumatlarını yoxlayaraq müvafiq geri qaytarma prosesini həyata keçirə bilər.

### ABB-Q021

**Soru (az):** ABB-nin inkasso xidmətindən istifadə etməyə başlamaq üçün nə lazımdır?

**Beklenen cevap:** ABB-də hesabın olması və inkasso üçün sənədlərin qəbuluna dair banka tapşırıq verilməsi kifayətdir.

**Kaynak 1:** [İnkasso xidmətləri ilə təhlükəsiz ticarət!](https://abb-bank.az/biznes/kicik-ve-orta-biznes/senedli-emeliyyatlar/inkasso)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2386**; `sections[4].paragraphs[1]`.

**Bölüm / FAQ:** İnkasso xidmətləri ilə təhlükəsiz ticarət! > İnkasso haqqında daha ətraflı > Detallar

**Kanıt:**

> - İnkasso xidmətindən faydalanmaq üçün ABB-də hesaba malik olmaq və inkasso üçün sənədlərin qəbuluna dair banka tapşırıq vermək kifayətdir.

### ABB-Q022

**Soru (az):** Ani kreditin geri ödəniş forması necədir?

**Beklenen cevap:** Annuitet qaydasında, hər ay bərabər hissələrlə ödənilir.

**Kaynak 1:** [Ani kredit](https://abb-bank.az/biznes/kicik-ve-orta-biznes/biznes-kreditleri/ani-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2365**; `sections[10].paragraphs[10]`.

**Bölüm / FAQ:** Ani kredit > Kredit haqqında detallar > Details

**Kanıt:**

> Geri ödəniş: Annunitet (hər ay bərabər hissələr ilə)

### ABB-Q023

**Soru (az):** DigiTransfer ilə xaricə pul göndərmək üçün mütləq filiala getmək lazımdırmı?

**Beklenen cevap:** Xeyr. Əməliyyatları mobil tətbiqdən onlayn həyata keçirmək olar.

**Kaynak 1:** [DigiTransfer/IBAN ilə köçürmə](https://abb-bank.az/ferdi/butun-emeliyyatlar/olkedaxili-ve-olkexarici-kocurmeler/digitransfer-pul-kocurme)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2458**; `faq[4]`.

**Bölüm / FAQ:** Xaricə pul göndərmək üçün banka getmək lazımdır?

**Kanıt:**

> Xeyr. Mobil tətbiq vasitəsilə bütün əməliyyatları onlayn şəkildə həyata keçirmək mümkündür. Filiala getmədən IBAN-la sərfəli köçürmə edə bilərsiniz.

### ABB-Q024

**Soru (az):** ABB-nin Zaqatala filialının ünvanı haradır?

**Beklenen cevap:** Zaqatala, Vidadi küçəsi 28a.

**Kaynak 1:** [Zaqatala filialı](https://abb-bank.az/filiallar#filial-288)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **3998**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** Zaqatala filialı

**Kanıt:**

> Ünvan: Zaqatala, Vidadi küçəsi 28a

### ABB-Q025

**Soru (az):** ABB-nin Qazax filialının iş saatları necədir?

**Beklenen cevap:** Bazar ertəsindən cüməyə qədər 09:00–17:00.

**Kaynak 1:** [Qazax filialı](https://abb-bank.az/filiallar#filial-294)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **3999**; `sections[0].paragraphs[2]`.

**Bölüm / FAQ:** Qazax filialı

**Kanıt:**

> İş saatları: Bazar ertəsi – Cümə: 09:00-17:00

## 2. Anlamsal/parafraz soru — 20 soru

### ABB-Q026

**Soru (az):** Uşağım ev tapşırıqlarını yerinə yetirdikcə ona cib xərcliyi vermək və öz balansını izləməsinə imkan yaratmaq istəyirəm. Alpha Card-da buna uyğun imkan varmı?

**Beklenen cevap:** Bəli. Alpha Card-ın uşaq profilində övladınız balansını izləyə, sizdən cib xərcliyi istəyə və verdiyiniz tapşırıqları yerinə yetirərək mükafat qazana bilər.

**Kaynak 1:** [Alpha Card](https://abb-bank.az/ferdi/kartlar/debet-kartlari/alpha-card)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2468**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** Alpha Card > Hər cəhətdən sərfəli > Uşaq profili

**Kanıt:**

> Övladınızın maliyyə vərdişlərini erkən yaşdan formalaşdırın. Uşaq profilində övladınız balansını izləyə, sizdən cib xərcliyi istəyə və tapşırıqlarınızı yerinə yetirərək mükafat qazana bilər.

### ABB-Q027

**Soru (az):** Tam DigiCard sifariş etsəm, kartı götürmək üçün mütləq banka gəlməliyəm, yoxsa evə gətirirlər?

**Beklenen cevap:** Bakı və Abşeronda pulsuz kuryer çatdırılması var; alternativ olaraq kartı istənilən ABB filialından götürmək olar.

**Kaynak 1:** [Tam DigiCard Tam Rəqəmsal, Tam Real](https://abb-bank.az/ferdi/kartlar/debet-kartlari/tam-digicard)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2476**; `sections[6].paragraphs[0]`.

**Bölüm / FAQ:** Tam DigiCard Tam Rəqəmsal, Tam Real > Kartınızı 3 addımda sifariş edin > Tam sürətlə ünvanınıza çatdıraq

**Kanıt:**

> Bakı və Abşeron ərazisində kuryerlə pulsuz təhvil ala və ya istənilən ABB filialından əldə edə bilərsiniz.

### ABB-Q028

**Soru (az):** Gündəlik xərclərimdən qalan xırda məbləğləri və qazandığım keşbeki öz-özünə yığıma yönəltmək istəyirəm. Dama-dama bunu edə bilir?

**Beklenen cevap:** Bəli. Dama-dama xərcləri yuvarlaqlaşdıraraq köçürməyi, Faydalı keşbek məbləğini yığıma yönəltməyi və “Avto-yığım” funksiyasını təklif edir.

**Kaynak 1:** [Dama-dama hədəflərinizə çatın!](https://abb-bank.az/ferdi/butun-hesablar/dama-dama)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1527**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** Dama-dama hədəflərinizə çatın! > Yaradın, toplayın, qazanın! > Avtomatik köçürmə imkanı

**Kanıt:**

> Xərclərin yuvarlaqlaşaraq köçürülməsi, Faydalı keşbek məbləğinin yığıma yönləndirilməsi və "Avto-yığım" funksiyası

### ABB-Q029

**Soru (az):** Filiala getmədən manat, dollar və avro üçün hesab açmaq istəyirəm. ABB-də bunu telefondan necə edə bilərəm?

**Beklenen cevap:** ABB mobile vasitəsilə tam onlayn DigiHesab açmaq olar; bu məhsul AZN, USD və EUR hesablarını dəstəkləyir.

**Kaynak 1:** [DigiHesab - Etibarlı və rəqəmsal](https://abb-bank.az/ferdi/butun-hesablar/digihesab)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1528**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** DigiHesab - Etibarlı və rəqəmsal

**Kanıt:**

> ABB mobile tətbiqi vasitəsilə tam onlayn şəkildə AZN, USD və EUR hesabları aça bilərsiniz.

### ABB-Q030

**Soru (az):** Pul başqa bankın kartındadır. Onu DigiHesab Max-a tətbiqdən keçirsəm, məndən mədaxil haqqı tutulacaq?

**Beklenen cevap:** Mənbəyə görə ABB mobile vasitəsilə istənilən bank kartından DigiHesab Max-a mədaxil komissiyasızdır.

**Kaynak 1:** [DigiHesab Max - hesab qalığından qazanın](https://abb-bank.az/ferdi/butun-hesablar/digihesab-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1529**; `sections[1].paragraphs[0]`.

**Bölüm / FAQ:** DigiHesab Max - hesab qalığından qazanın > Yığın, idarə edin, qazanın! > İstənilən bank kartından komissiyasız mədaxil

**Kanıt:**

> ABB mobile tətbiqindən istifadə etməklə istənilən bank kartından DigiHesab Max hesabınıza komissiyasız vəsait mədaxil edin.

### ABB-Q031

**Soru (az):** DigiDeposit-in vaxtı bitəndə hər dəfə yenidən müqavilə bağlamaq istəmirəm. Uzadılmanı əvvəlcədən avtomatik seçmək olur?

**Beklenen cevap:** Bəli. Rəsmiləşdirmə zamanı müqavilənin avtomatik uzanması seçimini etmək mümkündür.

**Kaynak 1:** [DigiDeposit - Tamamilə rəqəmsal](https://abb-bank.az/ferdi/emanetler/digideposit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1531**; `sections[1].paragraphs[0]`.

**Bölüm / FAQ:** DigiDeposit - Tamamilə rəqəmsal > DigiDeposit ilə qazanmağa başlayın. > Tamamilə onlayn

**Kanıt:**

> ABB mobile vasitəsilə istənilən vaxt, istənilən yerdə 30-a qədər depozit yaradın. Rəsmiləşmə zamanı müqavilənin avtomatik uzanması seçimi mümkündür.

### ABB-Q032

**Soru (az):** DigiDeposit-dəki pulu razılaşdığımız vaxtdan tez götürsəm, yığılmış faiz də mənə veriləcək?

**Beklenen cevap:** Xeyr. Mənbədə əmanət məbləği vaxtından əvvəl çıxarıldıqda heç bir faiz ödənilmədiyi göstərilir.

**Kaynak 1:** [DigiDeposit - Tamamilə rəqəmsal](https://abb-bank.az/ferdi/emanetler/digideposit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1531**; `sections[8].paragraphs[6]`.

**Bölüm / FAQ:** DigiDeposit - Tamamilə rəqəmsal > AZN

**Kanıt:**

> - Əmanət məbləği vaxtından əvvəl çıxarıldığı halda heç bir faiz ödənilmir.

### ABB-Q033

**Soru (az):** Bir nağd kreditim hələ bağlanmayıb, amma yenidən pula ehtiyacım yaranıb. İkincisi üçün müraciət edə bilərəm?

**Beklenen cevap:** Bəli, mövcud krediti bağlamadan paralel ikinci kredit üçün müraciət etmək olar.

**Kaynak 1:** [Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit](https://abb-bank.az/ferdi/kreditler/nagd-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1547**; `faq[10]`.

**Bölüm / FAQ:** Mövcud kreditimi bağlamadan əlavə kredit əldə edə bilərəm?

**Kanıt:**

> Bəli, əlavə kredit ehtiyacı yaranarsa, paralel şəkildə ikinci kredit üçün müraciət edə bilərsiniz.

### ABB-Q034

**Soru (az):** Əvvəl tətbiqdən kredit götürməyi özüm bağlamışdım. İndi yenə müraciət etmək istəyirəm, nəyi açmalıyam?

**Beklenen cevap:** ABB mobile-da “Təhlükəsizlik” bölməsinə daxil olaraq onlayn kredit icazəsini aktivləşdirmək lazımdır.

**Kaynak 1:** [Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit](https://abb-bank.az/ferdi/kreditler/nagd-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1547**; `faq[8]`.

**Bölüm / FAQ:** Onlayn kredit müraciətim ilə bağlı məhdudiyyəti necə aradan qaldıra bilərəm?

**Kanıt:**

> ABB mobile tətbiqindəki "Təhlükəsizlik" bölməsinə daxil olaraq onlayn kredit icazəsini aktivləşdirməklə müraciətlə bağlı məhdudiyyəti aradan qaldıra bilərsiniz.

### ABB-Q035

**Soru (az):** Rəsmi maaşım görünmür. Nağd kredit təklifi verəndə bank mənim hansı maliyyə məlumatlarıma baxa bilər?

**Beklenen cevap:** Kredit tarixçəsi, debet kart dövriyyəsi, cari hesab, depozit və digər hesablardakı əməliyyatlar nəzərə alınır.

**Kaynak 1:** [Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit](https://abb-bank.az/ferdi/kreditler/nagd-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1547**; `faq[4]`.

**Bölüm / FAQ:** Rəsmi gəlir tələbi olmadan kredit təklifi necə təyin olunur?

**Kanıt:**

> Rəsmi gəliri olmayan müştərilərin kredit tarixçəsi, debet kart dövriyyəsi, cari hesabı, depoziti və digər hesabları üzrə həyata keçirilən əməliyyatlar əsasında kredit təklifi təyin edilir.

### ABB-Q036

**Soru (az):** Maaş arayışım yoxdur, amma mağazadan aldığım əşyanın pulunu sonra hissə-hissə ödəmək istəyirəm. “İndi al, sonra ödə” üçün müraciət edə bilərəm?

**Beklenen cevap:** Mənbəyə görə rəsmi gəlir tələb olunmur; 20 yaşdan yuxarı Azərbaycan Respublikası vətəndaşları müraciət edə bilərlər.

**Kaynak 1:** [İndi al, sonra ödə](https://abb-bank.az/ferdi/kreditler/indi-al-sonra-ode)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1545**; `faq[1]`.

**Bölüm / FAQ:** "İndi al, sonra ödə" xidmətindən kimlər yararlana bilər?

**Kanıt:**

> 20 yaşdan yuxarı Azərbaycan Respublikasının vətəndaşları "İndi al, sonra ödə" xidməti üçün müraciət edə bilər. Müraciət üçün rəsmi gəlir tələb olunmur.

### ABB-Q037

**Soru (az):** Travel Card-da topladığım bonusları dostuma hədiyyə edib onun kartına göndərə bilərəm?

**Beklenen cevap:** Xeyr. Bonuslar fərdidir; başqa şəxsə ötürülməsi, hədiyyə edilməsi və ya başqa kart hesabına köçürülməsi mümkün deyil.

**Kaynak 1:** [Travel Card Visa Signature](https://abb-bank.az/ferdi/kartlar/debet-kartlari/travel-card-visa-signature)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2481**; `faq[13]`.

**Bölüm / FAQ:** Bonusları başqa şəxsə ötürmək mümkündür?

**Kanıt:**

> Xeyr, bonuslar fərdidir və yalnız kart sahibinə məxsus olur. Onların başqa şəxsə ötürülməsi, hədiyyə edilməsi və ya başqa kart hesabına köçürülməsi mümkün deyil.

### ABB-Q038

**Soru (az):** Travel Card-la aldığım məhsulu geri qaytardım. Həmin alışdan qazandığım bonuslar hesabımda qalacaq?

**Beklenen cevap:** Xeyr. Ləğv edilən və ya qaytarılan əməliyyata görə hesablanmış bonuslar silinir; bonuslar artıq istifadə edilibsə, bonus balansında mənfi fərq yarana bilər.

**Kaynak 1:** [Travel Card Visa Signature](https://abb-bank.az/ferdi/kartlar/debet-kartlari/travel-card-visa-signature)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2481**; `faq[11]`.

**Bölüm / FAQ:** Əməliyyat ləğv olunarsa, bonuslar qorunurmu?

**Kanıt:**

> Əgər bonus qazandıran əməliyyat sonradan ləğv olunarsa və ya qaytarılarsa, həmin əməliyyata görə hesablanmış bonuslar balansdan silinir. Əgər istifadəçi həmin bonusları artıq istifadə edibsə, bonus balansında mənfi fərq yarana bilər.

### ABB-Q039

**Soru (az):** Travel Card-dan nağd pul çıxarmışam və başqa karta pul yollamışam, amma bonus gəlməyib. Bunun səbəbi nədir?

**Beklenen cevap:** Nağdlaşdırma və kartdan-karta köçürmələr bonus hesablanmayan əməliyyatlardır.

**Kaynak 1:** [Travel Card Visa Signature](https://abb-bank.az/ferdi/kartlar/debet-kartlari/travel-card-visa-signature)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2481**; `faq[3]`.

**Bölüm / FAQ:** Bonuslar hansı əməliyyatlara görə hesablanmır?

**Kanıt:**

> Nağdlaşdırma əməliyyatları, kartdan-karta köçürmələr, eləcə də bankın bonus proqramı şərtlərinə əsasən istisna edilən bəzi ödəniş növləri üzrə bonus hesablanmır.

### ABB-Q040

**Soru (az):** Ödəniş etdiyim mağaza həm Faydalı Klub-da, həm də aylıq keşbek paketimdə var. İki faizi birləşdirəcəklər?

**Beklenen cevap:** Xeyr. Keşbek ən yüksək faizi olan kateqoriyaya uyğun hesablanır və uyğun kateqoriya başlığı ilə “Faydalı Keşbek” bölməsində görünür.

**Kaynak 1:** [Faydalı Klub - 20%-dək keşbek](https://abb-bank.az/ferdi/kesbek/faydali-klub)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1540**; `faq[2]`.

**Bölüm / FAQ:** Tərəfdaş həm Faydali klub, həm də “Faydalı" keşbek aylıq paketlərində olduğu halda nə baş verir?

**Kanıt:**

> Əgər tərəfdaş həm Faydali Klub, həm də aylıq keşbek paketlərində mövcuddursa, keşbek ən yüksək faiz olan kateqoriyaya uyğun olaraq hesablanacaq. Qazanılan həmin keşbeki uyğun kateqoriya başlığı ilə “Faydalı Keşbek” bölməsində görə bilərsiniz.

### ABB-Q041

**Soru (az):** Mağazada ayrıca POS aparatı almaq istəmirəm. Mobil POS-la təkcə telefon vasitəsilə kart ödənişi götürə bilərəm?

**Beklenen cevap:** Bəli. Mobil POS fiziki POS terminalına ehtiyac olmadan telefonla ödəniş qəbul etməyə imkan verir.

**Kaynak 1:** [Mobil POS](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/mobil-pos)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2407**; `sections[3].paragraphs[0]`.

**Bölüm / FAQ:** Mobil POS > Biznesiniz üçün faydaları > Müştəri rahatlığı

**Kanıt:**

> Fiziki POS terminalına ehtiyac olmadan sadəcə telefonla rahat və sürətli ödəniş qəbul edin.

### ABB-Q042

**Soru (az):** Hər satış üçün yenidən kod yaratmaq istəmirəm; müştəri özü məbləği yazsın. ABB-nin hansı QR növü buna uyğundur?

**Beklenen cevap:** Statik QR kod uyğundur: eyni kod çoxsaylı əməliyyatlarda işlədilir, məbləği isə müştəri özü daxil edir.

**Kaynak 1:** [QR kod](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/qr-kod)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2408**; `sections[7].paragraphs[0]`.

**Bölüm / FAQ:** QR kod > Statik QR kod

**Kanıt:**

> Eyni QR kod istənilən sayda əməliyyat üçün istifadə olunur. Müştərilər kodu oxudaraq məbləği özləri daxil edir və ödənişi həyata keçirirlər.

### ABB-Q043

**Soru (az):** Şirkətimin Ani Ödəniş Sistemi ilə köçürmə etməsi üçün bankın səhər açılmasını gözləməliyəm?

**Beklenen cevap:** Xeyr. Xidmət 24/7 işləyir və əməliyyat üçün iş saatlarını gözləməyə ehtiyac yoxdur.

**Kaynak 1:** [Ani Ödəniş Sistemi](https://abb-bank.az/biznes/korporativ/kocurmeler-1/ani-odenis-sistemi)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2391**; `sections[1].paragraphs[0]`.

**Bölüm / FAQ:** Ani Ödəniş Sistemi > Üstünlüklər > 24/7 xidmətinizdə

**Kanıt:**

> Müştərilər istənilən vaxt ödəniş əməliyyatları həyata keçirə bilərlər, bunun üçün iş saatlarını gözləməyə ehtiyac yoxdur

### ABB-Q044

**Soru (az):** Məhsullarımı internetdə satıram və alıcıların elə saytımda kartla pul ödəməsini istəyirəm. ABB-nin hansı xidməti bu iş üçündür?

**Beklenen cevap:** Virtual POS, yəni ePOS xidməti veb-sayt və elektron ticarət platformalarında kart ödənişlərinin qəbulunu təmin edir.

**Kaynak 1:** [Elektron ticarət (ePOS)](https://abb-bank.az/biznes/korporativ/online-xidmetler-korporativ/elektron-ticaret)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2399**; `sections[1].paragraphs[0]`.

**Bölüm / FAQ:** Elektron ticarət (ePOS)

**Kanıt:**

> Virtual POS (ePOS) – Veb saytlar və e-ticarət platformaları üçün onlayn ödəniş həlləri. Əgər siz e-ticarətlə məşğulsunuzsa, onlayn mağazanızda kartla ödənişlərin qəbulunu təşkil etmək və bununla da müştərilərinizə yüksək səviyyədə xidmət göstərmək üçün bizimlə əlaqə saxlayın.

### ABB-Q045

**Soru (az):** Nağd krediti filialda rəsmiləşdirəndə ödəniş gününü maaşıma uyğun daha gec tarixə salmaq istəsəm, bunu nə vaxt deməliyəm?

**Beklenen cevap:** Ödəniş tarixinin 15 günədək uzadılması üçün yalnız kredit müraciəti zamanı müraciət etmək olar; bu imkan filialda rəsmiləşdirilən nağd kreditlərə aiddir.

**Kaynak 1:** [Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit](https://abb-bank.az/ferdi/kreditler/nagd-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1547**; `faq[12]`.

**Bölüm / FAQ:** Kredit ödənişinin tarixini dəyişdirmək mümkündür?

**Kanıt:**

> Filiallarımızda rəsmiləşdirilən nağd kreditlər üçün kredit ödənişi tarixinin 15 günədək uzadılması üçün müraciət edə bilərsiniz. Tarixin uzadılması yalnız kredit müraciəti zamanı mümkündür.

## 3. Ürün adı ve teknik terim — 15 soru

### ABB-Q046

**Soru (az):** TamKart Max-da “Tam 12” funksiyası hansı əməliyyatlara şamil edilmir?

**Beklenen cevap:** ATM və POS terminallarla nağdlaşdırmaya, köçürmələrə, həmçinin 6012, 6050 və 6051 MCC kodlu əməliyyatlara şamil edilmir.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `faq[7]`.

**Bölüm / FAQ:** Tam 12 (13 ayadək faizsiz ödəniş imkanı) nədir?

**Kanıt:**

> Tam 12 - kredit kartı limitinin müəyyən hissəsindən istifadə etdiyiniz məbləği 13 ayadək faizsiz ödəməyə imkan verən funksionallıqdır. Tam 12 üzrə maksimum istifadə edilə bilən məbləğ kredit kartı limitinin 20%-ni, lakin maksimum 2 000 AZN təşkil edir. Funksionallıq müqavilə imzalandığı tarixdən etibarən ilk 30 gün ərzində edilən uyğun əməliyyatlara tətbiq olunur. Tam 12 üzrə faizsiz ödəniş müddəti əməliyyatın aparıldığı aydan sonrakı ilin həmin ayının sonunadək davam edir. Tam 12 aşağıdakı əməliyyatlara şamil edilmir:
> - ATM və POS terminallar vasitəsilə nağdlaşdırma əməliyyatlarına;
> - köçürmə əməliyyatlarına;
> - 6012, 6050 və 6051 MCC kodları ilə aparılan əməliyyatlara.

### ABB-Q047

**Soru (az):** TamKart Max-ın “Taksitə çevir” funksiyasından hansı əməliyyatlar üçün istifadə etmək olmaz?

**Beklenen cevap:** 13 ayadək faizsiz ödəniş imkanı olan əməliyyatlar, 20 AZN-dən aşağı əməliyyatlar və taksitə çevriləndə aylıq ödənişi 10 AZN-dən aşağı olan əməliyyatlar üçün istifadə etmək olmaz.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `faq[10]`.

**Bölüm / FAQ:** Taksitə çevir funksiyası nədir və hansı əməliyyatlara tətbiq edilmir?

**Kanıt:**

> Taksitə çevir funksiyası taksit şərtləri ilə həyata keçirilməyən əməliyyatları taksitə bölməyə imkan verir. Əməliyyatı ABB mobile tətbiqi vasitəsilə borcun yarandığı ayın sonunadək taksitə çevirə bilərsiniz.
> Taksitə çevir funksiyası aşağıdakı əməliyyatlara tətbiq edilmir:
> - 13 ayadək faizsiz ödəniş imkanı olan əməliyyatlara;
> - 20 AZN-dən aşağı məbləğdə olan əməliyyatlara;
> - taksitə çevrildikdə aylıq ödəniş məbləği 10 AZN-dən aşağı olan əməliyyatlara.

### ABB-Q048

**Soru (az):** TamKart Max ödəniş üsullarında göstərilən C2C nə deməkdir?

**Beklenen cevap:** C2C kartdan-karta köçürmə deməkdir.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `faq[4]`.

**Bölüm / FAQ:** TamKart Max kredit kartının ödənişini necə həyata keçirə bilərəm?

**Kanıt:**

> Ödənişi ABB mobile tətbiqi, ödəniş terminalları və C2C (kartdan-karta köçürmə) vasitəsilə həyata keçirə bilərsiniz.

### ABB-Q049

**Soru (az):** ABB-nin ePOS xidməti hansı beynəlxalq kart sistemlərinin kartlarını qəbul edir?

**Beklenen cevap:** VISA International, MasterCard Worldwide və American Express kartlarını qəbul edir.

**Kaynak 1:** [Elektron ticarət (ePOS)](https://abb-bank.az/biznes/korporativ/online-xidmetler-korporativ/elektron-ticaret)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2399**; `sections[3].paragraphs[0]`.

**Bölüm / FAQ:** Elektron ticarət (ePOS) > Qəbul edilə bilən kart növləri:

**Kanıt:**

> VISA International, MasterCard Worldwide və American Express kartları

### ABB-Q050

**Soru (az):** DigiTransfer ilə Amerikaya pul göndərərkən hesab məlumatlarından əlavə hansı bank kodu daxil edilməlidir?

**Beklenen cevap:** ABA routing code (ACH) daxil edilməlidir; dəqiq kodu vəsaitin göndəriləcəyi Amerika bankından öyrənmək lazımdır.

**Kaynak 1:** [DigiTransfer/IBAN ilə köçürmə](https://abb-bank.az/ferdi/butun-emeliyyatlar/olkedaxili-ve-olkexarici-kocurmeler/digitransfer-pul-kocurme)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2458**; `faq[7]`.

**Bölüm / FAQ:** Amerikaya necə sərfəli pul göndərə bilərəm?

**Kanıt:**

> Amerikaya pul köçürmək üçün hesab məlumatlarını və ABA routing code (ACH) daxil edərək köçürməni tamamlaya bilərsiniz. ABA routing code Amerika banklarına görə dəyişə bilər. Dəqiq məlumat əldə etmək üçün köçürmə edəcəyiniz Amerika bankı ilə əlaqə saxlayın.

### ABB-Q051

**Soru (az):** Ani Ödəniş Sistemində FIN və VÖEN-dən başqa hansı sadələşdirilmiş identifikatorlardan istifadə olunur?

**Beklenen cevap:** Mobil nömrə və e-poçt ünvanından da istifadə olunur.

**Kaynak 1:** [Ani Ödəniş Sistemi](https://abb-bank.az/biznes/korporativ/kocurmeler-1/ani-odenis-sistemi)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2391**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** Ani Ödəniş Sistemi > Üstünlüklər > Sürətli və sadə

**Kanıt:**

> Ödənişlər FIN kod, VÖEN, mobil nömrə və ya e-poçt kimi sadələşdirilmiş identifikatorlar vasitəsilə dərhal həyata keçirilir

### ABB-Q052

**Soru (az):** ABB-nin akkreditiv təsvirində SBLC hansı akkreditiv növünə aiddir və ödəniş nə vaxt yaranır?

**Beklenen cevap:** SBLC rezervli akkreditivə aiddir və mahiyyətcə qarantiyadır. Alıcı öhdəliyini yerinə yetirmədikdə satıcının emitent banka tələbi əsasında ödəniş həyata keçirilir.

**Kaynak 1:** [Akkreditiv](https://abb-bank.az/biznes/kicik-ve-orta-biznes/senedli-emeliyyatlar/akkreditiv)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2385**; `sections[9].paragraphs[2]`.

**Bölüm / FAQ:** Akkreditiv > ABB tərəfindən təklif olunan akkreditivlərin növləri > Örtüklü və bank hesabına qarantiyalar

**Kanıt:**

> Rezervli akkreditiv: Adında «akkreditiv» sözü olmasına baxmayaraq mahiyyətcə qarantiya sayılır. SBLC üzrə ödənişlər qarantiyada olduğu kimi Alıcı öz öhdəliyini yerinə yetirmədiyi təqdirdə Satıcının Emitent Banka tələbin irəli sürülməsi nəticəsində ödənişin həyata keçirilməsi.

### ABB-Q053

**Soru (az):** Geri çağrılmayan akkreditiv satıcının razılığı olmadan dəyişdirilə və ya ləğv edilə bilərmi?

**Beklenen cevap:** Xeyr. Satıcının, yəni benefisiarın razılığı olmadan dəyişdirilə və ya ləğv edilə bilməz; bu, emitent bankın qəti öhdəliyidir.

**Kaynak 1:** [Akkreditiv](https://abb-bank.az/biznes/kicik-ve-orta-biznes/senedli-emeliyyatlar/akkreditiv)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2385**; `sections[9].paragraphs[0]`.

**Bölüm / FAQ:** Akkreditiv > ABB tərəfindən təklif olunan akkreditivlərin növləri > Örtüklü və bank hesabına qarantiyalar

**Kanıt:**

> Geri çağrılmayan akkreditiv: Satıcının (Benefisiarın) razılığı olmadan ləğv edilə və ya dəyişdirilə bilməz. Geri çağrılmayan akkreditiv Emitent bankın qəti öhdəliyidir.

### ABB-Q054

**Soru (az):** Köçürülə bilən akkreditiv benefisiara hansı hüququ verir?

**Beklenen cevap:** Qəbul etdiyi akkreditivin bir və ya bir neçə hissəsini digər satıcılara yönəltmək hüququ verir.

**Kaynak 1:** [Akkreditiv](https://abb-bank.az/biznes/kicik-ve-orta-biznes/senedli-emeliyyatlar/akkreditiv)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2385**; `sections[9].paragraphs[5]`.

**Bölüm / FAQ:** Akkreditiv > ABB tərəfindən təklif olunan akkreditivlərin növləri > Örtüklü və bank hesabına qarantiyalar

**Kanıt:**

> Köçürülə bilən akkreditiv: Satıcıya (Benefisiara) qəbul etdiyi akkreditivin bir və ya bir neçə hissəsini digər Satıcılara yönəltmək hüququ verir.

### ABB-Q055

**Soru (az):** İnkassoda “akseptə qarşı sənədlər” şərti idxalçı üçün nə deməkdir?

**Beklenen cevap:** İdxalçı sənədləri əldə etmək üçün vekseli təsdiqləyir və müqaviləyə uyğun ödəniş etmək barədə qeyd-şərtsiz hüquqi öhdəlik qəbul edir.

**Kaynak 1:** [İnkasso xidmətləri ilə təhlükəsiz ticarət!](https://abb-bank.az/biznes/kicik-ve-orta-biznes/senedli-emeliyyatlar/inkasso)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2386**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** İnkasso xidmətləri ilə təhlükəsiz ticarət! > Mövcud xidmətlərin növləri > Akseptə qarşı sənədlər

**Kanıt:**

> Bu halda İdxalçı sənədləri əldə etmək üçün vekseli təsdiq edərək müqavilənin şərtlərinə uyğun olaraq ödəniş etmək üçün qeyd-şərtsiz hüquqi öhdəliyi qəbul edir

### ABB-Q056

**Soru (az):** ABB-də NFC dəstəkli Android cihazından təmassız ödəniş qəbul etmək üçün nəzərdə tutulan həllin adı nədir?

**Beklenen cevap:** Mobil POS.

**Kaynak 1:** [QR kod](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/qr-kod)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2408**; `sections[13].paragraphs[0]`.

**Bölüm / FAQ:** QR kod > Mobil POS

**Kanıt:**

> NFC dəstəkli Android mobil cihazlarından təmassız ödənişləri qəbul etmək üçün

### ABB-Q057

**Soru (az):** Fayda Max-ı aktivləşdirmək üçün tətbiqdə hansı bölməyə daxil olmaq lazımdır?

**Beklenen cevap:** “Sizin üçün” bölməsinə daxil olub “Fayda Max”ı bir dəfə aktivləşdirmək lazımdır.

**Kaynak 1:** [Fayda Max təkmilləşdirilmiş keşbek](https://abb-bank.az/ferdi/kesbek/fayda-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1538**; `sections[4].paragraphs[0]`.

**Bölüm / FAQ:** Fayda Max təkmilləşdirilmiş keşbek > Fayda Max ilə necə qazanmaq olar? > Fayda Max-ı aktivləşdirin

**Kanıt:**

> Sadəcə olaraq, "Sizin üçün"ə daxil olduqdan sonra "Fayda Max"-ı bir dəfə aktivləşdirmək kifayətdir

### ABB-Q058

**Soru (az):** Fayda Max-da “DigiDeposit gəlirinə keşbek” mükafatı hansı valyutadakı depozitlərə şamil olunur?

**Beklenen cevap:** Yalnız AZN valyutasında açılmış depozitlərə; digər valyutalardakı depozitlərə şamil olunmur.

**Kaynak 1:** [Fayda Max təkmilləşdirilmiş keşbek](https://abb-bank.az/ferdi/kesbek/fayda-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1538**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** Fayda Max təkmilləşdirilmiş keşbek > Fayda Max mükafatları > DigiDeposit gəlirinə keşbek

**Kanıt:**

> Yalnız AZN valyutasında açılmış depozitlər nəzərə alınır. Digər valyutalarda olan depozitlərə şamil olunmur.

### ABB-Q059

**Soru (az):** Avans kredit xətti hansı əməkhaqqı və pensiya kartı sahibləri üçün nəzərdə tutulub?

**Beklenen cevap:** ABB-nin emissiya etdiyi ödəniş kartları ilə əməkhaqqı və ya yaşa görə pensiya alan müştərilər üçün. Minimum yaş 20, müqavilə bitəndə maksimum yaş 70-dir.

**Kaynak 1:** [1000 AZN-dək Avans Krediti](https://abb-bank.az/ferdi/kreditler/avans-kredit-xetti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1541**; `faq[0]`.

**Bölüm / FAQ:** Kimlər avans əldə edə bilər?

**Kanıt:**

> Avans kredit, ABB-nin emissiya etdiyi ödəniş kartları vasitəsilə əməkhaqqı və/və ya yaşa görə pensiya alan müştərilər üçün nəzərdə tutulub.
> Yaş tələbi: Min. 20 yaş - Max. müqavilə müddətinin bitmə tarixinə 70 yaş.

### ABB-Q060

**Soru (az):** Sahibkar məhsulunda kreditin annuitet geri ödənişi ilə kredit xəttinin geri ödənişi necə fərqlənir?

**Beklenen cevap:** Kredit hər ay bərabər hissələrlə annuitet qaydasında, kredit xətti isə azad qaydada geri ödənilir.

**Kaynak 1:** [Sahibkar krediti/kredit xətti](https://abb-bank.az/biznes/kicik-ve-orta-biznes/biznes-kreditleri/sahibkar-krediti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2373**; `sections[10].paragraphs[5]`.

**Bölüm / FAQ:** Sahibkar krediti/kredit xətti > Kredit haqqında detallar > Details

**Kanıt:**

> Geri ödəniş: Kredit üzrə Annunitet (hər ay bərabər hissələr ilə), Kredit xətti üzrə isə azad

## 4. Sayısal bilgiler — 15 soru

### ABB-Q061

**Soru (az):** ABB-nin onlayn nağd krediti üzrə maksimum məbləğ və maksimum müddət nə qədərdir?

**Beklenen cevap:** Maksimum məbləğ 70 000 AZN, maksimum müddət 60 aydır.

**Kaynak 1:** [Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit](https://abb-bank.az/ferdi/kreditler/nagd-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1547**; `sections[0].paragraphs[1]; sections[0].paragraphs[2]; sections[0].paragraphs[3]; sections[0].paragraphs[4]`.

**Bölüm / FAQ:** Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit

**Kanıt:**

> 70 000 AZN-dək
> Məbləğ
> 60 ayadək
> Müddət

### ABB-Q062

**Soru (az):** TamKart Max üçün minimum və maksimum kredit məbləği nə qədərdir?

**Beklenen cevap:** Minimum 300 AZN, maksimum 30 000 AZN.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `sections[10].paragraphs[0]`.

**Bölüm / FAQ:** TamKart Max > Şərtlər və Tariflər > Tariflər

**Kanıt:**

> Kredit məbləği: 300 - 30 000 AZN

### ABB-Q063

**Soru (az):** TamKart Max-ın nominal illik faiz dərəcələri və FİFD aralığı hansılardır?

**Beklenen cevap:** Nominal illik faiz dərəcələri 27%, 28% və 29%; faktiki illik faiz dərəcəsi (FİFD) minimum 18,40%, maksimum 41,60%-dir.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `sections[10].paragraphs[1]; sections[10].paragraphs[2]`.

**Bölüm / FAQ:** TamKart Max > Şərtlər və Tariflər > Tariflər

**Kanıt:**

> İllik faiz dərəcəsi: 27%, 28%, 29%
> Faktiki illik faiz dərəcəsi: Min. 18.40% - maks. 41.60%

### ABB-Q064

**Soru (az):** TamKart Gold Kredit-in tariflərində nominal illik faiz dərəcəsi neçə faiz göstərilir?

**Beklenen cevap:** Nominal illik faiz dərəcəsi 22%-dir.

**Kaynak 1:** [TamKart Gold Kredit](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-visa-gold)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2484**; `sections[6].paragraphs[2]`.

**Bölüm / FAQ:** TamKart Gold Kredit > Tariflər

**Kanıt:**

> İllik faiz dərəcəsi: 22%

### ABB-Q065

**Soru (az):** Alpha Card üçün aylıq komissiyasız köçürmə və nağdlaşdırma limiti nə qədərdir, limit aşılarsa hansı komissiya tətbiq olunur?

**Beklenen cevap:** Aylıq 500 AZN-dək pulsuzdur; limit aşıldıqda 1%, minimum 1 AZN komissiya tətbiq olunur.

**Kaynak 1:** [Alpha Card](https://abb-bank.az/ferdi/kartlar/debet-kartlari/alpha-card)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2468**; `sections[5].paragraphs[1]`.

**Bölüm / FAQ:** Alpha Card > Tariflər

**Kanıt:**

> Köçürmə və nağdlaşdırma: Aylıq 500 AZN-dək pulsuz; Aylıq 500 AZN limit aşıldıqda 1% (min. 1 AZN)

### ABB-Q066

**Soru (az):** Tam DigiCard-a Emanat, MilliÖn və GoldenPay vasitəsilə mədaxilin aylıq pulsuz limiti və limiti aşma komissiyası nə qədərdir?

**Beklenen cevap:** Aylıq 1 000 AZN-dək komissiyasızdır; limit aşıldıqda 0,5% komissiya tətbiq olunur.

**Kaynak 1:** [Tam DigiCard Tam Rəqəmsal, Tam Real](https://abb-bank.az/ferdi/kartlar/debet-kartlari/tam-digicard)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2476**; `sections[9].paragraphs[7]`.

**Bölüm / FAQ:** Tam DigiCard Tam Rəqəmsal, Tam Real > Tariflər

**Kanıt:**

> - Emanat, MilliÖn və GoldenPay terminalları: aylıq 1 000 AZN-dək komissiyasız; limiti aşdıqda – 0.5%

### ABB-Q067

**Soru (az):** Alpha Card-ın plastik və rəqəmsal versiyalarının qiyməti nə qədərdir?

**Beklenen cevap:** Plastik kart 10 AZN, rəqəmsal kart 3 AZN-dir.

**Kaynak 1:** [Alpha Card](https://abb-bank.az/ferdi/kartlar/debet-kartlari/alpha-card)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2468**; `sections[5].paragraphs[9]`.

**Bölüm / FAQ:** Alpha Card > Tariflər

**Kanıt:**

> Kartın qiyməti: Plastik kart üçün 10 AZN, rəqəmsal kart üçün isə 3 AZN ödəniş tələb olunur.

### ABB-Q068

**Soru (az):** Tam DigiCard balansına illik gəlir neçə faizədəkdir və balansın hansı hissəsinə tətbiq olunur?

**Beklenen cevap:** İllik 6%-dəkdir və ayda bir dəfə karta köçürülür. Faiz balansın yalnız 1 000 AZN-dən artıq hissəsinə tətbiq olunur; maksimum limit 100 000 AZN-dir.

**Kaynak 1:** [Tam DigiCard Tam Rəqəmsal, Tam Real](https://abb-bank.az/ferdi/kartlar/debet-kartlari/tam-digicard)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2476**; `sections[3].paragraphs[0]`.

**Bölüm / FAQ:** Tam DigiCard Tam Rəqəmsal, Tam Real > Hər cəhətdən sərfəli > Kart balansına 6%-dək gəlir

**Kanıt:**

> Kart balansındakı vəsaitə illik 6%-dək gəlir hesablanır və ayda bir dəfə karta köçürülür. Faiz yalnız balansın 1 000 AZN-dən artıq olan hissəsinə tətbiq olunur (maksimum limit: 100 000 AZN).

### ABB-Q069

**Soru (az):** DigiHesab Max-da minimum faiz hesablanan məbləğ və hər hesab üzrə maksimum faiz hesablanan məbləğlər nə qədərdir?

**Beklenen cevap:** Minimum məbləğ 200 AZN və ya 200 USD-dir. Hər hesab üzrə maksimum faiz hesablanan məbləğ AZN üçün 3 000 000 AZN, USD üçün 300 000 USD-dir.

**Kaynak 1:** [DigiHesab Max - hesab qalığından qazanın](https://abb-bank.az/ferdi/butun-hesablar/digihesab-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1529**; `sections[0].paragraphs[3]; sections[0].paragraphs[4]; sections[0].paragraphs[5]; sections[0].paragraphs[6]; sections[0].paragraphs[7]; sections[0].paragraphs[8]`.

**Bölüm / FAQ:** DigiHesab Max - hesab qalığından qazanın

**Kanıt:**

> 200 AZN/USD
> Minimum faiz hesablanan məbləğ
> AZN/USD
> Hesab valyutası
> 3 mln. AZN / 300 000 USD
> Valyuta üzrə maksimum faiz hesablanan məbləğ (hər hesab üzrə)

### ABB-Q070

**Soru (az):** DigiDeposit-in AZN cədvəlinə görə 12 aylıq əmanətdə faiz aylıq və müddətin sonunda ödəniləndə illik dərəcələr neçədir?

**Beklenen cevap:** Aylıq ödəniş seçiləndə illik 8%, müddətin sonunda ödəniş seçiləndə illik 9%-dir.

**Kaynak 1:** [DigiDeposit - Tamamilə rəqəmsal](https://abb-bank.az/ferdi/emanetler/digideposit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1531**; `sections[8].paragraphs[0]; sections[8].paragraphs[4]`.

**Bölüm / FAQ:** DigiDeposit - Tamamilə rəqəmsal > AZN

**Kanıt:**

> Müddət | Aylıq | Müddətin sonu
> 12 ay | 8% | 9%

### ABB-Q071

**Soru (az):** DigiDeposit-in USD cədvəlinə görə 6 aylıq əmanətdə aylıq və müddətin sonunda faiz ödənişi üçün illik dərəcələr neçədir?

**Beklenen cevap:** Aylıq ödənişdə illik 2,5%, müddətin sonunda ödənişdə illik 3%-dir.

**Kaynak 1:** [DigiDeposit - Tamamilə rəqəmsal](https://abb-bank.az/ferdi/emanetler/digideposit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1531**; `sections[9].paragraphs[0]; sections[9].paragraphs[3]`.

**Bölüm / FAQ:** DigiDeposit - Tamamilə rəqəmsal > USD

**Kanıt:**

> Müddət | Aylıq | Müddətin sonu
> 6 ay | 2.5% | 3%

### ABB-Q072

**Soru (az):** Klassik əmanətin AZN cədvəlində 36 ay üçün aylıq və müddətin sonunda faiz ödənişi üzrə illik dərəcələr neçədir?

**Beklenen cevap:** Aylıq ödənişdə illik 9,5%, müddətin sonunda ödənişdə illik 10,5%-dir.

**Kaynak 1:** [Yüksək faizli klassik əmanət](https://abb-bank.az/ferdi/emanetler/klassik-emaneti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1534**; `sections[9].paragraphs[0]; sections[9].paragraphs[6]`.

**Bölüm / FAQ:** Yüksək faizli klassik əmanət > AZN

**Kanıt:**

> Əmanət müddəti | Aylıq | Müddətin sonu
> 36 ay | 9.5% | 10.5%

### ABB-Q073

**Soru (az):** Travel Card bonusları hesablandıqdan neçə gün sonra istifadə üçün aktivləşir?

**Beklenen cevap:** 14 günlük gözləmə müddəti tamamlandıqdan sonra aktivləşir.

**Kaynak 1:** [Travel Card Visa Signature](https://abb-bank.az/ferdi/kartlar/debet-kartlari/travel-card-visa-signature)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2481**; `faq[5]`.

**Bölüm / FAQ:** Bonuslardan nə vaxt istifadə edə bilərəm?

**Kanıt:**

> Bonuslar hesablandıqdan sonra 14 gün ərzində gözləmə müddəti tətbiq olunur, qeyd olunan müddət tamamlandıqdan sonra istifadə üçün aktivləşir.

### ABB-Q074

**Soru (az):** Avans kreditinin komissiyası və minimum komissiya məbləği nə qədərdir?

**Beklenen cevap:** Komissiya 5%, minimum komissiya 2 AZN-dir.

**Kaynak 1:** [1000 AZN-dək Avans Krediti](https://abb-bank.az/ferdi/kreditler/avans-kredit-xetti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1541**; `sections[0].paragraphs[5]; sections[0].paragraphs[6]`.

**Bölüm / FAQ:** 1000 AZN-dək Avans Krediti

**Kanıt:**

> 5% (min. 2 ₼)
> Komissiya

### ABB-Q075

**Soru (az):** İnkasso üçün sənədlərin qəbuluna görə komissiya faizi və minimum haqq nə qədərdir?

**Beklenen cevap:** Komissiya 0,1%-dir; minimum haqq müvafiq valyutada 100 AZN/USD/EUR-dur.

**Kaynak 1:** [İnkasso xidmətləri ilə təhlükəsiz ticarət!](https://abb-bank.az/biznes/kicik-ve-orta-biznes/senedli-emeliyyatlar/inkasso)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2386**; `sections[5].paragraphs[0]`.

**Bölüm / FAQ:** İnkasso xidmətləri ilə təhlükəsiz ticarət! > Tariflər > İnkasso əməliyyatları (Tariflər)

**Kanıt:**

> Sənədlərin inkassoya qəbulu: 0.1% (min. 100 AZN/USD/EUR)

## 5. Çoklu chunk gerektiren — 15 soru

### ABB-Q076

**Soru (az):** Tam DigiCard və Alpha Card-ın aylıq komissiyasız köçürmə və nağdlaşdırma limitlərini, həmçinin limitdən sonrakı komissiyalarını müqayisə edin.

**Beklenen cevap:** Tam DigiCard-da aylıq 3 000 AZN-dək, Alpha Card-da 500 AZN-dək pulsuzdur. Hər iki kartda müvafiq aylıq limit aşıldıqda komissiya 1%, minimum 1 AZN-dir.

**Kaynak 1:** [Tam DigiCard Tam Rəqəmsal, Tam Real](https://abb-bank.az/ferdi/kartlar/debet-kartlari/tam-digicard)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2476**; `sections[9].paragraphs[4]`.

**Bölüm / FAQ:** Tam DigiCard Tam Rəqəmsal, Tam Real > Tariflər

**Kanıt:**

> Köçürmə və nağdlaşdırma: Aylıq 3 000 AZN-dək pulsuz; Aylıq 3 000 AZN limit aşıldıqda 1% (min. 1 AZN)

**Kaynak 2:** [Alpha Card](https://abb-bank.az/ferdi/kartlar/debet-kartlari/alpha-card)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2468**; `sections[5].paragraphs[1]`.

**Bölüm / FAQ:** Alpha Card > Tariflər

**Kanıt:**

> Köçürmə və nağdlaşdırma: Aylıq 500 AZN-dək pulsuz; Aylıq 500 AZN limit aşıldıqda 1% (min. 1 AZN)

### ABB-Q077

**Soru (az):** DigiHesab və DigiHesab Max-ın dəstəklədiyi valyutalar necə fərqlənir?

**Beklenen cevap:** DigiHesab AZN, USD və EUR-da; DigiHesab Max isə AZN və USD-də açılır. EUR DigiHesab üçün göstərilir, DigiHesab Max üçün göstərilmir.

**Kaynak 1:** [DigiHesab - Etibarlı və rəqəmsal](https://abb-bank.az/ferdi/butun-hesablar/digihesab)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1528**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** DigiHesab - Etibarlı və rəqəmsal

**Kanıt:**

> ABB mobile tətbiqi vasitəsilə tam onlayn şəkildə AZN, USD və EUR hesabları aça bilərsiniz.

**Kaynak 2:** [DigiHesab Max - hesab qalığından qazanın](https://abb-bank.az/ferdi/butun-hesablar/digihesab-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1529**; `sections[0].paragraphs[5]; sections[0].paragraphs[6]`.

**Bölüm / FAQ:** DigiHesab Max - hesab qalığından qazanın

**Kanıt:**

> AZN/USD
> Hesab valyutası

### ABB-Q078

**Soru (az):** AZN ilə daha uzunmüddətli əmanət istəyirəm. DigiDeposit və Klassik əmanət üçün göstərilən müddət aralıqlarını müqayisə edin.

**Beklenen cevap:** DigiDeposit üçün 1–18 ay, Klassik əmanət üçün 3–36 ay göstərilir. Bu iki məhsul arasında daha uzun maksimum müddət Klassik əmanətdədir: 36 ay.

**Kaynak 1:** [DigiDeposit - Tamamilə rəqəmsal](https://abb-bank.az/ferdi/emanetler/digideposit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1531**; `sections[0].paragraphs[7]; sections[0].paragraphs[8]`.

**Bölüm / FAQ:** DigiDeposit - Tamamilə rəqəmsal

**Kanıt:**

> 1-18 ay
> Əmanət müddəti

**Kaynak 2:** [Yüksək faizli klassik əmanət](https://abb-bank.az/ferdi/emanetler/klassik-emaneti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1534**; `sections[0].paragraphs[7]; sections[0].paragraphs[8]`.

**Bölüm / FAQ:** Yüksək faizli klassik əmanət

**Kanıt:**

> 3-36 ay
> Əmanət müddəti

### ABB-Q079

**Soru (az):** AZN ilə açılmış DigiDeposit və Klassik əmanətdən pulu vaxtından əvvəl çıxarsam, faiz ödənişi baxımından hansı qayda tətbiq olunur?

**Beklenen cevap:** Hər iki məhsulun AZN cədvəlində əmanət məbləği vaxtından əvvəl çıxarıldıqda heç bir faiz ödənilmədiyi göstərilir.

**Kaynak 1:** [DigiDeposit - Tamamilə rəqəmsal](https://abb-bank.az/ferdi/emanetler/digideposit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1531**; `sections[8].paragraphs[6]`.

**Bölüm / FAQ:** DigiDeposit - Tamamilə rəqəmsal > AZN

**Kanıt:**

> - Əmanət məbləği vaxtından əvvəl çıxarıldığı halda heç bir faiz ödənilmir.

**Kaynak 2:** [Yüksək faizli klassik əmanət](https://abb-bank.az/ferdi/emanetler/klassik-emaneti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1534**; `sections[9].paragraphs[8]`.

**Bölüm / FAQ:** Yüksək faizli klassik əmanət > AZN

**Kanıt:**

> - Əmanət məbləği vaxtından əvvəl çıxarıldığı halda heç bir faiz ödənilmir.

### ABB-Q080

**Soru (az):** DigiHesab Max-a başqa bankın kartından pul əlavə etməklə Dama-dama-da avtomatik yığım üsulları arasında nə fərq var?

**Beklenen cevap:** DigiHesab Max-a ABB mobile ilə istənilən bank kartından komissiyasız mədaxil etmək olar. Dama-dama isə xərclərin yuvarlaqlaşdırılmasını, Faydalı keşbekin yığıma yönəldilməsini və “Avto-yığım” funksiyasını təklif edir.

**Kaynak 1:** [DigiHesab Max - hesab qalığından qazanın](https://abb-bank.az/ferdi/butun-hesablar/digihesab-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1529**; `sections[1].paragraphs[0]`.

**Bölüm / FAQ:** DigiHesab Max - hesab qalığından qazanın > Yığın, idarə edin, qazanın! > İstənilən bank kartından komissiyasız mədaxil

**Kanıt:**

> ABB mobile tətbiqindən istifadə etməklə istənilən bank kartından DigiHesab Max hesabınıza komissiyasız vəsait mədaxil edin.

**Kaynak 2:** [Dama-dama hədəflərinizə çatın!](https://abb-bank.az/ferdi/butun-hesablar/dama-dama)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1527**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** Dama-dama hədəflərinizə çatın! > Yaradın, toplayın, qazanın! > Avtomatik köçürmə imkanı

**Kanıt:**

> Xərclərin yuvarlaqlaşaraq köçürülməsi, Faydalı keşbek məbləğinin yığıma yönləndirilməsi və "Avto-yığım" funksiyası

### ABB-Q081

**Soru (az):** Avans krediti ilə onlayn nağd kreditin müraciətçilərə dair əməkhaqqı və ya pensiya şərtləri necə fərqlənir?

**Beklenen cevap:** Avans ABB-nin verdiyi kartlarla əməkhaqqı və ya yaşa görə pensiya alan müştərilər üçündür; yaş minimum 20, müqavilənin sonunda maksimum 70-dir. Onlayn nağd kreditə isə 20 yaşdan yuxarı Azərbaycan Respublikası vətəndaşları rəsmi gəlir tələbi olmadan müraciət edə bilərlər.

**Kaynak 1:** [1000 AZN-dək Avans Krediti](https://abb-bank.az/ferdi/kreditler/avans-kredit-xetti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1541**; `faq[0]`.

**Bölüm / FAQ:** Kimlər avans əldə edə bilər?

**Kanıt:**

> Avans kredit, ABB-nin emissiya etdiyi ödəniş kartları vasitəsilə əməkhaqqı və/və ya yaşa görə pensiya alan müştərilər üçün nəzərdə tutulub.
> Yaş tələbi: Min. 20 yaş - Max. müqavilə müddətinin bitmə tarixinə 70 yaş.

**Kaynak 2:** [Güzəştli Şərtlərlə Tam Onlayn Nağd Kredit](https://abb-bank.az/ferdi/kreditler/nagd-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1547**; `faq[2]`.

**Bölüm / FAQ:** Kimlər nağd kredit əldə edə bilər?

**Kanıt:**

> 20 yaşdan yuxarı Azərbaycan Respublikası vətəndaşları nağd kredit əldə edə bilər. Müraciət üçün rəsmi gəlir tələbi yoxdur. Müraciət zamanı şəxsiyyəti və iş yeri olduğu halda gəliri təsdiq edən sənədlər müştərinin icazəsi ilə elektron qaydada yoxlanılır.

### ABB-Q082

**Soru (az):** Əmanət üzrə nağd kredit və Əmanətçilər üçün kredit xətti depozitə nisbətdə məbləğ və komissiya baxımından necə fərqlənir?

**Beklenen cevap:** Əmanət üzrə nağd kreditdə məbləğ depozitin 70%-nə qədər, depozitin valyutasında isə 50 000-ə qədər göstərilir və xidmət haqqı 0,5%-dir. Əmanətçilər üçün kredit xəttində müvafiq nisbət 60%-ə qədər, depozitin valyutasında hədd 50 000-ə qədərdir və komissiya yoxdur.

**Kaynak 1:** [Əmanət üzrə nağd kredit](https://abb-bank.az/ferdi/kreditler/emanetci-nagd-krediti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1544**; `sections[2].paragraphs[0]; sections[2].paragraphs[5]`.

**Bölüm / FAQ:** Əmanət üzrə nağd kredit > Nağd kredit haqqında > Şərtlər

**Kanıt:**

> Məbləğ: Depozit məbləğinin 70%-nə qədər, depozitin valyutasında isə 50 000-ə qədər
> Xidmət haqqı: 0,5%

**Kaynak 2:** [Əmanətçilər üçün kredit xətti](https://abb-bank.az/ferdi/kreditler/emanetci-kredit-limiti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1543**; `sections[2].paragraphs[6]; sections[2].paragraphs[9]`.

**Bölüm / FAQ:** Əmanətçilər üçün kredit xətti > Kredit xətti haqqında > Terms

**Kanıt:**

> Məbləğ: Depozit məbləğinin 60%-nə qədər, depozitin valyutasında isə 50 000-ə qədər.
> Komissiya: Komissiya yoxdur.

### ABB-Q083

**Soru (az):** TamKart Max və TamKart Gold Kredit-in nominal illik faiz dərəcələrini müqayisə edin.

**Beklenen cevap:** TamKart Max üçün 27%, 28% və 29%; TamKart Gold Kredit üçün 22% göstərilir.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `sections[10].paragraphs[1]`.

**Bölüm / FAQ:** TamKart Max > Şərtlər və Tariflər > Tariflər

**Kanıt:**

> İllik faiz dərəcəsi: 27%, 28%, 29%

**Kaynak 2:** [TamKart Gold Kredit](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-visa-gold)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2484**; `sections[6].paragraphs[2]`.

**Bölüm / FAQ:** TamKart Gold Kredit > Tariflər

**Kanıt:**

> İllik faiz dərəcəsi: 22%

### ABB-Q084

**Soru (az):** Travel Card Visa Signature və ABB–Sea Breeze Visa Platinum ilə lounge zallarından illik neçə dəfə istifadə etmək olar?

**Beklenen cevap:** Travel Card Visa Signature ilə ildə 6 dəfə lounge zallarından istifadə etmək olar. ABB–Sea Breeze Visa Platinum ilə DragonPass çərçivəsində ildə 2 dəfə pulsuz giriş təqdim edilir.

**Kaynak 1:** [Travel Card Visa Signature](https://abb-bank.az/ferdi/kartlar/debet-kartlari/travel-card-visa-signature)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2481**; `sections[6].paragraphs[0]`.

**Bölüm / FAQ:** Travel Card Visa Signature > Ödəniş sistemlərinin üstünlükləri > Lounge zallarına giriş

**Kanıt:**

> Uçuşdan öncəki zamanı daha komfortlu keçirin. İl ərzində 6 dəfə lounge zallarının rahat atmosferindən yararlanın.

**Kaynak 2:** [ABB - Sea Breeze Visa Platinum](https://abb-bank.az/ferdi/kartlar/debet-kartlari/abb-sea-breeze-visa-platinum)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2466**; `sections[10].paragraphs[2]`.

**Bölüm / FAQ:** ABB - Sea Breeze Visa Platinum > Əlavə üstünlüklər > Detallar

**Kanıt:**

> Lounge zallar (ildə 2 dəfə): DragonPass proqramı çərçivəsində biznes zallara ildə 2 dəfə pulsuz giriş edə bilərsiniz.

### ABB-Q085

**Soru (az):** Ani kredit və Sahibkar krediti üçün maksimum kredit müddətlərini müqayisə edin; kredit xəttini nəzərə almayın.

**Beklenen cevap:** Ani kreditdə maksimum müddət 24 ay, Sahibkar kreditində 36 aydır.

**Kaynak 1:** [Ani kredit](https://abb-bank.az/biznes/kicik-ve-orta-biznes/biznes-kreditleri/ani-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2365**; `sections[10].paragraphs[6]`.

**Bölüm / FAQ:** Ani kredit > Kredit haqqında detallar > Details

**Kanıt:**

> Müddət: Minimum - 1 ay; Maksimum - 24 ay

**Kaynak 2:** [Sahibkar krediti/kredit xətti](https://abb-bank.az/biznes/kicik-ve-orta-biznes/biznes-kreditleri/sahibkar-krediti)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2373**; `sections[10].paragraphs[1]`.

**Bölüm / FAQ:** Sahibkar krediti/kredit xətti > Kredit haqqında detallar > Details

**Kanıt:**

> Kreditin müddəti: Kredit üzrə 36 ay, kredit xətti üzrə 12 ay

### ABB-Q086

**Soru (az):** Onlayn mağazam üçün ePOS ilə satış nöqtəsində Mobil POS arasında əsas istifadə fərqi nədir?

**Beklenen cevap:** ePOS veb-sayt və elektron ticarət platformalarında kart ödənişlərini qəbul etmək üçündür. Mobil POS isə ABB Biz tətbiqində Android cihazdan biznesin nağdsız ödənişlərini qəbul etmək üçündür.

**Kaynak 1:** [Elektron ticarət (ePOS)](https://abb-bank.az/biznes/korporativ/online-xidmetler-korporativ/elektron-ticaret)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2399**; `sections[1].paragraphs[0]`.

**Bölüm / FAQ:** Elektron ticarət (ePOS)

**Kanıt:**

> Virtual POS (ePOS) – Veb saytlar və e-ticarət platformaları üçün onlayn ödəniş həlləri. Əgər siz e-ticarətlə məşğulsunuzsa, onlayn mağazanızda kartla ödənişlərin qəbulunu təşkil etmək və bununla da müştərilərinizə yüksək səviyyədə xidmət göstərmək üçün bizimlə əlaqə saxlayın.

**Kaynak 2:** [Mobil POS](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/mobil-pos)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2407**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** Mobil POS

**Kanıt:**

> ABB Biz tətbiqindəki mobil POS terminal Android cihazlarda biznesiniz üçün nağdsız ödənişləri rahatlıqla qəbul etməyin müasir yoludur.

### ABB-Q087

**Soru (az):** ABB-nin QR kod ödənişi hansı sistemlə işləyir, Mobil POS isə hansı tətbiqdə və cihaz platformasında təqdim olunur?

**Beklenen cevap:** QR kod ödənişi AniPay sistemi ilə işləyir. Mobil POS ABB Biz tətbiqində Android cihazlar üçün təqdim olunur.

**Kaynak 1:** [QR kod](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/qr-kod)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2408**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** QR kod

**Kanıt:**

> Anipay sistemi ilə işləyən bu texnologiya müştərilərdən nağdsız ödənişləri qəbul etmək üçün istifadə olunur. QR kodu skan edən müştəri əlavə əməliyyata ehtiyac qalmadan ödənişi təsdiqləyir

**Kaynak 2:** [Mobil POS](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/mobil-pos)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2407**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** Mobil POS

**Kanıt:**

> ABB Biz tətbiqindəki mobil POS terminal Android cihazlarda biznesiniz üçün nağdsız ödənişləri rahatlıqla qəbul etməyin müasir yoludur.

### ABB-Q088

**Soru (az):** Filialda adi cari hesab açmaqla tətbiqdən DigiHesab açmağın əsas addımları necə fərqlənir?

**Beklenen cevap:** Cari hesab üçün ABB filialına gedib ərizə doldurmaq və şəxsiyyəti təsdiq edən sənədi təqdim etmək lazımdır. DigiHesab üçün ABB mobile-da “Bütün məhsullarım” → “Hesablar” → “DigiHesab aç” → “Fərqli valyutada cari hesab aç” yolu izlənir.

**Kaynak 1:** [Bir neçə valyutada cari hesab](https://abb-bank.az/ferdi/butun-hesablar/cari-hesab)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1526**; `sections[6].paragraphs[0]; sections[6].paragraphs[1]`.

**Bölüm / FAQ:** Bir neçə valyutada cari hesab > Cari hesab necə açılır?

**Kanıt:**

> ABB filialına gedin: Ən yaxın filialımızı tapın
> Hesab üçün müraciət və sənədlərin imzalanması: Müqavilə bağlamaq üçün ərizə doldurmaq və şəxsiyyəti təsdiq edən sənədi təqdim etmək kifayətdir.

**Kaynak 2:** [DigiHesab - Etibarlı və rəqəmsal](https://abb-bank.az/ferdi/butun-hesablar/digihesab)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1528**; `sections[4].paragraphs[0]; sections[4].paragraphs[1]; sections[4].paragraphs[2]`.

**Bölüm / FAQ:** DigiHesab - Etibarlı və rəqəmsal > 3 addıma DigiHesab açın.

**Kanıt:**

> ABB mobile-a daxil olun
> “Bütün məhsullarım” bölməsindən “Hesablara” daxil olun
> “DigiHesab aç” kliklədikdən sonra açılan pəncərədə “Fərqli valyutada cari hesab aç”ı seçin

### ABB-Q089

**Soru (az):** Gəncədə əmanət seyfi üçün hansı ABB filialına müraciət edə bilərəm və icarə üçün nə təqdim etməliyəm?

**Beklenen cevap:** Xidmət şəbəkəsinin seyf olan filiallar siyahısında Gəncə filialı göstərilir. İcarə müqaviləsi üçün ərizə doldurmaq və şəxsiyyət vəsiqəsini təqdim etmək kifayətdir.

**Kaynak 1:** [ABB xidmət şəbəkəsi: filiallar, şöbələr, bankomatlar və terminallar](https://abb-bank.az/filiallar)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **3997**; `sections[3].paragraphs[0]`.

**Bölüm / FAQ:** ABB xidmət şəbəkəsi: filiallar, şöbələr, bankomatlar və terminallar > Seyf olan filiallar

**Kanıt:**

> Gəncə filialı, Müştəri xidməti departamenti, Mərkəzi filialı, Nəsimi filialı, Sabunçu filialı, Səbail filialı, Sənaye filialı, Xətai filialı

**Kaynak 2:** [Depozit və əmanət seyfləri](https://abb-bank.az/ferdi/emanetler/depozit-seyfi)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1530**; `sections[2].paragraphs[1]`.

**Bölüm / FAQ:** Depozit və əmanət seyfləri > Əmanət qutusunu necə sifariş etmək olar? > Depozit və əmanət seyfləri

**Kanıt:**

> Əmanət seyfi üçün müraciət edin: İcarə müqaviləsini bağlamaq üçün ərizə doldurmaq və şəxsiyyət vəsiqəsini təqdim etmək kifayətdir.

### ABB-Q090

**Soru (az):** ABİF üzrə Avadanlıq krediti ilə Ani kreditin maksimum məbləğ və müddətlərini müqayisə edin.

**Beklenen cevap:** ABİF Avadanlıq krediti maksimum 3 000 000 AZN və 5 ilədəkdir. Ani kredit maksimum 500 000 AZN və 24 ayadəkdir.

**Kaynak 1:** [ABİF ilə güzəştli kreditlər](https://abb-bank.az/biznes/kicik-ve-orta-biznes/biznes-kreditleri/abif-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2364**; `sections[3].paragraphs[0]; sections[3].paragraphs[1]; sections[3].paragraphs[2]`.

**Bölüm / FAQ:** ABİF ilə güzəştli kreditlər > Kredit haqqında detallar > Avadanlıq krediti

**Kanıt:**

> Kreditin məqsədi: Avadanlıq və texnika alışı
> Məbləğ: 5 000 - 3 000 000 AZN-dək
> Müddət: 5 ilədək

**Kaynak 2:** [Ani kredit](https://abb-bank.az/biznes/kicik-ve-orta-biznes/biznes-kreditleri/ani-kredit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2365**; `sections[10].paragraphs[5]; sections[10].paragraphs[6]`.

**Bölüm / FAQ:** Ani kredit > Kredit haqqında detallar > Details

**Kanıt:**

> Məbləğ: Min. 5 000 AZN, Maks. - 500 000 AZN
> Müddət: Minimum - 1 ay; Maksimum - 24 ay

## 6. Çok dilli sorular — 10 soru

### ABB-Q091

**Soru (en):** When are monthly instalments for a TamKart Max purchase due, and in which month do repayments start?

**Beklenen cevap:** Instalments are due between the 1st and 10th of each month, starting in the month after the debt arose.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `faq[8]`.

**Bölüm / FAQ:** Taksit əməliyyatı nədir və aylıq ödəniş nə vaxt edilməlidir?

**Kanıt:**

> Taksit əməliyyatı – tərəfdaş mağazalardan etdiyiniz alış-verişin məbləğinin komissiyasız olaraq bərabər hissələrə bölünərək aylıq ödənişlərlə geri qaytarılmasıdır. Taksit üzrə aylıq ödənişi borcun formalaşdığı tarixdən sonrakı aydan başlamaqla, hər ayın 1-dən 10-dək həyata keçirməlisiniz.

### ABB-Q092

**Soru (en):** How many Travel Card bonus points do I need to cover a flight ticket purchase of 300 AZN?

**Beklenen cevap:** You need bonus points equal to 65 times the amount paid: 300 × 65 = 19,500 bonus points.

**Kaynak 1:** [Travel Card Visa Signature](https://abb-bank.az/ferdi/kartlar/debet-kartlari/travel-card-visa-signature)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2481**; `faq[8]`.

**Bölüm / FAQ:** Bonus balansının aviabilet, otel və digər xidmətlər üçün kifayət edib-etmədiyini necə öyrəmə bilərəm?

**Kanıt:**

> Müştəri aviabilet, otel və digər xidmmətlər üçün ödədiyi vəsaiti bonuslara dəyişmək üçün, ödədiyin məbləğin 65 misli qədər bonusu olmalıdır. Məsələn: 300 AZN-lik aviabilet üçün, müştərinin 300*65=19500 bonus balansı olmalıdır.

### ABB-Q093

**Soru (en):** What is the maximum number of DigiHesab accounts I can open in the same currency?

**Beklenen cevap:** You can open a maximum of 2 DigiHesab accounts in each currency.

**Kaynak 1:** [DigiHesab - Etibarlı və rəqəmsal](https://abb-bank.az/ferdi/butun-hesablar/digihesab)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1528**; `sections[3].paragraphs[0]`.

**Bölüm / FAQ:** DigiHesab - Etibarlı və rəqəmsal > 3 valyutada hesab > Hesabınızdan birbaşa köçürmə

**Kanıt:**

> Birbaşa hesabınızdan ölkədaxili və ölkəxarici köçürmələr edin. Hər valyutada maksimum 2 DigiHesab açmaq mümkündür

### ABB-Q094

**Soru (en):** Can I delete my ABB mobile profile directly in the app? If not, how can I have it blocked?

**Beklenen cevap:** The source states that the app has no direct profile deletion function. You can have your profile blocked by contacting the information centre at 937 or visiting a branch.

**Kaynak 1:** [ABB mobile tətbiqində profili necə silmək olar?](https://abb-bank.az/abb-mobile-tetbiqinde-profili-nece-silmek-olar)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **20**; `sections[0].paragraphs[0]`.

**Bölüm / FAQ:** ABB mobile tətbiqində profili necə silmək olar?

**Kanıt:**

> Hazırda ABB mobile proqramında birbaşa profil silmə funksiyası yoxdur. Bununla belə, Bankın Məlumat mərkəzinə (937) müraciət edərək və ya filiala yaxınlaşaraq profilinizi bloklaya bilərsiniz.

### ABB-Q095

**Soru (ru):** Как задаётся сумма при оплате динамическим QR-кодом ABB: покупатель вводит её самостоятельно?

**Beklenen cevap:** Динамический QR-код создаётся отдельно для каждого платежа, и сумма задаётся в нём заранее. Покупатель проверяет данные и подтверждает платёж без повторного ввода суммы.

**Kaynak 1:** [QR kod](https://abb-bank.az/biznes/mikro-biznes/odenis-sistemleri/qr-kod)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2408**; `sections[17].paragraphs[1]`.

**Bölüm / FAQ:** QR kod > QR ödənişlərini ABB Biz-də necə idarə etmək olar? > Statik və dinamik QR kod arasında hansı fərqlər var?

**Kanıt:**

> Dinamik QR kod isə hər ödəniş üçün ayrıca yaradılır və ödəniləcək məbləğ kodun daxilində əvvəlcədən müəyyən edilir. Müştəri QR kodu skan etdikdə məbləği yenidən daxil etmədən məlumatları yoxlayaraq ödənişi təsdiqləyir. Bu üsul məbləğin dəqiq göstərilməsinə və ödəniş zamanı yanlış məlumat daxil edilməsi ehtimalının azalmasına kömək edir.

### ABB-Q096

**Soru (ru):** Как долго действуют бонусы Travel Card и что происходит с ними после окончания срока действия карты?

**Beklenen cevap:** Бонусы действуют 24 месяца. После окончания срока действия карты бонусы считаются недействительными.

**Kaynak 1:** [Travel Card Visa Signature](https://abb-bank.az/ferdi/kartlar/debet-kartlari/travel-card-visa-signature)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2481**; `faq[10]`.

**Bölüm / FAQ:** Bonusların etibarlılıq müddəti nə qədərdir?

**Kanıt:**

> Bonusların qüvvədə qalma müddəti - 24 ay təşkil edir. Bonuslar kartın müddəti bitdikdən sonra etibarsız hesab edilir.

### ABB-Q097

**Soru (ru):** До какого момента нужно завершить уровни Fayda Max, чтобы получить награды в следующем месяце?

**Beklenen cevap:** Необходимые уровни нужно завершить до конца текущего месяца, чтобы получить награды в следующем.

**Kaynak 1:** [Fayda Max təkmilləşdirilmiş keşbek](https://abb-bank.az/ferdi/kesbek/fayda-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1538**; `sections[6].paragraphs[0]`.

**Bölüm / FAQ:** Fayda Max təkmilləşdirilmiş keşbek > Fayda Max ilə necə qazanmaq olar? > Mükafatlardan yararlanın

**Kanıt:**

> Gələn ay mükafatlar qazanmaq bu ayın sonuna qədər xüsusi səviyyələri tamamlamaqdan asılıdır

### ABB-Q098

**Soru (en):** After a purchase with TamKart Max at a partner store, how can I extend the instalment term and what is the deadline?

**Beklenen cevap:** Use ABB mobile to extend the purchase beyond the store’s offered maximum instalment term. The extension must be made by the end of the month in which the debt arose.

**Kaynak 1:** [TamKart Max](https://abb-bank.az/ferdi/kartlar/kredit-kartlari/tamkart-max)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **2482**; `faq[9]`.

**Bölüm / FAQ:** Taksit müddətini artırmaq nə deməkdir?

**Kanıt:**

> Tərəfdaş mağazada etdiyiniz alış-verişi mağazanın təqdim etdiyi maksimum taksit müddətindən daha uzun müddətə bölə bilərsiniz. Bunun üçün ABB mobile tətbiqindən istifadə edə bilərsiniz. Taksit müddətinin artırılması borcun yarandığı ayın sonunadək mümkündür.

### ABB-Q099

**Soru (en):** How close to the maturity date can I still add money to my DigiDeposit?

**Beklenen cevap:** You can increase the deposit until 90 days before the contract’s maturity date.

**Kaynak 1:** [DigiDeposit - Tamamilə rəqəmsal](https://abb-bank.az/ferdi/emanetler/digideposit)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **1531**; `sections[2].paragraphs[0]`.

**Bölüm / FAQ:** DigiDeposit - Tamamilə rəqəmsal > DigiDeposit ilə qazanmağa başlayın. > Yüksək gəlir

**Kanıt:**

> Üstəlik, müqavilənin bitmə tarixinə 90 gün qalanadək depozitinizi artırın.

### ABB-Q100

**Soru (en):** What security measures does ABB describe for Internet Banking transactions?

**Beklenen cevap:** ABB describes multifactor verification, additional transaction confirmation mechanisms and security systems.

**Kaynak 1:** [İnternet Banking - sizə bir addım daha yaxın](https://abb-bank.az/internet-banking)

**Korpus konumu:** `data/abb_pages.jsonl`, satır **71**; `faq[2]`.

**Bölüm / FAQ:** İnternet Banking təhlükəsizdirmi?

**Kanıt:**

> Bəli, əməliyyatlar çoxfaktorlu təsdiqləmə, əlavə təsdiq mexanizmləri və təhlükəsizlik sistemləri ilə qorunur. Məlumatların məxfiliyi və əməliyyatların təhlükəsizliyi yüksək səviyyədə təmin edilir.

from abb_scraper.extract.text import decode_cf_email, detect_language, fingerprint, normalize_text


class TestNormalizeText:
    def test_collapses_whitespace_and_nbsp(self):
        assert normalize_text("  Nağd kredit \n\t şərtləri ") == "Nağd kredit şərtləri"

    def test_replaces_cyrillic_and_turned_e_lookalikes_with_azerbaijani_schwa(self):
        assert normalize_text("Әmanәt") == "Əmanət"
        assert normalize_text("mǝblǝğ") == "məbləğ"

    def test_composes_decomposed_characters(self):
        decomposed = "ş"  # s + combining cedilla
        assert normalize_text(decomposed) == "ş"

    def test_removes_invisible_characters(self):
        assert normalize_text("ABB​ mobile­") == "ABB mobile"

    def test_decodes_html_entities_left_by_double_escaping(self):
        assert normalize_text("genişləndirmək &uuml;çün") == "genişləndirmək üçün"

    def test_removes_markdown_emphasis(self):
        assert normalize_text("Tarifləri **Yükləyin** və __oxuyun__") == "Tarifləri Yükləyin və oxuyun"

    def test_markdown_links_keep_their_text_and_document_urls(self):
        assert normalize_text("[ASAN Finans](https://asan.az) vasitəsilə") == "ASAN Finans vasitəsilə"
        assert normalize_text("[Yüklə](https://cdn.abb-bank.az/tarif.pdf)") == "Yüklə (https://cdn.abb-bank.az/tarif.pdf)"


class TestFingerprint:
    def test_ignores_case_and_spacing(self):
        assert fingerprint("Nağd Kredit ") == fingerprint("nağd   kredit")

    def test_treats_azerbaijani_dotted_and_dotless_i_alike(self):
        assert fingerprint("İLLİK FAİZ") == fingerprint("illik faiz")
        assert fingerprint("KREDIT") == fingerprint("kredıt") == fingerprint("kredit")


class TestDetectLanguage:
    def test_azerbaijani(self):
        text = "Nağd kredit şəxsi maliyyə ehtiyaclarını qarşılamaq üçün bank tərəfindən təqdim olunan kredit növüdür."
        assert detect_language(text) == "az"

    def test_english_with_azerbaijani_product_names(self):
        text = ("Get a cash loan of up to 70,000 AZN without visiting the branch. TamKart and ABB-Qarabağ "
                "cards give cashback on every purchase.")
        assert detect_language(text) == "en"

    def test_russian(self):
        text = ("Получите наличный кредит до 70 000 AZN, не посещая филиал банка. "
                "Без поручителей и справок о доходах, полностью онлайн через ABB mobile.")
        assert detect_language(text) == "ru"

    def test_too_little_text(self):
        assert detect_language("ABB mobile") is None


def test_decode_cf_email():
    assert decode_cf_email("4a23242c250a2b282867282b2421642b30") == "info@abb-bank.az"

from app.shared.domain_country import country_code_for_domain, country_display_name


def test_country_il_tld():
    assert country_code_for_domain("www.example.co.il") == "IL"


def test_country_uk_public_suffix():
    assert country_code_for_domain("news.bbc.co.uk") == "GB"


def test_country_generic_com():
    assert country_code_for_domain("www.google.com") == "GLOBAL"


def test_country_de_tld():
    assert country_code_for_domain("bund.de") == "DE"


def test_display_name():
    assert "Israel" in country_display_name("IL")

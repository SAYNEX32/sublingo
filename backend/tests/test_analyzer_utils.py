from app.nlp.analyzer import is_spoken_variant, looks_like_name, rough_level


def test_rough_level_bands():
    assert rough_level(4.4) == "B1"
    assert rough_level(3.9) == "B2"
    assert rough_level(3.2) == "C1"
    assert rough_level(2.0) == "C2"


def test_name_detection():
    assert looks_like_name(mid_total=5, mid_caps=5)
    assert not looks_like_name(mid_total=5, mid_caps=1)
    assert not looks_like_name(mid_total=0, mid_caps=0)

def test_spoken_variants_are_detected():
    for word in ("fuckin", "nothin", "lettin", "goin"):
        assert is_spoken_variant(word)


def test_real_words_are_kept():
    for word in ("cousin", "thin", "raisin", "begin", "captain", "origin"):
        assert not is_spoken_variant(word)
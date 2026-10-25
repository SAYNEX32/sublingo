from app.nlp.analyzer import looks_like_name, rough_level


def test_rough_level_bands():
    assert rough_level(4.4) == "B1"
    assert rough_level(3.9) == "B2"
    assert rough_level(3.2) == "C1"
    assert rough_level(2.0) == "C2"


def test_name_detection():
    assert looks_like_name(mid_total=5, mid_caps=5)
    assert not looks_like_name(mid_total=5, mid_caps=1)
    assert not looks_like_name(mid_total=0, mid_caps=0)
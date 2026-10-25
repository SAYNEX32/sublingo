from app.nlp.srt_parser import clean_text


def test_removes_html_and_brackets():
    assert clean_text("<i>Hello</i> [music] world") == "Hello world"


def test_removes_speaker_label():
    assert clean_text("WALTER: Hi there.") == "Hi there."


def test_removes_dialogue_dashes():
    assert clean_text("- Yes.\n- No.") == "Yes. No."


def test_music_only_is_empty():
    assert clean_text("♪ ♪") == ""
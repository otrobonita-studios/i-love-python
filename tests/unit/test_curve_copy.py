"""Public curve essay must be canonical copy, never the CLI notes."""

from art import curve_copy, hero_copy


def test_essay_ends_with_python_on_a_string() -> None:
    assert curve_copy.PARAGRAPHS[-1].endswith("Python on a string!")
    blob = "\n".join(curve_copy.PARAGRAPHS)
    assert "I ❤ NY" in blob
    assert "Milton Glaser" in blob
    assert "Kill the Quasar" not in blob
    assert "top menu" not in blob
    assert "hamburger" not in blob
    html = curve_copy.typeset_html(curve_copy.PARAGRAPHS[2])
    assert curve_copy.NY_HREF in html
    assert curve_copy.GLASER_HREF in html


def test_hero_copy_matches_the_visual_contract() -> None:
    assert hero_copy.CAPTION.startswith("Rendered by the code")
    assert "looks like it means it" in hero_copy.MUTED
    assert "sin³" in hero_copy.FORMULA
    assert hero_copy.READ_LETTER == "Read the letter"

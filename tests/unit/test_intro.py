"""House letter of introduction — canonical copy."""

from explain import intro


def test_intro_copy_is_the_house_letter() -> None:
    assert intro.PARAGRAPHS[0] == "Dear colleague —"
    assert intro.PARAGRAPHS[-1] == "Walk through. The rooms will introduce themselves."
    assert intro.TITLE == "I would like you to meet the house."
    assert intro.SIGN_OFF[-1] == "Otrobonita AI Labs"
    assert len(intro.ROOMS) == 6
    html = intro.typeset_html(intro.PARAGRAPHS[2])
    assert "app.py" in html
    assert "<code" in html
    blob = "\n".join(intro.PARAGRAPHS)
    assert "Kill the Quasar" not in blob
    assert "hamburger" not in blob

from app.prompts import get_prompt_template, render_prompt

def test_get_prompt_template():
    template = get_prompt_template("database_analysis")
    assert "Analysiere die Tabelle" in template

def test_render_prompt():
    template = "Hallo {{name}}!"
    rendered = render_prompt(template, name="Welt")
    assert rendered == "Hallo Welt!"

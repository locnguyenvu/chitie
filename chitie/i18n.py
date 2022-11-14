import ast
import os


def load_lang_dict() -> dict:
    lang = os.getenv("APP_LANG", "en")
    lang_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang', lang + '.json')
    translate_file = open(lang_path, "r", encoding="utf8")
    translate_content = translate_file.read()
    translate_dict = ast.literal_eval(translate_content)
    translate_file.close()
    return translate_dict


lang_dict = load_lang_dict()


def t(key) -> str:
    if key not in lang_dict:
        return key
    return lang_dict[key]

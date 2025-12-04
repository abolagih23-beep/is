from deep_translator import GoogleTranslator

def translate_text(source, target, text):
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:
        print("Translation Error:", e)
        return "Translation Failed"

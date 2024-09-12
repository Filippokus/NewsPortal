from django import template

register = template.Library()

# Список нежелательных слов
BAD_WORDS = ['редиска', 'ругательство1', 'ругательство2', 'Редиска']  # добавь сюда все нежелательные слова


@register.filter(name='censor')
def censor(value):
    words = value.split()
    censored_text = []

    for word in words:
        clean_word = word.strip('.,!?')  # Убираем знаки препинания для проверки слова
        if clean_word.lower() in BAD_WORDS:
            censored_word = clean_word[0] + '*' * (len(clean_word) - 1)
            censored_text.append(word.replace(clean_word, censored_word))  # Восстанавливаем знаки препинания
        else:
            censored_text.append(word)

    return ' '.join(censored_text)

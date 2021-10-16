import re

human_words = []
stop_words = ['товар', 'услуга', 'торговля', 'покупки', 'магазин', 'бизнес', 'мебель',
              'одежда', 'бренд', 'фриланс', 'доставка', 'самовывоз', 'директ', 'лайк',
              'лайки', 'сотрудничество', 'косметика', 'консультация', 'бизнеса', 'запись',
              'звоните', 'красота', 'etsy', 'наличии', 'наличие', 'бизнесу', 'ремонт',
              'сотрудничества', 'шугаринг', 'маникюр', 'отель', 'москва', 'макияж',
              'брови', 'direct', 'топ', 'smm', 'таро', 'час']

hash_human_words = set([hash(word) for word in human_words])
hash_stop_words = set([hash(word) for word in stop_words])


# иностранные слова


def is_our_client(text: str) -> bool:
    ews = re.findall("[A-Za-z]+", text)
    rws = re.findall("[ЁёА-Яа-я]+", text)
    hash_tokens = set([hash(word.lower()) for word in ews + rws])
    return is_russian(ews, rws) and is_human(hash_tokens) and not is_company(hash_tokens)


def is_company(hash_tokens):
    global hash_stop_words
    general_set = hash_tokens & hash_stop_words
    return bool(general_set)


def is_human(hash_tokens):
    global hash_human_words
    # for hash_token in hash_tokens:
    #    if hash_token in hash_human_words:
    #        return True
    #    else:
    #        pass
    return True


def is_russian(english_words, russian_words) -> bool:
    if len(english_words) > 3 and len(russian_words) == 0:
        return False
    elif len(english_words) > 0 and len(russian_words) > 3:
        return True
    elif len(english_words) == 0 and len(russian_words) > 0:
        return True
    else:
        return False

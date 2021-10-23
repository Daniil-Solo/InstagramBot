import re
from langdetect import detect, LangDetectException

human_words = []
stop_words = ['товар', 'услуга', 'торговля', 'покупки', 'магазин', 'бизнес', 'мебель',
              'одежда', 'бренд', 'фриланс', 'доставка', 'самовывоз', 'директ', 'лайк',
              'лайки', 'сотрудничество', 'косметика', 'консультация', 'бизнеса', 'запись',
              'звоните', 'красота', 'etsy', 'наличии', 'наличие', 'бизнесу', 'ремонт',
              'сотрудничества', 'шугаринг', 'маникюр', 'отель', 'москва',
              'брови', 'direct', 'топ', 'smm', 'таро', 'час', 'услуг', 'массаж', 'копирайтер',
              'режим', 'выходной', 'агенство', 'услуги', 'парикмахер', 'телефон', 'онлайн',
              'бронирование', 'тур', 'скидки', 'акции', 'заказ', 'заказа', 'сеть', 'образование',
              'сайт', 'туры', 'отели', 'аренда', 'агент', 'отправка']
master_words = ['эпоксидка', 'эпоксидной', 'смолы', 'эпоксидные', 'смолу', 'смола']
man_names = ['владислав', 'александр', 'андрей', 'сергей', 'никита', 'олег', 'владимир', 'даниил', 'дмитрий', 'алексей']

hash_human_words = set([hash(word) for word in human_words])
hash_stop_words = set([hash(word) for word in stop_words])
hash_master_words = set([hash(word) for word in master_words])
hash_man_names = set([hash(name) for name in man_names])

# иностранные слова


def is_our_client(text: str) -> bool:
    ews = re.findall("[A-Za-z]+", text)
    rws = re.findall("[ЁёА-Яа-я]+", text)
    hash_tokens = set([hash(word.lower()) for word in ews + rws])
    return is_relevant_language(text) and not is_company(hash_tokens) and not is_man(hash_tokens)


def is_master(text):
    global hash_master_words
    tokens = re.findall("[ЁёА-Яа-я]+", text)
    hash_tokens = set([hash(word.lower()) for word in tokens])
    general_set = hash_tokens & hash_master_words
    return bool(general_set)


def is_man(hash_tokens):
    global hash_man_names
    general_set = hash_tokens & hash_man_names
    return bool(general_set)


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


def is_relevant_language(text) -> bool:
    try:
        predict = detect(text)
    except LangDetectException:
        print("Описание не содержит букв")
        return False
    print("Предсказываемый язык описания: " + predict)
    if predict in ['ru', 'uk', 'br', 'bg', 'mk', 'sw', 'sv', 'sl']:
        return True
    else:
        return False

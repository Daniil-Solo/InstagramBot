import re

human_words = []
company_words = ['товар', 'услуга']

hash_human_words = set([hash(word) for word in human_words])
hash_company_words = set([hash(word) for word in company_words])


def is_our_client(text: str) -> bool:
    ews = re.findall("[A-Za-z]+", text)
    rws = re.findall("[ЁёА-Яа-я]+", text)
    hash_tokens = set([hash(word.lower()) for word in ews + rws])
    return is_russian(ews, rws) and is_human(hash_tokens) and not is_company(hash_tokens)


def is_company(hash_tokens):
    global hash_company_words
    general_set = hash_tokens & hash_company_words
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
    if len(english_words) > 0:
        if len(russian_words) == 0 or len(russian_words) <= 2:
            return False
        else:
            return True
    elif len(russian_words) == 0:
        return False
    else:
        return True


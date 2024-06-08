import string
import random


def generate_random(length=6, use_lowercase=False, use_capital=False, use_digit=False, use_punctuation=False):
    characters = []

    if use_capital:
        characters.extend(string.ascii_uppercase)
    if use_lowercase:
        characters.extend(string.ascii_lowercase)
    if use_digit:
        characters.extend(string.digits)
    if use_punctuation:
        characters.extend(string.punctuation)
    if not characters:
        raise ValueError("هیچ نوع کاراکتری برای انتخاب وجود ندارد")

    result = "".join(random.choice(characters) for i in range(length))
    return result

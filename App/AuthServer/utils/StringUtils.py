import random
import string

letters_and_digits = string.ascii_uppercase + string.ascii_lowercase + string.digits
def getRandomString(n):
    return ''.join(random.SystemRandom().choice(letters_and_digits) for _ in range(n))

CHARS = '63VhSRo0yHvg1upE4sDGXqjkx7Fd8KfmIPBJlU52brtaQciZM9NTLOnCzewYWA'

def encode(num, chars=CHARS):
    if num == 0:
        return chars[0]
    l = []
    base = len(chars)
    while num:
        rem = num % base
        num = num // base
        l.append(chars[rem])
    l.reverse()
    return ''.join(l)

def decode(string, chars=CHARS):
    base = len(chars)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += chars.index(char) * (base ** power)
        idx += 1

    return num


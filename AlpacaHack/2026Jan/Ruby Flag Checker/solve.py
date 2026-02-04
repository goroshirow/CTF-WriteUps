key = [2, 3, 5, 7, 11, 13, 17, 19, 23, 25, 29, 31, 35, 37, 41, 43, 47, 49, 53, 55, 59, 61, 65]
chiper = "Coufhlj@bixm|UF\\JCjP^P<"

def decode(chiper, key):
    decoded = ""
    for i in range(len(chiper)):
        decoded += chr(ord(chiper[i]) ^ key[i])
    return decoded

if __name__ == "__main__":
    print(decode(chiper, key))

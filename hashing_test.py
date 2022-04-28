import hashlib

with open("img.png", 'rb') as f:
    # hashed = hashlib.sha256(f.read()).hexdigest()
    content = f.read()

sha256 = hashlib.sha256(content)

print(sha256.hexdigest())

a = hashlib.sha256(sha256.digest())
print(a.hexdigest())
# hashlib.pbkdf2_hmac()


# IMPORTANT: pip install pyopenssl to install it
from OpenSSL import crypto, SSL


def cert_gen(emailAddress="me@me.com", commonName="127.0.0.1", countryName="IL",
             KEY_FILE="server2.pem"):
    # in the above line we define the default parameters
    # can look at generated file using openssl:
    # openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)  # 4096 bit

    # create a self-signed certificate
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)  # <-- Valid for 10 years!
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))


cert_gen()
# call function with default parameters, which are defined in teh function

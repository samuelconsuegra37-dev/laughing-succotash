import random
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64

# Public parameters (RFC 3526 - 1536 bit prime)
g = 2
p = int( "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
    "670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF",
    16
)

#randomly generated key
def generate_private_key(p):
    return random.randint(2, p - 2)

def generate_public_key(g, p, private_key):
    return pow(g, private_key, p)

def generate_shared_secret(their_public_key, my_private_key, p):
    return pow(their_public_key, my_private_key, p)

def derive_key(shared_secret):
    # Convert the shared secret to bytes and hash it to a fixed size
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(shared_secret.to_bytes(192, byteorder='big'))
    key = digest.finalize()
    return base64.urlsafe_b64encode(key)

def encrypt_message(key, message):
    f = Fernet(key)
    return f.encrypt(message.encode())

def decrypt_message(key, token):
    f = Fernet(key)
    return f.decrypt(token).decode()

#test
if __name__ == "__main__":
    alice_private = generate_private_key(p)
    bob_private = generate_private_key(p)

    alice_public = generate_public_key(g, p, alice_private)
    bob_public = generate_public_key(g, p, bob_private)

    alice_secret = generate_shared_secret(bob_public, alice_private, p)
    bob_secret = generate_shared_secret(alice_public, bob_private, p)

    print("Keys match:", alice_secret == bob_secret)

    # Test encryption
    key = derive_key(alice_secret)
    token = encrypt_message(key, "hello bob!")
    print("Encrypted:", token)
    print("Decrypted:", decrypt_message(key, token))
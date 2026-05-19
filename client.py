import socket
from dh import generate_private_key, generate_public_key, generate_shared_secret, derive_key, encrypt_message, decrypt_message, g, p

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 9999))
    print("Connected to server!")

    # DH handshake
    my_private = generate_private_key(p)
    my_public = generate_public_key(g, p, my_private)

    # Receive server's public key first
    their_public = int(client.recv(4096).decode())

    # Send our public key to server
    client.send(str(my_public).encode())

    # Compute shared secret and derive key
    shared_secret = generate_shared_secret(their_public, my_private, p)
    key = derive_key(shared_secret)
    print("Secure channel established!")

    while True:
        received = client.recv(4096)
        decrypted = decrypt_message(key, received)
        print(f"Them: {decrypted}")

        message = input("You: ")
        encrypted = encrypt_message(key, message)
        client.send(encrypted)

start_client()
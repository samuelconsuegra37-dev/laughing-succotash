import socket
from dh import generate_private_key, generate_public_key, generate_shared_secret, derive_key, encrypt_message, decrypt_message, g, p

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 9999))
    server.listen(1)
    print("Waiting for connection...")

    conn, addr = server.accept()
    print(f"Connected to {addr}")

    # DH handshake
    my_private = generate_private_key(p)
    my_public = generate_public_key(g, p, my_private)

    # Send our public key to client
    conn.send(str(my_public).encode())

    # Receive client's public key
    their_public = int(conn.recv(4096).decode())

    # Compute shared secret and derive key
    shared_secret = generate_shared_secret(their_public, my_private, p)
    key = derive_key(shared_secret)
    print("Secure channel established!")

    while True:
        message = input("You: ")
        encrypted = encrypt_message(key, message)
        conn.send(encrypted)

        received = conn.recv(4096)
        ecrypted = decrypt_message(key, received)
        print(f"Them: {ecrypted}")

start_server()


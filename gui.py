import tkinter as tk
import threading
import queue
import socket
import pyttsx3
from dh import generate_private_key, generate_public_key, generate_shared_secret, derive_key, encrypt_message, decrypt_message, g, p
from datetime import datetime

message_queue = queue.Queue()

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def add_message(chat_box, sender, message):
    chat_box.config(state="normal")
    chat_box.insert("end", f"{sender}: {message}\n")
    chat_box.config(state="disabled")
    chat_box.see("end")

def receive_messages(conn, key, chat_box):
    while True:
        try:
            received = conn.recv(4096)
            decrypted = decrypt_message(key, received)
            message_queue.put(("Them", decrypted))
        except:
            break

def save_message(sender, message):
    with open("chat_history.txt", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {sender}: {message}\n")


def send_message(conn, key, input_box, chat_box):
    message = input_box.get()
    if message:
        encrypted = encrypt_message(key, message)
        conn.send(encrypted)
        add_message(chat_box, "You", message)
        save_message("You", message)
        input_box.delete(0, "end")

def poll_queue(chat_box, window):
    while not message_queue.empty():
        sender, message = message_queue.get()
        add_message(chat_box, sender, message)
        save_message(sender, message)
        threading.Thread(target=speak, args=(message,), daemon=True).start()
    window.after(100, lambda: poll_queue(chat_box, window))

def create_window(title, conn, key):
    window = tk.Tk()
    window.title(title)
    window.geometry("400x500")

    chat_box = tk.Text(window, state="disabled", wrap="word")
    chat_box.pack(padx=10, pady=10, fill="both", expand=True)

    input_frame = tk.Frame(window)
    input_frame.pack(padx=10, pady=5, fill="x")

    input_box = tk.Entry(input_frame)
    input_box.pack(side="left", fill="x", expand=True)

    send_button = tk.Button(input_frame, text="Send", command=lambda: send_message(conn, key, input_box, chat_box))
    send_button.pack(side="right")

    # Start receiving messages in background thread
    threading.Thread(target=receive_messages, args=(conn, key, chat_box), daemon=True).start()

    # Start polling the queue
    poll_queue(chat_box, window)

    window.mainloop()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 9999))
    server.listen(1)
    print("Waiting for connection...")
    conn, addr = server.accept()
    print(f"Connected to {addr}")

    my_private = generate_private_key(p)
    my_public = generate_public_key(g, p, my_private)
    conn.send(str(my_public).encode())
    their_public = int(conn.recv(4096).decode())
    shared_secret = generate_shared_secret(their_public, my_private, p)
    key = derive_key(shared_secret)
    print("Secure channel established!")

    create_window("DH Chat - Server", conn, key)

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 9999))
    print("Connected to server!")

    my_private = generate_private_key(p)
    my_public = generate_public_key(g, p, my_private)
    their_public = int(client.recv(4096).decode())
    client.send(str(my_public).encode())
    shared_secret = generate_shared_secret(their_public, my_private, p)
    key = derive_key(shared_secret)
    print("Secure channel established!")

    create_window("DH Chat - Client", client, key)

# Ask user whether to run as server or client
mode = input("Run as (s)erver or (c)lient? ")
if mode == "s":
    start_server()
else:
    start_client()
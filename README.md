# laughing-succotash
A simple peer to peer chatting software built in python that uses Diffie-Helman key exchange and AES encryption. It has text to speech and chat history feature that saves the time stamp of when a message is sent. 

## How it works
Implements Diffie-Hellman key exchange from scratch using RFC 3526 1536-bit prime parameters. Both parties derive the same shared secret without ever transmitting it. The shared secret is hashed with SHA-256 and used as an AES-128 key via Fernet.

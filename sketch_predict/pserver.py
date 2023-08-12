import socket
import os
import io
import os.path

def Main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #host = socket.gethostname()
    port = 1002
    s.bind(('localhost', port))

    s.listen()
    print("Waiting for a connection...")

    c, addr = s.accept()
    print("Connection from: " + str(addr))

    #if os.path.isfile("image.png"):
        #os.remove("image.png")

    file = open("image1.png", "wb")
    while True:
        data = c.recv(1024)
        if not data:
            break
        file.write(data)
        #print(str(list(data)))

    print("Done.")
    c.close()
    s.close()

if __name__ == "__main__":
    while True:
        Main()
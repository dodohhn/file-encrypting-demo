
from Crypto import Random


from Crypto.Cipher import AES
import os
import os.path
import time

Attempts = 0
class Encryptor:
    
    def __init__(self, key):
        self.key = key
        self.base_dir = os.path.dirname(os.path.realpath(__file__))

    def pad(self, s):
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def resolve_path(self, file_name):
        if os.path.isabs(file_name):
            return file_name
        return os.path.join(self.base_dir, file_name)

    def encrypt(self, message, key):
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def encrypt_file(self, file_name):
        file_path = self.resolve_path(file_name)
        with open(file_path, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext, self.key)
        with open(file_path + ".enc", 'wb') as fo:
            fo.write(enc)
        os.remove(file_path)

    def decrypt(self, ciphertext, key):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")

    def decrypt_file(self, file_name):
        file_path = self.resolve_path(file_name)
        with open(file_path, 'rb') as fo:
            ciphertext = fo.read()
        dec = self.decrypt(ciphertext, self.key)
        with open(file_path[:-4], 'wb') as fo:
            fo.write(dec)
        os.remove(file_path)

    def getAllFilesinFolder(self, encrypted):
        source_dir = os.path.join(self.base_dir, "files")
        if not os.path.isdir(source_dir):
            raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

        return [
            entry.path
            for entry in os.scandir(source_dir)
            if entry.is_file()
            and entry.name.casefold().endswith(".enc") == encrypted
        ]

    def encrypt_all_files(self):
        dirs = self.getAllFilesinFolder(encrypted=False)
        for file_name in dirs:
            self.encrypt_file(file_name)
 

    def decrypt_all_files(self):
        dirs = self.getAllFilesinFolder(encrypted=True)
        for file_name in dirs:
            self.decrypt_file(file_name)


key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
enc = Encryptor(key)
data_file = enc.resolve_path("data.txt")
encrypted_data_file = enc.resolve_path("data.txt.enc")
clear = lambda: os.system('cls')

if os.path.isfile(encrypted_data_file):
    for attempt in range(3):
        enc.decrypt_file(encrypted_data_file)
        password = str(input("Enter password: "))
        with open(data_file, "r") as f:
            stored_password = f.read()
        enc.encrypt_file(data_file)
        if stored_password == password:
            break
        if attempt < 2:
            print(f"Incorrect password! You have {2 - attempt} attempt(s) left.")
            time.sleep(2)
        else:
            print("Incorrect Password! You have exceeded the maximum number of attempts. Exiting...")
            time.sleep(2)
            exit()

    while True:
        clear()
        choice = int(input(
            "1. Press '1' to encrypt file.\n2. Press '2' to decrypt file.\n3. Press '3' to Encrypt all files in the directory.\n4. Press '4' to decrypt all files in the directory.\n5. Press '5' to exit.\n"))
        clear()
        if choice == 1:
            enc.encrypt_file(str(input("Enter name of file to encrypt: ")))
        elif choice == 2:
            enc.decrypt_file(str(input("Enter name of file to decrypt: ")))
        elif choice == 3:
            enc.encrypt_all_files()
        elif choice == 4:
            enc.decrypt_all_files()
        elif choice == 5:
            exit()
        else:
            print("Please select a valid option!")

else:
    while True:
        clear()
        password = str(input("Setting up stuff. Enter a password that will be used for decryption: "))
        repassword = str(input("Confirm password: "))
        if password == repassword:
            break
        else:
            print("Passwords Mismatched!")
    f = open(data_file, "w+")
    f.write(password)
    f.close()
    enc.encrypt_file(data_file)
    print("Please restart the program to complete the setup")
    time.sleep(15)

# coding:utf-8

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key, load_der_private_key, load_der_public_key


class RSAEncryptor:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.padding = padding.PKCS1v15()

    def rsa_encrypt(self, biz_content):
        _pub = self.public_key
        if isinstance(biz_content, str):
            biz_content = biz_content.encode('utf-8')

        # 1024bit key
        default_encrypt_length = int(self.public_key.key_size / 8) - 11
        len_content = len(biz_content)
        if len_content < default_encrypt_length:
            return self.public_key.encrypt(biz_content, self.padding)  # base64.b64encode(self.public_key.encrypt(biz_content, _pub))
        offset = 0
        params_lst = []
        while len_content - offset > 0:
            if len_content - offset > default_encrypt_length:
                params_lst.append(self.public_key.encrypt(biz_content[offset:offset + default_encrypt_length], self.padding))
            else:
                params_lst.append(self.public_key.encrypt(biz_content[offset:], self.padding))
            offset += default_encrypt_length
        target = b''.join(params_lst)
        return target  # base64.b64encode(target)

    def rsa_decrypt(self, biz_content):
        _pri = self.private_key
        # biz_content = base64.b64decode(biz_content)
        # 1024bit key
        default_length = int(self.private_key.key_size / 8)
        len_content = len(biz_content)
        if len_content < default_length:
            return self.private_key.decrypt(biz_content, self.padding)
        offset = 0
        params_lst = []
        while len_content - offset > 0:
            if len_content - offset > default_length:
                params_lst.append(self.private_key.decrypt(biz_content[offset: offset + default_length], self.padding))
            else:
                params_lst.append(self.private_key.decrypt(biz_content[offset:], self.padding))
            offset += default_length
        target = b''.join(params_lst)
        return target

    def rsa_signature(self, data):
        signature = self.private_key.sign(data, self.padding, hashes.SHA256())
        return signature

    def rsa_verify(self, signature, message):
        self.public_key.verify(signature, message, self.padding, hashes.SHA256())

    def load_pem_private_key(self, data):
        self.private_key = load_pem_private_key(data, None, default_backend())

    def load_pem_public_key(self, data):
        self.public_key = load_pem_public_key(data, default_backend())

    def load_der_private_key(self, data):
        self.private_key = load_der_private_key(data, None, default_backend())

    def load_der_public_key(self, data):
        self.public_key = load_der_public_key(data, default_backend())

    def dump_der_private_key(self):
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def dump_der_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def dump_pem_private_key(self):
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def dump_pem_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def new_key(self):
        self.private_key = rsa.generate_private_key(65537, 2048, default_backend())
        self.public_key = self.private_key.public_key()

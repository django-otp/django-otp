class DumpEncryption:
    """Byte-wise rotation of given values"""
    ROT_LEN = 3

    @classmethod
    def encrypt(cls, value: bytes):
        # Rotate right
        return value[-cls.ROT_LEN:] + value[:-cls.ROT_LEN]

    @classmethod
    def decrypt(cls, value: bytes):
        print("decrypting")
        # Rotate left
        return value[cls.ROT_LEN:] + value[:cls.ROT_LEN]

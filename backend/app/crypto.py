import base64
import json
import os
import time
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

SECRET_KEY = os.environ.get("QR_SECRET_KEY", "your-256-bit-secret-key-here!!")
SALT = os.environ.get("QR_SALT", "fixed-salt-for-demo")
TOKEN_EXPIRY_DAYS = int(os.environ.get("TOKEN_EXPIRY_DAYS", "365"))


def _get_aes_key() -> bytes:
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT.encode(),
        iterations=100000,
    )
    return kdf.derive(SECRET_KEY.encode())


def encrypt_payload(asset_code: str) -> str:
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    
    payload = {
        "a": asset_code,
        "t": int(time.time()),
        "n": base64.urlsafe_b64encode(os.urandom(6)).decode().rstrip("=")
    }
    
    plaintext = json.dumps(payload).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # HMAC-SHA256 signature
    h = hmac.new(key, ciphertext + nonce, hashlib.sha256)
    sig = h.digest()
    
    # Format: base64url(ciphertext).base64url(tag+sig).base64url(nonce)
    # AES-GCM auth tag is last 16 bytes of ciphertext
    actual_ciphertext = ciphertext[:-16]
    tag = ciphertext[-16:]
    
    ct_b64 = base64.urlsafe_b64encode(actual_ciphertext).decode().rstrip("=")
    tag_sig_b64 = base64.urlsafe_b64encode(tag + sig).decode().rstrip("=")
    nonce_b64 = base64.urlsafe_b64encode(nonce).decode().rstrip("=")
    
    return f"{ct_b64}.{tag_sig_b64}.{nonce_b64}"


def decrypt_payload(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        ct_b64, tag_sig_b64, nonce_b64 = parts
        
        # Pad base64
        def pad_b64(s):
            return s + "=" * (4 - len(s) % 4)
        
        actual_ciphertext = base64.urlsafe_b64decode(pad_b64(ct_b64))
        tag_sig = base64.urlsafe_b64decode(pad_b64(tag_sig_b64))
        nonce = base64.urlsafe_b64decode(pad_b64(nonce_b64))
        
        tag = tag_sig[:16]
        sig = tag_sig[16:]
        
        key = _get_aes_key()
        
        # Verify HMAC
        h = hmac.new(key, actual_ciphertext + tag + nonce, hashlib.sha256)
        expected_sig = h.digest()
        if not hmac.compare_digest(sig, expected_sig):
            raise ValueError("Invalid signature")
        
        # Decrypt AES-GCM
        aesgcm = AESGCM(key)
        ciphertext = actual_ciphertext + tag
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        payload = json.loads(plaintext.decode())
        
        # Check expiry
        now = int(time.time())
        token_time = payload.get("t", 0)
        if now - token_time > TOKEN_EXPIRY_DAYS * 86400:
            raise ValueError("Token expired")
        
        return payload
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")

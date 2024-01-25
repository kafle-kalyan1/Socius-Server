import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from dotenv import load_dotenv
from hashlib import sha256


load_dotenv()

def decrypt_data(encrypted_data):
    secret_key = os.environ.get('SECRET_KEY').encode()
    # Decode the base64 encoded string to bytes 
    encrypted_bytes = base64.b64decode(encrypted_data)  

    cipher = Cipher(algorithms.AES(secret_key), modes.CFB(iv=secret_key), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the bytes     
    decrypted_bytes = decryptor.update(encrypted_bytes) + decryptor.finalize()

    # Decode bytes to string
    decrypted_data = decrypted_bytes.decode('utf-8')

    return decrypted_data
# Example usage in a Django view
def decrypt_view(request):
    if request.method == 'POST':
        secret_key = os.environ.get('SECRET_KEY').encode()
        encrypted_data = request.POST.get('encrypted_data', '')

        # Decrypt the data
        decrypted_data = decrypt_data(encrypted_data)

        if decrypted_data is not None:
            return JsonResponse({'decrypted_data': decrypted_data})
        else:
            return JsonResponse({'error': 'Failed to decrypt data'}, status=500)

    return JsonResponse({'error': 'Invalid request method'})

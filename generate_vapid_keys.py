from py_vapid import Vapid01
import base64

# Generate VAPID keys
vapid = Vapid01()
vapid.generate_keys()

# Get the public key in bytes and encode it in base64 URL-safe format
public_key_bytes = vapid.public_key.public_bytes()
public_key_base64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8')

# Get the private key in bytes and encode it in base64 URL-safe format
private_key_bytes = vapid.private_key.private_bytes()
private_key_base64 = base64.urlsafe_b64encode(private_key_bytes).decode('utf-8')

# Print the base64 encoded keys
print(f"VAPID_PUBLIC_KEY={public_key_base64}")
print(f"VAPID_PRIVATE_KEY={private_key_base64}")

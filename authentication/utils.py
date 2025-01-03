from django.core.signing import Signer, BadSignature


signer = Signer()


def generate_verification_token(name):
    return signer.sign(name)


def verify_token(token):
    print(f"Received Token: {token}") 
    try:
        email = signer.unsign(token)
        print(email)
        return email
    except BadSignature:
        print("BadSignature: Token is invalid or tampered.")
        return None
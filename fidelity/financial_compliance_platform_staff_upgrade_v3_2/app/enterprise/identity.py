"""OIDC/JWKS token verification adapter; configure trusted issuer and audience explicitly."""
import jwt
from jwt import PyJWKClient

class OIDCVerifier:
    def __init__(self, jwks_url: str, issuer: str, audience: str):
        if not jwks_url.startswith("https://"):
            raise ValueError("JWKS URL must use HTTPS")
        self.client = PyJWKClient(jwks_url, cache_keys=True)
        self.issuer, self.audience = issuer, audience
    def verify(self, token: str) -> dict:
        signing_key = self.client.get_signing_key_from_jwt(token)
        return jwt.decode(token, signing_key.key, algorithms=["RS256", "ES256"],
                          issuer=self.issuer, audience=self.audience,
                          options={"require": ["exp", "iat", "iss", "aud", "sub"]})

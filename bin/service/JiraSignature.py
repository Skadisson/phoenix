import base64
import oauth2 as oauth
from tlslite.utils import keyfactory
from bin.service import Environment


class JiraSignature(oauth.SignatureMethod):
    name = 'RSA-SHA1'

    def signing_base(self, request, consumer, token):
        if not hasattr(request, 'normalized_url') or request.normalized_url is None:
            raise ValueError("Base URL for request is not set.")

        sig = (
            oauth.escape(request.method),
            oauth.escape(request.normalized_url),
            oauth.escape(request.get_normalized_parameters()),
        )

        key = '%s&' % oauth.escape(consumer.secret)
        if token:
            key += oauth.escape(token.secret)
        raw = '&'.join(sig)
        raw_utf8 = raw.encode()
        return key, raw_utf8

    def sign(self, request, consumer, token):
        """Builds the base signature string."""
        key, raw = self.signing_base(request, consumer, token)

        env = Environment.Environment()
        absolute_path = env.get_path_private_key()
        with open(absolute_path, 'r') as f:
            data = f.read()
        private_key_string = data.strip()

        private_key = keyfactory.parsePrivateKey(private_key_string)
        signature = private_key.hashAndSign(raw)
        base_signature = base64.b64encode(signature)

        return base_signature

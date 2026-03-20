from OpenSSL import crypto
from os import exists
from os import getenv



def generate_csr():
    if not exists(getenv('CERTIFICATE_KEY')):
        print(f"Certificate key file '{getenv('CERTIFICATE_KEY')}' does not exist.")
        return

    # Load the private key
    with open(getenv('CERTIFICATE_KEY'), 'rb') as key_file:
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_file.read())

    # Create a CSR
    csr = crypto.X509Req()
    csr.get_subject().CN = "Your Common Name"
    csr.set_pubkey(private_key)
    csr.sign(private_key, 'sha256')

    # Save the CSR to a file
    with open('csr.pem', 'wb') as csr_file:
        csr_file.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr))

    print("CSR generated and saved to 'csr.pem'.")


    
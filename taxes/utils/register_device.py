import os
import requests
from loguru import logger
from dotenv import load_dotenv
from loguru import logger
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import os
import sys
from dotenv import load_dotenv  # You may need to install: pip install python-dotenv




load_dotenv('.env.zimra')  # Load ZIMRA specific environment variables

class DeviceRegistraion:
    # This class is responsible for registering the device with the ZIMRA API.
    def __init__(self, serial_number, certificate_path, certificate_key_path):
        self.serial_number = serial_number
        self.certificate_path = certificate_path
        self.certificate_key_path = certificate_key_path
        self.base_url = "https://api.zimra.co.zw/v1/devices/"  # Example URL, replace with actual
    
    def register_device(self):
        # Load the certificate and key
        with open(self.certificate_path, 'rb') as cert_file:
            cert_data = cert_file.read()
        
        with open(self.certificate_key_path, 'rb') as key_file:
            key_data = key_file.read()
        
        # Prepare the registration payload
        payload = {
            "serial_number": self.serial_number,
            "certificate": cert_data.decode('utf-8'),
            "certificate_key": key_data.decode('utf-8')
        }
        
        # Send the registration request to ZIMRA API
        response = requests.post(self.base_url + "register/", json=payload)
        
        if response.status_code == 201:
            print("Device registered successfully.")
            return response.json()  # Return the response data if needed
        else:
            print(f"Failed to register device. Status code: {response.status_code}, Response: {response.text}")
            return None
        
    
    

    def get_device_status(self):
        # This method can be used to check the status of the registered device.
        response = requests.get(self.base_url + f"status/{self.serial_number}/")
        
        if response.status_code == 200:
            print("Device status retrieved successfully.")
            return response.json()  # Return the status data
        else:
            print(f"Failed to retrieve device status. Status code: {response.status_code}, Response: {response.text}")
            return None
        

    


    def load_zimra_config(self, env_file='.env.zimra'):
        """
        Load ZIMRA configuration from .env.zimra file
        
        Expected format:
        DEVICE_ID=42
        DEVICE_SERIAL_NUMBER=0001
        PRIVATE_KEY_PATH=path/to/private.key
        """
        logger.info(f"Loading configuration from {env_file}")
        
        if not os.path.exists(env_file):
            logger.error(f"Configuration file {env_file} not found")
            raise FileNotFoundError(f"Configuration file {env_file} not found")
        
        load_dotenv(env_file)
        
        device_id = os.getenv('DEVICE_ID')
        device_serial = os.getenv('DEVICE_SERIAL_NUMBER')
        private_key_path = os.getenv('PRIVATE_KEY_PATH')
        
        logger.debug(f"Raw values - DEVICE_ID: {device_id}, DEVICE_SERIAL_NUMBER: {device_serial}, PRIVATE_KEY_PATH: {private_key_path}")
        
        if not all([device_id, device_serial, private_key_path]):
            missing = []
            if not device_id: missing.append('DEVICE_ID')
            if not device_serial: missing.append('DEVICE_SERIAL_NUMBER')
            if not private_key_path: missing.append('PRIVATE_KEY_PATH')
            error_msg = f"Missing required environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        config = {
            'device_id': int(device_id),
            'device_serial': device_serial,
            'private_key_path': private_key_path
        }
        
        logger.success(f"Configuration loaded successfully")
        logger.info(f"Device ID: {config['device_id']}")
        logger.info(f"Device Serial: {config['device_serial']}")
        logger.info(f"Private Key Path: {config['private_key_path']}")
        
        return config

    def create_cn_value(self, device_serial, device_id):
        """
        Create Common Name value in the format: ZIMRA-SN{serial}-{10_digit_device_id}
        
        Args:
            device_serial: Device serial number (e.g., "0001")
            device_id: Device ID (integer)
        
        Returns:
            Formatted CN string
        """
        logger.debug(f"Creating CN from serial: {device_serial}, device_id: {device_id}")
        
        # Format device ID as 10 digits with leading zeros
        device_id_formatted = f"{int(device_id):010d}"
        logger.debug(f"Formatted device ID (10 digits): {device_id_formatted}")
        
        # Format serial - ensure it doesn't have leading 'SN' if already present
        original_serial = device_serial
        if device_serial.startswith('SN'):
            device_serial = device_serial[2:]
            logger.debug(f"Removed 'SN' prefix from serial: {original_serial} -> {device_serial}")
        
        # Create CN in required format
        cn_value = f"ZIMRA-SN{device_serial}-{device_id_formatted}"
        
        logger.debug(f"Generated CN: {cn_value}")
        return cn_value

    def load_private_key(self, private_key_path, key_password=None):
        """Load private key from file"""
        logger.info(f"Loading private key from: {private_key_path}")
        
        if not os.path.exists(private_key_path):
            logger.error(f"Private key file not found: {private_key_path}")
            raise FileNotFoundError(f"Private key file not found: {private_key_path}")
        
        with open(private_key_path, 'rb') as key_file:
            private_key_data = key_file.read()
        
        # Try to load as PEM
        try:
            password = key_password.encode() if key_password else None
            private_key = load_pem_private_key(private_key_data, password=password)
            logger.debug("Successfully loaded PEM private key")
        except Exception as pem_error:
            logger.debug(f"Failed to load as PEM: {pem_error}")
            # Try as DER
            try:
                password = key_password.encode() if key_password else None
                private_key = serialization.load_der_private_key(private_key_data, password=password)
                logger.debug("Successfully loaded DER private key")
            except Exception as der_error:
                logger.error(f"Failed to load private key as PEM or DER: {der_error}")
                raise ValueError("Unable to load private key. Check format and password.")
        
        # Determine key type
        if isinstance(private_key, ec.EllipticCurvePrivateKey):
            key_type = "ECC"
            curve_name = private_key.curve.name
            logger.info(f"Loaded {key_type} private key (curve: {curve_name})")
        elif isinstance(private_key, rsa.RSAPrivateKey):
            key_type = "RSA"
            key_size = private_key.key_size
            logger.info(f"Loaded {key_type} private key (size: {key_size} bits)")
        else:
            key_type = "Unknown"
            logger.warning(f"Loaded private key of unknown type: {type(private_key)}")
        
        return private_key, key_type

    def create_zimra_csr(self, private_key_path, device_serial, device_id, key_password=None):
        """
        Create ZIMRA CSR with proper CN format from .env.zimra values
        """
        logger.info("Starting CSR generation")
        
        # Load the private key
        private_key, key_type = self.load_private_key(private_key_path, key_password)
        
        # Create the Common Name with proper format
        cn_value = self.create_cn_value(device_serial, device_id)
        logger.info(f"CSR Common Name: {cn_value}")
        
        # Build the subject
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ZW"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Zimbabwe Revenue Authority"),
            x509.NameAttribute(NameOID.COMMON_NAME, cn_value),
        ])
        
        logger.debug(f"Subject: {subject.rfc4514_string()}")
        
        # Start building CSR
        csr_builder = x509.CertificateSigningRequestBuilder().subject_name(subject)
        
        # Add Key Usage extension based on key type
        logger.debug(f"Adding Key Usage extension for {key_type} key")
        if isinstance(private_key, ec.EllipticCurvePrivateKey):
            # For ECC keys
            key_usage = x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            )
            logger.debug("ECC Key Usage: digital_signature only")
        else:
            # For RSA keys
            key_usage = x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            )
            logger.debug("RSA Key Usage: digital_signature, content_commitment, key_encipherment")
        
        csr_builder = csr_builder.add_extension(key_usage, critical=True)
        
        # Add Extended Key Usage for Client Authentication
        logger.debug("Adding Extended Key Usage: Client Authentication")
        csr_builder = csr_builder.add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=False
        )
        
        # Add Basic Constraints
        logger.debug("Adding Basic Constraints: CA=FALSE")
        csr_builder = csr_builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        )
        
        # Sign the CSR
        logger.info("Signing CSR with SHA-256")
        csr = csr_builder.sign(private_key, hashes.SHA256())
        
        logger.success("CSR generated successfully")
        return csr, cn_value

    def verify_csr_format(self, csr, expected_cn):
        """Verify the CSR has the correct format"""
        
        logger.info("Starting CSR verification")
        
        # Get subject components
        subject_dict = {}
        for attr in csr.subject:
            subject_dict[attr.oid._name] = attr.value
        
        logger.debug(f"Subject fields found: {subject_dict}")
        
        # Log all subject fields
        logger.info("Subject Fields Found:")
        for field, value in subject_dict.items():
            logger.info(f"  └─ {field}: {value}")
        
        verification_results = []
        
        # Verify Country
        if subject_dict.get('countryName') == 'ZW':
            logger.success("✓ Country: ZW")
            verification_results.append(("Country", True, "ZW"))
        else:
            logger.error(f"✗ Country should be 'ZW', found: {subject_dict.get('countryName')}")
            verification_results.append(("Country", False, subject_dict.get('countryName')))
        
        # Verify Organization
        if subject_dict.get('organizationName') == 'Zimbabwe Revenue Authority':
            logger.success("✓ Organization: Zimbabwe Revenue Authority")
            verification_results.append(("Organization", True, "Zimbabwe Revenue Authority"))
        else:
            logger.error(f"✗ Organization should be 'Zimbabwe Revenue Authority', found: {subject_dict.get('organizationName')}")
            verification_results.append(("Organization", False, subject_dict.get('organizationName')))
        
        # Verify Common Name
        actual_cn = subject_dict.get('commonName')
        if actual_cn == expected_cn:
            logger.success(f"Common Name: {actual_cn}")
            verification_results.append(("Common Name", True, actual_cn))
            
            # Parse components
            parts = actual_cn.split('-')
            if len(parts) == 3:
                serial_part = parts[1]  # SN0001
                device_id_part = parts[2]  # 0000000042
                
                logger.info(f"   ├─ Serial: {serial_part}")
                logger.info(f"   └─ Device ID: {device_id_part} (numeric: {int(device_id_part)})")
        else:
            logger.error(f"✗ Common Name mismatch")
            logger.error(f"   Expected: {expected_cn}")
            logger.error(f"   Found: {actual_cn}")
            verification_results.append(("Common Name", False, actual_cn))
        
        # Check extensions
        logger.info("Extensions:")
        for ext in csr.extensions:
            critical = "critical" if ext.critical else "non-critical"
            logger.info(f"  └─ {ext.oid._name} ({critical})")
            
            # Log specific extension details
            if ext.oid._name == 'keyUsage':
                ku = ext.value
                logger.debug(f"     Digital Signature: {ku.digital_signature}")
                logger.debug(f"     Content Commitment: {ku.content_commitment}")
                logger.debug(f"     Key Encipherment: {ku.key_encipherment}")
            elif ext.oid._name == 'extendedKeyUsage':
                eku = ext.value
                for usage in eku:
                    logger.debug(f"     {usage._name}")
        
        # Summary
        logger.info("Verification Summary:")
        all_valid = all(result[1] for result in verification_results)
        for field, valid, value in verification_results:
            status = "✅" if valid else "❌"
            logger.info(f"  {status} {field}: {value}")
        
        if all_valid:
            logger.success("✓ CSR appears valid for ZIMRA registration")
        else:
            logger.warning("⚠ CSR has issues that need to be fixed")
        
        return all_valid

    def save_csr(self, csr, output_path):
        """Save CSR to file"""
        logger.info(f"Saving CSR to: {output_path}")
        
        with open(output_path, 'wb') as f:
            f.write(csr.public_bytes(serialization.Encoding.PEM))
        
        # Verify file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.success(f"CSR saved successfully ({file_size} bytes)")
        else:
            logger.error(f"Failed to save CSR to {output_path}")
            raise IOError(f"Failed to save CSR to {output_path}")

    def display_csr(self, csr):
        """Display CSR in PEM format"""
        logger.info("CSR PEM Format:")
        pem_data = csr.public_bytes(serialization.Encoding.PEM).decode()
        for line in pem_data.split('\n'):
            if line:
                logger.info(line)

    # Main execution
    if __name__ == "__main__":
        logger.info("=" * 60)
        logger.info("ZIMRA CSR GENERATION TOOL")
        logger.info("=" * 60)
        
        try:
            # Load configuration from .env.zimra
            config = load_zimra_config('.env.zimra')
            
            # Ask for key password if needed
            key_password = None
            password_required = input("\n🔐 Is your private key encrypted? (y/n): ").lower().strip()
            if password_required == 'y':
                import getpass
                key_password = getpass.getpass("Enter private key password: ")
                logger.debug("Password provided (hidden)")
            
            # Create CSR
            logger.info("Starting CSR generation process")
            csr, cn_value = create_zimra_csr(
                config['private_key_path'],
                config['device_serial'],
                config['device_id'],
                key_password
            )
            
            # Verify CSR
            is_valid = verify_csr_format(csr, cn_value)
            
            # Save CSR
            output_file = f"zimra_device_{config['device_id']}.csr"
            save_csr(csr, output_file)
            
            # Display CSR
            logger.info("=" * 60)
            display_csr(csr)
            logger.info("=" * 60)
            
            if is_valid:

                logger.success("🎉 CSR generation completed successfully!")
                logger.info(f"📁 Output file: {output_file}")
                logger.info("📤 Use this CSR in the registerDevice API call")

            else:
                logger.warning("⚠ CSR generated but verification found issues")
                logger.info("Please review the warnings above before using this CSR")
            
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            sys.exit(1)

        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            sys.exit(1)
        

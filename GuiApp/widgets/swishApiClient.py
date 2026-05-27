"""Swish API client for creating payment requests, generating QR codes,
polling payment status, and cancelling payments.

Ref: https://developer.swish.nu/api
"""

import io
import os
import platform
import tempfile
import uuid

import requests
from qrcode import make as makeQRCode
from requests.exceptions import RequestException


class SwishApiError(Exception):
    """Raised when the Swish API returns an error response."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


# pylint: disable=import-outside-toplevel,too-many-return-statements,too-many-branches,broad-exception-caught


class SwishApiClient:
    """HTTP client for the Swish Merchant API.

    Uses client certificate authentication (PKCS#12 .p12 or PEM file).

    If a .p12 file is provided, the certificate and key are extracted
    using the cryptography library.  The extracted PEM data is written
    to temporary files that are deleted when the client is destroyed.

    API endpoints:
    - Create payment: PUT /api/v2/paymentrequests/{uuid}
    - QR code:       POST /api/v1/commerce
    - Status:        GET  /api/v1/paymentrequests/{id}
    - Cancel:        PATCH /api/v1/paymentrequests/{id}
    """

    CERT_DIR = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "payment_certificates"
    )

    @staticmethod
    def set_cert_dir(path: str):
        """Set the path to the payment certificate directory."""
        SwishApiClient.CERT_DIR = path

    @staticmethod
    def _get_search_dirs() -> list:
        """Return a list of directories to search for certificates.

        Includes the static CERT_DIR plus any connected USB drives.
        """
        dirs = []
        if SwishApiClient.CERT_DIR:
            dirs.append(SwishApiClient.CERT_DIR)

        system = platform.system()
        if system == "Linux":
            # Raspberry Pi OS auto-mounts under /media/pi/<label>
            pi_media = "/media/pi"
            if os.path.isdir(pi_media):
                for label in os.listdir(pi_media):
                    mount = os.path.join(pi_media, label)
                    if os.path.isdir(mount):
                        dirs.append(mount)
            # Also check /mnt
            if os.path.isdir("/mnt"):
                for label in os.listdir("/mnt"):
                    mount = os.path.join("/mnt", label)
                    if os.path.isdir(mount):
                        dirs.append(mount)
        elif system == "Windows":
            # Check all drive letters for removable media
            import string

            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.isdir(drive):
                    from ctypes import windll

                    drive_type = windll.kernel32.GetDriveTypeW(drive)
                    # DRIVE_REMOVABLE = 2, DRIVE_FIXED = 3 (only USB)
                    if drive_type == 2:
                        dirs.append(drive)

        return dirs

    @staticmethod
    def _scan_directory(directory: str) -> dict:
        """Scan a single directory for Swish certificate files.

        Returns the same dict format as detect_certificates(), or
        an empty dict if nothing was found.
        """
        result: dict = {}
        if not os.path.isdir(directory):
            return result

        files = os.listdir(directory)
        p12_files = [f for f in files if f.endswith(".p12")]
        pem_files = [f for f in files if f.endswith(".pem")]
        key_files = {f for f in files if f.endswith(".key")}

        # Look for a .p12 file
        if p12_files:
            result["cert_path"] = os.path.join(directory, p12_files[0])

        # Otherwise look for a .pem with matching .key
        if "cert_path" not in result:
            for pem in pem_files:
                base = os.path.splitext(pem)[0]
                key_name = f"{base}.key"
                if key_name in key_files:
                    result["cert_path"] = os.path.join(directory, pem)
                    result["key_path"] = os.path.join(directory, key_name)
                    break

        # CA cert — look for the standard name, or any other .pem
        ca_candidates = [f for f in pem_files if "root" in f.lower()]
        if not ca_candidates:
            ca_candidates = [
                f for f in pem_files if f not in (result.get("cert_path") or "")
            ]
        if ca_candidates:
            result["ca_cert_path"] = os.path.join(directory, ca_candidates[0])

        if "cert_path" not in result:
            return {}  # No cert found in this directory

        # Extract the Swish number from the certificate's Common Name
        swish_number = None
        try:
            swish_number = SwishApiClient._extract_swish_number(result["cert_path"])
        except Exception as exc:
            print(f"Could not extract Swish number from cert: {exc}")
        if not swish_number:
            basename = os.path.basename(result["cert_path"])
            import re

            match = re.search(r"(\d{10,15})", basename)
            if match:
                swish_number = match.group(1)
        if swish_number:
            result["payee_alias"] = swish_number

        return result

    @staticmethod
    def detect_certificates() -> dict:
        """Scan all known locations for Swish certificate files.

        Searches the static payment_certificates/ folder first, then
        any connected USB drives (auto-mounted on Raspberry Pi or
        removable drives on Windows).  Returns the first directory
        where certificates are found.

        Returns a dict with keys (all optional): cert_path, key_path,
        ca_cert_path, payee_alias.
        """
        for directory in SwishApiClient._get_search_dirs():
            result = SwishApiClient._scan_directory(directory)
            if result.get("cert_path"):
                return result
        return {}

    @staticmethod
    def _extract_swish_number(cert_path: str) -> str:
        """Read a .p12 or .pem certificate and return the Swish number
        from its Common Name (CN).

        For .p12 files this will fail without the correct password, so
        callers should fall back to filename-based extraction.
        """
        from cryptography import x509
        from cryptography.hazmat.primitives.serialization import (
            pkcs12,
        )

        if cert_path.endswith(".p12"):
            # Try with empty password — will fail for most .p12 files
            with open(cert_path, "rb") as f:
                p12_data = f.read()
            try:
                _, cert, _ = pkcs12.load_key_and_certificates(p12_data, b"")
            except Exception:
                # Password required; raise so caller can fall back
                raise ValueError("Cannot extract CN from .p12 without password")
        else:
            with open(cert_path, "rb") as f:
                cert_pem = f.read()
            cert = x509.load_pem_x509_certificate(cert_pem)

        cn_attributes = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        if cn_attributes:
            return cn_attributes[0].value
        return ""

    def __init__(
        self,
        base_url: str,
        cert_path: str,
        cert_password: str,
        ca_cert_path: str,
        payee_alias: str,
    ):
        """Initialise the client.

        Args:
            base_url: Swish API base URL.
            cert_path: Path to .p12, .pem, or .crt client certificate file.
            cert_password: Password for the .p12 certificate.
            ca_cert_path: Path to the CA certificate (.pem) file.
            payee_alias: The payee's Swish number.
        """
        self.base_url = base_url.rstrip("/")
        self.payee_alias = payee_alias
        self.ca_cert = ca_cert_path
        self._created_temp = False

        if cert_path.endswith(".p12"):
            self._cert_path, self._key_path = self._extract_p12(
                cert_path, cert_password
            )
        elif cert_path.endswith((".pem", ".crt", ".cert")):
            # Look for a matching .key file alongside the cert
            base, _ = os.path.splitext(cert_path)
            key_path = base + ".key"
            if os.path.isfile(key_path):
                self._key_path = key_path
            else:
                self._key_path = None
            self._cert_path = cert_path
        else:
            self._cert_path = cert_path
            self._key_path = None

    def _extract_p12(self, p12_path: str, password: str):
        """Extract certificate and key from a PKCS#12 file into PEM temp files."""
        from cryptography.hazmat.primitives.serialization import (
            Encoding,
            NoEncryption,
            PrivateFormat,
            pkcs12,
        )

        with open(p12_path, "rb") as f:
            p12_data = f.read()

        private_key, certificate, _ = pkcs12.load_key_and_certificates(
            p12_data, password.encode()
        )

        cert_pem = certificate.public_bytes(Encoding.PEM)
        key_pem = private_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.PKCS8,
            NoEncryption(),
        )

        # Write PEM data to temporary files (deleted on close)
        cert_file = tempfile.NamedTemporaryFile(suffix=".pem", delete=False)
        key_file = tempfile.NamedTemporaryFile(suffix=".pem", delete=False)

        cert_file.write(cert_pem)
        cert_file.close()
        key_file.write(key_pem)
        key_file.close()

        self._created_temp = True
        return cert_file.name, key_file.name

    def __del__(self):
        """Clean up temporary PEM files created from .p12 extraction."""
        if self._created_temp:
            for path in (self._cert_path, self._key_path):
                if path and os.path.exists(path):
                    os.unlink(path)

    def _make_request(
        self,
        method: str,
        path: str,
        body: dict = None,
        extra_headers: dict = None,
    ) -> requests.Response:
        """Send an HTTPS request to the Swish API with certificate auth."""
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        if extra_headers:
            headers.update(extra_headers)

        cert_arg = self._cert_path
        if self._key_path:
            cert_arg = (self._cert_path, self._key_path)

        # Determine CA verification.  If a path is provided and exists,
        # try using it; on SSL failure fall back to no-verification
        # (common in the Swish test/MSS environment).
        verify_ca = True
        if self.ca_cert and os.path.isfile(self.ca_cert):
            verify_ca = self.ca_cert

        # Suppress insecure-request warnings (acceptable for testing)
        try:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except ImportError:
            pass

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body,
                cert=cert_arg,
                verify=verify_ca,
                timeout=30,
            )
        except requests.exceptions.SSLError as exc:
            if verify_ca is not False and verify_ca is not True:
                print(
                    f"SSL verification failed with CA cert "
                    f"'{verify_ca}', retrying without verification. "
                    f"Error: {exc}"
                )
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body,
                    cert=cert_arg,
                    verify=False,
                    timeout=30,
                )
            else:
                raise SwishApiError(f"SSL error: {exc}") from exc
        except RequestException as exc:
            raise SwishApiError(f"Network error: {exc}") from exc

        if response.status_code >= 400:
            raise SwishApiError(
                f"Swish API returned {response.status_code}: " f"{response.text}",
                status_code=response.status_code,
            )

        return response

    def create_payment_request(
        self,
        amount: float,
        currency: str = "SEK",
        message: str = "",
        payee_payment_reference: str = "",
    ) -> dict:
        """Create a Swish payment request (PUT /v2/paymentrequests/{uuid}).

        Args:
            amount: Payment amount (e.g. 100.00).
            currency: ISO 4217 currency code (only SEK supported).
            message: Optional message (max 50 chars).
            payee_payment_reference: Optional merchant reference (max 35 chars).

        Returns:
            dict with keys: id, token, location_url.

        Raises:
            SwishApiError: On API or network errors.
        """
        instruction_uuid = uuid.uuid4().hex.upper()  # 32-char hex
        path = f"/swish-cpcapi/api/v2/paymentrequests/{instruction_uuid}"
        body = {
            "payeeAlias": self.payee_alias,
            "amount": amount,
            "currency": currency,
            "callbackUrl": "https://not-used.local/",  # Required but unused
            "message": message[:50] if message else "",
        }
        if payee_payment_reference:
            body["payeePaymentReference"] = payee_payment_reference[:35]

        response = self._make_request("PUT", path, body)
        location = response.headers.get("Location", "")
        token = response.headers.get("PaymentRequestToken", "")

        # Strip base URL to get the relative ID
        payment_id = location.rsplit("/", 1)[-1] if location else instruction_uuid

        return {
            "id": payment_id,
            "token": token,
            "location_url": location,
        }

    def get_qr_code(
        self,
        token: str,
        fmt: str = "png",
        size: int = 300,
    ) -> bytes:
        """Generate a QR code image from a payment request token.

        POST /qrg-swish/api/v1/commerce

        Falls back to local QR generation when the API endpoint is
        unavailable (e.g. in the MSS test environment).

        Args:
            token: The PaymentRequestToken from create_payment_request.
            fmt: Image format — "png", "jpg", or "svg".
            size: Size of the QR code in pixels (square).

        Returns:
            Raw image bytes (PNG).

        Raises:
            SwishApiError: On API or network errors (only when the API
                           was reachable but returned an error).
        """
        # First try the API endpoint
        try:
            return self._get_qr_from_api(token, fmt, size)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.SSLError,
            SwishApiError,
        ) as exc:
            print(
                f"QR API unavailable ({exc}), " f"falling back to local QR generation"
            )

        # Fallback: generate QR locally using the m-commerce token
        # format (token prefixed with "D")
        qr_content = f"D{token}"
        qr_img = makeQRCode(qr_content)
        qr_bytes = io.BytesIO()
        qr_img.save(qr_bytes, format="PNG")
        return qr_bytes.getvalue()

    def _get_qr_from_api(
        self,
        token: str,
        fmt: str = "png",
        size: int = 300,
    ) -> bytes:
        """Fetch a QR code image from the Swish API commerce endpoint."""
        commerce_url = f"{self.base_url}/qrg-swish/api/v1/commerce"
        headers = {"Content-Type": "application/json"}
        body = {"format": fmt, "size": size, "token": token}

        cert_arg = self._cert_path
        if self._key_path:
            cert_arg = (self._cert_path, self._key_path)

        verify_ca = True
        if self.ca_cert and os.path.isfile(self.ca_cert):
            verify_ca = self.ca_cert

        try:
            response = requests.request(
                method="POST",
                url=commerce_url,
                headers=headers,
                json=body,
                cert=cert_arg,
                verify=verify_ca,
                timeout=30,
            )
        except requests.exceptions.SSLError as exc:
            if verify_ca is not False and verify_ca is not True:
                print(
                    f"SSL verification failed for QR endpoint, "
                    f"retrying without verification. Error: {exc}"
                )
                response = requests.request(
                    method="POST",
                    url=commerce_url,
                    headers=headers,
                    json=body,
                    cert=cert_arg,
                    verify=False,
                    timeout=30,
                )
            else:
                raise

        if response.status_code != 201:
            raise SwishApiError(
                f"QR code generation failed ({response.status_code}): "
                f"{response.text}",
                status_code=response.status_code,
            )

        return response.content

    def get_payment_status(self, payment_id: str) -> dict:
        """Retrieve the current status of a payment request.

        GET /api/v1/paymentrequests/{id}

        Args:
            payment_id: The payment request ID.

        Returns:
            dict with keys including status, amount, paymentReference,
            errorCode, errorMessage, datePaid.

        Raises:
            SwishApiError: On API or network errors.
        """
        path = f"/swish-cpcapi/api/v1/paymentrequests/{payment_id}"
        response = self._make_request("GET", path)
        return response.json()

    def cancel_payment_request(self, payment_id: str) -> dict:
        """Cancel an outstanding payment request.

        PATCH /api/v1/paymentrequests/{id}

        Args:
            payment_id: The payment request ID.

        Returns:
            The updated payment request object with status "CANCELLED".

        Raises:
            SwishApiError: On API or network errors.
        """
        path = f"/swish-cpcapi/api/v1/paymentrequests/{payment_id}"
        body = [{"op": "replace", "path": "/status", "value": "cancelled"}]
        headers = {"Content-Type": "application/json-patch+json"}
        response = self._make_request("PATCH", path, body=body, extra_headers=headers)
        return response.json()

    @staticmethod
    def test_connection(
        base_url: str = "",
        cert_path: str = "",
        cert_password: str = "",
        ca_cert_path: str = "",
        payee_alias: str = "",
    ) -> str:
        """Quick connectivity test — tries to contact the Swish API.

        Builds a temporary client from the provided parameters (or
        auto-detected certs if omitted), then attempts a harmless GET
        to the payment-requests endpoint with a fake ID.  A 404
        response means the TLS handshake and authentication worked;
        anything else indicates a problem.

        Returns a human-readable status string.
        """
        # Auto-detect if no explicit cert given
        if not cert_path:
            detected = SwishApiClient.detect_certificates()
            cert_path = detected.get("cert_path", "")
            ca_cert_path = detected.get("ca_cert_path", ca_cert_path)
            if not payee_alias:
                payee_alias = detected.get("payee_alias", "")

        if not cert_path:
            return "No certificates found"

        if not payee_alias:
            return "Cannot read Swish# from certificate"

        try:
            client = SwishApiClient(
                base_url=base_url,
                cert_path=cert_path,
                cert_password=cert_password,
                ca_cert_path=ca_cert_path,
                payee_alias=payee_alias,
            )
            # Try to retrieve a non-existent payment request — 404 means
            # the API is reachable and the cert is accepted
            fake_id = "00000000000000000000000000000000"
            client.get_payment_status(fake_id)
            # If we get here without exception, something unexpected happened
            return "Unexpected response"
        except SwishApiError as exc:
            if exc.status_code == 404:
                return "Connected"
            if exc.status_code == 401:
                return "Certificate rejected"
            return f"HTTP {exc.status_code}"
        except Exception as exc:
            msg = str(exc)
            if "CERTIFICATE_VERIFY_FAILED" in msg:
                return "CA cert verification failed"
            if "DECRYPTION_FAILED" in msg or "bad record mac" in msg:
                return "Certificate rejected"
            if "ConnectionError" in msg or "Connection refused" in msg:
                return "Cannot reach server"
            if "Timeout" in msg:
                return "Connection timed out"
            if "Permission denied" in msg:
                return "Cannot read certificate"
            if "No such file" in msg or "No such device" in msg:
                return "Certificate file not found"
            if "nodename nor servname" in msg or "Name or service not known" in msg:
                return "Unknown host"
            return "Unknown error"

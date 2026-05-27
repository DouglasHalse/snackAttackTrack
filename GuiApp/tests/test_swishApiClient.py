"""Unit tests for the Swish API client (mocked HTTP)."""

from unittest.mock import MagicMock, patch

import pytest

from GuiApp.widgets.swishApiClient import SwishApiClient, SwishApiError

# pylint: disable=redefined-outer-name


@pytest.fixture
def client():
    return SwishApiClient(
        base_url="https://mss.cpc.getswish.net",
        cert_path="/fake/cert.pem",
        cert_password="swish",
        ca_cert_path="/fake/ca.pem",
        payee_alias="1234679304",
    )


# --- create_payment_request ---


class TestCreatePaymentRequest:
    def test_success(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.headers = {
            "Location": (
                "https://mss.cpc.getswish.net/swish-cpcapi/api/v1/"
                "paymentrequests/ABCD1234"
            ),
            "PaymentRequestToken": "tok_abc",
        }

        with patch(
            "GuiApp.widgets.swishApiClient.requests.request", return_value=mock_resp
        ) as mock_req:
            result = client.create_payment_request(amount=100.0)

        assert result["id"] == "ABCD1234"
        assert result["token"] == "tok_abc"
        mock_req.assert_called_once()

    def test_api_error(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "Bad request"

        with patch(
            "GuiApp.widgets.swishApiClient.requests.request", return_value=mock_resp
        ):
            with pytest.raises(SwishApiError) as exc:
                client.create_payment_request(amount=100.0)

        assert "400" in str(exc.value)


# --- get_qr_code ---


class TestGetQrCode:
    def test_success(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.content = b"<png data>"

        with patch(
            "GuiApp.widgets.swishApiClient.requests.request", return_value=mock_resp
        ):
            result = client.get_qr_code("tok_abc")

        assert result == b"<png data>"

    def test_api_failure_falls_back_to_local_qr(self, client):
        """When the QR API fails, the client generates the QR locally."""
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal error"

        with patch(
            "GuiApp.widgets.swishApiClient.requests.request", return_value=mock_resp
        ):
            result = client.get_qr_code("tok_abc")

        # Should return local QR bytes instead of raising
        assert isinstance(result, bytes)
        # PNG header starts with 89 50 4E 47
        assert result[:4] == b"\x89PNG"


# --- get_payment_status ---


class TestGetPaymentStatus:
    def test_paid(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "ABCD1234", "status": "PAID"}

        with patch(
            "GuiApp.widgets.swishApiClient.requests.request", return_value=mock_resp
        ):
            result = client.get_payment_status("ABCD1234")

        assert result["status"] == "PAID"

    def test_declined(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "ABCD1234", "status": "DECLINED"}

        with patch(
            "GuiApp.widgets.swishApiClient.requests.request", return_value=mock_resp
        ):
            result = client.get_payment_status("ABCD1234")

        assert result["status"] == "DECLINED"


# --- cancel_payment_request ---


class TestCancelPaymentRequest:
    def test_success(self, client):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "ABCD1234", "status": "CANCELLED"}

        with patch(
            "GuiApp.widgets.swishApiClient.requests.request", return_value=mock_resp
        ):
            result = client.cancel_payment_request("ABCD1234")

        assert result["status"] == "CANCELLED"

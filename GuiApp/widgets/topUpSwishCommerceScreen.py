"""Top-up payment screen using the Swish Commerce API.

After the user enters an amount, this screen:
1. Creates a Swish payment request via the API
2. Fetches a QR code from the payment token
3. Polls for payment status
4. Auto-credits the user when the payment is confirmed (PAID)
"""

import threading
import traceback
from datetime import datetime

from kivy.clock import Clock

from app_types import Credits, UserData
from widgets.GridLayoutScreen import GridLayoutScreen
from widgets.popups.creditsAnimationPopup import CreditsAnimationPopup
from widgets.popups.errorMessagePopup import ErrorMessagePopup
from widgets.settingsManager import SettingName
from widgets.swishApiClient import SwishApiClient, SwishApiError


class TopUpSwishCommerceScreen(GridLayoutScreen):
    """API-driven top-up screen for the Swish Commerce payment method."""

    POLL_INTERVAL = 3.0  # seconds between status checks
    POLL_TIMEOUT = 120.0  # maximum seconds to wait for payment

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._api_client: SwishApiClient = None
        self._payment_id: str = None
        self._poll_event = None
        self._poll_started = 0.0
        self.userData: UserData = None
        self.amount_to_be_payed: Credits = None
        self.ids.header.bind(on_back_button_pressed=self.on_back)

    def setAmountToBePayed(self, amount: Credits):
        assert isinstance(amount, Credits)
        self.amount_to_be_payed = amount

    # ------------------------------------------------------------------
    #  Lifecycle
    # ------------------------------------------------------------------

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.userData = self.manager.getCurrentPatron()
        self._start_payment_flow()

    def on_leave(self, *args):
        self._stop_polling()
        return super().on_leave(*args)

    # ------------------------------------------------------------------
    #  Payment flow
    # ------------------------------------------------------------------

    def _start_payment_flow(self):
        """Kick off the API-driven payment flow in a background thread."""
        self._show_state("loading")

        def run():
            try:
                client = self._build_api_client()
                result = client.create_payment_request(
                    amount=float(self.amount_to_be_payed),
                    message=(f"Snack Attack Top-up " f"{self.userData.firstName[:20]}"),
                )
                # Fetch QR code on the main thread (needs Kivy context)
                Clock.schedule_once(
                    lambda dt: self._on_payment_created(client, result), 0
                )
            except Exception as exc:
                traceback.print_exc()
                error_msg = str(exc).split("\n", maxsplit=1)[0][:120]
                Clock.schedule_once(lambda dt: self._show_error(error_msg), 0)

        threading.Thread(target=run, daemon=True).start()

    def _on_payment_created(self, client: SwishApiClient, result: dict):
        """Called on the main thread after the payment request is created."""
        self._api_client = client
        self._payment_id = result["id"]
        token = result["token"]

        if not token:
            self._show_error("Swish API did not return a payment token.")
            return

        # Fetch QR code in background
        def fetch_qr():
            try:
                qr_bytes = client.get_qr_code(token)
                Clock.schedule_once(lambda dt: self._show_qr_code(qr_bytes), 0)
            except Exception as exc:
                traceback.print_exc()
                error_msg = str(exc).split("\n", maxsplit=1)[0][:120]
                Clock.schedule_once(lambda dt: self._show_error(error_msg), 0)

        threading.Thread(target=fetch_qr, daemon=True).start()

    def _show_qr_code(self, qr_bytes: bytes):
        """Display the QR code and start polling."""
        # Save QR to a file (Kivy Image can't load from bytes directly)
        qr_path = "qr_online.png"
        with open(qr_path, "wb") as f:
            f.write(qr_bytes)

        self.ids.qrCodeImage.source = qr_path
        self.ids.qrCodeImage.reload()
        self._show_state("waiting")
        self._start_polling()

    # ------------------------------------------------------------------
    #  Polling
    # ------------------------------------------------------------------

    def _start_polling(self):
        self._poll_started = Clock.get_boottime()
        self._poll_event = Clock.schedule_interval(
            self._check_payment_status, self.POLL_INTERVAL
        )

    def _stop_polling(self):
        if self._poll_event:
            Clock.unschedule(self._poll_event)
            self._poll_event = None

    def _check_payment_status(self, dt):
        """Called every POLL_INTERVAL seconds to check payment status."""
        elapsed = Clock.get_boottime() - self._poll_started
        if elapsed > self.POLL_TIMEOUT:
            self._stop_polling()
            self._show_error("Payment timed out. Please try again.")
            return

        def poll():
            try:
                status = self._api_client.get_payment_status(self._payment_id)
                Clock.schedule_once(lambda dt: self._handle_status(status), 0)
            except Exception as exc:
                traceback.print_exc()
                error_msg = str(exc).split("\n", maxsplit=1)[0][:120]
                Clock.schedule_once(lambda dt: self._show_error(error_msg), 0)

        threading.Thread(target=poll, daemon=True).start()

    def _handle_status(self, status: dict):
        """Process the payment status response."""
        state = status.get("status", "")

        if state == "PAID":
            self._stop_polling()
            self._complete_payment()
        elif state in ("DECLINED", "ERROR", "CANCELLED"):
            self._stop_polling()
            error_code = status.get("errorCode", "")
            error_msg = status.get("errorMessage", "")
            self._show_error(
                f"Payment {state.lower()}."
                + (f" ({error_code}: {error_msg})" if error_code else "")
            )
        # else: still CREATED / pending — keep polling

    # ------------------------------------------------------------------
    #  Completion & error
    # ------------------------------------------------------------------

    def _complete_payment(self):
        """Add credits and navigate back."""
        self._show_state("success")

        self.manager.database.addTopUpTransaction(
            patronID=self.userData.patronId,
            amountBeforeTransaction=self.userData.totalCredits,
            amountAfterTransaction=(
                self.userData.totalCredits + self.amount_to_be_payed
            ),
            transactionDate=datetime.now(),
        )
        self.manager.database.addCredits(
            self.userData.patronId, self.amount_to_be_payed
        )

        self.manager.refreshCurrentPatron()

        CreditsAnimationPopup(
            title="Thank you for your top-up!",
            creditsBefore=self.userData.totalCredits,
            creditsAfter=(self.userData.totalCredits + self.amount_to_be_payed),
        ).open()

        self.manager.transition_back_from_top_up()

    def _show_error(self, message: str):
        """Stop and display an error message."""
        print(f"Swish Online Error: {message}")
        self._stop_polling()
        self._show_state("error")
        ErrorMessagePopup(errorMessage=message).open()

    # ------------------------------------------------------------------
    #  Navigation
    # ------------------------------------------------------------------

    def on_back(self, _):
        self._cancel_payment()
        self.manager.transitionToScreen(
            "topUpAmountScreen", transitionDirection="right"
        )

    def onCancel(self, *largs):
        self._cancel_payment()
        self.manager.transition_back_from_top_up()

    def _cancel_payment(self):
        """Attempt to cancel the payment request on Swish."""
        if not self._api_client or not self._payment_id:
            return
        try:
            self._api_client.cancel_payment_request(self._payment_id)
        except SwishApiError:
            pass  # Best-effort cancel; ignore errors

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------

    def _build_api_client(self) -> SwishApiClient:
        """Create a SwishApiClient from auto-detected certificates in the
        payment_certificates/ folder and the configured API base URL."""
        sm = self.manager.settingsManager

        base_url = sm.get_setting_value(settingName=SettingName.SWISH_API_BASE_URL)
        payee_alias = sm.get_setting_value(settingName=SettingName.PAYMENT_SWISH_NUMBER)

        # Auto-detect certificate files from payment_certificates/
        detected = SwishApiClient.detect_certificates()
        cert_path = detected.get("cert_path", "")
        ca_cert_path = detected.get("ca_cert_path", "")
        if not payee_alias:
            payee_alias = detected.get("payee_alias", "")

        if not cert_path:
            raise SwishApiError(
                "No Swish certificate found. "
                "Place your .p12 or .pem+.key files in "
                "GuiApp/payment_certificates/."
            )

        return SwishApiClient(
            base_url=base_url,
            cert_path=cert_path,
            cert_password="",
            ca_cert_path=ca_cert_path,
            payee_alias=payee_alias,
        )

    def _show_state(self, state: str):
        """Update the UI to reflect the current flow state.

        States: 'loading', 'waiting', 'success', 'error'
        """
        labels = {
            "loading": "Creating payment request...",
            "waiting": "Waiting for payment...",
            "success": "Payment confirmed",
            "error": "An error occurred",
        }
        self.ids.statusLabel.text = labels.get(state, "")

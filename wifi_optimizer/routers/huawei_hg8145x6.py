"""
wifi_optimizer/routers/huawei_hg8145x6.py

Router driver for Huawei HG8145X6 (ONT WiFi 6) — Entel ISP, Chile.

Confirmed HTML selectors (firmware version shipped by Entel as of 2026-03):

  Login page
    #txt_Username      — username field
    #txt_Password      — password field
    #loginbutton       — login button (two exist in DOM; .nth(1) is the visible one)

  Post-login navigation
    text=Advanced      — top-level menu entry
    #name_wlanconfig   — "WLAN" collapsible menu group
    #wlan2adv          — "2.4G Advanced Network Settings" sub-menu item
    #wlan5adv          — "5G Advanced Network Settings"  sub-menu item

  WLAN Advanced panel  (loaded inside an <iframe>: WlanAdvance.asp?2G / ?5G)
    #Channel           — channel dropdown (same id for both bands)
    #applyButton       — Apply button (onclick="Submit();")
"""
from __future__ import annotations

import logging
from playwright.sync_api import sync_playwright

from .base import BaseRouter

log = logging.getLogger(__name__)

# How long to wait for the AJAX panel to render after clicking a sub-menu
_PANEL_SETTLE_MS = 2_000
# Slack time after clicking Apply for the radio to restart
_APPLY_SETTLE_MS = 3_000


class HuaweiHG8145X6(BaseRouter):
    """
    Playwright-based driver for the Huawei HG8145X6.
    All interaction is scoped to confirmed selectors listed in the module docstring.
    """

    # ------------------------------------------------------------------
    # Public interface (implements BaseRouter)
    # ------------------------------------------------------------------

    def read_channels(self) -> tuple[int | None, int | None]:
        log.info("Reading current channels from %s …", self.url)
        ch24 = ch5 = None
        try:
            with sync_playwright() as p:
                page = self._new_page(p, headless=True)
                self._login(page)
                self._open_advanced_wlan(page)

                # 2.4 GHz
                page.wait_for_selector("#wlan2adv", state="visible", timeout=8_000)
                page.click("#wlan2adv")
                page.wait_for_timeout(_PANEL_SETTLE_MS)
                ch24 = self._read_channel(_find_panel_frame(page), "2.4")

                # 5 GHz
                page.click("#name_wlanconfig")
                page.wait_for_selector("#wlan5adv", state="visible", timeout=8_000)
                page.click("#wlan5adv")
                page.wait_for_timeout(_PANEL_SETTLE_MS)
                ch5 = self._read_channel(_find_panel_frame(page), "5")

                page.context.browser.close()
        except Exception as exc:
            log.warning("Could not read current channels: %s", exc)
        return ch24, ch5

    def apply_channels(
        self,
        channel_24: int | None,
        channel_5:  int | None,
        *,
        headed: bool = False,
    ) -> None:
        if channel_24 is None and channel_5 is None:
            log.info("No channel changes requested.")
            return

        log.info(
            "Applying channels → 2.4 GHz: %s | 5 GHz: %s",
            f"ch{channel_24}" if channel_24 else "unchanged",
            f"ch{channel_5}"  if channel_5  else "unchanged",
        )
        try:
            with sync_playwright() as p:
                page = self._new_page(p, headless=not headed, slow_mo=300 if headed else 0)
                self._login(page)

                if headed:
                    page.content()  # trigger content load for debugging

                self._open_advanced_wlan(page)

                if channel_24 is not None:
                    page.wait_for_selector("#wlan2adv", state="visible", timeout=8_000)
                    page.click("#wlan2adv")
                    page.wait_for_timeout(_PANEL_SETTLE_MS)
                    if headed:
                        _dump_panel(page, "2.4G")
                    panel = _find_panel_frame(page)
                    _set_channel(panel, "2.4", channel_24)
                    _submit(panel)

                if channel_5 is not None:
                    page.click("#name_wlanconfig")
                    page.wait_for_selector("#wlan5adv", state="visible", timeout=8_000)
                    page.click("#wlan5adv")
                    page.wait_for_timeout(_PANEL_SETTLE_MS)
                    if headed:
                        _dump_panel(page, "5G")
                    panel = _find_panel_frame(page)
                    _set_channel(panel, "5", channel_5)
                    _submit(panel)

                page.context.browser.close()
        except Exception as exc:
            log.error("Router automation error: %s", exc)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _new_page(p, *, headless: bool = True, slow_mo: int = 0):
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context(ignore_https_errors=True)
        page    = context.new_page()
        page.set_default_timeout(20_000)
        return page

    def _login(self, page) -> None:
        page.goto(self.url, wait_until="domcontentloaded")

        # Locate login form (may be in an iframe on some firmware versions)
        frame = page
        try:
            page.wait_for_selector("#txt_Username", state="visible", timeout=10_000)
        except Exception:
            frame = None
            for f in page.frames:
                try:
                    f.wait_for_selector("#txt_Username", state="visible", timeout=3_000)
                    frame = f
                    break
                except Exception:
                    continue
            if frame is None:
                raise RuntimeError("#txt_Username not found in page or any iframe.")

        frame.fill("#txt_Username", self.username)
        frame.fill("#txt_Password", self.password)

        # HG8145X6 has two #loginbutton elements; nth(1) is the visible one
        clicked = False
        try:
            frame.locator("#loginbutton").nth(1).click(timeout=5_000)
            clicked = True
        except Exception:
            pass

        if not clicked:
            for sel in [
                "#loginBtn", "#btn_login",
                "input[type='button'][value='Log In']",
                "input[type='button'][value*='ogin']",
                "input[type='submit']",
                "button[type='submit']",
            ]:
                try:
                    frame.click(sel, timeout=5_000)
                    clicked = True
                    break
                except Exception:
                    continue

        if not clicked:
            raise RuntimeError("Login button not found.")

        # Wait for the main menu to appear (router has constant JS polling,
        # so networkidle never fires — we wait for a known element instead)
        for sel in ["text=Advanced", "text=Avanzado", "#name_Advanced", "#indexMenuMain"]:
            try:
                page.wait_for_selector(sel, state="visible", timeout=10_000)
                log.info("Login successful.")
                return
            except Exception:
                continue

        try:
            page.wait_for_url("**/index.asp", timeout=10_000)
            log.info("Login successful (URL-based detection).")
        except Exception:
            raise RuntimeError("Login appeared to succeed but main menu was not detected.")

    @staticmethod
    def _open_advanced_wlan(page) -> None:
        for sel in ["text=Advanced", "text=Avanzado", "a[href*='advanced']"]:
            try:
                page.click(sel, timeout=6_000)
                break
            except Exception:
                continue
        page.wait_for_selector("#name_wlanconfig", state="visible", timeout=10_000)
        page.click("#name_wlanconfig")

    @staticmethod
    def _read_channel(frame, band: str) -> int | None:
        try:
            val = frame.locator("#Channel").first.evaluate("el => el.value")
            ch = int(val)
            log.info("Current %s GHz channel: ch%s", band, ch)
            return ch
        except Exception as exc:
            log.warning("Could not read %s GHz channel: %s", band, exc)
            return None


# ---------------------------------------------------------------------------
# Module-level helpers (not part of the public API)
# ---------------------------------------------------------------------------

def _find_panel_frame(page, selector: str = "#Channel"):
    """
    Return the frame that contains `selector`.
    HG8145X6 loads WLAN panels inside an <iframe> (WlanAdvance.asp?2G / ?5G).
    """
    try:
        if page.locator(selector).count() > 0:
            return page
    except Exception:
        pass

    for frame in page.frames:
        try:
            frame.wait_for_selector(selector, state="attached", timeout=2_000)
            log.info("Panel frame: %s", frame.url)
            return frame
        except Exception:
            continue

    log.warning("Frame with '%s' not found; falling back to main page.", selector)
    return page


def _set_channel(frame, band: str, channel: int) -> None:
    """Select `channel` in the #Channel dropdown of the active panel frame."""
    for sel in ["#Channel", "select#Channel", "select[id*='Channel']", "select[id*='channel']"]:
        try:
            loc = frame.locator(sel).first
            loc.wait_for(state="visible", timeout=5_000)
            loc.select_option(str(channel))
            log.info("%s GHz → ch%s", band, channel)
            return
        except Exception:
            continue
    log.warning("Channel dropdown not found for %s GHz.", band)


def _submit(frame) -> None:
    """Click the Apply button and wait for the radio to restart."""
    for sel in [
        "#applyButton",                        # HG8145X6 exact id
        "#confirmokbtn", "#apply_btn", "#btn_apply", "#btn_ok",
        "button[type='button'][id*='apply']",
        "input[type='button'][value='Apply']",
        "input[type='button'][value*='pply']",
        "input[type='submit']", "button[type='submit']",
    ]:
        try:
            frame.click(sel, timeout=5_000)
            log.info("Apply clicked ('%s'). Waiting for radio restart…", sel)
            frame.wait_for_timeout(_APPLY_SETTLE_MS)
            return
        except Exception:
            continue
    log.warning("Apply button not found — changes may not have been saved.")


def _dump_panel(page, label: str) -> None:
    """Log all select/input elements in the current panel (inspect mode only)."""
    log.info("── Panel elements [%s] ──", label)
    for sel in ["select", "input[type='text']", "input[type='button']", "button[type='button']"]:
        for el in page.locator(sel).all():
            try:
                log.info(
                    "  %-8s id=%-30s value=%-15s visible=%s",
                    sel.split("[")[0],
                    el.get_attribute("id") or "",
                    el.get_attribute("value") or el.input_value() or "",
                    el.is_visible(),
                )
            except Exception:
                pass

"""Offline browser smoke check, isolated temporary headless browser profile."""
import json
import os
from pathlib import Path

os.environ.setdefault("PLAYWRIGHT_NODEJS_PATH", "/opt/homebrew/bin/node")
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent
with sync_playwright() as w:
    browser = w.chromium.launch(
        headless=True,
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        timeout=15000,
    )
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto((root / "index.html").as_uri(), wait_until="load")
    page.wait_for_selector("#turns article")
    games = page.locator("#games button").count()
    assert games == 131, games
    page.locator("#cohort").select_option("local_mas")
    page.locator("#games button").filter(has_text="TS038_r04_mas_review").click()
    page.locator("#verdict").select_option("suspect")
    filtered = page.locator("#turns article").count()
    assert filtered > 0
    page.screenshot(path=str(root / "review_portal_desktop.png"))
    page.locator("#verdict").select_option("")
    page.locator("#kind").select_option("final")
    assert page.locator("#turns article").count() == 0  # no final in partial game
    page.set_viewport_size({"width": 390, "height": 844})
    page.screenshot(path=str(root / "review_portal_mobile.png"))
    assert not errors, errors
    result = dict(games=games, page_errors=errors, suspect_filter_rows=filtered,
                  partial_game_has_no_final=True, desktop_mobile_rendered=True)
    (root / "browser_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    browser.close()

import subprocess
import time
from playwright.sync_api import sync_playwright

REMOTE_DEBUGGING_PORT = "9223"
EMAIL = "gauri.desai@bito.ai"
TARGET_URL = "https://alpha.bito.ai/home/ai-agents/code-review-agent"  # Correct Target URL

def run():
    with sync_playwright() as p:
        # Launch Chromium with remote debugging port for Lighthouse
        browser = p.chromium.launch(
            headless=False,
            args=[f"--remote-debugging-port={REMOTE_DEBUGGING_PORT}"]
        )
        context = browser.new_context()
        page = context.new_page()

        # Step 1: Go to login page
        page.goto("https://alpha.bito.ai/auth/login")
        page.locator('#email').fill(EMAIL)
        page.locator('button:has-text("Continue")').click()

        print("➡️ Waiting 60 seconds for you to enter OTP manually in browser...")
        time.sleep(20)  # You can adjust if OTP screen loads faster/slower

        # Step 2: After OTP, click the "Submit" button
        print("🔲 Clicking Submit button...")
        page.locator('#regCodeBtn').click()  # Click the "Submit" button by ID

        # Step 3: Click the Sign in button for Akshay's_workspace using XPath
        page.locator('//h5[text()="Akshay\'s_workspace"]/ancestor::div[contains(@class, "card-body")]//button[text()="Sign in"]').click()

        # Optionally wait for navigation or confirmation
        page.wait_for_load_state("networkidle")
        time.sleep(10)

        # Step 3: Navigate to target logged-in page (Code Review Agent)
        print("🔗 Navigating to target page...")
        page.goto("https://alpha.bito.ai/home/ai-agents/code-review-agent")
        page.wait_for_load_state("networkidle")
        title = page.title()
        print(f"📄 Page Title: {title}")
        print(f"🎯 Ready to audit: {page.url}")

        # Step 4: Run Lighthouse via subprocess on current URL
        subprocess.run([
            "lighthouse",
            page.url,
            f"--port={REMOTE_DEBUGGING_PORT}",
            "--output=json",
            "--output=html",
            "--output-path=lh-report",
            "--only-categories=performance"
        ])

        print("✅ Lighthouse audit complete. Report saved as lh-report.html and lh-report.json.")
        browser.close()

if __name__ == "__main__":
    run()

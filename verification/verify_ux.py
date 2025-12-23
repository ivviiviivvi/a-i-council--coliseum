from playwright.sync_api import sync_playwright

def verify_ux_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the page
            page.goto("http://localhost:3000")

            # Wait for content to load
            page.wait_for_selector("h1")

            # 1. Verify Emojis are wrapped
            # We look for the span with role="img" and specific aria-label
            robot_emoji = page.locator('span[role="img"][aria-label="Robot"]')
            if robot_emoji.count() > 0:
                print("✅ Found accessible Robot emoji")
            else:
                print("❌ Robot emoji not found or not accessible")

            # 2. Verify Button Focus Styles
            # Force focus on a primary button
            button = page.locator(".btn-primary").first
            button.focus()

            # Take a screenshot to verify focus ring and emoji
            page.screenshot(path="verification/ux_verification.png")
            print("📸 Screenshot taken at verification/ux_verification.png")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_ux_changes()

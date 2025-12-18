from playwright.sync_api import sync_playwright, expect

def verify_buttons():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the home page
        try:
            page.goto("http://localhost:3000")
            print("Navigated to http://localhost:3000")
        except Exception as e:
            print(f"Failed to navigate: {e}")
            return

        # Wait for content to load
        page.wait_for_selector("h1")

        # Find the "View Agents" button
        # The content has "🤖 AI Agents", so the button is near that card.
        # But we can just search for the button text.
        view_agents_btn = page.get_by_role("button", name="View Agents")

        # Focus on the button to trigger focus-visible
        view_agents_btn.focus()

        # Take a screenshot of the focused button
        # We can take a screenshot of the specific element or the whole page
        # Let's take the whole page to see the context
        page.screenshot(path="verification/focus_state.png")
        print("Screenshot taken: verification/focus_state.png")

        # Also verify the decorative emojis are hidden
        # We can check if the span has aria-hidden=true
        emoji_span = page.locator("h2 span[aria-hidden='true']").first
        if emoji_span.count() > 0:
            print("Found aria-hidden span for emojis.")
        else:
            print("Did NOT find aria-hidden span for emojis.")

        browser.close()

if __name__ == "__main__":
    verify_buttons()

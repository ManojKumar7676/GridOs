import os
import time
from playwright.sync_api import sync_playwright

def capture_live():
    out_dir = os.path.abspath("showcase/assets/screenshots")
    os.makedirs(out_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page = context.new_page()
        
        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=45000)
        page.wait_for_selector('[data-testid="stTab"]', timeout=30000)
        time.sleep(3)
        
        tabs = page.query_selector_all('[data-testid="stTab"]')
        print(f"Total tabs: {len(tabs)}")
        
        # 1. Tab 0: Operations Dashboard
        print("Capturing Tab 0: Operations Dashboard...")
        tabs[0].click()
        time.sleep(3)
        page.screenshot(path=os.path.join(out_dir, "screenshot_tab2_scada.png"))
        
        # 2. Tab 6: Weather Imagery (Radar Vision)
        print("Capturing Tab 6: Weather Imagery...")
        tabs[6].click()
        time.sleep(3)
        page.screenshot(path=os.path.join(out_dir, "screenshot_tab3_radar.png"))
        
        # 3. Tab 2: Dispatch & Scenarios
        print("Capturing Tab 2: Dispatch & Scenarios...")
        tabs[2].click()
        time.sleep(3)
        page.screenshot(path=os.path.join(out_dir, "screenshot_tab4_analytics.png"))
        
        # 4. Tab 7: Evaluation
        print("Capturing Tab 7: Evaluation...")
        tabs[7].click()
        time.sleep(3)
        page.screenshot(path=os.path.join(out_dir, "screenshot_tab7_eval.png"))
        
        browser.close()
        print("Successfully captured all 4 live screenshots!")

if __name__ == "__main__":
    capture_live()

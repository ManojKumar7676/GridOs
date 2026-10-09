import os
import time
from playwright.sync_api import sync_playwright

def capture_platform_screenshots():
    out_dir = os.path.join(os.getcwd(), "storage", "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Connecting to Streamlit at http://localhost:8501...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # High resolution desktop viewport
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        page = context.new_page()
        
        page.goto("http://localhost:8501", timeout=60000)
        
        # Wait for Streamlit tabs to load
        print("Waiting for [data-testid='stTab']...")
        page.wait_for_selector('[data-testid="stTab"]', timeout=30000)
        time.sleep(5) # wait for all initial plots to load
        
        tabs = page.query_selector_all('[data-testid="stTab"]')
        print(f"Detected {len(tabs)} tabs.")
        
        # Target tabs:
        # Tab 1: Real-Time SCADA Dispatch Console (index 1)
        # Tab 2: Multimodal Radar Vision Station (index 2)
        # Tab 3: 24-Hour Diurnal Analytics (index 3)
        # Tab 6: Agent Evaluation & Audit Station (index 6)
        targets = [
            (1, "screenshot_tab2_scada.png", "Real-Time SCADA Dispatch Console"),
            (2, "screenshot_tab3_radar.png", "Multimodal Radar Vision Station"),
            (3, "screenshot_tab4_analytics.png", "24-Hour Diurnal Analytics"),
            (6, "screenshot_tab7_eval.png", "Agent Evaluation & Audit Station")
        ]
        
        for idx, filename, label in targets:
            print(f"\n--- Activating Tab {idx}: {label} ---")
            tab_element = tabs[idx]
            tab_element.scroll_into_view_if_needed()
            tab_element.click()
            time.sleep(4) # allow Streamlit to execute reactive state & render figures
            
            target_path = os.path.join(out_dir, filename)
            # Take screenshot of the viewport
            page.screenshot(path=target_path, full_page=False)
            size_kb = os.path.getsize(target_path) / 1024
            print(f"Captured: {filename} ({size_kb:.1f} KB)")
            
        browser.close()
        print("\nAll 4 platform screenshots successfully captured and stored in storage/screenshots/!")

if __name__ == "__main__":
    capture_platform_screenshots()

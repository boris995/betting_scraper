from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys


# Function for scraping data from the page
def scrape(new_driver, league):
    teams = []
    times = []
    odds = []

    teams_ = new_driver.find_elements(By.CSS_SELECTOR, ".rcl-ParticipantFixtureDetailsTeam_TeamName")
    times_ = new_driver.find_elements(By.CSS_SELECTOR, ".rcl-ParticipantFixtureDetails_BookCloses")
    odds_ = new_driver.find_elements(By.CSS_SELECTOR, ".sgl-ParticipantOddsOnly80_Odds")

    for i in teams_:
        teams.append(i.text)
    for i in times_:
        times.append(i.text)
    for key in odds_:
        odds.append(key.text)

    # Validate lengths to avoid mismatches and to clean data before putting in dataframes
    min_length = min(len(teams) // 2, len(times), len(odds) // 3)
    home_teams = teams[:min_length * 2:2]
    away_teams = teams[1:min_length * 2:2]
    home_odds = odds[:min_length]
    draw_odds = odds[min_length:min_length * 2]
    away_odds = odds[min_length * 2:min_length * 3]

    columns = ['Home Team', 'Away Team', "Home Odds", "Draw Odds", "Away Odds"]
    new_dataframe = pd.DataFrame(columns=columns)
    new_dataframe['Home Team'] = home_teams
    new_dataframe['Away Team'] = away_teams
    new_dataframe['Home Odds'] = home_odds
    new_dataframe['Draw Odds'] = draw_odds
    new_dataframe['Away Odds'] = away_odds

    # Save to Excel
    new_dataframe.to_excel(f"{league}.xlsx", index=False)
    print(f"Scraped and saved data for league: {league}")


# Open a new tab
# The `open_tab` function in the provided Python code is responsible for opening a new tab in the
# web browser controlled by Selenium WebDriver and switching the driver's focus to that newly
# opened tab. 
def open_tab(driver, link):
    driver.execute_script(f"""window.open('{link}', "_blank");""")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])


# Function to initialize a new driver
def create_new_driver():
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-popup-blocking")
    # options.add_argument("disable-infobars")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    driver.set_window_size(390, 844)
    # driver.fullscreen_window()
    return driver


# Accept cookies
# The `accept_cookies` function is responsible for handling the acceptance of cookies on a webpage
# using Selenium. It attempts to locate and click on the element that represents the "Accept"
# button for cookie consent.
def accept_cookies(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ccm-CookieConsentPopup_Accept"))
        ).click()
    except Exception:
        print("Cookies banner not found.")


# Scroll the page to load content
# The `scroll_page` function is responsible for simulating the
# action of scrolling down a webpage to load additional content with key DOWN
def scroll_page(driver):
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(5):  # Adjust range for more or fewer scrolls
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)


# Close all tabs except the active one
# The `close_inactive_tabs(driver)` function is responsible for closing all tabs except
# the currently active tab in the WebDriver session. It iterates through all the window
# handles available in the WebDriver session, switches to each handle one by one, closes
# the tab if it is not the current active tab, and finally switches back to the original
# active tab before the function call. This helps in keeping the WebDriver session
# organized and ensures that unnecessary tabs are closed to avoid clutter.
def close_inactive_tabs(driver):
    current_handle = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != current_handle:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(current_handle)
    
def load_page_with_dropdown(driver):
    # Main link with pages that are going to be clicked
    link = "https://www.bet365.com/#/AC/B1/C1/D1002/E91422157/G40/"
    # Create driver

    # Access Bet365 main links
    driver.get(link)
    # Loop to access the page twice to simulate human
    for _ in range(1):
        open_tab(driver, link)
    # Accept cookies on the page
    accept_cookies(driver)

    
# Main flow
def main():
    driver = create_new_driver()
    load_page_with_dropdown(driver)
    time.sleep(5)  # Wait for the page to load
    scrape(driver, 'England Premier League')
    dropdown = driver.find_element(By.CLASS_NAME, 'sph-MultiLevelDropDown ')
    ActionChains(driver).move_to_element(dropdown).click().perform()
    time.sleep(2)
    try:
        # Locate the parent container
        dropdown_container = driver.find_element(By.CLASS_NAME, "sph-MultiLevelDropDownContainer_ChildMenu")

        # Find all item labels within the dropdown
        labels_elements = dropdown_container.find_elements(By.CLASS_NAME, "sph-MultiLevelDropDownItem_Label")

        # Store all label names
        labels = [label.text.strip() for label in labels_elements if label.text.strip()]
        print(f"Labels found: {labels}")
    except Exception as e:
        print(f"Error processing dropdown: {e}")
        return []
    for label_text in labels:
        
        if label_text != 'England Premier League':
            try:
                # Find the specific label element by text
                item = driver.find_element(By.XPATH, f'//span[normalize-space()="{label_text}"]')
                parent_div = item.find_element(By.XPATH, "./ancestor::div[contains(@class, 'sph-MultiLevelDropDownItem')]")
                # Scroll to the element and click
                driver.execute_script("arguments[0].scrollIntoView(true);", item)
                ActionChains(driver).move_to_element(item).click().perform()
                print(f"Clicked on item: {label_text}")

                # Wait for the next page or action to complete
                time.sleep(5)
                new_link = driver.current_url
                print(f"Navigated to: {new_link}")
                open_tab(driver, new_link)
                time.sleep(5)
                scrape(driver, label_text)
                close_inactive_tabs(driver)
                load_page_with_dropdown(driver)
                dropdown = driver.find_element(By.CLASS_NAME, 'sph-MultiLevelDropDown ')
                ActionChains(driver).move_to_element(dropdown).click().perform()
                # Navigate back or reload dropdown if necessary
                # Add logic here if you need to return to the dropdown view
                

            except Exception as e:
                print(f"Failed to click on label '{label_text}': {e}")
                for _ in range(2):
                    open_tab(driver, new_link)

    driver.quit()


if __name__ == "__main__":
    main()

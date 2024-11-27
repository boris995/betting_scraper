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
    # driver.set_window_size(390, 844)
    driver.fullscreen_window()
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


# Extract unique spans inside a specific parent class
# The `extract_spans` function is responsible for extracting unique
# text content from specific `<span>` elements within a parent class on a webpage using
# Selenium.
def extract_spans(driver):
    try:
        scroll_page(driver)
        parent_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'sm-CouponLink')]")
        spans = set()  # Use a set to avoid duplicates
        for parent in parent_divs:
            span_elements = parent.find_elements(By.XPATH, ".//span")
            for span in span_elements:
                text = span.text.strip()
                if text:  # Ensure the text is not empty
                    spans.add(text)
        return list(spans)
    except Exception as e:
        print(f"Error extracting spans: {e}")
        return []


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

def click_closed_dropdowns(driver):
    """
    Finds all dropdowns where 'sm-SplashMarket_HeaderOpen' class is not added 
    and clicks on them to expand.
    """
    try:
        # Find all dropdown headers
        dropdowns = driver.find_elements(By.XPATH, "//div[contains(@class, 'sm-SplashMarket_Header') and not(contains(@class, 'sm-SplashMarket_HeaderOpen'))]")

        # Click each closed dropdown
        for dropdown in dropdowns:
            try:
                ActionChains(driver).move_to_element(dropdown).click().perform()
                print(f"Clicked on dropdown: {dropdown.text}")
                time.sleep(4)  # Add a small delay to ensure content loads
            except Exception as e:
                print(f"Failed to click on dropdown: {e}")
    except Exception as e:
        print(f"Error finding dropdowns: {e}")

# Main flow
def main():
    # Main link with pages that are going to be clicked
    link = "https://www.bet365.com/#/AS/B1/K^5/"
    # Create driver
    driver = create_new_driver()
    # Access Bet365 main links
    driver.get(link)
    # Loop to access the page twice to simulate human
    for _ in range(2):
        open_tab(driver, link)
    # Accept cookies on the page
    open_tab(driver, link)
    accept_cookies(driver)
    time.sleep(5)
    click_closed_dropdowns(driver)
    scroll_page(driver)
    # Extract all league names that are also link names
    spans = extract_spans(driver)
    
    print(f"Spans extracted: {spans}")
    # Loop through the links and access each league page
    for span_text in spans:
        try:
            # Normalize quotes in names so that it can access each page properly 
            normalized_text = span_text.replace("’", "'")  # Normalize quotes
            # Similar logic as in extract_spans() function (minimal redundancy)
            soccer_element = driver.find_element(By.XPATH, f'//span[normalize-space()="{normalized_text}"]')
            parent_div = soccer_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'sm-CouponLink')]")

            # Click the element with ActionChains to simulate human
            ActionChains(driver).move_to_element(parent_div).click().perform()
            time.sleep(5)  # Wait for the page to load

            # Save the new URL of the league that is going to be scraped below
            new_link = driver.current_url
            print(f"Navigated to: {new_link}")

            # Open the new link in a new tab to emulate human
            open_tab(driver, new_link)

            # Scrape the data 
            scrape(driver, span_text)

            # Return to the original tab and close the tabs

            close_inactive_tabs(driver)
            driver.get(link)
            for _ in range(2):
                open_tab(driver, link)
            accept_cookies(driver)
            time.sleep(5)
        except Exception as e:
            print(f"Failed to process span: {span_text}: {e}")
            for _ in range(2):
                open_tab(driver, link)

    driver.quit()


if __name__ == "__main__":
    main()

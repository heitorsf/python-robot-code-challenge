from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from datetime import datetime
from variables import search_phase, sections, nmonths
import os
import urllib
from RPA.Excel.Files import Files
import pdb

browser_lib = Selenium()
excel_lib = Files()
    

def click_button(locator):
    """Send click_button command for a xpath-located element.
    """
    button = browser_lib.find_elements("xpath://button[@" + locator + "]")
    browser_lib.click_button(button)


def set_input(locator, search_phrase, pressEnter=True):
    """Set input for a xpath-located element.
    """
    input = browser_lib.find_elements("xpath://input[@" + locator + "]")
    browser_lib.input_text(input, search_phrase)
    if pressEnter:
        browser_lib.press_keys(input, "ENTER")


def parse_date(date):
    """Convert NYTimes dates format to datetime object
    """
    # Current year date ex.: 'Aug. 13', 'July 4': add year
    date = date.replace(".", "")
    if len(date.split(" ")) == 2:
        cur_year = datetime.today().year
        date = f"{date}, {cur_year}"
        print(f"date: {date}")
    try:
        date_raw = datetime.strptime(date, "%b %d, %Y")
    except ValueError:
        try:
            date_raw = datetime.strptime(date, "%B %d, %Y")
        except ValueError:
            date_raw = datetime.strptime(date, "%m/%d/%Y")
    #date_formatted = datetime.strftime(date_raw, "%b/%d/%Y")
    return date_raw

def close_all():
    browser_lib.close_all_browsers()


def show_more_until(start_date):
    """Click "Show more" button until desired start date
    """
    start_date = parse_date(start_date)
    gofurther = True
    loc_dates_visible = "xpath://*[@data-testid='todays-date']"
    while gofurther:
        dates_visible = 0
        dates_visible = browser_lib.find_elements(loc_dates_visible)
        last_visible_date = parse_date(dates_visible[-1].text)
        if last_visible_date < start_date:
            gofurther = False
        else:
            click_button("data-testid='search-show-more-button'")


#wi = WorkItems()
#wi.get_input_work_item()
#search_phrase = wi.get_work_item_variable("search_phrase")
#category = wi.get_work_item_variable("category"
#n_months = wi.get_work_item_variable("n_months")

def main():
    # Inputs
    url = "https://www.nytimes.com/"
    search_phrase = "Bob Dylan"
    startDate = "07/04/2023"
    endDate = "08/12/2023"
    sections_to_show = ["Arts", "Movies", "Opinion"]
    types_to_show = ["Article"]
    
    try:
        # Access website
        browser_lib.open_available_browser(url)
    
        # Deal with compliance overlay
        overlay = browser_lib.find_elements("xpath://*[@id='complianceOverlay']")
        if len(overlay) > 0:
            button_continue = browser_lib.find_elements("xpath://button[contains(.,'Continue')]")
            browser_lib.click_button(button_continue)
        else:
            pass
        
        # Access search input field by clicking on search-button
        click_button("data-testid='search-button'")
        set_input("data-testid='search-input'", search_phrase)

        # Cookies dock: close
        loc_exitdock = "xpath://*[@data-testid='expanded-dock-btn-selector']"
        browser_lib.wait_until_page_contains_element(loc_exitdock)
        browser_lib.click_button(loc_exitdock)
        # To do: calculate date range (MM/DD/YYY)
        # Filter by date range
        click_button("data-testid='search-date-dropdown-a'")
        click_button("value='Specific Dates'")
        set_input("data-testid='DateRange-startDate'", startDate, pressEnter=False)
        set_input("data-testid='DateRange-endDate'", endDate)
    
        # Click to check the sections in the desired list
        browser_lib.find_element(f"xpath://*[@data-testid='section']").click()
        for sec in sections_to_show:
            browser_lib.find_element(f"xpath://*[@data-testid='section']/div/ul/*[contains(.,'{sec}')]").click()
        # Click to check the types in the desired list
        browser_lib.find_element(f"xpath://*[@data-testid='type']").click()
        for type in types_to_show:
            browser_lib.find_element(f"xpath://*[@data-testid='type']/div/ul/*[contains(.,'{type}')]").click()
    
        # Sort by newest
        sortby = browser_lib.find_element("xpath://*[@data-testid='SearchForm-sortBy']")
        browser_lib.select_from_list_by_value(sortby, 'newest')

        # Expand with "Show more" button until the desired startDate is shown
        show_more_until(startDate)

        # Gather data
        news = browser_lib.find_elements("xpath://li[@class='css-1l4w6pd']")
        news_split = [n.text.split("\n") for n in news]
        dates = [n[0] for n in news_split]
        category = [n[1] for n in news_split]
        title = [n[2] for n in news_split]
        description = [n[3] if n[3].endswith(".") else "" for n in news_split]
        
        # Get figure filename and download to ./output/figures dir
        fig_elements = browser_lib.find_elements("xpath://figure[@class='css-tap2ym']")
        figfilenames = []
        basedir = os.getcwd()
        os.chdir("output")
        os.chdir("figures")
        for fig_el in fig_elements:
            # Get first child element
            child1 = 0
            child1 = fig_el.find_element('xpath', '*')
            # Get "grandchild" element
            child2 = 0
            child2 = child1.find_element('xpath', '*')
            # Get source
            src = child2.get_attribute('src')
            # Get filename
            extensions = [".jpg", ".png", ".gif", ".tiff"]
            for ext in extensions:
                if ext in src:
                    figext = ext
                    break
            fname_end = src.find(".jpg") + len(".jpg")
            fname_start = src[:fname_end].rfind("/") + len("/")
            fname = src[fname_start:fname_end]
            figfilenames.append(fname)
            # Download figure
            urllib.request.urlretrieve(src, fname)
        os.chdir(basedir)



        pdb.set_trace()
        #loc_titles = "xpath://h4"
        #loc_dates = "xpath://*[@data-testid='todays-date']"
        #loc_descriptions = 
        #dates = browser_lib.find_elements(loc_dates_visible)



    finally:
        pass
        #browser_lib.close_all_browsers()

if __name__ == "__main__":
    main()
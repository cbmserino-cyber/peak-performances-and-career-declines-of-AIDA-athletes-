import csv
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from rich.console import Console
from rich.text import Text
from rich.progress import track

console = Console()

# WebDriver
options = Options()
options.headless = True  # Run in headless mode
service = FirefoxService(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

url = "https://www.aidainternational.org/Ranking/index.php"
driver.get(url)

# load filter
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "discipline")))

# dropdown available years
def get_available_years():
    try:
        year_dropdown = driver.find_element(By.ID, "year")
        options = year_dropdown.find_elements(By.TAG_NAME, "option")
        available_years = [opt.get_attribute("value") for opt in options if opt.get_attribute("value").isdigit()]
        console.print("\n[cyan]AVAILABLE YEARS:[/cyan]", available_years)
        return available_years
    except Exception as e:
        console.print(f"[red]❌ Failed to get available years:[/red] {e}")
        return []

# select category (discipline)
def select_discipline(discipline_value):
    try:
        discipline_dropdown = driver.find_element(By.ID, "discipline")
        Select(discipline_dropdown).select_by_value(discipline_value)
        console.print(f"\n[yellow]SELECTED DISCIPLINE:[/yellow] {discipline_value}")
    except Exception as e:
        console.print(f"[red]❌ Failed to select discipline:[/red] {e}")

# select year/s from dropdown
def select_year(year):
    try:
        year_dropdown = driver.find_element(By.ID, "year")
        Select(year_dropdown).select_by_value(year)
        console.print(f"\n[green]-> year: {year}[/ green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to select year:[/red] {e}")

# click apply button for filters
def apply_filters():
    try:
        apply_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'js-applyFilter')]"))
        )
        console.print("[blue]--> clicking[/ blue]")
        apply_button.click()
        time.sleep(3)  # Allow page to update
        console.print("[magenta]---> filters applied[/ magenta]")
    except Exception as e:
       console.print(f"[red]❌ Failed to apply filters:[/ red] {e}")
       
# extract ranking data
def scrape_rankings(year):
    rankings = []
    page_number = 1

    while True:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table__data"))
        )
        console.print(f"[cyan]----> Scraping page {page_number} for {year}[/cyan]")

        # Extract table rows
        table_rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'table__data')]/tbody/tr")

        for row in table_rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) >= 10:
                rankings.append([
                    year, columns[0].text.strip(), columns[1].text.strip(), columns[2].text.strip(),
                    columns[3].text.strip(), columns[4].text.strip(), columns[5].text.strip(),
                    columns[6].text.strip(), columns[7].text.strip(), columns[8].text.strip(),
                    columns[9].text.strip(), columns[10].text.strip()
                ])

        # Check for pagination links
        try:
            pagination_links = driver.find_elements(By.XPATH, "//div[@class='pagination-container']//a")
            next_page_link = None

            # Find the link for the next page
            for link in pagination_links:
                if link.text.strip().isdigit() and int(link.text.strip()) == page_number + 1:
                    next_page_link = link
                    break

            if next_page_link:
                console.print(f"[yellow]---> Navigating to page {page_number + 1}...[/yellow]")
                next_page_link.click()
                time.sleep(3)  # Wait for the next page to load
                page_number += 1
            else:
                break  # Exit loop if no more pages
        except Exception as e:
            console.print(f"[red]❌ No more pages:[/red] {e}")
            break

    console.print(f"[green]✅ {year} ranking fully scraped![/green]")
    return rankings
    
# get available years
available_years = get_available_years()

# years to scrape
start_year = 1993
end_year = 2025

# filter years within the range
years_to_scrape = [year for year in available_years if start_year <= int(year) <= end_year]

# select discipline
select_discipline("depth") 

# CSV
output_file = "aida_depthrankings_by_years.csv"
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(['Year', 'Rank', 'Athlete', 'Total Points', 'STA', 'DYN', 'DYNB', 'DNF', 'CWT', 'CWTB', 'CNF', 'FIM'])  # Headers

    # loop through years and scrape data
    for year in track(years_to_scrape, description="[green]Scraping Rankings...[/green]"):
        select_year(year)
        apply_filters()
        rankings_data = scrape_rankings(year)
        writer.writerows(rankings_data)

df = pd.read_csv(output_file)
df.to_csv(output_file, index=False)

console.print(f"\n[bold green]✅ Data saved to {output_file}, brader![/bold green]")

driver.quit()

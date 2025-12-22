"""
Handles downloading and processing of SEC EDGAR filings using 'edgar' tools.
"""
import os
from typing import Optional
from edgar import set_identity, Company
from ..config import Config

# Global variable to hold 10K report content in memory.
TEN_K_REPORT_CONTENT: str = ""

def download_and_load_10K(
        ticker: str,
        email: str,
        path: Optional[str] = None
) -> str:
    """
    Downloads the latest 10-K report for a company using edgartools and returns its text content.

    Args:
        ticker (str): The company's stock ticker (e.g., "NVDA").
        email (str): Your email address, required by the SEC for identification.
        path (Optional[str]): The path to save filings. If None, edgartools uses a default cache.

    Returns:
        str: The full text content of the latest 10-K report, or an empty string on failure.
    """
    global TEN_K_REPORT_CONTENT

    print("\nStarting Data Sourcing: 10-K Report...")
    try:
        # Setting the identity for the SEC
        set_identity(f"Agentic Guardrails Project {email}")

        print(f"Looking up company with ticker: {ticker}...")
        company = Company(ticker)

        print("Fetching list of all 10-K filings...")
        filings = company.get_filings(form="10-K")

        print("Identifying the latest 10-K filing...")
        latest_10k = filings.latest(1)

        print("Extracting clean text content from the filings...")
        content = latest_10k.text()

        # Saving to local path.
        if path:
            print(f"Saving the report to local directory: {path}")

            save_dir = os.path.join(path, ticker)
            os.makedirs(save_dir, exist_ok=True)

            filename = "10k_filing.txt"
            file_path = os.path.join(save_dir, filename)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Report saved locally at: {file_path}")

        TEN_K_REPORT_CONTENT = content
        print(f"Successfully loaded 10-K report for ticker: {ticker}.")
        print(f"Total characters: {len(TEN_K_REPORT_CONTENT):,}")

        return TEN_K_REPORT_CONTENT
    
    except Exception as e:
        print(f"ERROR: Failed to download or load the 10-K filing for ticker {ticker}")
        print(f"Error details: {e}")
        return ""
    
if __name__ == "__main__":
    COMPANY_TICKER = "NVDA"
    USER_EMAIL = "rmworkofficial1@gmail.com"

    DOWNLOAD_PATH = "/Users/rishabhmathur/Documents/Development/AI/Projects/Agentic_Guardrails/agentic_guardrails/data"

    if USER_EMAIL == "your.email@example.com":
        print("Please change the USER_EMAIL variable to your actual email address.")

    else:
        # Executing download and load process.
        report_content = download_and_load_10K(COMPANY_TICKER, USER_EMAIL, path=DOWNLOAD_PATH)

        if report_content:
            print("\nFiling Content Preview (first 1000 characters)")
            print(report_content[:1000] + "...")
#!/usr/bin/env python3
"""
Libraff.az Book Scraper
Scrapes all book data from libraff.az and saves to CSV
"""

import requests
import json
import csv
import time
from typing import List, Dict, Any
from pathlib import Path


class LibraffScraper:
    """Scraper for libraff.az book catalog"""

    def __init__(self):
        self.base_url = "https://www.libraff.az/kitab/page-{}/"
        self.params = {
            "items_per_page": "128",
            "result_ids": "pagination_contents",
            "is_ajax": "1"
        }
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6",
            "DNT": "1",
            "Referer": "https://www.libraff.az/kitab/",
            "Sec-Ch-Ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.session = requests.Session()
        self.all_books = []

    def fetch_page(self, page_num: int) -> Dict[str, Any]:
        """Fetch a single page of book data"""
        url = self.base_url.format(page_num)

        try:
            response = self.session.get(
                url,
                params=self.params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            # The response might be JSON or contain JSON in HTML
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                print(f"Warning: Page {page_num} returned non-JSON response")
                return {}

        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            return {}

    def extract_books_from_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract book data from API response"""
        books = []

        # Navigate to the products data
        if "cp_gtm" in response_data:
            view_products = response_data.get("cp_gtm", {}).get("view_products", {})

            for product_id, product_data in view_products.items():
                book = {
                    "product_id": product_id,
                    "item_name": product_data.get("item_name", ""),
                    "item_id": product_data.get("item_id", ""),  # ISBN
                    "currency": product_data.get("currency", ""),
                    "price": product_data.get("price", ""),
                    "quantity": product_data.get("quantity", ""),
                    "stock": product_data.get("stock", ""),
                    "item_category0": product_data.get("item_category0", ""),
                    "item_category1": product_data.get("item_category1", ""),
                    "item_category2": product_data.get("item_category2", ""),
                    "item_list_name": product_data.get("item_list_name", "")
                }
                books.append(book)

        return books

    def scrape_all_pages(self) -> List[Dict[str, Any]]:
        """Scrape all pages until no more data is found"""
        page_num = 1
        consecutive_empty_pages = 0
        max_empty_pages = 3  # Stop after 3 consecutive empty pages

        print(f"Starting scrape from page {page_num}...")

        while consecutive_empty_pages < max_empty_pages:
            print(f"Fetching page {page_num}...", end=" ")

            response_data = self.fetch_page(page_num)
            books = self.extract_books_from_response(response_data)

            if books:
                self.all_books.extend(books)
                print(f"Found {len(books)} books (Total: {len(self.all_books)})")
                consecutive_empty_pages = 0
            else:
                print("No books found")
                consecutive_empty_pages += 1

            page_num += 1

            # Be respectful - add a small delay between requests
            time.sleep(1)

        print(f"\nScraping complete! Total books collected: {len(self.all_books)}")
        return self.all_books

    def save_to_csv(self, filename: str = "libraff_books.csv"):
        """Save collected book data to CSV file"""
        if not self.all_books:
            print("No data to save!")
            return

        # Define CSV columns
        fieldnames = [
            "product_id",
            "item_name",
            "item_id",
            "currency",
            "price",
            "quantity",
            "stock",
            "item_category0",
            "item_category1",
            "item_category2",
            "item_list_name"
        ]

        filepath = Path(filename)

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.all_books)

            print(f"\nData saved to {filepath.absolute()}")
            print(f"Total records: {len(self.all_books)}")

            # Verify file size
            file_size = filepath.stat().st_size
            print(f"File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")

        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def run(self, output_file: str = "libraff_books.csv"):
        """Run the complete scraping process"""
        print("=" * 60)
        print("Libraff.az Book Scraper")
        print("=" * 60)

        # Scrape all pages
        self.scrape_all_pages()

        # Remove duplicates based on product_id
        unique_books = {}
        for book in self.all_books:
            product_id = book["product_id"]
            if product_id not in unique_books:
                unique_books[product_id] = book

        self.all_books = list(unique_books.values())
        print(f"After deduplication: {len(self.all_books)} unique books")

        # Save to CSV
        self.save_to_csv(output_file)

        print("\n" + "=" * 60)
        print("Scraping completed successfully!")
        print("=" * 60)


def main():
    """Main entry point"""
    scraper = LibraffScraper()
    scraper.run()


if __name__ == "__main__":
    main()

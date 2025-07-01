import cloudscraper
from bs4 import BeautifulSoup
import pyperclip
import platform

BASE_URL = "https://1337x.gameszonehub.workers.dev"  # Mirror site

def beep():
    if platform.system() == 'Windows':
        import winsound
        winsound.Beep(1000, 200)
    else:
        print('\a')  # ASCII bell for Linux/macOS

def get_search_results(query):
    query = query.replace(" ", "+")
    search_url = f"{BASE_URL}/search/{query}/1/"

    scraper = cloudscraper.create_scraper()
    response = scraper.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    if soup.title and "Just a moment" in soup.title.text:
        print("⚠️ Cloudflare still blocking even with cloudscraper.")
        return []

    table = soup.find('table', class_='table-list')
    if not table:
        print("❌ Table with class 'table-list' not found.")
        return []

    results = []
    rows = table.find_all('tr')[1:]  # Skip header row
    for row in rows:
        try:
            title_td = row.find('td', class_='coll-1 name')
            link_tag = title_td.find_all('a')[-1]
            title = link_tag.text.strip()
            detail_href = link_tag['href']
            detail_link = BASE_URL + detail_href

            seeds = row.find('td', class_='coll-2 seeds').text.strip()
            leeches = row.find('td', class_='coll-3 leeches').text.strip()
            size_td = row.find('td', class_=lambda c: c and 'coll-4' in c and 'size' in c)
            size = size_td.get_text(strip=True) if size_td else "?"

            uploader_td = row.find('td', class_='coll-5')
            uploader = uploader_td.text.strip() if uploader_td else "?"

            date_td = row.find('td', class_='coll-date')
            upload_date = date_td.text.strip() if date_td else "?"

            results.append({
                'title': title,
                'link': detail_link,
                'seeds': seeds,
                'leeches': leeches,
                'size': size,
                'uploader': uploader,
                'upload_date': upload_date
            })
        except Exception as e:
            print(f"⚠️ Skipped row due to error: {e}")
            continue
    return results

def get_magnet_link(detail_url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(detail_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    magnet = soup.find('a', href=lambda x: x and x.startswith('magnet:?'))
    return magnet['href'] if magnet else None

# Main
print("+--------------------------------------+")
print("|     Welcome to 1337x Scrapper        |")
print("+--------------------------------------+\n")

query = input("Enter Torrent Name to be searched: ")
results = get_search_results(query)

if not results:
    exit("❌ No torrents found or page was blocked.")

for idx, result in enumerate(results):
    print(f"{idx+1}. {result['title']}")
    print(f"   Size: {result['size']} | Seeds: {result['seeds']} | Leeches: {result['leeches']}")
    print(f"   Uploader: {result['uploader']} | Uploaded on: {result['upload_date']}\n")

choice = int(input("Enter the number to copy magnet link: "))
if 1 <= choice <= len(results):
    magnet_link = get_magnet_link(results[choice - 1]['link'])
    if magnet_link:
        pyperclip.copy(magnet_link)
        beep()
        print("\n✅ Magnet link copied to clipboard.")
    else:
        print("❌ Magnet link not found.")
else:
    print("❌ Invalid choice.")

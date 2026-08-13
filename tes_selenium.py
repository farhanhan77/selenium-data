from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def main():
    print("[INFO] Menyiapkan Chrome Driver otomatis...")
    
    # Konfigurasi agar Chrome jalan dengan stabil
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized") # Buka browser langsung full screen
    
    # 1. BUKA BROWSER CHROME AUTOMATION
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 2. NAVIGASI KE WEB DEMO QUOTES (Web dinamis ringan)
        url = "https://quotes.toscrape.com/js/"
        print(f"[INFO] Membuka URL: {url}")
        driver.get(url)
        
        # Beri waktu 3 detik agar JavaScript selesai merender teks
        time.sleep(15)
        
        # 3. CARI ELEMEN QUOTE PAKAI SELENIUM (By.CLASS_NAME)
        # Di Selenium, konsepnya sama kayak BeautifulSoup: cari class name-nya!
        quote_elements = driver.find_elements(By.CLASS_NAME, "quote")
        print(f"[SUCCESS] Berhasil menemukan {len(quote_elements)} kutipan via Selenium!\n")
        
        print("--- 3 Kutipan Pertama Hasil Scraping Dinamis ---")
        for i, elem in enumerate(quote_elements[:3], 1):
            # Ambil teks kutipan & penulisnya
            text = elem.find_element(By.CLASS_NAME, "text").text
            author = elem.find_element(By.CLASS_NAME, "author").text
            print(f"{i}. \"{text}\"")
            print(f"   - Penulis: {author}\n")
            
    except Exception as e:
        print(f"[ERROR] Terjadi kendala saat running Selenium: {e}")
        
    finally:
        # 4. TUTUP BROWSER KEMBALI
        print("[INFO] Menutup browser...")
        driver.quit()

if __name__ == "__main__":
    main()
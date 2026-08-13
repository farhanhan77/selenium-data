from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import psycopg2
from psycopg2.extras import execute_values
import time

# ==========================================
# 1. KONFIGURASI DATABASE
# ==========================================
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "crypto_db"
DB_USER = "postgres"
DB_PASSWORD = "admin123"

# ==========================================
# 2. FUNGSI SCRAPE SELENIUM (EXTRACT & TRANSFORM)
# ==========================================
def scrape_all_quotes():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://quotes.toscrape.com/js/"
    driver.get(url)
    
    quotes_data = []
    page_number = 1

    try:
        while True:
            print(f"   [Scraping] Memproses Halaman {page_number}...")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "quote"))
            )
            
            quote_elements = driver.find_elements(By.CLASS_NAME, "quote")
            for elem in quote_elements:
                text = elem.find_element(By.CLASS_NAME, "text").text
                author = elem.find_element(By.CLASS_NAME, "author").text
                # Simpan dalam format tuple untuk PostgreSQL
                quotes_data.append((text, author))

            # Trigger Klik tombol 'Next'
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "li.next > a")
                next_button.click()
                page_number += 1
                time.sleep(1)
            except Exception:
                print("   [INFO] Mencapai halaman terakhir.")
                break

    except Exception as e:
        print(f"[ERROR] Kendala saat scraping: {e}")

    finally:
        driver.quit()

    return quotes_data

# ==========================================
# 3. FUNGSI SETUP TABEL & INGESTION (LOAD)
# ==========================================
def save_to_postgres(data_list):
    if not data_list:
        print("[INFO] Tidak ada data untuk disimpan.")
        return

    create_table_query = """
    CREATE TABLE IF NOT EXISTS quotes (
        id SERIAL PRIMARY KEY,
        quote_text TEXT NOT NULL,
        author VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    insert_query = """
    INSERT INTO quotes (quote_text, author)
    VALUES %s;
    """

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            client_encoding='utf8'
        )
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        # Buat tabel jika belum ada
        cursor.execute(create_table_query)

        # Batch insert seluruh data sekaligus
        execute_values(cursor, insert_query, data_list)
        conn.commit()

        print(f"[SUCCESS] Berhasil memasukkan {len(data_list)} data kutipan ke tabel 'quotes' PostgreSQL!")

    except Exception as error:
        print(f"[ERROR] Gagal menyimpan ke PostgreSQL: {error}")
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ==========================================
# 4. EKSEKUSI PIPELINE
# ==========================================
if __name__ == "__main__":
    print("[INFO] Memulai Pipeline ETL Selenium -> PostgreSQL...")
    
    # Step 1: Extract & Transform via Selenium
    print("[1/2] Membuka browser & mengumpulkan data kutipan...")
    quotes = scrape_all_quotes()
    print(f"      Total data terkumpul: {len(quotes)} kutipan.")

    # Step 2: Load ke PostgreSQL
    print("[2/2] Memasukkan data ke PostgreSQL...")
    save_to_postgres(quotes)
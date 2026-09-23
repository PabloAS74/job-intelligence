from app.scraper.remotive import RemotiveScraper

def main():
    scraper = RemotiveScraper()
    ofertas = scraper.scrape("python")
    
    print(f"\n✅ ¡Se han encontrado {len(ofertas)} ofertas!\n")
    
    for i, oferta in enumerate(ofertas[:3]):
        print(f"--- Oferta {i+1} ---")
        print(f"Puesto:  {oferta.title}")
        # Cambiamos oferta.company_name por oferta.company
        print(f"Empresa: {oferta.company}") 
        print(f"URL:     {oferta.url}")
        print("-" * 20)

if __name__ == "__main__":
    main()
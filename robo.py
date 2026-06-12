from playwright.sync_api import sync_playwright
import time

PORTAL_URL = "https://portal.gooroocredito.com.br"

EMAIL = "bruno.mascio@gooroocredito.com.br"
SENHA = "Admin@3256"


def executar_teste_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=700
        )

        context = browser.new_context()
        page = context.new_page()

        print("Abrindo portal...")
        page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=60000)

        time.sleep(8)

        print("URL atual:", page.url)
        page.screenshot(path="debug_login.png", full_page=True)

        print("Procurando campos...")

        campos = page.locator("input")
        qtd = campos.count()

        print(f"Quantidade de inputs encontrados: {qtd}")

        for i in range(qtd):
            try:
                print(
                    i,
                    campos.nth(i).get_attribute("type"),
                    campos.nth(i).get_attribute("name"),
                    campos.nth(i).get_attribute("placeholder")
                )
            except:
                pass

        input("Veja o navegador. Pressione ENTER para continuar...")

        browser.close()


if __name__ == "__main__":
    executar_teste_login()

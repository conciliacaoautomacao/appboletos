from playwright.sync_api import sync_playwright
import time

PORTAL_URL = "https://portal.gooroocredito.com.br"
COBRANCAS_URL = "https://portal.gooroocredito.com.br/painel/cobrancas-menu/"

EMAIL = "bruno.mascio@gooroocredito.com.br"
SENHA = "Admin@3256"


def executar_teste_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=700
        )

        page = browser.new_page()

        print("Abrindo portal...")
        page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=60000)

        page.fill('input[name="login"]', EMAIL)
        page.fill('input[name="password"]', SENHA)

        print("Resolva o captcha manualmente e clique em ENTRAR no navegador.")
        print("Depois que o portal abrir o painel, volte aqui e pressione ENTER.")
        
        input("Pressione ENTER após concluir o login...")
        
        print("Acessando Cobranças...")
        page.goto(COBRANCAS_URL, wait_until="domcontentloaded", timeout=60000)

        time.sleep(5)

        print("URL atual:", page.url)
        page.screenshot(path="debug_cobrancas.png", full_page=True)

        input("Pressione ENTER para fechar...")
        browser.close()


if __name__ == "__main__":
    executar_teste_login()

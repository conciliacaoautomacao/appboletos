from playwright.sync_api import sync_playwright
import time

PORTAL_URL = "https://portal.gooroocredito.com.br"
COBRANCAS_URL = "https://portal.gooroocredito.com.br/painel/cobrancas-menu/"

EMAIL = "bruno.mascio@gooroocred.com.br"
SENHA = "Admin@3256"


def executar_teste_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500
        )

        page = browser.new_page()

        # 1. Abrir portal
        page.goto(PORTAL_URL, wait_until="networkidle")

        # 2. Preencher login
        page.fill('input[type="email"]', EMAIL)

        # 3. Preencher senha
        page.fill('input[type="password"]', SENHA)

        # 4. Clicar em entrar
        page.click('button:has-text("ENTRAR")')

        # 5. Esperar entrar no painel
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        # 6. Abrir tela de cobranças
        page.goto(COBRANCAS_URL, wait_until="networkidle")

        # 7. Validar tela
        page.wait_for_selector("text=Cobranças", timeout=30000)

        print("✅ Login e acesso à tela de Cobranças funcionaram.")

        input("Pressione ENTER para fechar o navegador...")
        browser.close()


if __name__ == "__main__":
    executar_teste_login()

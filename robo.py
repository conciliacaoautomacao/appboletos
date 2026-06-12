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

        time.sleep(5)

        print("URL atual:", page.url)
        page.screenshot(path="debug_login.png", full_page=True)

        print("Procurando campo de e-mail...")

        campo_email = page.locator(
            'input[name="email"], input[type="email"], input[placeholder*="E-mail"], input[placeholder*="email"]'
        ).first

        campo_email.wait_for(timeout=60000)
        campo_email.fill(EMAIL)

        print("Procurando campo de senha...")

        campo_senha = page.locator(
            'input[name="password"], input[type="password"], input[placeholder*="Senha"], input[placeholder*="senha"]'
        ).first

        campo_senha.wait_for(timeout=60000)
        campo_senha.fill(SENHA)

        print("Clicando em entrar...")

        page.locator(
            'button:has-text("ENTRAR"), button:has-text("Entrar")'
        ).first.click()

        time.sleep(5)

        print("URL depois do login:", page.url)
        page.screenshot(path="debug_pos_login.png", full_page=True)

        input("Pressione ENTER para fechar...")
        browser.close()


if __name__ == "__main__":
    executar_teste_login()

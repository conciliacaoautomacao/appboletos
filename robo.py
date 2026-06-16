from playwright.sync_api import sync_playwright
import time
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

PORTAL_URL = "https://portal.gooroocredito.com.br"
COBRANCAS_URL = "https://portal.gooroocredito.com.br/painel/cobrancas-menu/"

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

EMAIL = os.getenv("PORTAL_EMAIL")
SENHA = os.getenv("PORTAL_SENHA")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

NOSSO_NUMERO_TESTE = "175119"
VALOR_PAGO_TESTE = "1.446,50"
DATA_PAGAMENTO_TESTE = "16/06/2026"

def buscar_boletos_pendentes():

    res = (
        supabase
        .table("robo_boletos")
        .select("*")
        .eq("status_robo", "PENDENTE")
        .order("id")
        .execute()
    )

    return res.data


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

        print("Preenchendo Nosso Número...")

        campo_nosso_numero = page.get_by_role(
            "textbox",
            name="Nosso número"
        )

        campo_nosso_numero.wait_for(timeout=30000)
        campo_nosso_numero.click()
        campo_nosso_numero.fill(NOSSO_NUMERO_TESTE)

        time.sleep(2)

        print("Clicando em Aplicar Filtros...")

        botao_filtro = page.get_by_role(
            "button",
            name="Aplicar Filtros"
        )

        botao_filtro.click()
        time.sleep(5)

        print("Lendo linhas da tabela...")

        linhas = page.locator("table tbody tr")
        qtd_linhas = linhas.count()

        print(f"Total de linhas encontradas: {qtd_linhas}")

        if qtd_linhas == 0:
            print("Nenhum boleto encontrado.")
            input("Pressione ENTER para fechar...")
            browser.close()
            return

        texto_linha = linhas.first.inner_text()
        print("LINHA:", texto_linha)

        if "Em aberto" not in texto_linha:
            print("Boleto não está Em aberto. Não será processado.")
            input("Pressione ENTER para fechar...")
            browser.close()
            return

        print("Boleto está Em aberto. Abrindo edição...")

        botao_olho = linhas.first.locator("button").first
        botao_olho.wait_for(timeout=30000)

        botao_olho.evaluate("""
            el => {
                el.scrollIntoView({block: 'center', inline: 'center'});
                el.click();
            }
        """)

        time.sleep(5)

        page.screenshot(
            path="debug_edicao_aberta.png",
            full_page=True
        )

        print("Preenchendo Valor pago...")

        campo_valor_pago = page.get_by_role(
            "textbox",
            name="Valor pago"
        )

        campo_valor_pago.wait_for(timeout=30000)
        campo_valor_pago.scroll_into_view_if_needed()
        campo_valor_pago.click(force=True)

        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(VALOR_PAGO_TESTE)

        time.sleep(1)

        print("Valor pago preenchido.")

        print("Abrindo Data do pagamento...")

        campo_data_pagamento = page.get_by_role(
            "textbox",
            name="Data do pagamento"
        )

        campo_data_pagamento.wait_for(timeout=30000)
        campo_data_pagamento.scroll_into_view_if_needed()

        container_data = page.locator(
            "label:has-text('Data do pagamento')"
        ).locator(
            "xpath=ancestor::div[contains(@class, 'v-input')][1]"
        )

        print("Clicando no ícone do calendário...")

        campo_data_pagamento.click(force=True)
        time.sleep(1)

        # força abrir o datepicker via seta para baixo
        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)

        time.sleep(2)

        page.screenshot(
            path="debug_apos_clique_icone_calendario.png",
            full_page=True
        )

        dia, mes, ano = DATA_PAGAMENTO_TESTE.split("/")
        dia_sem_zero = str(int(dia))

        print(f"Selecionando dia {dia_sem_zero}...")

        dias = page.locator("button.v-btn").filter(
            has_text=dia_sem_zero
        )

        qtd_dias = dias.count()
        print("Dias encontrados:", qtd_dias)

        if qtd_dias == 0:
            raise Exception("Dia não encontrado no calendário.")

        dias.filter(has_text=dia_sem_zero).first.click(force=True)

        time.sleep(1)

        print("Data selecionada.")

        print("Selecionando Status Pago dentro da edição...")

        campo_status_edicao = page.locator(
            "label:has-text('Status')"
        ).last.locator(
            "xpath=ancestor::div[contains(@class, 'v-input')][1]//input[@type='text']"
        )

        campo_status_edicao.click(force=True)

        time.sleep(1)

        opcao_pago = page.locator(".v-list-item").filter(
            has_text="Pago"
        ).last

        opcao_pago.click(force=True)

        time.sleep(1)

        page.screenshot(
            path="debug_status_pago_dentro_edicao.png",
            full_page=True
        )

        print("Clicando em SALVAR...")

        botao_salvar = page.get_by_role(
            "button",
            name="SALVAR"
        ).last

        botao_salvar.wait_for(timeout=30000)
        botao_salvar.click(force=True)

        time.sleep(5)

        page.screenshot(
            path="debug_apos_salvar.png",
            full_page=True
        )

        print("Processo salvo. Confira o resultado.")

        input("Confira se salvou corretamente. Pressione ENTER para fechar.")

        browser.close()


if __name__ == "__main__":

    boletos = buscar_boletos_pendentes()

    print(
        f"Boletos pendentes encontrados: {len(boletos)}"
    )

    for b in boletos:
        print(
            b["id"],
            b["nosso_numero"],
            b["valor_pago"],
            b["data_do_pagamento"]
        )

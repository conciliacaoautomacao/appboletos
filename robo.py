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

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def buscar_boletos_pendentes():
    res = (
        supabase
        .table("robo_boletos")
        .select("*")
        .eq("status_robo", "PENDENTE")
        .order("created_at")
        .execute()
    )
    return res.data


def atualizar_boleto(nosso_numero, dados):
    supabase.table("robo_boletos").update(dados).eq(
        "nosso_numero",
        str(nosso_numero)
    ).execute()


def formatar_valor_br(valor):
    return (
        f"{float(valor):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_data_br(data_bd):
    ano, mes, dia = str(data_bd).split("-")
    return f"{dia}/{mes}/{ano}"


def identificar_status_portal(texto_linha):
    texto = texto_linha.lower()

    if "em aberto" in texto:
        return "Em aberto"
    if "pago" in texto:
        return "Pago"
    if "baixado" in texto:
        return "Baixado"
    if "cancelado" in texto:
        return "Cancelado"
    if "liquidado" in texto:
        return "Liquidado"

    return "DESCONHECIDO"


def fazer_login(page):
    print("Abrindo portal...")
    page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=60000)

    page.fill('input[name="login"]', EMAIL)
    page.fill('input[name="password"]', SENHA)

    print("Resolva o captcha manualmente e clique em ENTRAR no navegador.")
    print("Depois que o portal abrir o painel, volte aqui e pressione ENTER.")

    print("Aguardando login ser concluído automaticamente...")

    page.wait_for_url(
        "**/painel/**",
        timeout=180000
    )
    
    print("Login detectado. Acessando Cobranças...")
    page.goto(COBRANCAS_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)


def processar_boleto(page, boleto):
    nosso_numero = str(boleto["nosso_numero"])
    valor_pago = formatar_valor_br(boleto["valor_pago"])
    data_pagamento = formatar_data_br(boleto["data_do_pagamento"])

    print("--------------------------------")
    print("Processando boleto:", nosso_numero)
    print("Valor:", valor_pago)
    print("Data:", data_pagamento)

    atualizar_boleto(nosso_numero, {
        "status_robo": "PROCESSANDO",
        "etapa": "INICIADO",
        "tentativas": int(boleto.get("tentativas") or 0) + 1
    })

    try:
        page.goto(COBRANCAS_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        campo_nosso_numero = page.get_by_role(
            "textbox",
            name="Nosso número"
        )

        campo_nosso_numero.wait_for(timeout=30000)
        campo_nosso_numero.click(force=True)
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        campo_nosso_numero.fill(nosso_numero)

        time.sleep(1)

        botao_filtro = page.get_by_role(
            "button",
            name="Aplicar Filtros"
        )

        botao_filtro.click()
        time.sleep(5)

        linhas = page.locator("table tbody tr")
        qtd_linhas = linhas.count()

        if qtd_linhas == 0:
            atualizar_boleto(nosso_numero, {
                "status_robo": "ERRO",
                "status_boleto_portal": "NAO_ENCONTRADO",
                "mensagem_retorno": "Boleto não encontrado no portal",
                "etapa": "PESQUISA",
                "processed_at": datetime.now().isoformat()
            })
            return

        texto_linha = linhas.first.inner_text()
        status_portal = identificar_status_portal(texto_linha)

        if status_portal != "Em aberto":
            atualizar_boleto(nosso_numero, {
                "status_robo": "NAO_PROCESSADO",
                "status_boleto_portal": status_portal,
                "mensagem_retorno": f"Não processado - boleto já {status_portal}",
                "etapa": "VALIDACAO_STATUS",
                "processed_at": datetime.now().isoformat()
            })
            print(f"Não processado - boleto já {status_portal}")
            return

        atualizar_boleto(nosso_numero, {
            "status_boleto_portal": "Em aberto",
            "etapa": "BOLETO_EM_ABERTO"
        })

        botao_olho = linhas.first.locator("button").first
        botao_olho.wait_for(timeout=30000)

        botao_olho.evaluate("""
            el => {
                el.scrollIntoView({block: 'center', inline: 'center'});
                el.click();
            }
        """)

        time.sleep(5)

        campo_valor_pago = page.get_by_role(
            "textbox",
            name="Valor pago"
        )

        campo_valor_pago.wait_for(timeout=30000)
        campo_valor_pago.scroll_into_view_if_needed()
        campo_valor_pago.click(force=True)

        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type(valor_pago)

        time.sleep(1)

        campo_data_pagamento = page.get_by_role(
            "textbox",
            name="Data do pagamento"
        )

        campo_data_pagamento.wait_for(timeout=30000)
        campo_data_pagamento.scroll_into_view_if_needed()
        campo_data_pagamento.click(force=True)

        time.sleep(1)

        page.keyboard.press("ArrowDown")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)

        dia, mes, ano = data_pagamento.split("/")
        dia_sem_zero = str(int(dia))

        dias = page.locator("button.v-btn").filter(
            has_text=dia_sem_zero
        )

        if dias.count() == 0:
            raise Exception("Dia não encontrado no calendário.")

        dias.first.click(force=True)

        time.sleep(1)

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

        botao_salvar = page.get_by_role(
            "button",
            name="SALVAR"
        ).last

        botao_salvar.wait_for(timeout=30000)
        botao_salvar.click(force=True)

        time.sleep(5)

        atualizar_boleto(nosso_numero, {
            "status_robo": "SUCESSO",
            "status_boleto_portal": "Pago",
            "mensagem_retorno": "Baixa realizada com sucesso",
            "etapa": "FINALIZADO",
            "processed_at": datetime.now().isoformat()
        })

        print("Baixa realizada com sucesso:", nosso_numero)

    except Exception as e:
        atualizar_boleto(nosso_numero, {
            "status_robo": "ERRO",
            "mensagem_retorno": str(e),
            "etapa": "ERRO",
            "processed_at": datetime.now().isoformat()
        })

        print("Erro ao processar boleto:", nosso_numero, e)


if __name__ == "__main__":
    boletos = buscar_boletos_pendentes()

    print(f"Boletos pendentes encontrados: {len(boletos)}")

    if not boletos:
        exit()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=700
        )

        page = browser.new_page()

        fazer_login(page)

        for boleto in boletos:
            processar_boleto(page, boleto)

        print("Fila finalizada.")

        time.sleep(3)
        
        browser.close()

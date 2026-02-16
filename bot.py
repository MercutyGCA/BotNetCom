import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from datetime import datetime



# =====================================
# CONFIGURAÇÕES
# =====================================

TOKEN = ""
SPREADSHEET_ID = "1TZ3W0kvBKrua0hQr2mY4pRCPNWkATfRpsDa413Wnnvo"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# =====================================
# CONEXÃO GOOGLE SHEETS
# =====================================

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

print("Planilha conectada!")

sheet_clientes = client.open_by_key(SPREADSHEET_ID).worksheet("CONTRATOS")
sheet_logs = client.open_by_key(SPREADSHEET_ID).worksheet("LOGS")


# =====================================
# FUNÇÃO DE BUSCA
# =====================================

def buscar_por_cpf(cpf_digitado):
    cpf_digitado = cpf_digitado.replace(".", "").replace("-", "").strip()
    dados = sheet.get_all_records()

    for linha in dados:
        cpf_planilha = str(linha["CPF"]).replace(".", "").replace("-", "").strip()

        if cpf_planilha == cpf_digitado:
            return linha["NOME"], linha["LINK"]

    return None, None

# =====================================
# FUNÇÃO DE REGISTRO DE LOG
# =====================================

def registrar_log(user, cpf, status):
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    sheet_logs.append_row([
        data_hora,
        user.id,
        user.username,
        cpf,
        status
    ])

# =====================================
# HANDLER DO BOT
# =====================================

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpf = update.message.text.strip()
    user = update.message.from_user

    nome, link = buscar_por_cpf(cpf)

    if nome:
        resposta = (
            f"✅ Cliente encontrado!\n\n"
            f"👤 Nome: {nome}\n"
            f"📄 Contrato: {link}"
        )
        registrar_log(user, cpf, "ENCONTRADO")
    else:
        resposta = "❌ CPF não encontrado."
        registrar_log(user, cpf, "NAO_ENCONTRADO")

    await update.message.reply_text(resposta)


# =====================================
# INICIAR BOT
# =====================================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

print("🤖 Bot rodando...")
app.run_polling()

from config import CURRENCY

# /add
ADD_USAGE = f"Uso: /add <monto> <descripción> [@username]\nEjemplo: /add 50.0 supermercado"
ADD_INVALID_AMOUNT = "El monto debe ser un número. Ej: /add 50.0 tienda"
ADD_ZERO_AMOUNT = "El monto debe ser mayor a 0."
ADD_NO_DESCRIPTION = "Agrega una descripción. Ej: /add 50.0 supermercado"

# Conversation flow
ASK_AMOUNT = "¿Cuánto?"
ASK_AMOUNT_INVALID = "Ingresa un número válido. ¿Cuánto?"
ASK_AMOUNT_ZERO = "El monto debe ser mayor a 0. ¿Cuánto?"
ASK_DESCRIPTION = "¿Descripción?\n_(si pagó otra persona, agrega @username al final)_"
ASK_DESCRIPTION_EMPTY = "Agrega una descripción.\n_(si pagó otra persona, agrega @username al final)_"

# Category selection
SELECT_CATEGORY = "Selecciona una categoría:"
CATEGORY_ERROR = "Algo salió mal. Intenta /add de nuevo."

# /list, /mine
NO_EXPENSES = "No hay gastos registrados este mes."
NO_MY_EXPENSES = "No tienes gastos registrados este mes."

# /adduser, /removeuser
ADDUSER_USAGE = "Uso: /adduser @username <telegram_id>\nEj: /adduser @ariadna 987654321"
ADDUSER_MISSING_ID = "También necesitas el ID. Uso: /adduser @username <telegram_id>"
ADDUSER_INVALID_ID = "El ID debe ser un número."
ADDUSER_SUCCESS = "✅ @{username} agregado."
REMOVEUSER_USAGE = "Uso: /removeuser @username\nEj: /removeuser @ariadna"
REMOVEUSER_SUCCESS = "✅ @{username} eliminado."

# Access control
NO_ACCESS = "⛔ No tienes acceso a este bot."
ADMIN_ONLY_ADD = "⛔ Solo el admin puede agregar usuarios."
ADMIN_ONLY_REMOVE = "⛔ Solo el admin puede eliminar usuarios."

# Misc
CANCELLED = "Cancelado."
TIMEOUT = "⏱ Tiempo agotado. Usa /add para intentar de nuevo."

# Help
HELP_TEXT = (
    "*Comandos disponibles:*\n\n"
    "/add — Registrar gasto (paso a paso)\n"
    f"/add <monto> <descripción> — Registrar gasto rápido\n"
    f"/add <monto> <descripción> @username — Registrar gasto de otro\n"
    "/list — Ver todos los gastos del mes\n"
    "/total — Ver total del mes\n"
    "/mine — Ver mis gastos del mes\n"
    "/summary — Ver cuánto aportó cada quien\n"
    "/categories — Ver gastos por categoría\n"
    "/help — Ver esta ayuda"
)

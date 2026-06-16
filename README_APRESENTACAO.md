# Bot de busca de precos no Telegram

Arquivos:

- `bot_busca_precos_gpu.py`: bot funcional com scraping, comparacao, alerta, historico SQLite e exportacao CSV.
- `requirements_bot.txt`: bibliotecas necessarias.

## Como executar no PowerShell

```powershell
cd "C:\Users\F4pla\Documents\Codex\2026-05-30\files-mentioned-by-the-user-telegranbotexemplo\outputs"
python -m pip install -r requirements_bot.txt
$env:TELEGRAM_BOT_TOKEN="SEU_TOKEN_DO_BOTFATHER"
python bot_busca_precos_gpu.py
```

## Comandos para demonstrar

- `/start` ou `/menu`: abre o menu.
- `/gpu`: coleta os precos das RTX 5050.
- `/cpu`: coleta os precos do Ryzen 5 5600GT.
- `/memoria`: coleta os precos das memorias Kingston Fury 8GB e 16GB.
- `/gabinete`: coleta os precos do Corsair 3000D RGB Airflow.
- `/todos`: coleta todos os produtos cadastrados.
- `/comparar`: compara todos os produtos pelo menor preco.
- `/comparar ryzen`: compara apenas os produtos que combinam com o termo.
- `/buscar rtx`: busca pelo termo digitado.
- `/alerta 2200`: mostra produtos abaixo do limite.
- `/alerta 200 memoria`: mostra memorias abaixo de R$ 200.
- `/historico`: usa SQLite e pandas para mostrar menor, maior e media.
- `/exportar`: envia um CSV pelo Telegram.
- `/exportar memoria`: envia um CSV apenas da categoria/termo buscado.

## Observacao importante

Se algum site mudar o HTML ou bloquear scraping, o bot mostra uma observacao no resultado em vez de travar. Para trabalho de faculdade, isso e bom de comentar: scraping depende da estrutura dos sites.

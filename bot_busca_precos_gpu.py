from __future__ import annotations

import csv
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None

try:
    import pandas as pd
except Exception:
    pd = None

try:
    import telebot as tl
except Exception:
    tl = None


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("PRICE_DB_PATH", str(BASE_DIR / "precos_hardware.db")))
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "token_bot_aqui")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


@dataclass(frozen=True)
class Product:
    key: str
    categoria: str
    grupo: str
    loja: str
    nome: str
    url: str


PRODUCTS = [
    Product(
        key="gpu_rtx5050_terabyte",
        categoria="gpu",
        grupo="GeForce RTX 5050 8GB",
        loja="Terabyte",
        nome="MSI GeForce RTX 5050 Gaming 8GB",
        url="https://www.terabyteshop.com.br/produto/40399/placa-de-video-msi-nvidia-geforce-rtx-5050-gaming-8gb-gddr6-dlss-ray-tracing",
    ),
    Product(
        key="gpu_rtx5050_kabum",
        categoria="gpu",
        grupo="GeForce RTX 5050 8GB",
        loja="KaBuM",
        nome="MSI GeForce RTX 5050 Ventus 2X OC 8GB",
        url="https://www.kabum.com.br/produto/888165/placa-de-video-msi-geforce-rtx-5050-8g-ventus-2x-oc-nvidia-geforce-8gb-gddr6-128-bits-2617-mhz-dlss-4-ray-tracing-g5050-8v2c",
    ),
    Product(
        key="gpu_rtx5050_pichau",
        categoria="gpu",
        grupo="GeForce RTX 5050 8GB",
        loja="Pichau",
        nome="Zotac GeForce RTX 5050 Gaming Twin Edge OC 8GB",
        url="https://www.pichau.com.br/placa-de-video-zotac-geforce-rtx-5050-gaming-twin-edge-oc-8gb-gddr6-128-bit-zt-b50500h-10m-nac",
    ),
    Product(
        key="gpu_rtx5050_amazon",
        categoria="gpu",
        grupo="GeForce RTX 5050 8GB",
        loja="Amazon",
        nome="MSI GeForce RTX 5050 Shadow 2X OC 8GB",
        url="https://www.amazon.com.br/MSI-GeForce-RTX-5050-SHADOW/dp/B0FG33PH79",
    ),
    Product(
        key="cpu_ryzen5600gt_kabum",
        categoria="cpu",
        grupo="Ryzen 5 5600GT",
        loja="KaBuM",
        nome="AMD Ryzen 5 5600GT AM4",
        url="https://www.kabum.com.br/produto/520368/processador-amd-ryzen-5-5600gt-3-6-ghz-4-6ghz-max-turbo-cache-4mb-6-nucleos-12-threads-am4-100-100001488box",
    ),
    Product(
        key="cpu_ryzen5600gt_pichau",
        categoria="cpu",
        grupo="Ryzen 5 5600GT",
        loja="Pichau",
        nome="AMD Ryzen 5 5600GT AM4",
        url="https://www.pichau.com.br/processador-amd-ryzen-5-5600gt-6-core-12-threads-3-6ghz-4-6ghz-turbo-cache-19mb-am4-100-100001488box",
    ),
    Product(
        key="cpu_ryzen5600gt_terabyte",
        categoria="cpu",
        grupo="Ryzen 5 5600GT",
        loja="Terabyte",
        nome="AMD Ryzen 5 5600GT AM4",
        url="https://www.terabyteshop.com.br/produto/27314/processador-amd-ryzen-5-5600gt-36ghz-46ghz-turbo-6-cores-12-threads-cooler-wraith-stealth-am4-100-100001488box",
    ),
    Product(
        key="cpu_ryzen5600gt_amazon",
        categoria="cpu",
        grupo="Ryzen 5 5600GT",
        loja="Amazon",
        nome="AMD Ryzen 5 5600GT AM4",
        url="https://www.amazon.com.br/Processador-AMD-Ryzen-5600GT-Threads/dp/B0CQ4DTJYX",
    ),
    Product(
        key="ram_kingston8gb_kabum",
        categoria="memoria",
        grupo="Kingston Fury Beast DDR4 3200MHz 8GB",
        loja="KaBuM",
        nome="Kingston Fury Beast DDR4 3200MHz 8GB",
        url="https://www.kabum.com.br/produto/172365/memoria-ram-kingston-fury-beast-8gb-3200mhz-ddr4-cl16-preto-kf432c16bb-8",
    ),
    Product(
        key="ram_kingston16gb_kabum",
        categoria="memoria",
        grupo="Kingston Fury Beast DDR4 3200MHz 16GB",
        loja="KaBuM",
        nome="Kingston Fury Beast DDR4 3200MHz 16GB",
        url="https://www.kabum.com.br/produto/172366/memoria-ram-kingston-fury-beast-16gb-3200mhz-ddr4-cl16-preto-kf432c16bb1-16",
    ),
    Product(
        key="ram_kingston8gb_terabyte",
        categoria="memoria",
        grupo="Kingston Fury Beast DDR4 3200MHz 8GB",
        loja="Terabyte",
        nome="Kingston Fury Beast DDR4 3200MHz 8GB",
        url="https://www.terabyteshop.com.br/produto/19314/memoria-kingston-fury-beast-8gb-3200mhz-ddr4-black-kf432c16bb8",
    ),
    Product(
        key="ram_kingston16gb_terabyte",
        categoria="memoria",
        grupo="Kingston Fury Beast DDR4 3200MHz 16GB",
        loja="Terabyte",
        nome="Kingston Fury Beast DDR4 3200MHz 16GB",
        url="https://www.terabyteshop.com.br/produto/21175/memoria-kingston-fury-beast-16gb-3200mhz-ddr4-preto-kf432c16bb16",
    ),
    Product(
        key="ram_kingston8gb_pichau",
        categoria="memoria",
        grupo="Kingston Fury Beast DDR4 3200MHz 8GB",
        loja="Pichau",
        nome="Kingston Fury Beast DDR4 3200MHz 8GB",
        url="https://www.pichau.com.br/memoria-kingston-fury-beast-8gb-1x8gb-ddr4-3200mhz-c16-preta-kf432c16bb-8",
    ),
    Product(
        key="ram_kingston16gb_pichau",
        categoria="memoria",
        grupo="Kingston Fury Beast DDR4 3200MHz 16GB",
        loja="Pichau",
        nome="Kingston Fury Beast DDR4 3200MHz 16GB",
        url="https://www.pichau.com.br/memoria-kingston-fury-beast-16gb-1x16gb-ddr4-3200mhz-c16-preto-kf432c16bb1-16",
    ),
    Product(
        key="ram_kingston8gb_amazon",
        categoria="memoria",
        grupo="Kingston Fury Beast DDR4 3200MHz 8GB",
        loja="Amazon",
        nome="Kingston Fury Beast DDR4 3200MHz 8GB",
        url="https://www.amazon.com.br/KF432C16BB-Mem%C3%B3ria-3200Mhz-desktop-gamers/dp/B097K5J1SB",
    ),
    Product(
        key="ram_kingston16gb_amazon",
        categoria="memoria",
        grupo="Kingston Fury Beast DDR4 3200MHz 16GB",
        loja="Amazon",
        nome="Kingston Fury Beast DDR4 3200MHz 16GB",
        url="https://www.amazon.com.br/KF432C16BB1-16-Mem%C3%B3ria-3200Mhz-desktop/dp/B097K2MRS3",
    ),
    Product(
        key="gabinete_corsair3000d_pichau",
        categoria="gabinete",
        grupo="Corsair 3000D RGB Airflow",
        loja="Pichau",
        nome="Gabinete Gamer Corsair 3000D RGB Airflow",
        url="https://www.pichau.com.br/gabinete-gamer-corsair-3000d-airflow-rgb-mid-tower-lateral-de-vidro-com-3-fans-preto-cc-9011255-ww",
    ),
    Product(
        key="gabinete_corsair3000d_kabum",
        categoria="gabinete",
        grupo="Corsair 3000D RGB Airflow",
        loja="KaBuM",
        nome="Gabinete Gamer Corsair 3000D RGB Airflow",
        url="https://www.kabum.com.br/produto/469168/gabinete-gamer-corsair-3000d-rgb-airflow-mid-tower-atx-lateral-em-vidro-temperado-com-fan-preto-cc-9011255-ww",
    ),
]

PRICE_RE = re.compile(r"R\$\s*\d[\d.,\s]*(?:[,.]\s*\d{2})?")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def brl_to_float(text: Any) -> Optional[float]:
    if text is None:
        return None

    raw_text = str(text)
    match = re.search(r"\d[\d.,\s]*", raw_text)
    if not match:
        return None

    raw = re.sub(r"\s+", "", match.group(0))
    raw = re.sub(r"[^0-9,.]", "", raw)
    if not raw:
        return None

    if "," in raw and "." in raw:
        if raw.rfind(",") > raw.rfind("."):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "," in raw:
        parts = raw.split(",")
        if len(parts[-1]) in (1, 2):
            raw = raw.replace(".", "").replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "." in raw:
        parts = raw.split(".")
        if len(parts[-1]) in (1, 2):
            raw = raw.replace(",", "")
        else:
            raw = raw.replace(".", "")

    try:
        return float(raw)
    except ValueError:
        return None


def format_brl(value: Optional[float]) -> str:
    if value is None:
        return "preco indisponivel"
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS historico_precos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_key TEXT NOT NULL,
                categoria TEXT NOT NULL DEFAULT 'geral',
                grupo TEXT NOT NULL DEFAULT '',
                loja TEXT NOT NULL,
                nome TEXT NOT NULL,
                url TEXT NOT NULL,
                preco REAL,
                preco_texto TEXT,
                status TEXT NOT NULL,
                erro TEXT,
                coletado_em TEXT NOT NULL
            )
            """
        )
        existing_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(historico_precos)").fetchall()
        }
        if "categoria" not in existing_columns:
            conn.execute(
                "ALTER TABLE historico_precos ADD COLUMN categoria TEXT NOT NULL DEFAULT 'geral'"
            )
        if "grupo" not in existing_columns:
            conn.execute(
                "ALTER TABLE historico_precos ADD COLUMN grupo TEXT NOT NULL DEFAULT ''"
            )


def save_result(result: Dict[str, Any]) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO historico_precos
            (produto_key, categoria, grupo, loja, nome, url, preco, preco_texto, status, erro, coletado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result["produto_key"],
                result["categoria"],
                result["grupo"],
                result["loja"],
                result["nome"],
                result["url"],
                result["preco"],
                result["preco_texto"],
                result["status"],
                result["erro"],
                result["coletado_em"],
            ),
        )


def extract_title(soup: BeautifulSoup, fallback: str) -> str:
    selectors = ["#productTitle", "h1", 'meta[property="og:title"]', "title"]
    for selector in selectors:
        tag = soup.select_one(selector)
        if not tag:
            continue
        text = tag.get("content") if tag.name == "meta" else tag.get_text(" ", strip=True)
        text = clean_text(text)
        if text:
            return text[:180]
    return fallback


def flatten_json(data: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(data, dict):
        yield data
        for value in data.values():
            yield from flatten_json(value)
    elif isinstance(data, list):
        for item in data:
            yield from flatten_json(item)


def jsonld_candidates(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    candidates = []
    scripts = soup.find_all("script", attrs={"type": re.compile("ld\\+json", re.I)})
    for script in scripts:
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue

        for obj in flatten_json(data):
            if "price" not in obj:
                continue
            price = brl_to_float(obj.get("price"))
            if price is None:
                continue
            candidates.append(
                {
                    "value": price,
                    "text": str(obj.get("price")),
                    "context": "jsonld offer price",
                    "source": "jsonld",
                }
            )
    return candidates


def selector_candidates(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    candidates = []
    selectors = [
        '[itemprop="price"]',
        'meta[property="product:price:amount"]',
        'meta[property="og:price:amount"]',
        'meta[name="twitter:data1"]',
        "#corePrice_feature_div .a-price .a-offscreen",
        "#corePrice_feature_div .a-offscreen",
        ".apexPriceToPay .a-offscreen",
        "#price_inside_buybox",
        "#priceblock_ourprice",
        "[data-testid*=price]",
        "[class*=price]",
        "[class*=Price]",
        "[class*=preco]",
        "[class*=Preco]",
        "[class*=valor]",
        "[class*=Valor]",
    ]

    for selector in selectors:
        for tag in soup.select(selector)[:20]:
            text = tag.get("content") or tag.get("value") or tag.get_text(" ", strip=True)
            text = clean_text(text)
            price = brl_to_float(text)
            if price is None:
                continue
            context = clean_text(tag.parent.get_text(" ", strip=True) if tag.parent else text)
            candidates.append(
                {
                    "value": price,
                    "text": text,
                    "context": context[:240],
                    "source": f"selector:{selector}",
                }
            )
    return candidates


def text_candidates(text: str) -> List[Dict[str, Any]]:
    candidates = []
    for match in PRICE_RE.finditer(text):
        price_text = clean_text(match.group(0))
        price = brl_to_float(price_text)
        if price is None:
            continue
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 120)
        candidates.append(
            {
                "value": price,
                "text": price_text,
                "context": clean_text(text[start:end]),
                "source": "page_text",
            }
        )
    return candidates


def candidate_score(candidate: Dict[str, Any], loja: str) -> int:
    context = f"{candidate['source']} {candidate['context']}".lower()
    score = 0

    if "jsonld" in context:
        score += 4
    if "product:price" in context or "itemprop" in context:
        score += 4
    if "coreprice" in context or "apexpricetopay" in context:
        score += 5
    if "a vista" in context or "avista" in context or "à vista" in context:
        score += 5
    if "pix" in context:
        score += 4
    if "por:" in context or " por " in context:
        score += 2
    if "preco" in context or "price" in context or "valor" in context:
        score += 2

    if loja.lower() == "amazon":
        if "este item" in context or "outros vendedores" in context:
            score += 4
        if "frequentemente comprados" in context or "clientes que visualizaram" in context:
            score -= 8

    if re.search(r"\b\d+\s*x\s*de\b", context):
        score -= 7
    if "parcel" in context or "sem juros" in context or "cartao" in context:
        score -= 5
    if "cupom" in context or " off" in context or "desconto de r$" in context:
        score -= 6
    if "frete" in context and candidate["value"] < 500:
        score -= 6
    if " de: " in context or "de r$" in context or "preco antigo" in context:
        score -= 2

    return score


def choose_best_price(soup: BeautifulSoup, loja: str) -> Tuple[Optional[float], str]:
    page_text = clean_text(soup.get_text(" ", strip=True))
    candidates = jsonld_candidates(soup)
    candidates.extend(selector_candidates(soup))
    candidates.extend(text_candidates(page_text))

    filtered = []
    for candidate in candidates:
        value = candidate["value"]
        if 50 <= value <= 50000:
            candidate["score"] = candidate_score(candidate, loja)
            filtered.append(candidate)

    if not filtered:
        return None, ""

    filtered.sort(key=lambda item: (item["score"], -item["value"]), reverse=True)
    best = filtered[0]
    return best["value"], best["text"]


def fetch_product(product: Product) -> Dict[str, Any]:
    collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "produto_key": product.key,
        "categoria": product.categoria,
        "grupo": product.grupo,
        "loja": product.loja,
        "nome": product.nome,
        "url": product.url,
        "preco": None,
        "preco_texto": "",
        "status": "erro",
        "erro": "",
        "coletado_em": collected_at,
    }

    try:
        response = requests.get(product.url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        result["nome"] = extract_title(soup, product.nome)
        price, price_text = choose_best_price(soup, product.loja)

        if price is None:
            result["erro"] = "Nao foi possivel encontrar o preco na pagina."
            return result

        result["preco"] = price
        result["preco_texto"] = price_text
        result["status"] = "ok"
        return result
    except Exception as exc:
        result["erro"] = str(exc)
        return result


def product_matches(product: Product, term: str) -> bool:
    text = " ".join(
        [
            product.key,
            product.categoria,
            product.grupo,
            product.loja,
            product.nome,
            product.url,
        ]
    ).lower()
    return term.lower() in text


def products_by_category(categoria: str) -> List[Product]:
    return [product for product in PRODUCTS if product.categoria == categoria]


def products_by_term(term: str) -> List[Product]:
    return [product for product in PRODUCTS if product_matches(product, term)]


def collect_products(products: List[Product], save: bool = True) -> List[Dict[str, Any]]:
    init_db()
    results = []
    for product in products:
        result = fetch_product(product)
        results.append(result)
        if save:
            save_result(result)
        time.sleep(0.7)
    return results


def collect_all(save: bool = True) -> List[Dict[str, Any]]:
    return collect_products(PRODUCTS, save=save)


def sort_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        results,
        key=lambda item: (
            item.get("grupo", ""),
            item["preco"] is None,
            item["preco"] if item["preco"] is not None else 999999,
            item["loja"],
        ),
    )


def ranking_text(results: List[Dict[str, Any]], title: str = "Produtos encontrados") -> str:
    ordered = sort_results(results)
    lines = [
        title,
        f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
    ]

    groups = sorted({item.get("grupo") or item["nome"] for item in ordered})
    for group_name in groups:
        group_items = [
            item for item in ordered if (item.get("grupo") or item["nome"]) == group_name
        ]
        ok_items = [item for item in group_items if item["preco"] is not None]

        lines.append(group_name)
        if ok_items:
            best = sort_results(ok_items)[0]
            lines.append(f"Melhor preco: {best['loja']} - {format_brl(best['preco'])}")
        else:
            lines.append("Nenhum preco encontrado nesta consulta.")
        lines.append("")

        for index, item in enumerate(sort_results(group_items), start=1):
            price = format_brl(item["preco"])
            lines.append(f"{index}. {item['loja']} - {price}")
            lines.append(item["nome"][:120])
            lines.append(item["url"])
            if item["erro"]:
                lines.append(f"Obs: {item['erro'][:120]}")
            lines.append("")
        lines.append("")

    return "\n".join(lines).strip()


def split_message(text: str, limit: int = 3900) -> List[str]:
    if len(text) <= limit:
        return [text]

    parts = []
    current = ""
    for block in text.split("\n\n"):
        candidate = f"{current}\n\n{block}".strip() if current else block
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            parts.append(current)
        current = block

    if current:
        parts.append(current)
    return parts


def send_long_message(bot: "tl.TeleBot", chat_id: int, text: str) -> None:
    for part in split_message(text):
        bot.send_message(chat_id, part)


def history_text() -> str:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        if pd is not None:
            df = pd.read_sql_query(
                """
                SELECT categoria, grupo, loja, nome, preco, status, coletado_em
                FROM historico_precos
                WHERE preco IS NOT NULL
                ORDER BY coletado_em
                """,
                conn,
            )
            if df.empty:
                return "Ainda nao existe historico. Use /gpu, /cpu, /memoria ou /gabinete para coletar precos."

            lines = ["Historico de precos", ""]
            for (grupo, loja), group in df.groupby(["grupo", "loja"]):
                group = group.sort_values(by="coletado_em")
                menor = float(group["preco"].min())
                maior = float(group["preco"].max())
                media = float(group["preco"].mean())
                ultimo = group.iloc[-1]
                lines.append(f"{grupo} - {loja}")
                lines.append(f"Atual: {format_brl(float(ultimo['preco']))}")
                lines.append(f"Menor: {format_brl(menor)}")
                lines.append(f"Maior: {format_brl(maior)}")
                lines.append(f"Media: {format_brl(media)}")
                lines.append("")
            return "\n".join(lines).strip()

        rows = conn.execute(
            """
            SELECT grupo, loja, MIN(preco), MAX(preco), AVG(preco), COUNT(*)
            FROM historico_precos
            WHERE preco IS NOT NULL
            GROUP BY grupo, loja
            ORDER BY grupo, loja
            """
        ).fetchall()

    if not rows:
        return "Ainda nao existe historico. Use /gpu, /cpu, /memoria ou /gabinete para coletar precos."

    lines = ["Historico de precos", ""]
    for grupo, loja, menor, maior, media, total in rows:
        lines.append(f"{grupo} - {loja} ({total} coletas)")
        lines.append(f"Menor: {format_brl(menor)}")
        lines.append(f"Maior: {format_brl(maior)}")
        lines.append(f"Media: {format_brl(media)}")
        lines.append("")
    return "\n".join(lines).strip()


def export_csv(results: List[Dict[str, Any]]) -> Path:
    path = BASE_DIR / "ultimo_resultado_hardware.csv"
    fields = [
        "categoria",
        "grupo",
        "loja",
        "nome",
        "preco",
        "preco_texto",
        "status",
        "erro",
        "coletado_em",
        "url",
    ]

    if pd is not None:
        pd.DataFrame(results)[fields].to_csv(path, index=False, encoding="utf-8-sig")
        return path

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result.get(field) for field in fields})
    return path


def build_bot() -> "tl.TeleBot":
    if tl is None or requests is None or BeautifulSoup is None:
        raise SystemExit(
            "Instale as bibliotecas com: pip install pyTelegramBotAPI requests beautifulsoup4 pandas"
        )

    if not TOKEN or TOKEN == "COLE_SEU_TOKEN_AQUI":
        raise SystemExit(
            "Defina o token antes de executar. Exemplo no PowerShell:\n"
            '$env:TELEGRAM_BOT_TOKEN="SEU_TOKEN_DO_BOTFATHER"\n'
            "python bot_busca_precos_gpu.py"
        )

    bot = tl.TeleBot(TOKEN)

    @bot.message_handler(commands=["start", "menu"])
    def menu(msg: "tl.types.Message") -> None:
        text = """
Hardware Price Monitor

Comandos:
/gpu - buscar precos das RTX 5050 nos sites
/cpu - buscar precos do Ryzen 5 5600GT
/memoria - buscar Kingston Fury DDR4 8GB e 16GB
/gabinete - buscar Corsair 3000D RGB Airflow
/todos - buscar todos os produtos cadastrados
/comparar - comparar e ordenar pelo menor preco
/comparar ryzen - comparar apenas um termo
/buscar rtx - buscar produto, loja ou categoria
/alerta 2200 - ver quem esta abaixo do limite
/historico - resumo salvo no SQLite com pandas
/exportar - gerar CSV da ultima consulta
/ajuda - mostrar ajuda
""".strip()
        bot.reply_to(msg, text)

    def run_category(msg: "tl.types.Message", categoria: str, title: str) -> None:
        products = products_by_category(categoria)
        bot.reply_to(
            msg,
            f"Buscando {len(products)} ofertas de {categoria}. Aguarde alguns segundos...",
        )
        results = collect_products(products, save=True)
        send_long_message(bot, msg.chat.id, ranking_text(results, title))

    @bot.message_handler(commands=["gpu"])
    def gpu(msg: "tl.types.Message") -> None:
        run_category(msg, "gpu", "Comparador de GPUs RTX 5050")

    @bot.message_handler(commands=["cpu"])
    def cpu(msg: "tl.types.Message") -> None:
        run_category(msg, "cpu", "Comparador Ryzen 5 5600GT")

    @bot.message_handler(commands=["memoria"])
    def memoria(msg: "tl.types.Message") -> None:
        run_category(msg, "memoria", "Comparador Kingston Fury DDR4 3200MHz")

    @bot.message_handler(commands=["gabinete"])
    def gabinete(msg: "tl.types.Message") -> None:
        run_category(msg, "gabinete", "Comparador Corsair 3000D RGB Airflow")

    @bot.message_handler(commands=["todos", "comparar"])
    def comparar(msg: "tl.types.Message") -> None:
        command = msg.text.split(maxsplit=1)[0].lower()
        term = msg.text.split(maxsplit=1)[1].strip() if len(msg.text.split(maxsplit=1)) > 1 else ""
        products = products_by_term(term) if term else PRODUCTS

        if not products:
            bot.reply_to(msg, f"Nenhum produto cadastrado para: {term}")
            return

        label = f" para '{term}'" if term else ""
        bot.reply_to(
            msg,
            f"Comparando {len(products)} ofertas{label}. Aguarde alguns segundos...",
        )
        results = collect_products(products, save=True)
        title = "Comparador geral de hardware" if command == "/todos" else "Comparador de precos"
        send_long_message(bot, msg.chat.id, ranking_text(results, title))

    @bot.message_handler(commands=["buscar"])
    def buscar(msg: "tl.types.Message") -> None:
        term = msg.text.replace("/buscar", "", 1).strip().lower()
        if not term:
            bot.reply_to(msg, "Use assim: /buscar rtx, /buscar ryzen, /buscar memoria ou /buscar kabum")
            return

        products = products_by_term(term)
        if not products:
            bot.reply_to(msg, "Nenhum produto cadastrado para esse termo.")
            return

        bot.reply_to(msg, f"Buscando {len(products)} ofertas para: {term}")
        results = collect_products(products, save=True)
        send_long_message(bot, msg.chat.id, ranking_text(results, f"Resultados para: {term}"))

    @bot.message_handler(commands=["alerta"])
    def alerta(msg: "tl.types.Message") -> None:
        args = msg.text.replace("/alerta", "", 1).strip().split(maxsplit=1)
        limit = brl_to_float(args[0]) if args else None
        if limit is None:
            bot.reply_to(msg, "Use assim: /alerta 2200 ou /alerta 200 memoria")
            return

        term = args[1].strip() if len(args) > 1 else ""
        products = products_by_term(term) if term else PRODUCTS
        if not products:
            bot.reply_to(msg, f"Nenhum produto cadastrado para: {term}")
            return

        bot.reply_to(msg, f"Verificando produtos abaixo de {format_brl(limit)}...")
        results = collect_products(products, save=True)
        found = [item for item in sort_results(results) if item["preco"] is not None and item["preco"] <= limit]

        if not found:
            bot.send_message(msg.chat.id, f"Nenhum produto ficou abaixo de {format_brl(limit)} agora.")
            return

        send_long_message(bot, msg.chat.id, ranking_text(found, f"Alerta: abaixo de {format_brl(limit)}"))

    @bot.message_handler(commands=["historico"])
    def historico(msg: "tl.types.Message") -> None:
        send_long_message(bot, msg.chat.id, history_text())

    @bot.message_handler(commands=["exportar"])
    def exportar(msg: "tl.types.Message") -> None:
        term = msg.text.replace("/exportar", "", 1).strip().lower()
        products = products_by_term(term) if term else PRODUCTS
        if not products:
            bot.reply_to(msg, f"Nenhum produto cadastrado para: {term}")
            return

        bot.reply_to(msg, "Gerando CSV com a consulta atual...")
        results = collect_products(products, save=True)
        csv_path = export_csv(results)
        with csv_path.open("rb") as file:
            bot.send_document(msg.chat.id, file, visible_file_name=csv_path.name)

    @bot.message_handler(commands=["ajuda"])
    def ajuda(msg: "tl.types.Message") -> None:
        menu(msg)

    @bot.message_handler(func=lambda message: True)
    def unknown(msg: "tl.types.Message") -> None:
        bot.reply_to(msg, "Comando nao reconhecido. Digite /menu para ver as opcoes.")

    return bot


if __name__ == "__main__":
    print("Iniciando Hardware Price Monitor...")
    print(f"Banco SQLite: {DB_PATH}")
    telegram_bot = build_bot()
    telegram_bot.infinity_polling(skip_pending=True)

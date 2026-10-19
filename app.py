#!/usr/bin/env python3
"""Descubra seu signo - servidor web usando apenas a biblioteca padrao do Python.

Nao precisa de XAMPP, pip, nem permissao de administrador.
Execute:  python app.py   e abra   http://localhost:8000
"""
import html
import os
import sqlite3
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "signos.db")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PORT = 8000

# slug, nome, simbolo, elemento, modalidade, planeta, (mes_ini, dia_ini), (mes_fim, dia_fim),
# cor, pedra, numero, qualidades, desafios, descricao, compatibilidade
SIGNOS = [
    ("aries", "Áries", "♈", "Fogo", "Cardinal", "Marte", (3, 21), (4, 19),
     "Vermelho", "Diamante", "9",
     "Corajoso, determinado, confiante, entusiasmado",
     "Impulsivo, impaciente, pavio curto",
     "O pioneiro do zodíaco. Ariano gosta de agir primeiro e pensar depois, encara desafios de frente e tem energia de sobra para começar novos projetos.",
     "Leão, Sagitário, Gêmeos, Aquário"),
    ("touro", "Touro", "♉", "Terra", "Fixo", "Vênus", (4, 20), (5, 20),
     "Verde", "Esmeralda", "6",
     "Confiável, paciente, prático, leal",
     "Teimoso, possessivo, resistente a mudanças",
     "Amante do conforto e da estabilidade. Taurino valoriza os prazeres sensoriais, trabalha com persistência e constrói relações duradouras.",
     "Virgem, Capricórnio, Câncer, Peixes"),
    ("gemeos", "Gêmeos", "♊", "Ar", "Mutável", "Mercúrio", (5, 21), (6, 20),
     "Amarelo", "Ágata", "5",
     "Curioso, comunicativo, versátil, bem-humorado",
     "Inconstante, ansioso, superficial às vezes",
     "A mente ágil do zodíaco. Geminiano adora conversar, aprender e conhecer gente nova, e se adapta a qualquer ambiente com facilidade.",
     "Libra, Aquário, Áries, Leão"),
    ("cancer", "Câncer", "♋", "Água", "Cardinal", "Lua", (6, 21), (7, 22),
     "Prata", "Pérola", "2",
     "Protetor, intuitivo, carinhoso, dedicado",
     "Sensível demais, melancólico, apegado ao passado",
     "Profundamente ligado à família e ao lar. Canceriano percebe emoções alheias com facilidade e cuida de quem ama com muito zelo.",
     "Escorpião, Peixes, Touro, Virgem"),
    ("leao", "Leão", "♌", "Fogo", "Fixo", "Sol", (7, 23), (8, 22),
     "Dourado", "Rubi", "1",
     "Generoso, carismático, criativo, leal",
     "Orgulhoso, dramático, gosta de ser o centro das atenções",
     "O rei da selva zodiacal. Leonino irradia calor e confiança, inspira os outros e adora brilhar, mas também sabe ser muito generoso.",
     "Áries, Sagitário, Gêmeos, Libra"),
    ("virgem", "Virgem", "♍", "Terra", "Mutável", "Mercúrio", (8, 23), (9, 22),
     "Verde-musgo", "Safira", "5",
     "Organizado, analítico, prestativo, detalhista",
     "Perfeccionista, crítico, preocupado em excesso",
     "Atento aos detalhes e sempre buscando melhorar. Virginiano é confiável, trabalhador e gosta de ser útil de maneira prática.",
     "Touro, Capricórnio, Câncer, Escorpião"),
    ("libra", "Libra", "♎", "Ar", "Cardinal", "Vênus", (9, 23), (10, 22),
     "Rosa", "Opala", "6",
     "Diplomático, justo, sociável, elegante",
     "Indeciso, evita conflitos, dependente de aprovação",
     "Em busca constante de equilíbrio e harmonia. Libriano preza pela justiça, pela beleza e por relações agradáveis.",
     "Gêmeos, Aquário, Leão, Sagitário"),
    ("escorpiao", "Escorpião", "♏", "Água", "Fixo", "Plutão e Marte", (10, 23), (11, 21),
     "Vinho", "Topázio", "8",
     "Intenso, determinado, perspicaz, leal",
     "Ciumento, desconfiado, reservado demais",
     "Profundo e magnético. Escorpiano não gosta de superficialidades, vai fundo nas emoções e tem uma força de vontade impressionante.",
     "Câncer, Peixes, Virgem, Capricórnio"),
    ("sagitario", "Sagitário", "♐", "Fogo", "Mutável", "Júpiter", (11, 22), (12, 21),
     "Roxo", "Turquesa", "3",
     "Otimista, aventureiro, honesto, divertido",
     "Sem tato, inquieto, foge de compromissos",
     "O explorador do zodíaco. Sagitariano ama liberdade, viagens e filosofia, e contagia todos com seu otimismo.",
     "Áries, Leão, Libra, Aquário"),
    ("capricornio", "Capricórnio", "♑", "Terra", "Cardinal", "Saturno", (12, 22), (1, 19),
     "Marrom", "Granada", "8",
     "Disciplinado, responsável, ambicioso, paciente",
     "Pessimista, rígido, workaholic",
     "Focado em metas de longo prazo. Capricorniano leva a vida a sério, é persistente e conquista seu espaço com esforço contínuo.",
     "Touro, Virgem, Escorpião, Peixes"),
    ("aquario", "Aquário", "♒", "Ar", "Fixo", "Urano e Saturno", (1, 20), (2, 18),
     "Azul-elétrico", "Ametista", "4",
     "Original, independente, humanitário, inventivo",
     "Distante, teimoso, imprevisível",
     "O inovador do zodíaco. Aquariano pensa fora da caixa, valoriza a liberdade e se preocupa com causas coletivas.",
     "Gêmeos, Libra, Áries, Sagitário"),
    ("peixes", "Peixes", "♓", "Água", "Mutável", "Netuno e Júpiter", (2, 19), (3, 20),
     "Verde-água", "Água-marinha", "7",
     "Sonhador, empático, artístico, compassivo",
     "Escapista, ingênuo, muito influenciável",
     "Sensível e imaginativo. Pisciano sente o mundo com intensidade, tem veia artística forte e uma compaixão genuína pelos outros.",
     "Câncer, Escorpião, Touro, Capricórnio"),
]


def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS signos (
            slug TEXT PRIMARY KEY, nome TEXT, simbolo TEXT, elemento TEXT,
            modalidade TEXT, planeta TEXT,
            mes_ini INTEGER, dia_ini INTEGER, mes_fim INTEGER, dia_fim INTEGER,
            cor TEXT, pedra TEXT, numero TEXT,
            qualidades TEXT, desafios TEXT, descricao TEXT, compatibilidade TEXT
        )""")
    con.execute("DELETE FROM signos")
    for s in SIGNOS:
        con.execute(
            "INSERT INTO signos VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (s[0], s[1], s[2], s[3], s[4], s[5], s[6][0], s[6][1], s[7][0], s[7][1],
             s[8], s[9], s[10], s[11], s[12], s[13], s[14]),
        )
    con.commit()
    con.close()


def buscar_por_data(mes, dia):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        for r in con.execute("SELECT * FROM signos"):
            ini = (r["mes_ini"], r["dia_ini"])
            fim = (r["mes_fim"], r["dia_fim"])
            if ini <= fim:
                if ini <= (mes, dia) <= fim:
                    return dict(r)
            elif (mes, dia) >= ini or (mes, dia) <= fim:  # Capricornio (vira o ano)
                return dict(r)
    finally:
        con.close()
    return None


def buscar_por_slug(slug):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        r = con.execute("SELECT * FROM signos WHERE slug = ?", (slug,)).fetchone()
        return dict(r) if r else None
    finally:
        con.close()


def listar_signos():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute("SELECT * FROM signos")]
    finally:
        con.close()


# ---------------------------------------------------------------- HTML ----

def e(txt):
    return html.escape(str(txt))


def layout(titulo, corpo):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titulo)}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="/static/css/style.css" rel="stylesheet">
</head>
<body>
  <nav class="navbar navbar-dark navbar-estrelas">
    <div class="container">
      <a class="navbar-brand fw-semibold" href="/">✨ Meu Signo</a>
    </div>
  </nav>
  {corpo}
  <footer class="text-center py-4 rodape">
    <small>Feito para fins de entretenimento · Datas aproximadas (tropical)</small>
  </footer>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""


def pagina_inicial(erro=None):
    hoje = date.today().isoformat()
    alerta = f'<div class="alert alert-danger py-2">{e(erro)}</div>' if erro else ""
    grade = "".join(
        f'<a class="col-4 col-md-2 text-decoration-none" href="/signo/{e(s["slug"])}">'
        f'<div class="mini-signo"><span class="simbolo">{s["simbolo"]}</span>'
        f'<small>{e(s["nome"])}</small></div></a>'
        for s in listar_signos()
    )
    corpo = f"""
  <main class="container py-5">
    <div class="row justify-content-center">
      <div class="col-lg-6">
        <div class="card cartao-form shadow-lg">
          <div class="card-body p-4 p-md-5 text-center">
            <div class="display-3 mb-2">🔮</div>
            <h1 class="h2 mb-2">Descubra o seu signo</h1>
            <p class="text-secondary mb-4">Informe sua data de nascimento e veja as principais características do seu signo.</p>
            {alerta}
            <form action="/buscar" method="get" class="text-start">
              <label for="data" class="form-label">Data de nascimento</label>
              <input type="date" class="form-control form-control-lg mb-4" id="data" name="data"
                     min="1900-01-01" max="{hoje}" required>
              <button type="submit" class="btn btn-lg btn-estrela w-100">Descobrir meu signo</button>
            </form>
          </div>
        </div>
      </div>
    </div>
    <h2 class="h5 text-center mt-5 mb-3 text-light">Ou explore os 12 signos</h2>
    <div class="row g-3 justify-content-center">{grade}</div>
  </main>"""
    return layout("Descubra o seu signo", corpo)


def pagina_signo(s):
    def lista(texto):
        return "".join(f'<span class="badge rounded-pill etiqueta">{e(x.strip())}</span>' for x in texto.split(","))

    periodo = f'{s["dia_ini"]:02d}/{s["mes_ini"]:02d} a {s["dia_fim"]:02d}/{s["mes_fim"]:02d}'
    info = [
        ("Elemento", s["elemento"]), ("Modalidade", s["modalidade"]),
        ("Planeta regente", s["planeta"]), ("Cor", s["cor"]),
        ("Pedra", s["pedra"]), ("Número da sorte", s["numero"]),
    ]
    info_html = "".join(
        f'<div class="col-6 col-md-4"><div class="info-item"><small>{e(k)}</small><strong>{e(v)}</strong></div></div>'
        for k, v in info
    )
    corpo = f"""
  <main class="container py-5">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card cartao-signo shadow-lg">
          <div class="card-body p-4 p-md-5">
            <div class="text-center mb-4">
              <div class="simbolo-grande">{s["simbolo"]}</div>
              <h1 class="display-5 mb-1">{e(s["nome"])}</h1>
              <p class="text-secondary">{e(periodo)}</p>
            </div>
            <p class="lead text-center">{e(s["descricao"])}</p>
            <hr class="my-4">
            <div class="row g-3 mb-4">{info_html}</div>
            <h2 class="h5">Qualidades</h2>
            <div class="mb-3">{lista(s["qualidades"])}</div>
            <h2 class="h5">Pontos de atenção</h2>
            <div class="mb-3">{lista(s["desafios"])}</div>
            <h2 class="h5">Mais compatível com</h2>
            <div class="mb-4">{lista(s["compatibilidade"])}</div>
            <div class="text-center">
              <a href="/" class="btn btn-estrela px-4">← Consultar outra data</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>"""
    return layout(f'{s["nome"]} - Meu Signo', corpo)


def pagina_404():
    corpo = """<main class="container py-5 text-center text-light">
      <h1 class="display-4">404</h1><p>Página não encontrada.</p>
      <a href="/" class="btn btn-estrela">Voltar ao início</a></main>"""
    return layout("Não encontrado", corpo)


# ------------------------------------------------------------- Servidor ---

TIPOS = {".css": "text/css", ".js": "application/javascript", ".png": "image/png",
         ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".ico": "image/x-icon"}


class Handler(BaseHTTPRequestHandler):
    def responder(self, corpo, status=200, tipo="text/html; charset=utf-8"):
        dados = corpo.encode("utf-8") if isinstance(corpo, str) else corpo
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def redirecionar(self, destino):
        self.send_response(302)
        self.send_header("Location", destino)
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        caminho = url.path

        if caminho == "/":
            return self.responder(pagina_inicial())

        if caminho == "/buscar":
            valor = parse_qs(url.query).get("data", [""])[0]
            try:
                d = date.fromisoformat(valor)
                if d > date.today() or d.year < 1900:
                    raise ValueError
            except ValueError:
                return self.responder(pagina_inicial("Informe uma data de nascimento válida."), 400)
            s = buscar_por_data(d.month, d.day)
            return self.redirecionar(f"/signo/{s['slug']}")

        if caminho.startswith("/signo/"):
            s = buscar_por_slug(caminho[len("/signo/"):])
            if s:
                return self.responder(pagina_signo(s))
            return self.responder(pagina_404(), 404)

        if caminho.startswith("/static/"):
            arquivo = os.path.normpath(os.path.join(STATIC_DIR, caminho[len("/static/"):]))
            if arquivo.startswith(STATIC_DIR) and os.path.isfile(arquivo):
                ext = os.path.splitext(arquivo)[1].lower()
                with open(arquivo, "rb") as f:
                    return self.responder(f.read(), tipo=TIPOS.get(ext, "application/octet-stream"))

        self.responder(pagina_404(), 404)

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    init_db()
    servidor = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Servidor rodando em http://localhost:{PORT}  (Ctrl+C para parar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")
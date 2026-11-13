"""Servidor HTTP do jogo da velha usando apenas a biblioteca padrao do Python.

Executar:  python servidor.py
Depois abra http://127.0.0.1:8000
"""

from __future__ import annotations

import secrets
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from jogo_da_velha import JogoDaVelha

PORTA = 8000
PASTA_WEB = Path(__file__).resolve().parent / "web"
COOKIE = "sessao"

_sessoes: dict[str, JogoDaVelha] = {}
_trava = threading.Lock()


def render_pagina(jogo: JogoDaVelha) -> str:
    """Monta o HTML da pagina a partir do template e do estado da partida."""
    casas: list[str] = []
    for posicao, marca in enumerate(jogo.tabuleiro):
        classes = ["casa"]
        if marca == "X":
            classes.append("casa--x")
        elif marca == "O":
            classes.append("casa--o")
        if posicao in jogo.linhas_vencedoras:
            classes.append("casa--vencedora")

        if marca or jogo.terminado:
            conteudo = (
                '<button class="casa__botao" type="button" disabled>'
                f"{marca}</button>"
            )
        else:
            conteudo = (
                '<form method="post" action="/jogar">'
                f'<input type="hidden" name="posicao" value="{posicao}">'
                '<button class="casa__botao" type="submit"'
                f' aria-label="Jogar na casa {posicao + 1}"></button>'
                "</form>"
            )
        casas.append(f'<div class="{" ".join(classes)}">{conteudo}</div>')

    if jogo.vencedor:
        status = f"{jogo.vencedor} venceu!"
        status_tipo = f"vitoria-{jogo.vencedor.lower()}"
    elif jogo.empate:
        status = "Deu velha! Empate."
        status_tipo = "empate"
    else:
        status = f"Vez de {jogo.vez}"
        status_tipo = f"vez-{jogo.vez.lower()}"

    html = (PASTA_WEB / "index.html").read_text(encoding="utf-8")
    substituicoes = {
        "{{casas}}": "\n        ".join(casas),
        "{{status_tipo}}": status_tipo,
        "{{status}}": status,
    }
    for chave, valor in substituicoes.items():
        html = html.replace(chave, valor)
    return html


class JogoHandler(BaseHTTPRequestHandler):
    server_version = "JogoDaVelha/1.0"

    # -- utilidades -------------------------------------------------
    def _cookie(self, nome: str) -> str:
        cabecalho = self.headers.get("Cookie", "")
        for parte in cabecalho.split(";"):
            chave, _, valor = parte.strip().partition("=")
            if chave == nome:
                return valor
        return ""

    def _sessao(self) -> tuple[str, JogoDaVelha, bool]:
        identificador = self._cookie(COOKIE)
        with _trava:
            if identificador and identificador in _sessoes:
                return identificador, _sessoes[identificador], False
            identificador = secrets.token_urlsafe(16)
            jogo = JogoDaVelha()
            _sessoes[identificador] = jogo
            return identificador, jogo, True

    def _enviar(
        self,
        status: HTTPStatus,
        corpo: bytes,
        tipo: str,
        cookie: str | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        if cookie:
            self.send_header(
                "Set-Cookie", f"{COOKIE}={cookie}; Path=/; SameSite=Lax"
            )
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(corpo)

    def _redirecionar(self, cookie: str | None = None) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", "/")
        self.send_header("Content-Length", "0")
        if cookie:
            self.send_header(
                "Set-Cookie", f"{COOKIE}={cookie}; Path=/; SameSite=Lax"
            )
        self.end_headers()

    def _nao_encontrado(self) -> None:
        corpo = b"404 - pagina nao encontrada"
        self._enviar(
            HTTPStatus.NOT_FOUND, corpo, "text/plain; charset=utf-8"
        )

    # -- rotas ------------------------------------------------------
    def do_GET(self) -> None:
        caminho = self.path.split("?", 1)[0]

        if caminho in ("/", "/index.html"):
            identificador, jogo, nova = self._sessao()
            with _trava:
                html = render_pagina(jogo)
            self._enviar(
                HTTPStatus.OK,
                html.encode("utf-8"),
                "text/html; charset=utf-8",
                cookie=identificador if nova else None,
            )
            return

        if caminho == "/style.css":
            try:
                css = (PASTA_WEB / "style.css").read_bytes()
            except OSError:
                self._nao_encontrado()
                return
            self._enviar(HTTPStatus.OK, css, "text/css; charset=utf-8")
            return

        self._nao_encontrado()

    def do_POST(self) -> None:
        caminho = self.path.split("?", 1)[0]
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            tamanho = 0
        dados = parse_qs(self.rfile.read(tamanho).decode("utf-8", "replace"))

        identificador, jogo, nova = self._sessao()
        cookie = identificador if nova else None

        with _trava:
            if caminho == "/jogar":
                try:
                    posicao = int(dados.get("posicao", ["-1"])[0])
                except ValueError:
                    posicao = -1
                jogo.jogar(posicao)
            elif caminho == "/reiniciar":
                jogo.reiniciar()
            else:
                self._nao_encontrado()
                return

        self._redirecionar(cookie)


def main() -> None:
    servidor = ThreadingHTTPServer(("127.0.0.1", PORTA), JogoHandler)
    print(f"Jogo da velha em http://127.0.0.1:{PORTA}  (Ctrl+C para encerrar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()

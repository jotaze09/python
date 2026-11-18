"""Regras do jogo da velha e IA (minimax) em Python puro.

Sem dependencias externas: o servidor HTTP (servidor.py) usa este modulo.
"X" sempre comeca; no modo "computador" o computador joga com "O".
"""

from __future__ import annotations

import math

X = "X"
O = "O"

MODOS = ("humano", "computador")

LINHAS = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


class JogoDaVelha:
    """Uma partida de jogo da velha."""

    def __init__(self, modo: str = "humano") -> None:
        self.modo = modo if modo in MODOS else "humano"
        self.reiniciar()

    def reiniciar(self) -> None:
        self.tabuleiro: list[str] = [""] * 9
        self.vez = X
        self.vencedor = ""
        self.linhas_vencedoras: tuple[int, ...] = ()
        self.jogadas = 0

    @property
    def empate(self) -> bool:
        return not self.vencedor and self.jogadas == 9

    @property
    def terminado(self) -> bool:
        return bool(self.vencedor) or self.empate

    def jogar(self, posicao: int) -> bool:
        """Marca a casa indicada; devolve False se a jogada for invalida."""
        if self.terminado or not 0 <= posicao <= 8 or self.tabuleiro[posicao]:
            return False

        self.tabuleiro[posicao] = self.vez
        self.jogadas += 1

        linha = self._linha_vencedora(self.tabuleiro, self.vez)
        if linha:
            self.vencedor = self.vez
            self.linhas_vencedoras = linha
        elif not self.empate:
            self.vez = O if self.vez == X else X

        return True

    def jogar_computador(self) -> int | None:
        """Faz a jogada do computador (O) e devolve a casa escolhida."""
        if self.terminado or self.modo != "computador" or self.vez != O:
            return None
        posicao = self.melhor_jogada(O)
        self.jogar(posicao)
        return posicao

    def melhor_jogada(self, simbolo: str) -> int:
        """Casa que `simbolo` deve escolher (minimax: nunca perde)."""
        return self._minimax(list(self.tabuleiro), simbolo)[1]

    def _minimax(
        self, tabuleiro: list[str], simbolo: str, profundidade: int = 0
    ) -> tuple[float, int]:
        vencedor = self._vencedor_de(tabuleiro)
        if vencedor == O:
            return 10 - profundidade, -1
        if vencedor == X:
            return profundidade - 10, -1
        if all(tabuleiro):
            return 0, -1

        adversario = X if simbolo == O else O
        melhor_nota = -math.inf if simbolo == O else math.inf
        melhor_posicao = -1

        for posicao, casa in enumerate(tabuleiro):
            if casa:
                continue
            tabuleiro[posicao] = simbolo
            nota = self._minimax(tabuleiro, adversario, profundidade + 1)[0]
            tabuleiro[posicao] = ""
            if (simbolo == O and nota > melhor_nota) or (
                simbolo == X and nota < melhor_nota
            ):
                melhor_nota, melhor_posicao = nota, posicao

        return melhor_nota, melhor_posicao

    @staticmethod
    def _vencedor_de(tabuleiro: list[str] | tuple[str, ...]) -> str:
        for a, b, c in LINHAS:
            if tabuleiro[a] and tabuleiro[a] == tabuleiro[b] == tabuleiro[c]:
                return tabuleiro[a]
        return ""

    @staticmethod
    def _linha_vencedora(
        tabuleiro: list[str] | tuple[str, ...], simbolo: str
    ) -> tuple[int, ...]:
        for linha in LINHAS:
            if all(tabuleiro[i] == simbolo for i in linha):
                return linha
        return ()

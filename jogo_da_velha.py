"""Regras do jogo da velha em Python puro.

Sem dependencias externas: o servidor HTTP (servidor.py) usa este modulo.
"X" sempre comeca.
"""

from __future__ import annotations

X = "X"
O = "O"

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
    """Uma partida de jogo da velha entre dois jogadores."""

    def __init__(self) -> None:
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

    @staticmethod
    def _linha_vencedora(
        tabuleiro: list[str] | tuple[str, ...], simbolo: str
    ) -> tuple[int, ...]:
        for linha in LINHAS:
            if all(tabuleiro[i] == simbolo for i in linha):
                return linha
        return ()

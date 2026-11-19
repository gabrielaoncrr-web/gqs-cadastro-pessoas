"""Repositório de pessoas que persiste no MySQL."""

import mysql.connector

from pessoa import Pessoa


class RepositorioPessoasMySQL:
    """Mesmos métodos do CadastroPessoas, mas gravando no MySQL."""

    def __init__(self, host="localhost", port=3306,
                 user="root", password="root123", database="pessoas_db"):
        self.__config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        self.__criarTabela()

    def __conectar(self):
        return mysql.connector.connect(**self.__config)

    def __criarTabela(self):
        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pessoas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    idade INT NOT NULL,
                    email VARCHAR(100) NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def cadastrar(self, nome, idade, email):
        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO pessoas (nome, idade, email) VALUES (%s, %s, %s)",
                (nome, idade, email))
            conn.commit()
            return Pessoa(nome, idade, email)
        finally:
            conn.close()

    def buscarPorNome(self, nome):
        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT nome, idade, email FROM pessoas WHERE nome = %s LIMIT 1",
                (nome,))
            linha = cur.fetchone()
            if linha is None:
                return None
            return Pessoa(linha[0], linha[1], linha[2])
        finally:
            conn.close()

    def listar(self):
        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute("SELECT nome, idade, email FROM pessoas")
            return [Pessoa(linha[0], linha[1], linha[2])
                    for linha in cur.fetchall()]
        finally:
            conn.close()

    def alterar(self, nome, novo_nome, nova_idade, novo_email):
        if self.buscarPorNome(nome) is None:
            return None

        conn = self.__conectar()
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE pessoas SET nome = %s, idade = %s, email = %s "
                "WHERE nome = %s LIMIT 1",
                (novo_nome, nova_idade, novo_email, nome))
            conn.commit()
            return Pessoa(novo_nome, nova_idade, novo_email)
        finally:
            conn.close()

"""Persistent pgvector with parameterized, exact cosine search."""
import math
from typing import Any
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from .models import Chunk


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        """TODO: retain connection settings; validate model dimensions."""
        if type(dimensions) is not int or not 1 <= dimensions <= 2000:
            raise ValueError("Invalid vector dimensions")
        self.dimensions = dimensions
        self.connection = psycopg.connect(database_url, connect_timeout=10, row_factory=dict_row)

    def close(self) -> None:
        self.connection.close()

    def create_schema(self) -> None:
        """TODO: create table with vector column and source/page/filter metadata."""
        with self.connection.transaction(), self.connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute(sql.SQL("""CREATE TABLE IF NOT EXISTS day6_chunks (
                strategy text NOT NULL, chunk_id text NOT NULL,
                document_id text NOT NULL, source text NOT NULL, page integer NOT NULL,
                text text NOT NULL, metadata jsonb NOT NULL, embedding vector({}) NOT NULL,
                PRIMARY KEY(strategy,chunk_id))""").format(sql.Literal(self.dimensions)))
            cursor.execute("SELECT atttypmod FROM pg_attribute WHERE attrelid='day6_chunks'::regclass AND attname='embedding'")
            if cursor.fetchone()["atttypmod"] != self.dimensions:
                raise ValueError("Existing table has different vector dimensions")

    def versions(self) -> dict:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT current_setting('server_version') AS postgres, extversion AS pgvector FROM pg_extension WHERE extname='vector'")
            result = dict(cursor.fetchone())
        self.connection.commit()
        return result

    def _vector(self, values: list[float]) -> str:
        if len(values) != self.dimensions or not all(math.isfinite(v) for v in values) or not any(values):
            raise ValueError("Vector length/nonfinite/zero-vector error")
        return "[" + ",".join(str(float(v)) for v in values) + "]"

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """TODO: validate lengths/dimensions and write stable IDs without duplicates.

        When re-ingesting changed source documents, remove obsolete chunks too.
        """
        if len(chunks) != len(vectors) or len({c.chunk_id for c in chunks}) != len(chunks):
            raise ValueError("Mismatched vectors or duplicate IDs")
        records = [(strategy, c.chunk_id, c.document_id, c.source, c.page, c.text,
                    Jsonb(c.metadata), self._vector(v)) for c, v in zip(chunks, vectors)]
        # Full strategy snapshot, replaced atomically. Also removes stale chunks
        # and removed documents. Unrelated strategies/tables are untouched.
        with self.connection.transaction(), self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM day6_chunks WHERE strategy=%s", (strategy,))
            cursor.executemany("""INSERT INTO day6_chunks
                (strategy,chunk_id,document_id,source,page,text,metadata,embedding)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s::vector)""", records)

    def count(self, strategy: str) -> int:
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT count(*) AS n FROM day6_chunks WHERE strategy=%s", (strategy,))
            count = cursor.fetchone()["n"]
        self.connection.commit()
        return count

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """TODO: filter permitted metadata in SQL, rank by cosine distance, return top-k.

        Return chunk ID, text, score and metadata. Parameterize user-supplied values.
        """
        if not 1 <= top_k <= 100:
            raise ValueError("Invalid top_k")
        if filters is not None and (set(filters) != {"chapter"} or type(filters["chapter"]) is not int):
            raise ValueError("Only the verified integer chapter filter is allowed")
        vector = self._vector(query_vector)
        statement = """SELECT chunk_id,document_id,source,page,text,metadata,
            1-(embedding <=> %s::vector) AS score FROM day6_chunks WHERE strategy=%s"""
        args: list = [vector, strategy]
        if filters:
            statement += " AND metadata @> %s"
            args.append(Jsonb(filters))
        statement += " ORDER BY embedding <=> %s::vector,chunk_id LIMIT %s"
        args.extend([vector, top_k])
        with self.connection.cursor() as cursor:
            cursor.execute(statement, args)
            rows = [dict(row) for row in cursor.fetchall()]
        self.connection.commit()
        return rows

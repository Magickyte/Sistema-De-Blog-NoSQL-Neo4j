from pathlib import Path
from neo4j import GraphDatabase

from config import DB_CONFIG


def inicializar_bd():
    """Ejecuta el script crear_bd.cypher contra la instancia configurada de Neo4j."""
    cypher_path = Path(__file__).parent / "crear_bd.cypher"
    raw_text = cypher_path.read_text(encoding="utf-8")

    # Eliminar comentarios de línea // y separar sentencias por ';'
    clean_lines = [
        line for line in raw_text.splitlines()
        if not line.strip().startswith("//")
    ]
    statements = [
        stmt.strip()
        for stmt in "\n".join(clean_lines).split(";")
        if stmt.strip()
    ]

    driver = GraphDatabase.driver(
        DB_CONFIG["uri"],
        auth=(DB_CONFIG["user"], DB_CONFIG["password"])
    )
    try:
        with driver.session() as session:
            for stmt in statements:
                session.run(stmt)
        print("Base de datos Neo4j inicializada correctamente.")
    finally:
        driver.close()


if __name__ == "__main__":
    inicializar_bd()

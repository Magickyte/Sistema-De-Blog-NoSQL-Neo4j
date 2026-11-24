from datetime import datetime
from neo4j import GraphDatabase
from config import DB_CONFIG


class DatabaseManager:
    def __init__(self):
        self._driver = None

    def obtener_driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                DB_CONFIG["uri"],
                auth=(DB_CONFIG["user"], DB_CONFIG["password"])
            )
        return self._driver

    def cerrar(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def ejecutar_cypher(self, query, **params):
        driver = self.obtener_driver()
        with driver.session() as session:
            return list(session.run(query, **params))

    # -------------------------------------------------------------
    # USUARIOS Y AUTENTICACIÓN
    # -------------------------------------------------------------
    def obtener_usuario_por_email(self, email):
        records = self.ejecutar_cypher(
            "MATCH (u:User) WHERE toLower(u.email) = toLower($email) "
            "RETURN u.user_id AS user_id, u.name AS name, u.password AS password, u.role AS role",
            email=email
        )
        return records[0] if records else None

    def registrar_usuario(self, nombre, email, password, role):
        existing = self.obtener_usuario_por_email(email)
        if existing:
            return False, "El correo electrónico ya existe."

        self.ejecutar_cypher(
            "OPTIONAL MATCH (all_u:User) "
            "WITH COALESCE(MAX(all_u.user_id), 0) + 1 AS next_id "
            "CREATE (:User {user_id: next_id, name: $name, email: toLower($email), password: $password, role: COALESCE($role, 'USER')})",
            name=nombre, email=email, password=password, role=role
        )
        return True, "Usuario creado exitosamente."

    def obtener_todos_los_usuarios(self):
        return self.ejecutar_cypher(
            "MATCH (u:User) RETURN u.user_id AS user_id, u.name AS name, u.role AS role ORDER BY u.name"
        )

    def eliminar_usuario(self, user_id):
        self.ejecutar_cypher(
            "MATCH (u:User {user_id: $user_id}) "
            "OPTIONAL MATCH (u)-[:PUBLISHED]->(a:Article) "
            "OPTIONAL MATCH (a)<-[:ON_ARTICLE]-(ca:Comment) "
            "OPTIONAL MATCH (u)-[:WROTE_COMMENT]->(cu:Comment) "
            "DETACH DELETE cu, ca, a, u",
            user_id=user_id
        )

    # -------------------------------------------------------------
    # ARTÍCULOS Y COMENTARIOS
    # -------------------------------------------------------------
    def crear_articulo(self, user_id, titulo, texto, cat_ids, tag_ids):
        art_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        res = self.ejecutar_cypher(
            "MATCH (u:User {user_id: $user_id}) "
            "OPTIONAL MATCH (all_a:Article) "
            "WITH u, COALESCE(MAX(all_a.article_id), 0) + 1 AS next_id "
            "CREATE (u)-[:PUBLISHED]->(a:Article {article_id: next_id, title: $title, art_date: $art_date, text: $text}) "
            "RETURN a.article_id AS article_id",
            user_id=user_id, title=titulo, art_date=art_date, text=texto
        )
        nuevo_art_id = int(res[0]["article_id"])

        if cat_ids:
            self.ejecutar_cypher(
                "MATCH (a:Article {article_id: $article_id}), (c:Category) "
                "WHERE c.category_id IN $ids "
                "MERGE (a)-[:IN_CATEGORY]->(c)",
                article_id=nuevo_art_id, ids=cat_ids
            )

        if tag_ids:
            self.ejecutar_cypher(
                "MATCH (a:Article {article_id: $article_id}), (t:Tag) "
                "WHERE t.tag_id IN $ids "
                "MERGE (a)-[:HAS_TAG]->(t)",
                article_id=nuevo_art_id, ids=tag_ids
            )

    def obtener_articulos(self):
        return self.ejecutar_cypher(
            "MATCH (u:User)-[:PUBLISHED]->(a:Article) "
            "OPTIONAL MATCH (a)-[:IN_CATEGORY]->(c:Category) "
            "OPTIONAL MATCH (a)-[:HAS_TAG]->(t:Tag) "
            "RETURN a.article_id AS article_id, a.title AS title, a.art_date AS art_date, "
            "a.text AS text, u.name AS author, "
            "collect(DISTINCT c.name) AS categories, collect(DISTINCT t.name) AS tags "
            "ORDER BY a.article_id DESC"
        )

    def obtener_comentarios(self):
        return self.ejecutar_cypher(
            "MATCH (u:User)-[:WROTE_COMMENT]->(c:Comment)-[:ON_ARTICLE]->(a:Article) "
            "RETURN a.article_id AS article_id, c.comment_id AS comment_id, "
            "c.text AS text, c.comment_date AS comment_date, u.name AS author "
            "ORDER BY c.comment_id ASC"
        )

    def agregar_comentario(self, user_id, article_id, texto):
        comment_date = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.ejecutar_cypher(
            "MATCH (u:User {user_id: $user_id}), (a:Article {article_id: $article_id}) "
            "OPTIONAL MATCH (all_c:Comment) "
            "WITH u, a, COALESCE(MAX(all_c.comment_id), 0) + 1 AS next_id "
            "CREATE (u)-[:WROTE_COMMENT]->(c:Comment {comment_id: next_id, comment_date: $comment_date, text: $text})-[:ON_ARTICLE]->(a)",
            article_id=article_id, user_id=user_id, comment_date=comment_date, text=texto
        )

    def eliminar_articulo(self, article_id):
        self.ejecutar_cypher(
            "MATCH (a:Article {article_id: $article_id}) "
            "OPTIONAL MATCH (a)<-[:ON_ARTICLE]-(c:Comment) "
            "DETACH DELETE c, a",
            article_id=article_id
        )

    def eliminar_comentario(self, comment_id):
        self.ejecutar_cypher(
            "MATCH (c:Comment {comment_id: $comment_id}) DETACH DELETE c",
            comment_id=comment_id
        )

    # -------------------------------------------------------------
    # CATEGORÍAS Y TAGS
    # -------------------------------------------------------------
    def agregar_categoria(self, nombre):
        self.ejecutar_cypher(
            "OPTIONAL MATCH (all_c:Category) "
            "WITH COALESCE(MAX(all_c.category_id), 0) + 1 AS next_id "
            "MERGE (c:Category {name: $name}) "
            "ON CREATE SET c.category_id = next_id",
            name=nombre
        )

    def agregar_tag(self, nombre):
        self.ejecutar_cypher(
            "OPTIONAL MATCH (all_t:Tag) "
            "WITH COALESCE(MAX(all_t.tag_id), 0) + 1 AS next_id "
            "MERGE (t:Tag {name: $name}) "
            "ON CREATE SET t.tag_id = next_id",
            name=nombre
        )

    def obtener_categorias(self):
        return self.ejecutar_cypher("MATCH (c:Category) RETURN c.category_id AS id, c.name AS name ORDER BY c.name")

    def obtener_tags(self):
        return self.ejecutar_cypher("MATCH (t:Tag) RETURN t.tag_id AS id, t.name AS name ORDER BY t.name")
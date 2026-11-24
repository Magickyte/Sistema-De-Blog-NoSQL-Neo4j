// =============================================================
// SCRIPT 1: BASE DE DATOS DE GRAFOS Y DATOS INICIALES
// Neo4j (Cypher)
// =============================================================

// 1. LIMPIEZA TOTAL
// -------------------------------------------------------------
MATCH (n) DETACH DELETE n;


// 2. DATOS INICIALES (NODOS Y RELACIONES)
// -------------------------------------------------------------
// Usuarios por defecto (ID 1 = Admin, ID 2 = Juan)
// Categorías iniciales (ID 1 = Tecnología, ID 2 = Programación)
// Etiquetas iniciales (ID 1 = Neo4j, ID 2 = Python)
// Artículos iniciales (Art 1 por Admin, Art 2 por Juan)
// Comentarios iniciales (Comm 1 por Juan en Art 1, Comm 2 por Admin en Art 2)
CREATE
    (u1:User {
        user_id: 1,
        name: 'Administrador Global',
        email: 'admin@blog.com',
        password: 'admin123',
        role: 'ADMIN'
    }),
    (u2:User {
        user_id: 2,
        name: 'Juan',
        email: 'juan@blog.com',
        password: 'user123',
        role: 'USER'
    }),
    (c1:Category {category_id: 1, name: 'Tecnología'}),
    (c2:Category {category_id: 2, name: 'Programación'}),
    (t1:Tag {tag_id: 1, name: 'Neo4j'}),
    (t2:Tag {tag_id: 2, name: 'Python'}),
    (a1:Article {
        article_id: 1,
        title: 'Introducción a Neo4j y Python',
        art_date: '24/09/2026 19:51',
        text: 'En este primer artículo aprenderemos cómo conectar Python con bases de datos Neo4j siguiendo las mejores prácticas: modelando entidades como nodos y relaciones mediante consultas Cypher.'
    }),
    (a2:Article {
        article_id: 2,
        title: 'El futuro de las bases de datos',
        art_date: '24/09/2026 19:51',
        text: 'La tecnología avanza rápido, pero las bases de datos orientadas a grafos destacan en el entorno moderno gracias a su flexibilidad, rendimiento en relaciones complejas y capacidad de análisis.'
    }),
    (cm1:Comment {
        comment_id: 1,
        comment_date: '24/09/2026 19:51',
        text: '¡Excelente artículo! Justo lo que necesitaba para estructurar correctamente mi proyecto.'
    }),
    (cm2:Comment {
        comment_id: 2,
        comment_date: '24/09/2026 19:51',
        text: 'Muy buena reflexión, Juan. Es importante conocer los fundamentos. ¡Sigue así!'
    }),
    (u1)-[:PUBLISHED]->(a1),
    (u2)-[:PUBLISHED]->(a2),
    (a1)-[:IN_CATEGORY]->(c2),
    (a2)-[:IN_CATEGORY]->(c1),
    (a1)-[:HAS_TAG]->(t1),
    (a1)-[:HAS_TAG]->(t2),
    (a2)-[:HAS_TAG]->(t1),
    (u2)-[:WROTE_COMMENT]->(cm1)-[:ON_ARTICLE]->(a1),
    (u1)-[:WROTE_COMMENT]->(cm2)-[:ON_ARTICLE]->(a2);

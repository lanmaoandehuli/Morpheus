"""
RAG 写作知识检索服务
从 pgmemory (PostgreSQL + pgvector) 检索写作知识，用于辅助草稿生成。
"""
import os
import logging
from typing import List

logger = logging.getLogger("morpheus.rag")

# pgmemory 连接配置
PG_HOST = "localhost"
PG_PORT = 15432
PG_DBNAME = "opencloud"
PG_USER = "opencloud"
PG_PASSWORD = "opencloud123"

# Zhipu embedding 配置
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
ZHIPU_EMBEDDING_MODEL = "embedding-3"


def _get_zhipu_api_key() -> str:
    """从环境变量或 .env 文件读取 ZHIPU_API_KEY"""
    key = os.environ.get("ZHIPU_API_KEY", "")
    if key:
        return key.strip('"').strip("'")
    # 尝试从 .env 读取
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ZHIPU_API_KEY"):
                    _, _, val = line.partition("=")
                    return val.strip().strip('"').strip("'")
    return ""


def _generate_embedding(text: str) -> List[float]:
    """调用 Zhipu embedding API 生成向量"""
    import httpx

    api_key = _get_zhipu_api_key()
    if not api_key:
        raise RuntimeError("ZHIPU_API_KEY not found")

    resp = httpx.post(
        f"{ZHIPU_BASE_URL}/embeddings",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"model": ZHIPU_EMBEDDING_MODEL, "input": text},
        timeout=15.0,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["data"][0]["embedding"]


def _search_by_vector(query_embedding: List[float], top_k: int = 3) -> List[str]:
    """通过向量相似度搜索"""
    import psycopg2

    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME,
        user=PG_USER, password=PG_PASSWORD,
        connect_timeout=5,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT content, 1 - (embedding <=> %s::vector) AS similarity
                FROM memories
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding_str, embedding_str, top_k),
            )
            rows = cur.fetchall()
            return [row[0] for row in rows if row[0]]
    finally:
        conn.close()


def _search_by_text(query: str, top_k: int = 3) -> List[str]:
    """降级：通过 ILIKE 全文搜索"""
    import psycopg2

    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME,
        user=PG_USER, password=PG_PASSWORD,
        connect_timeout=5,
    )
    try:
        # 取 query 中的关键词（去除短词）
        keywords = [w for w in query.replace("，", " ").replace("、", " ").split() if len(w) >= 2]
        if not keywords:
            keywords = [query[:20]]
        # 用 OR 组合
        conditions = " OR ".join(["content ILIKE %s"] * len(keywords))
        params = [f"%{kw}%" for kw in keywords[:5]]
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT content FROM memories WHERE {conditions} LIMIT %s",
                params + [top_k],
            )
            rows = cur.fetchall()
            return [row[0] for row in rows if row[0]]
    finally:
        conn.close()


def search_writing_knowledge(query: str, top_k: int = 3) -> List[str]:
    """
    搜索写作知识。
    优先使用向量检索，失败则降级为文本搜索。
    任何异常均返回空列表，不阻塞主流程。
    """
    if not query or not query.strip():
        return []

    # 尝试向量检索
    try:
        embedding = _generate_embedding(query[:500])
        results = _search_by_vector(embedding, top_k)
        if results:
            logger.info("RAG vector search returned %d results for query: %s", len(results), query[:60])
            return results
    except Exception as e:
        logger.warning("RAG vector search failed, falling back to text search: %s", e)

    # 降级：文本搜索
    try:
        results = _search_by_text(query, top_k)
        if results:
            logger.info("RAG text search returned %d results for query: %s", len(results), query[:60])
            return results
    except Exception as e:
        logger.warning("RAG text search also failed: %s", e)

    return []

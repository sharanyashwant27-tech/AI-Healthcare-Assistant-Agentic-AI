"""Neo4j knowledge graph client with in-memory fallback (GraphRAG)."""

from typing import Any, Dict, List, Optional, Tuple

from core.config import settings
from core.logging import get_logger
from graphrag.schema import BENEFITS, EXAMPLE_PATH, PATIENT_CENTERED_ENTITIES, RELATIONSHIPS

logger = get_logger(__name__)


class InMemoryGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def upsert_node(self, label: str, key: str, props: Dict[str, Any]) -> None:
        self.nodes[f"{label}:{key}"] = {"label": label, "key": key, **props}

    def relate(
        self,
        from_label: str,
        from_key: str,
        rel: str,
        to_label: str,
        to_key: str,
        props: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.edges.append(
            {
                "from": f"{from_label}:{from_key}",
                "to": f"{to_label}:{to_key}",
                "rel": rel,
                "props": props or {},
            }
        )

    def neighbors(self, label: str, key: str, rel: Optional[str] = None) -> List[Dict[str, Any]]:
        node_id = f"{label}:{key}"
        out = []
        for e in self.edges:
            if e["from"] == node_id and (rel is None or e["rel"] == rel):
                n = dict(self.nodes.get(e["to"], {"id": e["to"]}))
                n["via"] = e["rel"]
                out.append(n)
            elif e["to"] == node_id and (rel is None or e["rel"] == rel):
                n = dict(self.nodes.get(e["from"], {"id": e["from"]}))
                n["via"] = e["rel"]
                out.append(n)
        return out

    def search(self, term: str) -> List[Dict[str, Any]]:
        term_l = term.lower()
        return [n for n in self.nodes.values() if term_l in str(n).lower()]

    def paths_from(self, label: str, key: str, max_depth: int = 6) -> List[List[Dict[str, Any]]]:
        """BFS path expansion for explainable relationship reasoning."""
        start = f"{label}:{key}"
        if start not in self.nodes:
            return []
        paths: List[List[Dict[str, Any]]] = []
        queue: List[Tuple[str, List[Dict[str, Any]], set[str]]] = [
            (start, [{"label": label, "key": key, **self.nodes[start]}], {start})
        ]
        while queue:
            node_id, path, visited = queue.pop(0)
            if len(path) > 1:
                paths.append(path)
            if len(path) >= max_depth:
                continue
            for e in self.edges:
                nxt = None
                rel = e["rel"]
                if e["from"] == node_id and e["to"] not in visited:
                    nxt = e["to"]
                elif e["to"] == node_id and e["from"] not in visited:
                    nxt = e["from"]
                if not nxt:
                    continue
                node = dict(self.nodes.get(nxt, {"id": nxt}))
                node["via"] = rel
                queue.append((nxt, path + [node], visited | {nxt}))
        return paths[:50]


class Neo4jGraphService:
    RELATIONSHIPS = RELATIONSHIPS
    ENTITIES = PATIENT_CENTERED_ENTITIES
    BENEFITS = BENEFITS

    def __init__(self) -> None:
        self._driver = None
        self._memory = InMemoryGraph()
        self._use_memory = False
        self._connect()
        self.seed_demo_graph()

    def _connect(self) -> None:
        try:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            with self._driver.session() as session:
                session.run("RETURN 1")
            logger.info("neo4j_connected", uri=settings.neo4j_uri)
        except Exception as exc:  # noqa: BLE001
            logger.warning("neo4j_fallback_memory", error=str(exc))
            self._use_memory = True
            self._driver = None

    def run(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self._use_memory or self._driver is None:
            return []
        with self._driver.session() as session:
            result = session.run(cypher, params or {})
            return [r.data() for r in result]

    def upsert_node(self, label: str, key: str, props: Dict[str, Any]) -> None:
        if self._use_memory or self._driver is None:
            self._memory.upsert_node(label, key, props)
            return
        props = {**props, "key": key}
        self.run(
            f"MERGE (n:{label} {{key: $key}}) SET n += $props RETURN n",
            {"key": key, "props": props},
        )

    def relate(
        self,
        from_label: str,
        from_key: str,
        rel: str,
        to_label: str,
        to_key: str,
        props: Optional[Dict[str, Any]] = None,
    ) -> None:
        if rel not in self.RELATIONSHIPS:
            raise ValueError(f"Unsupported relationship: {rel}")
        if self._use_memory or self._driver is None:
            self._memory.relate(from_label, from_key, rel, to_label, to_key, props)
            return
        self.run(
            f"""
            MERGE (a:{from_label} {{key: $from_key}})
            MERGE (b:{to_label} {{key: $to_key}})
            MERGE (a)-[r:{rel}]->(b)
            SET r += $props
            RETURN r
            """,
            {"from_key": from_key, "to_key": to_key, "props": props or {}},
        )

    def seed_demo_graph(self) -> None:
        """Seed patient-centered graph + John diabetes example path."""
        # Core demo patient (p1) + John example
        entities = [
            ("Patient", "p1", {"name": "Demo Patient"}),
            ("Patient", "john", {"name": "John"}),
            ("Disease", "influenza", {"name": "Influenza"}),
            ("Disease", "migraine", {"name": "Migraine"}),
            ("Disease", "diabetes", {"name": "Diabetes"}),
            ("Disease", "kidney_disease", {"name": "Kidney Disease"}),
            ("Symptom", "fever", {"name": "Fever"}),
            ("Symptom", "headache", {"name": "Headache"}),
            ("Symptom", "cough", {"name": "Cough"}),
            ("Symptom", "polyuria", {"name": "Frequent urination"}),
            ("Medicine", "paracetamol", {"name": "Paracetamol"}),
            ("Medicine", "metformin", {"name": "Metformin"}),
            ("Allergy", "penicillin", {"name": "Penicillin"}),
            ("Doctor", "d1", {"name": "Dr. Sharma", "specialty": "Internal Medicine"}),
            ("Doctor", "dr_patel", {"name": "Dr. Patel", "specialty": "Endocrinology"}),
            ("Hospital", "h1", {"name": "City General Hospital"}),
            ("Hospital", "city_general", {"name": "City General Hospital"}),
            ("Insurance", "ins1", {"name": "HealthPlus Gold"}),
            ("LabTest", "cbc", {"name": "CBC"}),
            ("LabTest", "creatinine", {"name": "Creatinine Test"}),
            ("Appointment", "a1", {"status": "scheduled"}),
            ("Appointment", "a_john", {"status": "scheduled"}),
        ]
        for label, key, props in entities:
            self.upsert_node(label, key, props)

        rels = [
            # Demo patient hub
            ("Patient", "p1", "HAS_SYMPTOM", "Symptom", "fever"),
            ("Patient", "p1", "HAS_SYMPTOM", "Symptom", "cough"),
            ("Patient", "p1", "HAS_DISEASE", "Disease", "influenza"),
            ("Patient", "p1", "TAKES_MEDICINE", "Medicine", "paracetamol"),
            ("Patient", "p1", "ALLERGIC_TO", "Allergy", "penicillin"),
            ("Patient", "p1", "VISITS", "Hospital", "h1"),
            ("Patient", "p1", "BOOKED", "Appointment", "a1"),
            ("Patient", "p1", "COVERED_BY", "Insurance", "ins1"),
            ("Patient", "p1", "HAS_LAB_TEST", "LabTest", "cbc"),
            ("Patient", "p1", "TREATED_BY", "Doctor", "d1"),
            ("Doctor", "d1", "REFERRED_TO", "Hospital", "h1"),
            ("Doctor", "d1", "PRESCRIBED", "Medicine", "paracetamol"),
            ("Disease", "influenza", "HAS_SYMPTOM", "Symptom", "fever"),
            ("Disease", "influenza", "HAS_SYMPTOM", "Symptom", "cough"),
            ("Disease", "migraine", "HAS_SYMPTOM", "Symptom", "headache"),
            # John example path:
            # John → Diabetes → Metformin → Kidney Disease → Creatinine → Doctor → Hospital
            ("Patient", "john", "HAS_DISEASE", "Disease", "diabetes"),
            ("Patient", "john", "HAS_SYMPTOM", "Symptom", "polyuria"),
            ("Patient", "john", "TAKES_MEDICINE", "Medicine", "metformin"),
            ("Patient", "john", "HAS_LAB_TEST", "LabTest", "creatinine"),
            ("Patient", "john", "TREATED_BY", "Doctor", "dr_patel"),
            ("Patient", "john", "VISITS", "Hospital", "city_general"),
            ("Patient", "john", "COVERED_BY", "Insurance", "ins1"),
            ("Patient", "john", "BOOKED", "Appointment", "a_john"),
            ("Medicine", "metformin", "INDICATED_FOR", "Disease", "diabetes"),
            ("Disease", "diabetes", "ASSOCIATED_WITH", "Disease", "kidney_disease"),
            ("Disease", "kidney_disease", "MONITORED_BY", "LabTest", "creatinine"),
            ("Doctor", "dr_patel", "PRESCRIBED", "Medicine", "metformin"),
            ("Doctor", "dr_patel", "REFERRED_TO", "Hospital", "city_general"),
            ("Appointment", "a_john", "TREATED_BY", "Doctor", "dr_patel"),
        ]
        for item in rels:
            self.relate(*item)

        logger.info(
            "graph_seeded",
            entities=len(entities),
            relationships=len(rels),
            example="John -> Diabetes -> Metformin -> Kidney Disease -> Creatinine -> Doctor -> Hospital",
        )

    def query_symptoms_to_diseases(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        if self._use_memory or self._driver is None:
            results = []
            for s in symptoms:
                for node in self._memory.search(s):
                    if node.get("label") == "Symptom":
                        for n in self._memory.neighbors("Symptom", node["key"], "HAS_SYMPTOM"):
                            if n.get("label") == "Disease":
                                results.append(n)
            return results
        return self.run(
            """
            UNWIND $symptoms AS s
            MATCH (sym:Symptom)
            WHERE toLower(sym.name) CONTAINS toLower(s)
            MATCH (d:Disease)-[:HAS_SYMPTOM]->(sym)
            RETURN DISTINCT d.name AS disease, d.key AS key
            """,
            {"symptoms": symptoms},
        )

    def patient_neighborhood(self, patient_key: str = "john") -> Dict[str, List[Dict[str, Any]]]:
        """Return patient-centered linked entities for GraphRAG context."""
        groups = {
            "diseases": "HAS_DISEASE",
            "symptoms": "HAS_SYMPTOM",
            "medicines": "TAKES_MEDICINE",
            "allergies": "ALLERGIC_TO",
            "doctors": "TREATED_BY",
            "hospitals": "VISITS",
            "lab_tests": "HAS_LAB_TEST",
            "insurance": "COVERED_BY",
            "appointments": "BOOKED",
        }
        if self._use_memory or self._driver is None:
            return {
                name: self._memory.neighbors("Patient", patient_key, rel)
                for name, rel in groups.items()
            }
        out: Dict[str, List[Dict[str, Any]]] = {}
        for name, rel in groups.items():
            rows = self.run(
                f"""
                MATCH (p:Patient {{key: $key}})-[:{rel}]->(n)
                RETURN n.name AS name, n.key AS key, labels(n)[0] AS label
                """,
                {"key": patient_key},
            )
            out[name] = rows
        return out

    def explain_path(self, patient_key: str = "john") -> List[Dict[str, Any]]:
        """
        Explainable example path:
        John → Diabetes → Metformin → Kidney Disease → Creatinine → Doctor → Hospital
        """
        if patient_key == "john":
            # Canonical demo path for explainability
            canonical = [
                {"step": 0, "label": "Patient", "key": "john", "name": "John", "via": None},
                {"step": 1, "label": "Disease", "key": "diabetes", "name": "Diabetes", "via": "HAS_DISEASE"},
                {"step": 2, "label": "Medicine", "key": "metformin", "name": "Metformin", "via": "TAKES_MEDICINE"},
                {
                    "step": 3,
                    "label": "Disease",
                    "key": "kidney_disease",
                    "name": "Kidney Disease",
                    "via": "ASSOCIATED_WITH",
                },
                {
                    "step": 4,
                    "label": "LabTest",
                    "key": "creatinine",
                    "name": "Creatinine Test",
                    "via": "MONITORED_BY",
                },
                {"step": 5, "label": "Doctor", "key": "dr_patel", "name": "Dr. Patel", "via": "TREATED_BY"},
                {
                    "step": 6,
                    "label": "Hospital",
                    "key": "city_general",
                    "name": "City General Hospital",
                    "via": "VISITS",
                },
            ]
            if self._use_memory or self._driver is None:
                return canonical

        if self._use_memory or self._driver is None:
            paths = self._memory.paths_from("Patient", patient_key, max_depth=7)
            preferred = []
            for path in paths:
                names = " ".join(str(p.get("name", "")).lower() for p in path)
                if "diabetes" in names and "metformin" in names:
                    preferred.append(path)
            best = preferred[0] if preferred else (paths[0] if paths else [])
            return [
                {
                    "step": i,
                    "label": n.get("label"),
                    "key": n.get("key"),
                    "name": n.get("name"),
                    "via": n.get("via"),
                }
                for i, n in enumerate(best)
            ]

        rows = self.run(
            """
            MATCH path = (p:Patient {key: $key})-[:HAS_DISEASE]->(d:Disease {key: 'diabetes'})
            OPTIONAL MATCH (p)-[:TAKES_MEDICINE]->(m:Medicine {key: 'metformin'})
            OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(kd:Disease {key: 'kidney_disease'})
            OPTIONAL MATCH (kd)-[:MONITORED_BY]->(lt:LabTest {key: 'creatinine'})
            OPTIONAL MATCH (p)-[:TREATED_BY]->(doc:Doctor)
            OPTIONAL MATCH (p)-[:VISITS]->(h:Hospital)
            RETURN p.name AS patient, d.name AS disease, m.name AS medicine,
                   kd.name AS complication, lt.name AS lab_test,
                   doc.name AS doctor, h.name AS hospital
            LIMIT 1
            """,
            {"key": patient_key},
        )
        if not rows:
            return []
        r = rows[0]
        ordered = [
            ("Patient", r.get("patient")),
            ("Disease", r.get("disease")),
            ("Medicine", r.get("medicine")),
            ("Disease", r.get("complication")),
            ("LabTest", r.get("lab_test")),
            ("Doctor", r.get("doctor")),
            ("Hospital", r.get("hospital")),
        ]
        return [
            {"step": i, "label": label, "name": name}
            for i, (label, name) in enumerate(ordered)
            if name
        ]

    def reason(self, query: str, patient_key: Optional[str] = None) -> Dict[str, Any]:
        """Relationship reasoning entrypoint for GraphRAG."""
        q = query.lower()
        patient_key = patient_key or ("john" if "john" in q or "diabetes" in q else "p1")
        neighborhood = self.patient_neighborhood(patient_key)
        path = self.explain_path(patient_key)
        keyword_hits = self._memory.search(query) if self._use_memory else []
        return {
            "patient_key": patient_key,
            "neighborhood": neighborhood,
            "explanation_path": path,
            "keyword_hits": keyword_hits[:15],
            "example_path_template": [
                f"{label}:{key} ({name})" for label, key, name in EXAMPLE_PATH
            ],
            "benefits": self.BENEFITS,
            "entities": self.ENTITIES,
        }

    def describe(self) -> Dict[str, Any]:
        return {
            "database": "Neo4j",
            "mode": self.health(),
            "entities": self.ENTITIES,
            "relationships": self.RELATIONSHIPS,
            "benefits": self.BENEFITS,
            "example": "John → Diabetes → Metformin → Kidney Disease → Creatinine Test → Doctor → Hospital",
        }

    def health(self) -> str:
        return "memory" if self._use_memory else "ok"

    def close(self) -> None:
        if self._driver:
            self._driver.close()


_graph: Optional[Neo4jGraphService] = None


def get_graph_service() -> Neo4jGraphService:
    global _graph
    if _graph is None:
        _graph = Neo4jGraphService()
    return _graph

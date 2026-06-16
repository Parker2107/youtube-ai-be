from neo4j import GraphDatabase
# pyright: ignore[reportArgumentType]
from typing import cast

dummydata = [
    {
  "video_id": "vid_001",
  "title": "How Transformers Changed AI",
  "entities": [
    {
      "name": "Transformer",
      "type": "CONCEPT"
    },
    {
      "name": "Attention Mechanism",
      "type": "CONCEPT"
    },
    {
      "name": "RNN",
      "type": "CONCEPT"
    },
    {
      "name": "OpenAI",
      "type": "ORGANIZATION"
    },
    {
      "name": "ChatGPT",
      "type": "TECHNOLOGY"
    },
    {
      "name": "Large Language Model",
      "type": "CONCEPT"
    }
  ],
  "relationships": [
    {
      "source": "Transformer",
      "target": "Attention Mechanism",
      "relation": "USES"
    },
    {
      "source": "Transformer",
      "target": "RNN",
      "relation": "REPLACES"
    },
    {
      "source": "OpenAI",
      "target": "ChatGPT",
      "relation": "CREATED"
    },
    {
      "source": "ChatGPT",
      "target": "Transformer",
      "relation": "DEPENDS_ON"
    },
    {
      "source": "Large Language Model",
      "target": "Transformer",
      "relation": "USES"
    }
  ]
},
    {
  "video_id": "vid_002",
  "title": "The Twin Prime Conjecture",
  "entities": [
    {
      "name": "Twin Prime Conjecture",
      "type": "CONCEPT"
    },
    {
      "name": "Twin Primes",
      "type": "CONCEPT"
    },
    {
      "name": "Prime Numbers",
      "type": "CONCEPT"
    },
    {
      "name": "Prime Gap",
      "type": "CONCEPT"
    },
    {
      "name": "Number Theory",
      "type": "CONCEPT"
    },
    {
      "name": "Edmund Landau",
      "type": "PERSON"
    },
    {
      "name": "Yitang Zhang",
      "type": "PERSON"
    }
  ],
  "relationships": [
    {
      "source": "Twin Prime Conjecture",
      "target": "Twin Primes",
      "relation": "RELATED_TO"
    },
    {
      "source": "Twin Primes",
      "target": "Prime Numbers",
      "relation": "PART_OF"
    },
    {
      "source": "Prime Gap",
      "target": "Prime Numbers",
      "relation": "RELATED_TO"
    },
    {
      "source": "Twin Prime Conjecture",
      "target": "Number Theory",
      "relation": "PART_OF"
    },
    {
      "source": "Edmund Landau",
      "target": "Twin Prime Conjecture",
      "relation": "RELATED_TO"
    },
    {
      "source": "Yitang Zhang",
      "target": "Prime Gap",
      "relation": "CONTRIBUTED_TO"
    }
  ]
},
    {
  "video_id": "vid_003",
  "title": "Building APIs with Django",
  "entities": [
    {
      "name": "Django",
      "type": "TECHNOLOGY"
    },
    {
      "name": "Python",
      "type": "TECHNOLOGY"
    },
    {
      "name": "Django REST Framework",
      "type": "TECHNOLOGY"
    },
    {
      "name": "PostgreSQL",
      "type": "TECHNOLOGY"
    },
    {
      "name": "REST API",
      "type": "CONCEPT"
    },
    {
      "name": "Authentication",
      "type": "CONCEPT"
    }
  ],
  "relationships": [
    {
      "source": "Django",
      "target": "Python",
      "relation": "DEPENDS_ON"
    },
    {
      "source": "Django REST Framework",
      "target": "Django",
      "relation": "DEPENDS_ON"
    },
    {
      "source": "Django",
      "target": "PostgreSQL",
      "relation": "USES"
    },
    {
      "source": "Django REST Framework",
      "target": "REST API",
      "relation": "IMPLEMENTS"
    },
    {
      "source": "Authentication",
      "target": "REST API",
      "relation": "PART_OF"
    }
  ]
},
    {
  "video_id": "vid_004",
  "title": "Introduction to Knowledge Graphs",
  "entities": [
    {
      "name": "Knowledge Graph",
      "type": "CONCEPT"
    },
    {
      "name": "Neo4j",
      "type": "TECHNOLOGY"
    },
    {
      "name": "Node",
      "type": "CONCEPT"
    },
    {
      "name": "Relationship",
      "type": "CONCEPT"
    },
    {
      "name": "Graph Database",
      "type": "CONCEPT"
    },
    {
      "name": "Cypher",
      "type": "TECHNOLOGY"
    }
  ],
  "relationships": [
    {
      "source": "Neo4j",
      "target": "Knowledge Graph",
      "relation": "IMPLEMENTS"
    },
    {
      "source": "Knowledge Graph",
      "target": "Node",
      "relation": "PART_OF"
    },
    {
      "source": "Knowledge Graph",
      "target": "Relationship",
      "relation": "PART_OF"
    },
    {
      "source": "Neo4j",
      "target": "Graph Database",
      "relation": "IMPLEMENTS"
    },
    {
      "source": "Cypher",
      "target": "Neo4j",
      "relation": "DEPENDS_ON"
    }
  ]
}
]

class Neo4jGraphBuilder:

    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "qwertyuiop"))

    def build_graph(self, graph_data):

      with self.driver.session(database="youtube") as session:

        # Create Video Node
        session.run(
            """
            MERGE (v:Video {video_id: $video_id})
            SET v.title = $title
            """,
            video_id=graph_data["video_id"],
            title=graph_data["title"]
        )

        # Create Entity Nodes + Video Relationships
        for entity in graph_data["entities"]:

            label = entity["type"]

            query = f"""
            MERGE (e:{label} {{name:$name}})

            WITH e

            MATCH (v:Video {{video_id:$video_id}})

            MERGE (v)-[:MENTIONS]->(e)
            """

            session.run(
                query,
                name=entity["name"],
                video_id=graph_data["video_id"]
            )

        # Create Entity Relationships
        for rel in graph_data["relationships"]:

            query = f"""
            MATCH (a {{name:$source}})
            MATCH (b {{name:$target}})
            MERGE (a)-[:{rel['relation']}]->(b)
            """

            session.run(
                query,
                source=rel["source"],
                target=rel["target"]
            )

    def clear_graph(self):

        with self.driver.session(database="youtube") as session:
            session.run("MATCH (n) DETACH DELETE n")
            
            
if __name__ == "__main__":

    builder = Neo4jGraphBuilder()

    builder.clear_graph()

    for graph in dummydata:
        builder.build_graph(graph)

    print("Graph loaded successfully")
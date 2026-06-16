from ollama import chat
import json

ENTITY_TYPES = [
    "CONCEPT",
    "PERSON",
    "ORGANIZATION",
    "LOCATION",
    "TECHNOLOGY",
]

RELATION_TYPES = [
    "USES",
    "REPLACES",
    "CREATED",
    "WORKS_FOR",
    "LOCATED_IN",
    "PART_OF",
    "DEPENDS_ON",
    "RELATED_TO",
    "ENABLES",
    "IMPLEMENTS"
]


def create_relations(text):

    entity_types = "\n".join(
        f"- {entity}" for entity in ENTITY_TYPES
    )

    relation_types = "\n".join(
        f"- {relation}" for relation in RELATION_TYPES
    )

# Do not include explanations.
# Do not include markdown.
# Do not include code blocks.
# Do not include text before or after the JSON.

    prompt = f"""
You are a Knowledge Graph Extraction System.

Your task is to analyze the provided transcript chunk and extract:

1. Entities
2. Relationships between entities

Rules:

Return ONLY valid JSON.

- Use only the entity types above.
- Use only the relation types above.
- Do not invent entities.
- Do not invent relationships.
- Ignore generic locations such as "world", "society", or "people".

Return ONLY valid JSON.

A relationship must be directly supported by the text.

Do not create relationships based solely on proximity of entities.

----------------------------------------
ALLOWED ENTITY TYPES
----------------------------------------

{entity_types}

----------------------------------------
ALLOWED RELATION TYPES
----------------------------------------

{relation_types}

Only use the relation types listed above.

If no relation clearly exists, do not invent one.

----------------------------------------
OUTPUT SCHEMA
----------------------------------------

{{
    "entities": [
        {{
            "name": "string",
            "type": "one of allowed entity types"
        }}
    ],
    "relationships": [
        {{
            "source": "entity_name",
            "target": "entity_name",
            "relation": "one of allowed relation types"
        }}
    ]
}}

----------------------------------------
TRANSCRIPT CHUNK
----------------------------------------

{text}

RETURN ONLY JSON.
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )
    result = json.loads(response["message"]["content"])
    print(result)

    for entity in result["entities"]:
        assert entity["type"] in ENTITY_TYPES

    for rel in result["relationships"]:
        assert rel["relation"] in RELATION_TYPES
    return result


# create_relations("The Transformer architecture revolutionized natural language processing by replacing many recurrent neural network based approaches. One of its key innovations was the Attention Mechanism, which allowed models to focus on relevant parts of the input sequence. OpenAI later used Transformer-based architectures to develop ChatGPT, which became one of the most widely used AI systems in the world.")
create_relations("- [Derek] On the morning of the 17th of April, 2013, the journal Annals of Mathematics received a curious email. It claimed to contain a 50 page proof relating to one of the oldest unsolved problems in mathematics. A problem that great mathematician Edmund Landau called unattackable. But this proof didn't come from a famous professor, it came from an unknown. (bright music) Someone who had once spent years working at a subway restaurant. - So, they're like, okay, surely this isn't gonna work out, but whatever. You know, we'll send it to a referee. - [Derek] They expected to find a mistake in an afternoon, but they didn't. So, they went through it again, closely studying the fragile parts where a proof like this normally falls apart, but still nothing. Soon they realized they were witnessing a breakthrough. - Oh, damn, he did it. - So, how did he do It? What did the experts miss and what was the problem he was working on? He was working on a new way to attack one of the hardest unsolved problems in number theory, the twin prime conjecture. The twin primes are prime numbers separated by just one number, like 11 and 13 or 17 and 19. As you go up, the number line, primes become rarer and twin primes become rarer still. But the twin prime conjecture claims that there are infinitely many of them you never run out. But is it true? Well, one way to approach this problem is to look at the gaps between consecutive primes as you go up the number line. (bright music) Now, at first they seem chaotic, but if you average them out, a clear trend emerges. The average gap between two primes grows roughly as the natural logarithm of the number N. So, for example, the average gap between primes around 100, is approximately 4.6. The average gap between primes around 1000 is 6.9. Logarithms grow very slowly, but they do keep growing forever. So, as N approaches infinity, the average gap between primes also goes to infinity, which is not particularly encouraging if you expect to always be able to find primes that are just two apart. But if you start checking large numbers, then after a million you quickly find the twin primes, 1,000,037 and 1,000,039. Past a billion, there's 1,000,000,007 and 1,000,000,009.")
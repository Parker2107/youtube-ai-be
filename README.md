# YouTube AI Chatbot

An intelligent chatbot system that analyzes YouTube videos using advanced NLP techniques and vector embeddings. The system extracts transcripts from any YouTube video, intelligently chunks content while preserving semantic meaning, generates dense vector embeddings, and stores them in a pgvector database. Users can then query the system with natural language questions, and the chatbot retrieves the most relevant video segments using similarity search (RAG - Retrieval-Augmented Generation), enabling accurate, context-grounded answers directly from video content without hallucination.

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone <repo-url>
cd youtube-ai-be
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

Activate:

**Mac/Linux:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. NLTK Setup

Run once after installation:

```bash
python
```

Then in Python:

```python
import nltk
nltk.download('punkt')
```

This downloads the pretrained sentence tokenizer for sentence-aware chunking.

---

## Pipeline

```text
YouTube URL
    ↓
Extract Transcript
    ↓
Preprocess Text
    ↓
Semantic Chunking (sentence-aware)
    ↓
Generate Embeddings
    ↓
Store in pgvector Database
    ↓
User Query
    ↓
Embed Query
    ↓
Similarity Search
    ↓
Retrieve Relevant Chunks
    ↓
Generate Answer (LLM)
```

---

## Core Components

### 1. Transcript Fetching

The system extracts video transcripts directly from YouTube videos using the `youtube-transcript-api` library. This library:

- Accepts YouTube video URLs or video IDs
- Retrieves auto-generated or manually uploaded captions
- Returns transcript data with timestamps for each segment
- Handles errors gracefully when transcripts are unavailable

The `transcript.py` service module provides helper functions to:

- Extract video IDs from various YouTube URL formats
- Fetch transcripts with proper error handling
- Process transcript metadata

### 2. Chunking Strategies

The system supports two intelligent chunking approaches:

#### Raw Chunking (`chunk_transcript`)

- Splits transcripts based on **token count** (default: 200 tokens max)
- Maintains overlap of the last 3 entries for context continuity
- Preserves timestamp information for each chunk
- Ideal for preserving temporal references in the transcript

#### Semantic Chunking (`semantic_chunking`)

- Splits transcripts into **sentence-aware chunks** using NLTK
- Respects semantic boundaries (complete sentences)
- Maintains 1-sentence overlap between chunks for semantic continuity
- Filters out sentences with fewer than 3 words
- Produces cleaner, more meaningful chunks

#### Preprocessing (`preprocess_transcript`)

- Removes speaker indicators (`>>` characters)
- Normalizes whitespace (collapses multiple spaces/newlines)
- Strips leading and trailing whitespace
- Applied before chunking for cleaner text

### 3. Vector Storing

The system stores embeddings in **pgvector**, a PostgreSQL extension that enables:

- Dense vector storage for embeddings
- Fast similarity search using vector operations
- Scalable storage for large transcript datasets
- Integration with Django ORM for seamless data management

The `embedding.py` service:

- Generates embeddings for each chunk using sentence-transformers
- Stores vectors alongside chunk text and metadata
- Organizes embeddings for efficient retrieval

### 4. Retrieval

The retrieval pipeline performs similarity-based search:

- **Query Embedding**: User questions are embedded using the same model
- **Similarity Search**: pgvector finds the most similar chunks using cosine similarity
- **Ranking**: Retrieved chunks are ranked by relevance score
- **Context Assembly**: Top-k chunks are combined to form the LLM context
- **Answer Generation**: The LLM generates answers based on retrieved context

This RAG (Retrieval-Augmented Generation) approach ensures:

- Answers grounded in video content
- Reduced hallucination through explicit source retrieval
- Relevant context preservation with proper chunking


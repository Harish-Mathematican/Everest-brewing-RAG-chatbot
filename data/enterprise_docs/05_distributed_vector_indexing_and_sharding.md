# 📐 #Gyan Labs — Distributed Vector Indexing, Sharding & Quantization

## Abstract
As enterprise knowledge bases scale to millions of technical artifacts, memory footprint and retrieval latency become the primary operational bottlenecks. **#Gyan Labs RAG Platform** employs hierarchical indexing and scalar quantization to maintain sub-10ms P99 search latencies at multi-million vector scale.

## Indexing Topology
1. **HNSW (Hierarchical Navigable Small World) Graphs:**
   - Multi-layer proximity graph construction with `M=16` (connections per node) and `efConstruction=200`.
   - Logarithmic search complexity $\mathcal{O}(\log N)$ ensuring constant-time neighbor discovery across cluster nodes.

2. **Product Quantization (PQ-8) & Dimensionality Reduction:**
   - Compresses 384-dimensional and 768-dimensional float32 vectors into 8-bit quantized centroid codes.
   - Reduces RAM memory footprint by 75% while maintaining greater than 98.4% retrieval fidelity.

3. **Multi-Region Vector Sharding:**
   - Vector indexes are horizontally partitioned across Canadian (Toronto / Montreal) and US (San Francisco / Seattle) data centers using consistent hashing.

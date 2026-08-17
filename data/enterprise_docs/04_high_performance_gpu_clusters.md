# ⚡ #Gyan Labs — GPU Infrastructure & Distributed Model Training

## Infrastructure Overview
#Gyan Labs operates dedicated high-performance GPU clusters distributed across North American tier-3+ data centers in **Montreal (QC), Toronto (ON), Seattle (WA), and San Francisco (CA)**.

### Compute Fleet Specifications:
- **Primary Training Clusters:** Nodes equipped with **8x NVIDIA H100 SXM5 GPUs (80GB HBM3 memory per GPU)** interconnected via 3.2 Tbps NVIDIA Quantum-2 InfiniBand.
- **Inference & RAG Acceleration:** Nodes powered by **NVIDIA L40S and A100 Tensor Core GPUs** optimized for low-latency vLLM and TensorRT-LLM model serving.
- **Unified Vector Storage:** Distributed NVMe storage arrays achieving over 1.2M random read IOPS for real-time embedding lookups.

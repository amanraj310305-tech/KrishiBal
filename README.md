# KrishiBal – AI-Driven Smart Farming Platform for Smallholder Agriculture

KrishiBal is a research-oriented AI platform designed to support smallholder farmers in India through computer vision, conversational AI and real-time data integration. The system focuses on building accessible, multilingual and low-cost decision-support tools for agricultural advisory, crop health monitoring and information access in low-resource rural environments.

The project was developed by **Aman Raj (B.Tech Computer Science Engineering, GITAM University)** as an applied research initiative aimed at studying how modern machine learning and natural language technologies can be deployed responsibly for sustainable agriculture and social impact.

---

## Research Motivation

Smallholder farmers frequently experience delayed crop disease diagnosis, limited access to agronomic expertise, language barriers in digital platforms, and fragmented availability of weather, policy and market information.  
This project investigates how computer vision and conversational AI systems, combined with real-time data pipelines, can provide practical and scalable decision-support solutions in multilingual and low-infrastructure agricultural settings.

---

## Core Contributions

### Plant Disease Detection (Computer Vision)
A deep learning–based image classification pipeline that detects crop diseases from farmer-captured images and returns interpretable disease labels along with recommended treatment measures. The system includes image preprocessing, model inference, class mapping and web-based deployment for real-time usage.

### Multilingual Conversational Advisory System
A conversational AI system supporting both text and voice queries for delivering agricultural guidance. The module integrates speech-to-text, domain-focused large language model prompting, and text-to-speech synthesis to enable accessible interaction for farmers with diverse literacy and language backgrounds.

### Real-Time Agricultural Information Integration
The platform aggregates and exposes multiple external data sources, including localized weather information, agriculture-related news and government scheme updates, enabling context-aware advisory and decision support.

### Community Knowledge Sharing and Farmer Marketplace
A lightweight forum and direct farmer-to-consumer marketplace interface that enables peer knowledge exchange, collaborative problem solving and improved market access for smallholder farmers.

### End-to-End Machine Learning and Data Pipeline
A structured research workflow covering dataset preparation, preprocessing, feature engineering, model training, evaluation and iterative experimentation to ensure reliable performance and reproducibility.

---

## Research Scope and Future Work

Future research directions include multilingual speech recognition and translation for regional languages, early crop stress and disease severity estimation, multimodal fusion of satellite imagery with ground-level images, and controlled evaluation studies with real farmer interaction data to assess robustness, usability and fairness of the advisory system.

---

## Project Presentation

Download the full project presentation (slides covering architecture, methodology, experiments, demonstrations, results and future scope):  
**[Krisibal Project Presentation (PDF)](KrishiBal_compressed.pdf)**

---

## Technical Stack

**Programming Languages**  
Python (primary), C, Java

**Machine Learning and Data Science**  
NumPy, Pandas, scikit-learn, OpenCV, PyTorch, YOLOv8

**Natural Language Processing and Speech**  
NLTK, large-language-model based conversational pipelines, speech-to-text and text-to-speech components

**Backend and Web**  
Flask, REST APIs

**Databases**  
SQL and NoSQL (cloud-based data storage)

**Tools**  
Git, GitHub, Google Colab, Jupyter notebooks, research experimentation workflows

---

## How to Run

```bash
git clone https://github.com/yourusername/krisibal-ai-smart-farming.git
cd krisibal-ai-smart-farming
pip install -r requirements.txt
python app.py

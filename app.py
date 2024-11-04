from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
from typing import List, Dict
from collections import defaultdict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Advanced Health NER API",
    description="NER API specifically for detecting diseases, symptoms, and treatments.",
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)




model_dir = "model"
nlp = spacy.load(model_dir)

# Color mapping for health-related entities
ENTITY_COLORS = {
    "DISEASE": "red",
    "SYMPTOM": "orange",
    "TREATMENT": "green"
}

# Frequency counters for entities
entity_frequency = defaultdict(lambda: defaultdict(int))

class TextRequest(BaseModel):
    text: str


class CommonEntityResponse(BaseModel):
    category: str
    entities: List[Dict[str, int]]
    
    
class EntityDetail(BaseModel):
    entity: str
    text: str
    color: str = None
    frequency: int = None

class EntityResponse(BaseModel):
    text: str
    entities: List[EntityDetail]

@app.post("/extract_entities", response_model=EntityResponse)
async def extract_entities(request: TextRequest):
    doc = nlp(request.text)
    entities = []
    
    for ent in doc.ents:
        entity_type = ent.label_.lower()
        
        # Increment frequency count
        entity_frequency[entity_type][ent.text] += 1
        
        entity_info = {
            "entity": ent.label_,
            "text": ent.text,
            "color": ENTITY_COLORS.get(ent.label_, "grey"),
            "frequency": entity_frequency[entity_type][ent.text]
        }
        entities.append(entity_info)
    
    return EntityResponse(text=request.text, entities=entities)

# @app.get("/get_common_entities", response_model=Dict[str, List[Dict[str, int]]])
# async def get_common_entities(top_n: int = 5):
#     # Adjusting output to match expected dictionary format for FastAPI validation
#     results = {
#         category: [{"text": text, "count": count} for text, count in sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:top_n]]
#         for category, freqs in entity_frequency.items()
#     }
#     return results


@app.get("/get_common_entities", response_model=List[CommonEntityResponse])
async def get_common_entities(top_n: int = 5):
    results = []
    for category, freqs in entity_frequency.items():
        common_entities = sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:top_n]
        results.append({"category": category, "entities": [{k: v} for k, v in common_entities]})
    return results

@app.post("/batch_extract_entities", response_model=List[EntityResponse])
async def batch_extract_entities(request: List[TextRequest]):
    responses = []
    
    for item in request:
        doc = nlp(item.text)
        entities = []
        
        for ent in doc.ents:
            entity_type = ent.label_.lower()
            
            # Increment frequency count
            entity_frequency[entity_type][ent.text] += 1
            
            entity_info = {
                "entity": ent.label_,
                "text": ent.text,
                "color": ENTITY_COLORS.get(ent.label_, "grey"),
                "frequency": entity_frequency[entity_type][ent.text]
            }
            entities.append(entity_info)
        
        responses.append(EntityResponse(text=item.text, entities=entities))
    
    return responses

@app.post("/category_specific_extraction", response_model=EntityResponse)
async def category_specific_extraction(category: str, request: TextRequest):
    doc = nlp(request.text)
    entities = []
    
    for ent in doc.ents:
        if ent.label_.lower() == category.lower():
            entity_frequency[category][ent.text] += 1
            
            entity_info = {
                "entity": ent.label_,
                "text": ent.text,
                "color": ENTITY_COLORS.get(ent.label_, "grey"),
                "frequency": entity_frequency[category][ent.text]
            }
            entities.append(entity_info)
    
    return EntityResponse(text=request.text, entities=entities)

@app.get("/entity_trends")
async def entity_trends():
    trends = {category: dict(freqs) for category, freqs in entity_frequency.items()}
    return {"trends": trends}

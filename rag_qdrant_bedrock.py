from pprint import pprint
import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from dotenv import dotenv_values
import json
import boto3

class RAG_QDRANT_BEDROCK:
    def __init__(self):
        self.name = 'RAG_QDRANT_BEDROCK'
        self.description = 'Retrieve and Generate with Qdrant and Bedrock'
        load_dotenv()
        values_env = dotenv_values(".env")
        URL = values_env['QDRANT_URL']
        COLLECTION_NAME = values_env['QDRANT_COLLECTION']
        DIMENSION = int(values_env['DIMENSION'])
        MODEL_NAME = values_env['MODEL_NAME']
        API_KEY = values_env['QDRANT_KEY']
        self.model = SentenceTransformer(MODEL_NAME)  
        self.URL = URL
        self.COLLECTION_NAME = COLLECTION_NAME
        self.DIMENSION = DIMENSION
        self.MODEL_NAME = MODEL_NAME
        self.API_KEY = API_KEY
    
    
    def get_qdrant_client(self):
        client = qc.QdrantClient(url=self.URL,api_key=self.API_KEY)
        METRIC = qmodels.Distance.COSINE
        return client
    
   
    def retrieve(self,query:str)-> str:
        client = self.get_qdrant_client()
        model = self.model
        query_filter = None
        xq = model.encode(query,convert_to_tensor=True)
        search_result = client.search(collection_name=self.COLLECTION_NAME,
                                        query_vector=xq.tolist(),
                                        query_filter=query_filter,
                                        limit=5)
        contexts =""
        for result in search_result:
            contexts +=  result.payload['content']+"\n---\n"
        return contexts
    

    def generate_completion(self,context:str,query:str)->str:

        prompt_data = f"""Human: Answer the question based on the following context:
        {context}\n\n {query}
        Assistant:"""

        body = json.dumps({"prompt": prompt_data, 
                           "max_tokens_to_sample": 500})
        modelId = "anthropic.claude-instant-v1"  
        accept = "application/json"
        contentType = "application/json"

        bedrock_runtime_client = boto3.client('bedrock-runtime')

        response = bedrock_runtime_client.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())

        response_text = response_body.get("completion")
        
        return response_text
    
    def query(self,query:str)->str:
        context = self.retrieve(query)
        completion = self.generate_completion(context,query)
        return completion
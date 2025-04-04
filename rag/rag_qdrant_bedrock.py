from pprint import pprint
import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *
from sentence_transformers import SentenceTransformer
import boto3
import json
import os

import json
import boto3
import os

class RAG_QDRANT_BEDROCK:
    def __init__(self):
        self.name = 'RAG_QDRANT_BEDROCK'
        self.description = 'Retrieve and Generate with Qdrant and Bedrock'

        URL = os.environ.get('QDRANT_URL')
        COLLECTION_NAME = os.environ.get('QDRANT_COLLECTION')
        DIMENSION = int(os.environ.get('DIMENSION'))
        MODEL_NAME = os.environ.get('MODEL_NAME')
        API_KEY = os.environ.get('QDRANT_KEY')
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
        {context}\n\n {query}. If you do not find the answer from the context please state I do not know
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
    
    def query_nova(self,query:str)->str:
        context = self.retrieve(query)
        completion = self.generate_completion_nova(context,query)
        return completion
    
    def generate_completion_nova(self,context:str,query:str)->str:
        
        SYSTEM_PROMPT = """
        You are a virtual assistant.
        Please answer the questions based on the provided context.
        If the answer is not found in the context, please answer I do not know.
        """
        system = [{ "text": SYSTEM_PROMPT }]

        client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name="us-east-1")

        messages=[]
        messages.append({"role": "user", "content": [{"text": query}]})
        messages.append({"role": "user", "content": [{"text": context}]})

        model_response = client.converse(
            modelId="amazon.nova-lite-v1:0", 
            messages=messages,
            system = system
        )

        return((model_response["output"]["message"]["content"][0]["text"]))

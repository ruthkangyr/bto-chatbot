# imports
import os
import re
import logging
from typing import Literal
from pydantic import BaseModel, Field
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.tools import tool
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langgraph.graph import MessagesState, StateGraph, START, END

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Base directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Load Models (Upgraded to state-of-the-art open models)
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
API_KEY = os.getenv("LLM_API_KEY", "not_required")

# Recommended upgrades:
# - Orchestrator (best-in-class tool calling): qwen2.5-7b-instruct (or qwen2.5-14b-instruct)
# - Generator & Grader (deep reasoning): deepseek-r1-distill-qwen-14b (or qwen2.5-14b-instruct)
# Default unified model: qwen2.5-7b-instruct (you only need to download this ONE model in LM Studio!)
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "qwen2.5-7b-instruct")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL", "qwen2.5-7b-instruct")

logger.info(f"Connecting to LLM server at: {BASE_URL}")
logger.info(f"Orchestrator Model: {ORCHESTRATOR_MODEL} | Generator/Grader Model: {GENERATOR_MODEL}")

llm_orchestrator = ChatOpenAI(
    base_url=BASE_URL, 
    api_key=API_KEY, 
    model_name=ORCHESTRATOR_MODEL,
    temperature=0
)
llm_generator = ChatOpenAI(
    base_url=BASE_URL, 
    api_key=API_KEY, 
    model_name=GENERATOR_MODEL,
    temperature=0.3
)

# Backward-compatibility aliases
llm_llama = llm_orchestrator
llm_deepseek = llm_generator

# Load embeddings
def load_embeddings(model_name: str):
    """
    Loads HuggingFace embeddings from local directory if available,
    otherwise falls back to downloading/loading from HuggingFace Hub.
    """
    possible_local_paths = [
        os.path.join(CURRENT_DIR, "models", model_name),
        os.path.join(".", "models", model_name),
        os.path.join("models", model_name)
    ]
    
    for path in possible_local_paths:
        if os.path.exists(path):
            logger.info(f"Loading local embedding model from: {path}")
            try:
                return HuggingFaceEmbeddings(model_name=path, model_kwargs={'device': 'cpu'})
            except Exception as e:
                logger.warning(f"Failed to load embedding from {path}: {e}")
    
    logger.info(f"Loading embedding model from Hub: {model_name}")
    try:
        return HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})
    except Exception as e:
        logger.critical(f"Critical error loading embeddings: {e}")
        raise

# Ingest HDB BTO Knowledge Base & Official URLs
documents = []

# 1. Load official pages directly from Singapore HDB (Housing & Development Board) website
hdb_urls = [
    "https://www.hdb.gov.sg/buying-a-flat",
    "https://www.hdb.gov.sg/buying-a-flat/bto-sbf-and-open-booking-of-flats/finding-a-new-flat",
    "https://www.hdb.gov.sg/buying-a-flat/bto-sbf-and-open-booking-of-flats/process-for-buying-a-new-flat",
    "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/application-for-an-hdb-flat-eligibility-hfe-letter",
    "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/couples-and-families",
    "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/couples-and-families/enhanced-cpf-housing-grant",
    "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/couples-and-families/stepup-cpf-housing-grant",
    "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/singles",
    "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/singles/enhanced-cpf-housing-grant",
    "https://www.hdb.gov.sg/buying-a-flat/flat-grant-and-loan-eligibility/housing-loan/housing-loan-from-hdb"
]

header_template = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

try:
    logger.info("Scraping official HDB website pages...")
    web_loader = WebBaseLoader(web_paths=hdb_urls, header_template=header_template)
    web_docs = web_loader.load()
    documents.extend(web_docs)
    logger.info(f"Successfully scraped {len(web_docs)} official HDB page(s).")
except Exception as e:
    logger.warning(f"Could not load official HDB URLs directly: {e}.")

# 2. Also load curated local knowledge document (bto_knowledge.md)
data_dir = os.path.join(CURRENT_DIR, "data")
if os.path.exists(data_dir):
    try:
        logger.info(f"Loading knowledge base documents from: {data_dir}")
        md_loader = DirectoryLoader(data_dir, glob="**/*.md", loader_cls=TextLoader)
        documents.extend(md_loader.load())
    except Exception as e:
        logger.error(f"Error loading local data directory: {e}")

if not documents:
    logger.warning("No documents loaded. Initializing fallback BTO knowledge document.")
    from langchain_core.documents import Document
    documents = [
        Document(page_content="Singapore HDB BTO Flat Types: Standard, Plus, Prime. Maximum Enhanced CPF Housing Grant (EHG) is $120,000 for families and $60,000 for singles. Income ceiling for families is $16,000.")
    ]

# Split data into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    add_start_index=True,
)
docs = text_splitter.split_documents(documents)
logger.info(f"Knowledge base split into {len(docs)} chunks.")

# Create vector store with embeddings
embeddings = load_embeddings("sentence-transformers/all-mpnet-base-v2")
vectorstore = FAISS.from_documents(docs, embeddings)
logger.info("FAISS vectorstore successfully initialized.")

# Initialize a retriever for querying the vector store
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3, "fetch_k": 5})

# Create the Retrieval QA chain
retrieval_qa_chain = RetrievalQA.from_chain_type(
    llm=llm_llama,
    retriever=retriever,
    return_source_documents=True
)

@tool
def tool_retriever(query: str) -> str:
    """
    Retrieves official Singapore HDB BTO, housing grants, flat types, and eligibility information to answer the user query.
    Args:
        query: The search query string describing the housing question.
    """
    return retrieval_qa_chain.invoke({"query": query})['result']

# Augment the LLM with tools
tools = [tool_retriever]
tools_by_name = {tool.name: tool for tool in tools}
llm_with_tools = llm_llama.bind_tools(tools)

def node_orchestrator(state: MessagesState):
    system_msg = (
        "You are an expert Singapore HDB (Housing & Development Board) BTO & Housing Grants advisor. "
        "Your role is to help citizens understand BTO flat eligibility, flat types (Standard, Plus, Prime), "
        "CPF housing grants (such as the Enhanced CPF Housing Grant - EHG up to $120,000), income ceilings, "
        "and the HFE (HDB Flat Eligibility) letter application process. "
        "Plan how to answer the question accurately based on official Singapore HDB policies. "
        "Decide whether to use the following retrieval tool to find authoritative policies: {}.".format([i for i in tools_by_name])
    )
    response = llm_with_tools.invoke([SystemMessage(content=system_msg)] + state["messages"])
    return {"messages": [response]}

def node_tool(state: dict):
    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

def node_generate(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]

    question = messages[0].content
    answer = last_message.content

    system_msg = (
        "You are an expert Singapore HDB housing advisor. "
        "Rephrase and synthesize the retrieved information into a clear, direct, and well-structured answer to the user's question. "
        "Guidelines:\n"
        "- Ensure all eligibility conditions, income ceilings, flat classification rules (Standard, Plus, Prime), and grant numbers are accurate according to Singapore regulations.\n"
        "- Use clear bullet points and bold highlights for important criteria, amounts, and deadlines.\n"
        "- Keep the explanation friendly, concise, and easy to read for home buyers.\n\n"
        "Retrieved Information: {}\n"
        "User Question: {}".format(answer, question)
    )

    response = llm_deepseek.invoke([SystemMessage(content=system_msg)])
    return {"messages": [response]}

# Conditional edge function to route to the tool node or end based upon whether the Supervisor made a tool call
def edge_continue(state: MessagesState) -> Literal["node_tool", END]:
    """
    Decide if we should continue the loop or stop based upon whether the Orchestrator made a tool call
    """
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tool_call"
    return END

# Check whether tool result is a relevant answer to the user question
def edge_relevance(state: MessagesState) -> Literal["node_orchestrator", END]:
    """
    Determines whether the retrieved documents are relevant to the question.
    """
    class Grade(BaseModel):
        """Binary score for relevance check."""
        binary_score: str = Field(description="Relevance score 'yes' or 'no'")

    llm = llm_deepseek.with_structured_output(Grade)

    prompt = ChatPromptTemplate.from_template(
        """You are a grader assessing whether the retrieved housing document contains relevant information to answer the user's question about Singapore HDB BTO flats, grants, or eligibility. \n
        User Question: {question} \n
        Retrieved Document/Answer: {answer} \n
        If the answer contains keywords or semantic meaning relevant to the user question, grade it as 'yes'. \n
        Give a binary score 'yes' or 'no'."""
    )

    chain = prompt | llm

    messages = state["messages"]
    last_message = messages[-1]

    question = messages[0].content
    answer = last_message.content

    try:
        scored_result = chain.invoke({"question": question, "answer": answer})
        score = scored_result.binary_score.lower().strip()
    except Exception as e:
        logger.warning(f"Relevance grader exception: {e}. Defaulting to 'yes'.")
        score = "yes"
    
    if "yes" in score:
        return "relevant"
    else:
        return "retry"

# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("orchestrator", node_orchestrator)
agent_builder.add_node("tool", node_tool)
agent_builder.add_node("generate", node_generate)

# Add edges to connect nodes
agent_builder.add_edge(START, "orchestrator")
agent_builder.add_conditional_edges(
    "orchestrator",
    edge_continue,
    {
        "tool_call": "tool",
        END: END,
    },
)
agent_builder.add_conditional_edges(
    "tool",
    edge_relevance,
    {
        "retry": "orchestrator",
        "relevant": "generate",
    },
)
agent_builder.add_edge("generate", END)

# Compile the agent
agent = agent_builder.compile()

app = FastAPI(title="HDB BTO & Housing Grants AI Assistant")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Input(BaseModel):
    descr: str

@app.get("/ping")
@app.get("/api/health")
async def ping():
    return {"status": "ok", "message": "HDB BTO AI Assistant service is healthy!"}

@app.post("/invoke")
@app.post("/api/invoke")
async def invoke_agent(input: Input):
    try:
        # Clean user query
        query = input.descr.strip()
        if (query.startswith("'") and query.endswith("'")) or (query.startswith('"') and query.endswith('"')):
            query = query[1:-1].strip()

        messages = [HumanMessage(content=query)]
        result_state = agent.invoke({"messages": messages})

        # Process response message
        final_message = result_state['messages'][-1].content
        
        # Strip thinking tags if generated by reasoning models (e.g. DeepSeek R1)
        delimiter = '</think>'
        if delimiter in final_message:
            final_message = final_message.split(delimiter, 1)[1]
        elif '<think>' in final_message:
            final_message = re.sub(r'<think>.*?</think>', '', final_message, flags=re.DOTALL)
        
        response_to_user = final_message.strip()
        return {'response': response_to_user}

    except Exception as e:
        logger.error(f"Error handling /invoke: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Mount compiled React + Tailwind frontend assets if available
frontend_dist = os.path.join(CURRENT_DIR, "..", "frontend", "dist")
if not os.path.exists(frontend_dist):
    frontend_dist = os.path.join(CURRENT_DIR, "frontend", "dist")

if os.path.exists(frontend_dist) and os.path.exists(os.path.join(frontend_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

@app.get("/", response_class=HTMLResponse)
async def index():
    # 1. Prefer compiled React + Tailwind frontend
    possible_index_paths = [
        os.path.join(CURRENT_DIR, "..", "frontend", "dist", "index.html"),
        os.path.join(CURRENT_DIR, "frontend", "dist", "index.html"),
    ]
    for idx_path in possible_index_paths:
        if os.path.exists(idx_path):
            with open(idx_path, "r", encoding="utf-8") as file:
                return file.read()

    # 2. Fallback to standalone webpage.html
    html_paths = [
        os.path.join(CURRENT_DIR, "webpage.html"),
        "./webpage.html"
    ]
    for p in html_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as file:
                return file.read()
    return "<h1>HDB BTO Assistant: frontend not found</h1>"

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
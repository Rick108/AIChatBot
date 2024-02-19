import boto3
from langchain.memory import ConversationBufferMemory
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
import boto3
from langchain.memory import ConversationBufferMemory
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from langchain.agents import create_sql_agent
from langchain_experimental.sql import SQLDatabaseChain
from langchain.agents.agent_types import AgentType
from langchain.llms import GooglePalm, VertexAI
from langchain_community.embeddings import VertexAIEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool



# def bedrock_chatbot():
#     bedrock_runtime = boto3.client(
#         service_name='bedrock-runtime',
#         aws_access_key_id= 'AKIATT6RTTXJAXOJONYP',
#         aws_secret_access_key='2eCUrxW6rNtjPng8grtCzl0Zh/zPbZ2MC6r6y1wV',
#         region_name='us-east-1'
#     )
#
#     model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}  # parameters define
#     llm = Bedrock(model_id="anthropic.claude-v2", model_kwargs=model_parameter, client=bedrock_runtime)  # model define
#     memory = ConversationBufferMemory()
#     conversation = ConversationChain(
#         llm=llm, verbose=True, memory=memory
#     )
#     return conversation.predict

def bedrock_chatbot():
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        aws_access_key_id= 'AKIATT6RTTXJAXOJONYP',
        aws_secret_access_key='2eCUrxW6rNtjPng8grtCzl0Zh/zPbZ2MC6r6y1wV',
        region_name='us-east-1'
    )

    #model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}  # parameters define
    #llm = Bedrock(model_id="anthropic.claude-v2", model_kwargs=model_parameter, client=bedrock_runtime)  # model define
    llm = VertexAI(model_name='text-bison@002')
    llm.temperature = 0.1

    input_db = SQLDatabase.from_uri('sqlite:///db.db')

    few_shots = {
        "List all artists.": "SELECT * FROM artists;",
        "Find all albums for the artist 'AC/DC'.": "SELECT * FROM albums WHERE ArtistId = (SELECT ArtistId FROM artists WHERE Name = 'AC/DC');",
        "List all tracks in the 'Rock' genre.": "SELECT * FROM tracks WHERE GenreId = (SELECT GenreId FROM genres WHERE Name = 'Rock');",
        "Find the total duration of all tracks.": "SELECT SUM(Milliseconds) FROM tracks;",
        "List all customers from Canada.": "SELECT * FROM customers WHERE Country = 'Canada';",
        "How many tracks are there in the album with ID 5?": "SELECT COUNT(*) FROM tracks WHERE AlbumId = 5;",
        "Find the total number of invoices.": "SELECT COUNT(*) FROM invoices;",
        "List all tracks that are longer than 5 minutes.": "SELECT * FROM tracks WHERE Milliseconds > 300000;",
        "Who are the top 5 customers by total purchase?": "SELECT CustomerId, SUM(Total) AS TotalPurchase FROM invoices GROUP BY CustomerId ORDER BY TotalPurchase DESC LIMIT 5;",
        "Which albums are from the year 2000?": "SELECT * FROM albums WHERE strftime('%Y', ReleaseDate) = '2000';",
        "How many employees are there": 'SELECT COUNT(*) FROM "employee"',
    }
    few_shot_docs = [
        Document(page_content=question, metadata={"sql_query": few_shots[question]})
        for question in few_shots.keys()
    ]

    embeddings = VertexAIEmbeddings()

    vector_db = FAISS.from_documents(few_shot_docs, embeddings)
    retriever = vector_db.as_retriever()

    tool_description = """
    This tool will help you understand similar examples to adapt them to the user question.
    Input to this tool should be the user question.
    """

    retriever_tool = create_retriever_tool(
        retriever, name="sql_get_similar_examples", description=tool_description
    )
    custom_tool_list = [retriever_tool]

    custom_suffix = """
    I should first get the similar examples I know.
    If the examples are enough to construct the query, I can build it.
    Otherwise, I can then look at the tables in the database to see what I can query.
    Then I should query the schema of the most relevant tables
    """

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=SQLDatabaseToolkit(db=input_db, llm=llm),
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        max_iterations=20,
    )
    return agent_executor

from langchain_core.prompts import ChatPromptTemplate

POLICY_ANALYSIS_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are an expert analyst specializing in EU policy and regulation."),
    ("human", "{user_input}"),
])

SUMMARY_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are an expert analyst specializing in EU policy and regulation. Summarize the following policy document concisely."),
    ("human", "{document}"),
])

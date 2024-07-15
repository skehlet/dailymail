import boto3
import json

from langchain_aws import ChatBedrock
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.globals import set_debug
from app_settings import LLM, CONTEXT_WINDOW_SIZE, BEDROCK_REGION

set_debug(True)



def get_key_from_secrets_manager(secret_name):
    region_name = "us-west-2"
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    return json.loads(get_secret_value_response["SecretString"]).get(secret_name)

def get_openai_api_key():
    return get_key_from_secrets_manager("OPENAI_API_KEY")

def get_anthropic_api_key():
    return get_key_from_secrets_manager("ANTHROPIC_API_KEY")

def get_llm():
    """
    For Bedrock, find the right kwargs from:
    https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/providers?model=mistral.mistral-7b-instruct-v0:2
    """
    model_kwargs = {}
    if LLM.startswith("gpt"):
        return ChatOpenAI(
            model_name=LLM,
            model_kwargs=model_kwargs,
            openai_api_key=get_openai_api_key(),
        )
    elif LLM.startswith("claude"):
        return ChatAnthropic(
            model_name=LLM,
            model_kwargs=model_kwargs,
            anthropic_api_key=get_anthropic_api_key(),
        )
    elif LLM.startswith("amazon.titan"):
        model_kwargs["maxTokenCount"] = 1500
    elif LLM.startswith("meta.llama2"):
        model_kwargs["max_gen_len"] = 1500
    elif LLM.startswith("mistral"):
        model_kwargs["max_tokens"] = 1500
    return ChatBedrock(
        model_id=LLM,
        model_kwargs=model_kwargs,
        region_name=BEDROCK_REGION,
    )


def get_summarization_prompt():
    from langchain.prompts import ChatPromptTemplate

    prompt_template = """\
Please provide a concise summary of the following text, limiting it to four or five sentences.
Then, in a new paragraph, please highlight one or two interesting aspects about it in a separate sentence or two.

{text}""".strip()
    return ChatPromptTemplate.from_template(prompt_template)


def get_summarization_and_topic_relevancy_prompt(topic):
    from langchain.prompts import ChatPromptTemplate

    prompt_template = f"""\
Please provide a concise summary of the following text, limiting it to three or four sentences.

In a new paragraph, determine and state whether the text is 'RELEVANT' or 'NOT RELEVANT' to the topic at hand ('{topic.strip()}'). Please provide a one-sentence justification explaining the relevance or lack thereof.

If and only if the text is deemed 'RELEVANT', please include an additional paragraph titled 'Of interest'. In this paragraph, highlight one or two interesting aspects about the text in a separate sentence or two.

Ensure that your response is formatted as follows:

Summary: <summary here>

<RELEVANT or NOT RELEVANT>: <one-sentence justification explaining the relevance or lack thereof>

(Only if RELEVANT)
Of interest: <one or two interesting aspects about the text in a separate sentence or two>

{{text}}""".strip()
    return ChatPromptTemplate.from_template(prompt_template)


def llm_summarize_text(text, topic=None):
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser

    if topic:
        prompt = get_summarization_and_topic_relevancy_prompt(topic)
    else:
        prompt = get_summarization_prompt()
    llm = get_llm()
    output_parser = StrOutputParser()
    chain = {"text": RunnablePassthrough()} | prompt | llm | output_parser
    results = chain.invoke(text[:CONTEXT_WINDOW_SIZE]).strip()

    print("-" * 80)
    print(results)
    print("-" * 80)

    return results


if __name__ == "__main__":
    llm_summarize_text(
        """\
Volkswagen resurrected the GTX badge to denote its heated up electric cars, but
it looks set to replace it with GTI and R variants.

Thomas Schäfer, CEO of the Volkswagen brand, told Autocar, “GTX is the
performance brand of the MEB [EV architecture], but we’ll work our way back to
GTI and R in the next products going forward”.

The change will likely take a few years to sweep through the Volkswagen EV
range, with Mr Schäfer clarifying “the current products, this is what it is, but
future products will go back to a clear portfolio [of GTI and R]”.
""".strip(),
        "vw id.gti ",
    )
#     llm_summarize_text(
#         """\
# I’ve got another new Chillville Spotify list all set to go. We’ve got new music
# from Beth Gibbons, Justice, London Grammar, Charli XCX, Washed Out, Moby, Billie
# Eilish, and Badbadnotgood + classics from Saint Etienne, The Stone Roses, Air,
# 808 State, and Massive Attack + some amazing tracks from Vegyn, Sampha, Porches,
# Jessica Pratt, Blood Orange, The Roots, Alex G, Chromatics, JMSN, Kitty, Arca,
# Jungle, DJ Shadow & more. Good things!
# """.strip(),
#         "\"thievery corporation\"",
#     )

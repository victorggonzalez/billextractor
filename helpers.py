"""
This module provides helper functions for extracting data from PDF invoices 
and processing it into structured formats using LangChain and OpenAI's GPT-3.5-turbo model.

Functions:
    get_pdf_text(pdf_doc):
        Extracts text content from a PDF file.

    extracted_data(pages_data):
        Extracts structured invoice data from raw text using a language model.

    create_docs(user_pdf_list):
        Processes a list of PDF files, extracts invoice data, and returns it as a pandas DataFrame.

Dependencies:
    - os
    - re
    - ast
    - httpx
    - pandas
    - dotenv
    - langchain_openai
    - langchain.prompts
    - pypdf
"""
import os
import re
import ast
import httpx
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pypdf import PdfReader

# Load .env to get the OpenAI API key
load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo",
    http_client=httpx.Client(verify=False),
    temperature=0.0
)


def get_pdf_text(pdf_doc):
    """
    Extracts text from a PDF document.
    Args:
        pdf_doc (str): The file path to the PDF document.
    Returns:
        str: The extracted text from the PDF document.
    """

    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def extracted_data(pages_data):
    """
    Extracts structured data from the raw text of a PDF document using a language model.
    Args:
        pages_data (str): The raw text extracted from the PDF document.
    Returns:
        str: The structured data extracted from the PDF document in a dictionary format.
    """
    template = """Extract all the following values : Invoice ID, DESCRIPTION, Issue Date, UNIT PRICE, AMOUNT, Bill For, From and Terms from: {pages}
    Expected output: remove any dollar symbols {{'Invoice ID': '1001329','DESCRIPTION': 'UNIT PRICE','AMOUNT': '2','Date': '5/4/2023','AMOUNT': '1100.00', 'Bill For': 'james', 'From': 'excel company', 'Terms': 'pay this now'}}
    """
    prompt_template = PromptTemplate(
        input_variables=["pages"], template=template)
    full_response = llm(prompt_template.format(pages=pages_data))
    return full_response


def create_docs(user_pdf_list):
    """
    Processes a list of user-provided PDF files, extracts relevant data from each file,
    and compiles the extracted data into a pandas DataFrame.

    Args:
        user_pdf_list (list): A list of file paths to PDF documents to be processed.

    Returns:
        pandas.DataFrame: A DataFrame containing the extracted data with the following columns:
            - 'Invoice ID': The unique identifier for the invoice (integer).
            - 'DESCRIPTION': A description of the invoice (string).
            - 'Issue Date': The date the invoice was issued (string).
            - 'UNIT PRICE': The unit price of items in the invoice (string).
            - 'AMOUNT': The total amount of the invoice (integer).
            - 'Bill For': The entity or individual the bill is for (string).
            - 'From': The entity or individual issuing the bill (string).
            - 'Terms': The terms of the invoice (string).

    Notes:
        - The function uses helper functions `get_pdf_text` and `extracted_data` to process
          and extract data from the PDF files.
        - The extracted data is expected to be in a string format that can be converted
          into a dictionary.
        - The function removes dollar signs (`$`) and newline characters (`\n`) from the
          extracted data before processing it.
        - The `eval` function is used to convert the string representation of the data
          into a dictionary. Ensure the input data is sanitized to avoid security risks.
    """
    df = pd.DataFrame({'Invoice ID': pd.Series(dtype='int'),
                       'DESCRIPTION': pd.Series(dtype='str'),
                       'Issue Date': pd.Series(dtype='str'),
                      'UNIT PRICE': pd.Series(dtype='str'),
                       'AMOUNT': pd.Series(dtype='int'),
                       'Bill For': pd.Series(dtype='str'),
                       'From': pd.Series(dtype='str'),
                       'Terms': pd.Series(dtype='str')
                       })

    for filename in user_pdf_list:
        raw_data = get_pdf_text(filename)
        llm_extracted_data = extracted_data(raw_data)

        llm_extracted_data = re.sub(r'\$', '', llm_extracted_data.content)
        llm_extracted_data = re.sub(r'\n', '', llm_extracted_data)

        llm_extracted_data = ast.literal_eval(llm_extracted_data)
        # Append the extracted data to the dataframe
        df = pd.concat([df, pd.DataFrame([llm_extracted_data])],
                       ignore_index=True)

    df.head()
    return df

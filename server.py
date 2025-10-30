from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from kws import news_agenda_fetch, fuzzy_search

import ollama

NEWS_SYSTEM_PROMPT = {'role': 'system', 'content': """You are an AI assistant that produces news headlines from city council meeting agendas.
- Always select the most important topics for headlines
- Provide the response to the user's query only. Do not add any other phrases."""}

NEWS_PROMPT = """Please produce a news headline from this document. The headline should be a short phrase or sentence

Agenda:
{agenda}"""

SUMMARY_SYSTEM_PROMPT = {'role': 'system', 'content': """You are an AI assistant that answers questions using information from city council meeting agendas.
- Use information provided in context for your response
- Only add information relevant to the headlines in your response
- Provide the response to the user's query only. Do not add any other phrases."""}

SUMMARY_PROMPT = """Context:
{agenda}

Query:
Produce a summary of the city council meeting agenda."""

QUERY_SYSTEM_PROMPT = {'role': 'system', 'content': """You are an AI assistant that answers questions using information from city council meeting agendas.
- Use information provided in context for your response"""}

QUERY_PROMPT = """Context:
{context}

Query:
{question}"""

folder = "irvine_agendas_2025"
model = "llama3"

class Server(HTTPServer):
    def __init__(self, address, request_handler):
        super().__init__(address, request_handler)


class RequestHandler(BaseHTTPRequestHandler):
    news = news_agenda_fetch(folder)
    
    def __init__(self, request, client_address, server_class):
        self.server_class = server_class
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        print("request received. headers: ", self.headers)
        request_type = self.headers.get('type')

        self.do_news()
        
    def do_POST(self):
        print("post request received", self.headers)
        content_length = int(self.headers['Content-Length'])
        context = self.rfile.read(content_length)

        user_query = self.headers.get('query')
        # context = self.headers.get('context')
        print('querying with context', context)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        question = QUERY_PROMPT.format(context=context, question=user_query)
        
        response = ollama.chat(model, messages=[
                QUERY_SYSTEM_PROMPT,
                {
                    'role': 'user',
                    'content': question,
                },
            ]).message.content

        response_json = json.dumps({'type': 'query', 'content': response})
        
        self.wfile.write(response_json.encode())

        
    def do_news(self):
        keywords = self.headers.get('tags')

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        response = {'type': 'news', 'content' : get_news(folder, keywords)}

        response_json = json.dumps(response)
        news = json.loads(response_json)
        
        self.wfile.write(response_json.encode())

def get_agendas(folder, keywords):
    return fuzzy_search(news_agenda_fetch(folder), keywords)
        
def get_news(folder, keywords):
    agendas = get_agendas(folder, keywords)
    content = []

    for agenda in agendas:
        headline_prompt = NEWS_PROMPT.format(agenda=agenda['text'])

        headline = ollama.chat(model, messages=[
            NEWS_SYSTEM_PROMPT,
            {
                'role': 'user',
                'content': headline_prompt,
            },
        ]).message.content

        summary_prompt = SUMMARY_PROMPT.format(agenda=agenda['text'])

        summary = ollama.chat(model, messages=[
            SUMMARY_SYSTEM_PROMPT,
            {
                'role': 'user',
                'content': summary_prompt
            },
        ]).message.content

        response = {'headline': headline,
                    'original': agenda['link'],
                    'summary': summary}

        response = json.dumps(response)

        content.append(response)

    return content

def start_server(port, server_class=Server, handler_class=RequestHandler):
    server_address = ('', port)
    http_server = server_class(server_address, handler_class)
    print(f"Starting server on {''}:{port}")
    http_server.serve_forever()


def main():
    start_server(port=8000)


if __name__ == "__main__":
    main()

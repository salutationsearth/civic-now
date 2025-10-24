from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from kws import news_agenda_fetch, news_agenda_fetch

NEWS_SYSTEM_PROMPT = """You are an AI assistant that produces news headlines from city council meeting agendas.
- Always select the most important topics for headlines
- Follow the JSON format provided"""

NEWS_PROMPT = """Please produce a news headline from this document. Return your response with property "tag" and "headline".

Agenda:
{agenda}"""

SUMMARY_SYSTEM_PROMPT = """You are an AI assistant that answers questions using information from city council meeting agendas.
- Use information provided in context for your response
- Only add information relevant to the headlines in your response"""

SUMMARY_PROMPT = """Context:
{agenda}

Query:
Produce a summary of the city council meeting agenda."""

folder = "irvine_agendas_2025"

class Server(HTTPServer):
    def __init__(self, address, request_handler):
        super().__init__(address, request_handler)


class RequestHandler(BaseHTTPRequestHandler):
    news = news_agenda_fetch(folder)
    
    def __init__(self, request, client_address, server_class):
        self.server_class = server_class
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        request_type = self.headers.get('type')

        if request_type == 'query':
            self.do_query()
        elif request_type == 'news':
            self.do_news()

    def do_query(self):
        user_query = self.headers.get('query')
        context = self.headers.get('context')
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        print("{}".format(user_query))

        QUERY_SYSTEM_PROMPT = """You are an AI assistant that answers questions using information from city council meeting agendas.
        - Use information provided in context for your response"""

        QUERY_PROMPT = """Context:
        {context}

        Query:
        {question}"""

        question = QUERY_PROMPT.format(context, user_query)
        
        response = ollama.chat(model, messages=[
                QUERY_SYSTEM_PROMPT,
                {
                    'role': 'user',
                    'content': question,
                },
            ])

        response_json = json.dumps({'type': 'query', 'content': response})
        
        self.wfile.write(response_json.encode())

    def do_news(self):
        keywords = json.loads(self.headers.get('tags'))
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        response = {'type': 'news', 'content' : get_news(folder, keywords)}

        """content = [{'tag': 'Taxes', 'headline': 'Taxes raised by 500%'},
            {'tag': 'Parks', 'headline': 'All parks will be destroyed'},
            {'tag': 'Roads', 'headline': '$50 billion to build new roads that puncture tires'},
            {'tag': 'Transit', 'headline': '$10 trillion will be spent on new buses that will never arrive'}]"""
        response_json = json.dumps(response)
        news = json.loads(response_json)
        
        self.wfile.write(response_json.encode())

def get_agendas(folder, keywords):
    return fuzzy_search(news_agenda_fetch(folder), keywords)
        
def get_news(folder, keywords):
    agendas = get_agendas(folder, keywords)

    for agenda in agendas:
        headline_prompt = NEWS_PROMPT.format(agenda['text'])

        headline = ollama.chat(model, messages=[
            NEWS_SYSTEM_PROMPT,
            {
                'role': 'user',
                'content': question,
            },
        ])

        summary_prompt = SUMMARY_PROMPT.format(agenda['text'])

        summary = ollama.chat(model, messages=[
            SUMMARY_SYSTEM_PROMPT,
            {
                'role': 'user',
                'content': summary_prompt
            },
        ])

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

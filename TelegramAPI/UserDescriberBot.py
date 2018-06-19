import requests
import logging
import json

from util import try_add_info

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)


class UserDescriberBot:
    def __init__(self, token):
        self.base_url = 'https://api.telegram.org/bot'
        self.token = token

    def run(self):
        offset = None
        while True:
            updates = self.send_request('getUpdates', logging.DEBUG,
                                        offset=offset)
            for update in updates['result']:
                method_name, answer = self.handle_update(update)
                if answer:
                    logger.info(f'Should send "{method_name}"')
                    self.send_request(method_name, **answer)
                offset = update['update_id'] + 1

    @property
    def url(self):
        return f"{self.base_url}{self.token}"

    def send_request(self, method_name, log_level=logging.INFO, **kwargs):
        response = requests.post('{}/{}'.format(self.url, method_name),
                                 params=kwargs)
        server_answer = response.json()
        if server_answer['ok']:
            logger.log(log_level, f'Successfully sent "{method_name}" msg')
        else:
            logger.error(f"{server_answer['error_code']}: {server_answer['description']}")
        return server_answer

    def handle_update(self, update):
        inline_query = update.get('inline_query')
        if inline_query:
            logger.info('Got "inline_query"')
            results = self.handle_inline_query(inline_query)
            return 'answerInlineQuery', {
                'inline_query_id': str(inline_query['id']),
                'results': json.dumps(results)}

        callback_query = update.get('callback_query')
        if callback_query:
            logger.info('Got "callback_query"')
            return 'editMessageText', self.handle_callback_query(callback_query)

        # TODO: return error msg
        logger.info('Got unexpected msg type')
        return None, None

    def handle_inline_query(self, inline_query):
        inline_keyboard = self.generate_inline_keyboard(inline_query)
        query = inline_query['query']
        query = (query if query
                 else 'Press to the "Give" button to see basic information '
                      '(fullname, username, id) about you telegram account')
        content = {'message_text': query}

        inline_query_result_article = {
            'type': 'article',
            'id': inline_query['id'] + '/0',
            'title': 'Ask user for his info',
            'description': query,
            'input_message_content': content,
            'reply_markup': {'inline_keyboard': inline_keyboard}
        }
        return [inline_query_result_article]

    def handle_callback_query(self, callback_query):
        user = callback_query['from']
        text = ["Access is denied"]
        if callback_query['data'] == 'give':
            text.clear()
            try_add_info('first_name', user, 'First name: {}', text)
            try_add_info('last_name', user, 'Last name: {}', text)
            try_add_info('username', user, 'Username: @{}', text)
            try_add_info('id', user, 'Telegram ID: <b>{}</b>', text)
        return {'inline_message_id': callback_query['inline_message_id'],
                'text': '\n'.join(text), 'parse_mode': 'HTML'}

    def generate_inline_keyboard(self, inline_query):
        return [[
            {'text': 'Give', 'callback_data': 'give'},
            {'text': 'Deny', 'callback_data': 'deny'}
        ]]

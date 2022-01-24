import logging
import requests


TIHONYA_WEB_SERVER = "http://84.201.135.25:8000"


def Play():
    r = requests.post(TIHONYA_WEB_SERVER, data={'action': ['play']})
    logging.warning(r.status_code)
    logging.warning(r.reason)
      

def Stop():
    r = requests.post(TIHONYA_WEB_SERVER, data={'action': ['stop']})
    logging.warning(r.status_code)
    logging.warning(r.reason)


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    response_text = 'Что сделать с тихоней?'
    end_session = 'false'
    if 'request' in event and \
            'original_utterance' in event['request'] \
            and len(event['request']['original_utterance']) > 0:
        text = event['request']['original_utterance']
        if text[:len('выключи')] == 'выключи':
            Stop()
            response_text = 'Выключила'
            end_session = 'true'
        elif text[:len('включи')] == 'включи':
            Play()
            response_text = 'Включила'
            end_session = 'true'
        else:
            response_text = 'Не поняла'
    return {
        'version': event['version'],
        'session': event['session'],
        'response': {
            # Respond with the original request or welcome the user if this is the beginning of the dialog and the request has not yet been made.
            'text': response_text,
            # Don't finish the session after this response.
            'end_session': end_session
        },
    }
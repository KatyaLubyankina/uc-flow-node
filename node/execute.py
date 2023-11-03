from typing import List, Optional
import ujson
from json import JSONDecodeError
from uc_http_requester.requester import Request, Response


def get_request(url: str,
                method: Request.Method,
                data: Optional[dict]=None,
                headers: Optional[dict] = None,
                ) -> Request:
        request = Request(
            method=method,
            url=url        
            )
        if headers:
            request.headers = headers
        if data:
            request.json = data
        return request


def validate_response(response: Response, correct_code: int=200) -> [dict, List[dict]]:
    try:
        if response.status_code != correct_code:
            raise Exception(f'{response.status_code =} {response.content = }')
        if response.text:
            content = ujson.loads(response.text)
            if content.get('errors'):
                raise Exception(f'content errors: {content = }')
        else:
            content = dict()
    except JSONDecodeError:
        raise Exception(JSONDecodeError)
    return content

def get_attr(params, attr):
    obj = params.get(attr)
    return obj[0].get(attr) if obj else None

def params_delete_none_object(params) -> dict:
    res: dict = {}
    for key, value in params.items():
        res.update({key: value}) if value is not None else ...
    return res

def get_request_params(parameters: dict) -> dict:
    params = dict()
    if parameters:
        for param in parameters:
            params[param] = get_attr(parameters, param)
    params = params_delete_none_object(params)
    return params
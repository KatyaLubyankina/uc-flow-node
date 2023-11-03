from typing import List

from pydantic import SecretStr
from uc_flow_schemas import flow
from uc_flow_schemas.flow import (
    Property,
    NodeType as BaseNodeType, DisplayOptions, OptionValue,
)

from typing import List

from uc_flow_nodes.schemas import NodeRunContext
from uc_flow_nodes.service import NodeService
from uc_flow_nodes.views import info, execute
from uc_flow_schemas import flow
from uc_flow_schemas.flow import Property, RunState, OptionValue
from node.execute import get_request, validate_response
from uc_http_requester.requester import Request
import urllib.parse

class NodeType(flow.NodeType):
    id: str = 'bc74cb31-9d39-4b5f-ade9-e57aad736f1b'
    secret: SecretStr = '999'
    type: BaseNodeType.Type = BaseNodeType.Type.action
    displayName: str = 'Ydisk_node'
    group: List[str] = ["integration"]
    version: int = 1
    icon: str = '<svg><text x="8" y="50" font-size="50">🤖</text></svg>'
    description: str = 'action'
    inputs: List[str] = ['main']
    outputs: List[str] = ['main']
    properties: List[Property] = [
        Property(
            displayName='Operation',
            name='operation',
            type=Property.Type.OPTIONS,
            required=True,
            options=[
                OptionValue(
                    name='Upload file',
                    value = 'upload',
                    description='Загрузить файл на Яндекс Диск'
                ),
                OptionValue(
                    name='Get list of files',
                    value='get',
                    description='Получить список всех файлов'
                )
            ],
        ),
        Property(
            displayName='Authentication token',
            name='token',
            type=Property.Type.STRING,
            description='Токен доступа к Яндекс Диск',
            required=True,
        ),
        Property(
            displayName='External file url',
            name='url',
            type=Property.Type.JSON,
            description='URL внешнего ресурса, который следует загрузить',
            required=True,
            displayOptions=DisplayOptions(
                show={
                    'operation': [
                    'upload'
                    ]
                },
            ),
        ),
        Property(
            displayName='Path to file in Ydisk',
            name='path',
            type=Property.Type.STRING,
            required=True,
            description='Путь, куда будет помещён ресурс, включая название и расширение',
            displayOptions=DisplayOptions(
                show={
                    'operation': [
                    'upload'
                    ]
                },
            ),
        ),
        Property(
            displayName='Type of files sorting',
            name='sorting',
            required=True,
            type=Property.Type.OPTIONS,
            description='Выберите тип сортировки',
            options=[
                OptionValue(name='By name',value='name'),
                OptionValue(name='By upload date', value='date')
            ],
            displayOptions=DisplayOptions(
                show={
                    'operation': [
                    'get'
                    ]
                },
            ),
        ),
        Property(
            displayName='Limit output',
            name='limit',
            type=Property.Type.NUMBER,
            description='Количество выводимых вложенных ресурсов',
            displayOptions=DisplayOptions(
                show={
                    'operation': [
                    'get'
                    ]
                },
            ),
        ),
    ]


class InfoView(info.Info):
    class Response(info.Info.Response):
        node_type: NodeType


class ExecuteView(execute.Execute):
    async def post(self, json: NodeRunContext) -> NodeRunContext:
        properties = json.node.data.properties
        operation = properties['operation']
        token = properties['token']
        base_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        if operation == 'upload':
            url = properties['url'][0].get("path")
            path = properties['path']
            url = urllib.parse.quote(url, safe='')
            path = urllib.parse.quote(path, safe='')
            request_url = base_url + f'/{operation}?path={path}&url={url}' 
            headers = {'Authorization': f'OAuth {token}'}
            request = get_request(str(request_url), Request.Method.post, headers=headers)
            response = await request.execute()
            result = validate_response(response, correct_code=202)
            await json.save_result(result)
        else:
            sorting = properties['sorting']
            operation = 'files' if sorting == 'name' else 'last-uploaded'
            request_url = base_url + f'/{operation}'
            if 'limit' in properties:
                request_url += f"?limit={properties['limit']}"
            headers = {'Authorization': f'OAuth {token}'}
            request = get_request(str(request_url), Request.Method.get, headers=headers)
            response = await request.execute()
            result = validate_response(response)
            await json.save_result(result['items'])

        json.state = RunState.complete
        return json


class Service(NodeService):
    class Routes(NodeService.Routes):
        Info = InfoView
        Execute = ExecuteView

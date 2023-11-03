from typing import List

from uc_flow_nodes.schemas import NodeRunContext
from uc_flow_nodes.service import NodeService
from uc_flow_nodes.views import info, execute
from uc_flow_schemas import flow
from uc_flow_schemas.flow import Property, RunState, OptionValue
from typing import List
from pydantic import SecretStr
from uc_flow_schemas import flow
from uc_flow_schemas.flow import (
    Property,
    NodeType as BaseNodeType, OptionValue,
    DisplayOptions
)
from node.enums import Option, Operation, Parameters, Authentication
from uc_http_requester.requester import Request
from node.execute import validate_response, get_request, get_request_params

class NodeType(flow.NodeType):
    id: str = '6d3ef24c-5674-4d13-8167-0fc554fe6582'
    secret: SecretStr = '999'
    type: BaseNodeType.Type = BaseNodeType.Type.action
    displayName: str = 'AlfaCRM_node'
    group: List[str] = ["integration"]
    version: int = 1
    icon: str = '<svg><text x="8" y="50" font-size="50">🤖</text></svg>'
    description: str = 'Authentication for AlfaCRM'
    inputs: List[str] = ['main']
    outputs: List[str] = ['main']
    properties: List[Property] = [
        Property(
            displayName='Option',
            name='option',
            required=True,
            type=Property.Type.OPTIONS,
            options = [
                OptionValue(name='Authentication',value=Option.authentication),
                OptionValue(name='Customer', value=Option.customer)
            ]
        ),
        Property(
            displayName='CRM hostname',
            name=Authentication.host_name,
            default='uiscom.s20.online',
            required=True,
            type=Property.Type.STRING,
        ),
        Property(
            displayName='Email',
            name=Authentication.email,
            required=True,
            type=Property.Type.EMAIL,
            default='vehemop789@weirby.com',
            displayOptions=DisplayOptions(
                show={
                    'option': [
                    Option.authentication
                    ]
                },
            ),
        ),
        Property(
            displayName='API key(v2api)',
            name=Authentication.key,
            required=True,
            type=Property.Type.STRING,
            default='7acaf091-77b5-11ee-8640-3cecef7ebd64',
            displayOptions=DisplayOptions(
                show={
                    'option': [
                    Option.authentication
                    ]
                },
            ),
        ),
        Property(
            displayName='Token',
            name='token',
            type=Property.Type.JSON,
            required=True,
            displayOptions=DisplayOptions(
                show={
                    'option': [
                    Option.customer
                    ]
                },
            )
        ),
        Property(            
            displayName='Operation',
            name='operation',
            required=True,
            type=Property.Type.OPTIONS,
            options=[
                OptionValue(
                    name='Index',
                    value=Operation.index,   
                    description='Чтение списка с фильтрацией и  пейджинация',
                ),
                OptionValue(
                    name='Create',
                    value=Operation.create,
                    description='Создание новой модели',
                ),
                OptionValue(
                    name='Update',
                    value=Operation.update,   
                    description='Изменение свойств модели',
                ),
            ],
            displayOptions=DisplayOptions(
                show={
                    'option': [
                    Option.customer
                    ]
                },
            ),
        
        ),
        Property(
            displayName='Branch',
            name='branch',
            type=Property.Type.NUMBER,
            required=True,
            default=1,
            displayOptions=DisplayOptions(
                show={
                    'option': [
                    Option.customer
                    ]
                },
            )
        ),
        Property(
            displayName='Parameters',
            name='parameters',
            type=Property.Type.COLLECTION,
            placeholder='Add',
            default={},
            displayOptions=DisplayOptions(
                show={
                    'operation': [
                    Operation.index, Operation.create, Operation.update
                    ]
                },
            ),
            options=[
                Property(
                    displayName='Is_study',
                    name=Parameters.is_study,
                    type=Property.Type.BOOLEAN,
                    description='Состояние клиента (0-лид, 1 - клиент)',
                ),
                Property(
                    displayName='ID',
                    name=Parameters.id,
                    type=Property.Type.NUMBER,
                    default = '',
                    description='Полное имя',
                ),
                Property(
                    displayName='Name',
                    name=Parameters.name,
                    type=Property.Type.STRING,
                    description='Имя клиента',
                ),
                Property(
                    displayName='Lead_status_id',
                    name=Parameters.lead_status_id,
                    type=Property.Type.NUMBER,
                    description='Этап воронки продаж',
                ),
                Property(
                    displayName='Page',
                    name=Parameters.page,
                    type=Property.Type.NUMBER,
                    description='Этап воронки продаж',
                ),
            ]
        ),
    ]


class InfoView(info.Info):
    class Response(info.Info.Response):
        node_type: NodeType


class ExecuteView(execute.Execute):
    async def post(self, json: NodeRunContext) -> dict:
        properties = json.node.data.properties
        option = properties['option']
        host_name = properties['host_name']
        if option == Option.authentication:
            try:
                email = properties['email']
                key = properties['key']
                url = f'https://{host_name}/v2api/auth/login'
                data = {"email":email, "api_key":key}
                request = get_request(url, data, Request.Method.post)
                response = await request.execute()
                result = validate_response(response)
                await json.save_result(result)
                json.state = RunState.complete
            except Exception as e:
                self.log.warning(f'Error {e}')
                await json.save_error(str(e))
                json.state = RunState.error
            return json
        else:
            token = properties["token"].get("token")
            operation = properties["operation"]
            branch = properties["branch"]
            url = f'https://uiscom.s20.online/v2api/{branch}/customer/{operation}'
            try:
                header = {'X-ALFACRM-TOKEN': token}
                params = properties["parameters"]
                data = get_request_params(params)
                if 'is_study' in data:
                    data['is_study'] = int(data['is_study'])
                request = get_request(
                    url=url, 
                    method=Request.Method.post, 
                    data=data,
                    headers=header
                )
                response = await request.execute()
                result = validate_response(response)
                await json.save_result(result)
                json.state = RunState.complete
            except Exception as e:
                self.log.warning(f'Error {e}')
                await json.save_error(str(e))
                json.state = RunState.error
            return json

        
class Service(NodeService):
    class Routes(NodeService.Routes):
        Info = InfoView
        Execute = ExecuteView


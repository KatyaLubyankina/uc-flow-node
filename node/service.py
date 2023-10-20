import ujson
from typing import List, Tuple, Any

from uc_flow_nodes.schemas import NodeRunContext
from uc_flow_nodes.service import NodeService
from uc_flow_nodes.views import info, execute
from uc_flow_schemas import flow
from uc_flow_schemas.flow import Property, CredentialProtocol, RunState, OptionValue
from uc_http_requester.requester import Request


class NodeType(flow.NodeType):
    id: str = '3ab2fd9e-c71b-4094-9ff1-54dbb56479db'
    type: flow.NodeType.Type = flow.NodeType.Type.action
    name: str = 'Сalculator'
    displayName: str = 'Сalculator'
    icon: str = '<svg><text x="8" y="50" font-size="50">🤖</text></svg>'
    description: str = 'Calculate sum of string and number'
    properties: List[Property] = [
        Property(
            displayName='Текстовое поле',
            name='first_number',
            type=Property.Type.STRING,
            placeholder='Введите первое число',
            description='String',
            required=True,
            default='0',
        ),
        Property(
            displayName='Числовое поле',
            name='second_number',
            type=Property.Type.NUMBER,
            placeholder='Введите второе число',
            description='Number',
            required=True,
            default=0,
        ),
        Property(
            displayName='Формат ответа',
            name='answer_format',
            type=Property.Type.OPTIONS,
            description='Format',
            required=True,
            options=[OptionValue(name='Строка',value='string'),OptionValue(name='Число', value='number')],
        )
    ]


class InfoView(info.Info):
    class Response(info.Info.Response):
        node_type: NodeType


class ExecuteView(execute.Execute):
    async def post(self, json: NodeRunContext) -> NodeRunContext:
        first_number = json.node.data.properties['first_number']
        second_number = json.node.data.properties['second_number']
        answer_format = json.node.data.properties['answer_format']
        try:
            first_number = int(first_number)
        except Exception as e:
            self.log.warning(f'Error {e}')
            await json.save_error(str(e))
            json.state = RunState.error
        else:
            try:
                summ = first_number + second_number
                if answer_format == 'string':
                    summ = str(summ)
                await json.save_result({
                    "result": summ
                })
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

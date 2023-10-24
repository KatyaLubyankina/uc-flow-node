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



class NodeType(flow.NodeType):
    id: str = '5d684caf-1c2a-40b0-a8cd-97026720de97'
    secret: SecretStr = '999'
    type: BaseNodeType.Type = BaseNodeType.Type.action
    displayName: str = 'New_hollihop'
    group: List[str] = ["integration"]
    version: int = 1
    icon: str = '<svg><text x="8" y="50" font-size="50">🤖</text></svg>'
    description: str = 'action'
    inputs: List[str] = ['main']
    outputs: List[str] = ['main']
    properties: List[Property] = [
        Property(
            displayName='Первое поле',
            name='first_field',
            type=Property.Type.OPTIONS,
            noDataExpression=True,
            options=[
                OptionValue(
                    name='Значение 1',
                    value = 'first_field_first_option',
                    description='Значение 1'
                ),
                OptionValue(
                    name='Значение 2',
                    value='first_field_second_option',
                    description='Значение 2'
                )
            ],
        ),
        Property(
            displayName='Второе поле',
            name='second_field',
            type=Property.Type.OPTIONS,
            noDataExpression=True,
            options=[
                OptionValue(
                    name='Значение 1',
                    value = 'second_field_first_option',
                    description='Значение 1',
                ),
                OptionValue(
                    name='Значение 2',
                    value='second_field_second_option',
                    description='Значение 2',
                ),
            ]
        ),
        Property(
            displayName='Поле для ввода почты',
            name='email',
            type=Property.Type.EMAIL,
            noDataExpression=True,
            displayOptions=DisplayOptions(
                show={
                    'first_field': [
                       'first_field_first_option'
                    ],'second_field':['second_field_first_option']
                },
            ),
        ),
        Property(
            displayName=' Поле для ввода даты и времени',
            name='email',
            type=Property.Type.DATETIME,
            noDataExpression=True,
            displayOptions=DisplayOptions(
                show={
                    'first_field': [
                       'first_field_second_option'
                    ],'second_field':['second_field_second_option']
                },
            ),
        )
    ]


class InfoView(info.Info):
    class Response(info.Info.Response):
        node_type: NodeType


class ExecuteView(execute.Execute):
    async def post(self, json: NodeRunContext) -> NodeRunContext:
        json.state = RunState.complete
        return json


class Service(NodeService):
    class Routes(NodeService.Routes):
        Info = InfoView
        Execute = ExecuteView

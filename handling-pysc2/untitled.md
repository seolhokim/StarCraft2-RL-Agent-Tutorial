# How to select your SCV!?

## 이 장에서 배울 것

SCV를 선택하고, 상대방의 진영으로 SCV를 정찰보내고 빙빙 돌리다가 마패를 박는\(상대방이 보이는 곳에 커맨드센터를 지음으로써 굴욕을 주는\) 행위를 해볼 것입니다.

## ㅇ

시작해보겠습니다. 일단 지난번의 agent는 no\_op\(\)을 통해 아무 action없이 대기하는 agent를 만들었습니다. 이번엔 어떻게 처리해야 SCV를 선택하고, 상대방 진영에 보내고, 자원이 될 때, 커맨드 센터를 지을 수 있을까요?

이전의 step function을 살펴보겠습니다.

```python
class Agent(base_agent.BaseAgent):
    def step(self,obs):
        super(Agent,self).step(obs)
        return actions.FUNCTIONS.no_op()
```

return을 통해 action을 output으로 주면 되는 간단한 구조인 것입니다! 먼저, SCV가 존재하는지 observation에서 확인해야 합니다.

```python
from pysc2.lib import units
scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
```

이렇게 input으로 현재 화면에서 보이는 scvs들을 잡습니다. 이제, 그중 scv 아무 놈을 잡아서, 선택해줍니다.

```python
scv = scvs[0]
return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
```

3select\_point를 통해 scv의 좌표를 선택해 scv를 콕 찝은 상태입니다. 다음 step으로 넘어가게 되면 그 scv에게 명령을 내려야 하겠죠! 그리고 현재 scv를 잡는 행위는 그만해야합니다.

그렇다면 이를 다음과 같은 함수를 만들어 해결할 수 있습니다.

```python
def unit_type_is_selected(obs,unit_type):
    if len(obs.observation.single_select) > 0 and obs.observation.single_select[0].unit_type == unit_type:
        return True
    elif len(obs.observation.multi_select) > 0 and obs.observation.multi_select[0].unit_type == unit_type:        
        return True
    else:
        return False
```

위의 행동들을 합쳐 SCV를 잡은채로 가만히 있도록 하는 Agent를 만들어 보겠습니다.

```python
class Agent(base_agent.BaseAgent):
    def unit_type_is_selected(self,obs,unit_type):
        if (len(obs.observation.single_select) > 0 and obs.observation.single_select[0].unit_type == unit_type):
            return True
        elif (len(obs.observation.multi_select) > 0 and obs.observation.multi_select[0].unit_type == unit_type):
            return True
        else :
            return False
    def step(self,obs):
        super(Agent,self).step(obs)
        scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        if len(scvs) > 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
            scv = scvs[0]
            return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
        else:
            return actions.FUNCTIONS.no_op()
```

이제는 agent를 골랐을 때, 아무것도 안하는게 아닌, SCV를 선택된 적 starting point로  정찰을 보내고, 빙빙돌려야합니다. 그렇게 하기 위해선,

1. SCV 한 기를 클릭\(위에서진행\)
2. SCV를 부대지정
3. SCV를 카메라로 따라다니며 체력확인 및 컨트롤
   * 카메라로 따라다니지않고 observation의 single\_select의 healty entity를 이용할 수도 있지만, 그러면 컨트롤하기 어려우므로 카메라를 따라가도록 하겠습니다.
4. 마

아래처럼 부대지정이 1번이 되어있지않는 경우에 아래처럼 그룹지정을 합니다.

```python
CONTROL_GROUP_SET = 1
CONTROL_GROUP_RECALL = 0
SCV_GROUP_ORDER = 1
def step(self,obs):
    super(Agent,self).step(obs)
    scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        
    if len(scvs) > 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
        scv = scvs[0]
        return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
    elif self.unit_type_is_selected(obs,units.Terran.SCV) and obs.observation.control_groups[SCV_GROUP_ORDER][0] == 0:
        return actions.FUNCTIONS.select_control_group([CONTROL_GROUP_SET], [SCV_GROUP_ORDER])
    else :
        return actions.FUNCTIONS.no_op()
```

다음은, 카메라를 따라다니도록 해야하는데, 여기서 편법\(?\)을 사용할 예정입니다. FUNCTIONS에 camera move가 있긴하지만 미니맵을 쪼개서 사용하는 방식으로 사용하여, 부대지정한 유닛으로 이동하는게 까다롭습니다. 그렇기때문에 pynput 을 이용하겠습니다.

```python
import pynput
keyboard_button = pynput.keyboard.Controller()
keyboard_key = pynput.keyboard.Key
CONTROL_GROUP_SET = 1
CONTROL_GROUP_RECALL = 0
SCV_GROUP_ORDER = 1
NOT_QUEUED = [0]
MOVE_SCREEN = 331

def step(self,obs):
    super(Agent,self).step(obs)
    scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        
    if len(scvs) > 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
        scv = scvs[0]
        return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
    elif self.unit_type_is_selected(obs,units.Terran.SCV) and obs.observation.control_groups[SCV_GROUP_ORDER][0] == 0:
        return actions.FUNCTIONS.select_control_group([CONTROL_GROUP_SET], [SCV_GROUP_ORDER])
    elif len([x for x in obs.observation.feature_units if x.is_selected == 1]) == 0:
        keyboard_button.press(str(SCV_GROUP_ORDER))
        keyboard_button.release(str(SCV_GROUP_ORDER))
        keyboard_button.press(str(SCV_GROUP_ORDER))
        keyboard_button.release(str(SCV_GROUP_ORDER))
        return actions.FUNCTIONS.select_control_group([CONTROL_GROUP_RECALL], [SCV_GROUP_ORDER])
    elif len([x for x in obs.observation.feature_units if ((x.is_selected == 1) and x.order_length == 0)]) == 1 :
        x,y = random.randint(0,64),random.randint(0,64)
        return actions.FunctionCall(MOVE_SCREEN,[NOT_QUEUED,[x,y]])
    else:
        return actions.FUNCTIONS.no_op()
```

부대지정한 유닛이 맵에서 사라지면 SCV부대지정 키를 눌러 그곳으로 camera를 이동하고, SCV가 아무것도안하면 random으로 이동시켜 뺑뺑 돌게 만드는 스크립트입니다.

\#프로토스로 바꿔 짓게하기. 유닛생산, 공




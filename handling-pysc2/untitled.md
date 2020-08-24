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

이제는 agent를 골랐을 때, 아무것도 안하는게 아닌, SCV를 선택된 적 starting point로  정찰을 보내고, 빙빙돌려야합니다. 그렇게 하기 위해선 SCV가 공격받고 있는지, 가만히 있는지들을 확인하는 function을 만들어야 합니다.

```python

```


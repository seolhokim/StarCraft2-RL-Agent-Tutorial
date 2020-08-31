# CollectMineralShards



```python
from pysc2.env import sc2_env
from pysc2.lib import features 
from pysc2.agents import base_agent
from pysc2.lib import actions

from absl import app

MAPNAME = 'CollectMineralShards'
APM = 300
APM = int(APM / 18.75)
UNLIMIT = 0
VISUALIZE = True
REALTIME = True

SCREEN_SIZE = 84
MINIMAP_SIZE = 64

players = [sc2_env.Agent(sc2_env.Race.terran)]

interface = features.AgentInterfaceFormat(\
                feature_dimensions = features.Dimensions(\
                screen = SCREEN_SIZE, minimap = MINIMAP_SIZE), use_feature_units = True)

class Agent(base_agent.BaseAgent):
    def step(self,obs):
        super(Agent,self).step(obs)
        return actions.FUNCTIONS.no_op()
    


def main(args):
    agent = Agent()
    try:
        with sc2_env.SC2Env(map_name = MAPNAME, players = players,\
                agent_interface_format = interface,\
                step_mul = APM, game_steps_per_episode = UNLIMIT,\
                visualize = VISUALIZE, realtime = REALTIME) as env:
            agent.setup(env.observation_spec(), env.action_spec())

            timestep = env.reset()
            agent.reset()

            while True:
                step_actions = [agent.step(timestep[0])]
                if timestep[0].last():
                    break
                timestep = env.step(step_actions)
    except KeyboardInterrupt:
        pass
app.run(main)
```

다음의 스크립트를 통해 CollectMineralShards 맵을 실행시켜볼 수 있습니다. 이제 RL을 할 수 있도록 이 환경에서 필요한 정보를 빼오도록 하겠습니다.

![](../.gitbook/assets/.png%20%281%29.png)



MDP 정의, 환경 정의는 같은 문제의 같은 목적이라도 충분히 다르게 정의할 수 있고, 그 정의에 따라 문제가 얼마나 복잡해지느냐는 물론이고, time series의 길이와 action dimension사이의 trade off의 균형, 가장 중요한 성능까지 좌지우지될 수 있습니다.

저는 이번 튜토리얼을 통해, AlphaStar논문에서의 Agent Network에서 적용된 AutoRegressive model을 모방해, 화면 RGB와 action은 두 개의 마린과 mineralshards들을 entity로 모두 넣을 생각입니다.\(화면 RGB만으로 충분할것으로 보이지만\)

기본적으로 제가 생각한  필요 정보들은 다음과 같습니다.

* 화면의 정보
  * observation.screen\_features.player\_relative 를 사용할 예정입니다.\(마린은 1, Mineralshards 은 3\)
* 화면의 마린과 Mineralshards\(dynamic length\)
  * x좌표
    * observation.feature\_units.x
  * y좌표
    * observation.feature\_units.y
  * alliance
    * observation.feature\_units.alliance
      * \(Mineralshards는 3, marine은 1\)

그렇다면, state를 구하는 function을 만들어보겠습니다. 

```python
def get_state(obs):
    screen = obs.observation.feature_screen.player_relative
    units_info = obs.observation.feature_units
    units_info = [[unit.x,unit.y,unit.alliance] for unit in units_info]
    return np.expand_dims(np.array(screen),0), np.expand_dims(np.array(units_info),0)
```

그렇다면 action은 어떻게 정의할 수 있을까요? 저는 위에서 말했듯이 AutoRegressive 모델을 만들기 위해 다음과 같이 정의하여보았습니다.

* Action
  * unit selection
    * mineralshards
    * marine
  * target unit selection
    * marine
    * mineralshards
    * none
  * target point
    * x,y

이들을 통합해 만든 스크립트입니다. Brain은 현재 마구잡이 random으로 action하도록 만들어진 상태입니다.

```python
MOVE_SCREEN = 331
NOT_QUEUED = [0]

SELF = features.PlayerRelative.SELF
NEUTRAL = features.PlayerRelative.NEUTRAL

MINERALSHARDS = 1680
MARINES = 48


class Brain:
    def __init__(self):
        self.action_lst = []
    def network(self, obs,screen_info,units_info): 
        ## network를 잠시 function형태로 쓰겠습니다.
        units_info = obs.observation.feature_units
        units_info = [[unit.alliance,unit.x,unit.y] for unit in units_info]
        #모든 selection풀기 지금 deselect 기능 못쓰므로 잘못눌렀다면 no_op()해주어야함
        unit = random.choice(units_info)
        if unit[0] == NEUTRAL:
            return actions.FUNCTIONS.no_op(), actions.FUNCTIONS.no_op(), actions.FUNCTIONS.no_op()
        else:
            action_1 = actions.FUNCTIONS.select_point("select",(unit[1],unit[2]))
            if random.randint(0,1) == 0: # target unit이 잡혔을 시
                target_unit = random.choice(units_info)
                action_2 = actions.FunctionCall(MOVE_SCREEN,[NOT_QUEUED,[target_unit[1],target_unit[2]]])
                action_3 = actions.FUNCTIONS.no_op()
            else: # target unit없을시
                action_2 = actions.FUNCTIONS.no_op
                x = random.randint(0,SCREEN_SIZE - 1)
                y = random.randint(0,SCREEN_SIZE - 1)
                action_3 = actions.FunctionCall(MOVE_SCREEN,[NOT_QUEUED,[x,y]])
            return action_1,action_2,action_3
    def action(self,obs,screen_info,units_info):
        if len(self.action_lst) == 0:
            [self.action_lst.append(x) for x in self.network(obs,screen_info,units_info)]
        return self.action_lst.pop(0) 
            
class Agent(base_agent.BaseAgent):
    def __init__(self):
        super(Agent, self).__init__()
        self.brain = Brain()
    def get_state(self,obs):
        screen = obs.observation.feature_screen.player_relative
        units_info = obs.observation.feature_units
        units_info = [[unit.x,unit.y,unit.alliance] for unit in units_info]
        return np.expand_dims(np.array(screen),0), np.expand_dims(np.array(units_info),0) # .transpose(1, 0)
    def step(self, obs):
        super(Agent, self).step(obs)
        screen_info, units_info = self.get_state(obs)
        action = self.brain.action(obs,screen_info,units_info)
        #self.brain.train()
        return action

```

다음은 reward를 받아와보겠습니다. 위의 스크립트로 본다면 98번째 줄에서 reward를 확인해야합니다. 

```python
    try:
        with sc2_env.SC2Env(map_name=MAPNAME, players=players, \
                            agent_interface_format=interface, \
                            step_mul=APM, game_steps_per_episode=UNLIMIT, \
                            visualize=VISUALIZE, realtime=REALTIME) as env:
            agent.setup(env.observation_spec(), env.action_spec())

            timestep = env.reset()
            agent.reset()
            reward = 0
            while True:
                step_actions = [agent.step(timestep[0])]
                if timestep[0].last():
                    break
                timestep = env.step(step_actions)
                reward -= timestep[0].observation.player.minerals 
    except KeyboardInterrupt:
        pass
```

그렇다면 전체 코드는 다음과 같습니다.

```python
from pysc2.env import sc2_env
from pysc2.lib import features
from pysc2.agents import base_agent
import numpy as np
from pysc2.lib import actions

from absl import app

import random

MAPNAME = 'CollectMineralShards'
APM = 300
APM = int(APM / 18.75)
UNLIMIT = 0
VISUALIZE = True
REALTIME = True

SCREEN_SIZE = 84
MINIMAP_SIZE = 64


MOVE_SCREEN = 331
NOT_QUEUED = [0]

SELF = features.PlayerRelative.SELF
NEUTRAL = features.PlayerRelative.NEUTRAL

MINERALSHARDS = 1680
MARINES = 48

players = [sc2_env.Agent(sc2_env.Race.terran)]

interface = features.AgentInterfaceFormat( \
    feature_dimensions=features.Dimensions( \
        screen=SCREEN_SIZE, minimap=MINIMAP_SIZE), use_feature_units=True)

class Brain:
    def __init__(self):
        self.action_lst = []
    def network(self, obs,screen_info,units_info): 
        ## network를 잠시 function형태로 쓰겠습니다.
        units_info = obs.observation.feature_units
        units_info = [[unit.alliance,unit.x,unit.y] for unit in units_info]
        #모든 selection풀기 지금 deselect 기능 못쓰므로 잘못눌렀다면 no_op()해주어야함
        unit = random.choice(units_info)
        if random.randint(0,1) == 0:
            #아무것도 안하는 행위(이미 마린들이 목표를향해 움직인다면 아무것도안하고 있어도 괜찮음)
            return actions.FUNCTIONS.no_op(), actions.FUNCTIONS.no_op(), actions.FUNCTIONS.no_op()
        elif unit[0] == NEUTRAL:
            return actions.FUNCTIONS.no_op(), actions.FUNCTIONS.no_op(), actions.FUNCTIONS.no_op()
        else:
            action_1 = actions.FUNCTIONS.select_point("select",(unit[1],unit[2]))
            if random.randint(0,1) == 0: # target unit이 잡혔을 시
                target_unit = random.choice(units_info)
                action_2 = actions.FunctionCall(MOVE_SCREEN,[NOT_QUEUED,[target_unit[1],target_unit[2]]])
                action_3 = actions.FUNCTIONS.no_op()
            else: # target unit없을시
                action_2 = actions.FUNCTIONS.no_op()
                x = random.randint(0,SCREEN_SIZE - 1)
                y = random.randint(0,SCREEN_SIZE - 1)
                action_3 = actions.FunctionCall(MOVE_SCREEN,[NOT_QUEUED,[x,y]])
            return action_1,action_2,action_3
    def action(self,obs,screen_info,units_info):
        if len(self.action_lst) == 0:
            [self.action_lst.append(x) for x in self.network(obs,screen_info,units_info)]
        return self.action_lst.pop(0) 
            
class Agent(base_agent.BaseAgent):
    def __init__(self):
        super(Agent, self).__init__()
        self.brain = Brain()
    def get_state(self,obs):
        screen = obs.observation.feature_screen.player_relative
        units_info = obs.observation.feature_units
        units_info = [[unit.x,unit.y,unit.alliance] for unit in units_info]
        return np.expand_dims(np.array(screen),0), np.expand_dims(np.array(units_info),0) # .transpose(1, 0)
    def step(self, obs):
        super(Agent, self).step(obs)
        screen_info, units_info = self.get_state(obs)
        action = self.brain.action(obs,screen_info,units_info)
        #self.brain.train()
        return action


def main(args):
    agent = Agent()
    try:
        with sc2_env.SC2Env(map_name=MAPNAME, players=players, \
                            agent_interface_format=interface, \
                            step_mul=APM, game_steps_per_episode=UNLIMIT, \
                            visualize=VISUALIZE, realtime=REALTIME) as env:
            agent.setup(env.observation_spec(), env.action_spec())

            timestep = env.reset()
            agent.reset()
            while True:
                reward = - timestep[0].observation.player.minerals 
                step_actions = [agent.step(timestep[0])]
                if timestep[0].last():
                    break
                timestep = env.step(step_actions)
                reward += timestep[0].observation.player.minerals 
    except KeyboardInterrupt:
        pass


app.run(main)
```

완료입니다!

이후 테스트하고싶은 것은 CollectMineralsAndGas 맵에서 MultiObjective로 미네랄과 가스의 weights 를 주어 weights에 따라 미네랄과 가스의 채취량을 조절할 수 있는가에 대한 테스트를 개인적으로 진행할 예정입니다.

번외로, units로 screen에 안보이더라도 확인가능한지




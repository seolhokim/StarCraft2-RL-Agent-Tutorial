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

* 화면의 RGB
  * observation.screen\_features.player\_relative 를 사용할 예정입니다.
* 화면의 마린과 Mineralshards\(dynamic length\)
  * x좌표
    * observation.feature\_units.x
  * y좌표
    * observation.feature\_units.y
  * alliance
    * observation.feature\_units.alliance
      * \(Mineralshards는 3, marine은 1\)

이후 테스트하고싶은 것은 CollectMineralsAndGas 맵에서 MultiObjective로 미네랄과 가스의 weights 를 주어 weights에 따라 미네랄과 가스의 채취량을 조절할 수 있는가에 대한 테스트를 개인적으로 진행할 예정입니다.

번외로, units로 screen에 안보이더라도 확인가능한지




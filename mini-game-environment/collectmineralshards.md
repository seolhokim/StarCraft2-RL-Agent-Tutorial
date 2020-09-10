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

하지만 가장중요한 것은 확실한 것을 조금씩 쌓아가는 것입니다. minimal한 환경에서 minimal한 agent network를 통해 점점 발전시켜나가는 것이 디버깅과 개선점에대한 실험을 쉽고 빠르게 진행할 수 있도록 합니다. 그렇기에, 먼저 다음과 같이 environment를 정의해보겠습니다.

* Environment Definition :
  * State : 2 \* 32\(screen\_size\) \* 32\(screen\_size\)
    * feature\_screen : 2 \* 32 \* 32
      * is\_selected : 1 \* 32 \* 32
      * player\_relative : 1 \* 32 \* 32
  * Action : 
    * screen : 1 \* 32 \* 32
  * Reward : 
    * mineral : 0 ~ n \(미네랄 한개당 1\)
* Agent Definition :
  * Algorithm : 
    * PPO + GAE
  * Network :
    * CNN + MLP

Agent Network를 CNN-based로 하게되면 단점이 있습니다. 이전의 Starcraft II 연구들에 의하면, action에대한 일관성이 부족하다고 합니다. 예를들면, 일꾼 유닛이 건물을 지으러 가다가도 다시 미네랄을 캐러가는등 이전의 정보에 대한 전달 능력이 부족합니다. 그렇기 때문에, 저희는 마린이 움직이는동안은 마린에게 아무 action도 주지 않을 것입니다. 또 그러면 생기는 문제가, 길게움직이면 시간이 많이가고, 적게움직이면 시간이 짧게갑니다. 하지만 그에대한 패널티가 부족하죠. 물론 제한시간 2분동안 더 많은 reward를 받기 위해, 어느정도 학습이 될 것으로 예상하고, 환경을 다뤄보도록하겠습니다.

state는 다음과 같은 함수를 통해 state를 받아올 수 있습니다.

```python
def get_state(obs):
    player_relative = np.expand_dims(np.array(obs.observation.feature_screen.player_relative),0)
    selected = np.expand_dims(np.array(obs.observation.feature_screen.selected),0)
    state = np.concatenate([player_relative, selected],0)
    return state
```

기본적인 유닛 움직임과 reward는 Basic about pysc2의 How to select your SCV!? 섹션에서 보고 오시면 random agent정도는 쉽게 만들 수 있을 것입니다. 이상입니다.






# Build Marine! and Attack!

## 이 장에서 배울것

자원이 되면, supply depot을 짓고,  Barrack을 지은 뒤, 공격가는 것을 목표로 하겠습니다.



## Let's Start!

우선 이전의 스크립트에서 필요한 부분을 가져오겠습니다.

```python
from pysc2.env import sc2_env
from pysc2.agents import base_agent
from pysc2.lib import actions,units,features 

from absl import app

MAPNAME = 'Simple64'
APM = 300
APM = int(APM / 18.75)
UNLIMIT = 0
VISUALIZE = True
REALTIME = True

NOT_QUEUED = [0]

players = [sc2_env.Agent(sc2_env.Race.terran),\
           sc2_env.Bot(sc2_env.Race.zerg,\
           sc2_env.Difficulty.very_easy)]

interface = features.AgentInterfaceFormat(\
                feature_dimensions = features.Dimensions(\
                screen = 84, minimap = 64), use_feature_units = True)
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
        if obs.first(): 
            player_y, player_x = (obs.observation.feature_minimap.player_relative == PLAYER_SELF).nonzero()
            xmean = player_x.mean()
            ymean = player_y.mean()
            if xmean <= 31 and ymean <= 31:
                self.scout_coordinates = (40, 40)
            else:
                self.scout_coordinates = (20, 20)
        scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        if len(scvs) > 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
            #유닛 셀렉
            scv = scvs[0]
            return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
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

g사실, 서플라이 디팟 하나 짓게하는데도 은근히 생각해볼 것들이 많습니다.

1. 서플라이디팟을 짓는다.
   * 인구수 체크!
   * 지금 서플라이디팟을 짓고있는지 확인!
   * 자원 확인!\(지금 가능한행동인지확인!\)
   * SCV를 선택해 적당한 위치에 짓기 시작해야합니다.

이렇게 rule-based가 어렵습니다 ㅜㅜ. 한꺼번에 적용한 스크립트를 보고 빠르게 넘어가도록하죠!

```python
class Agent(base_agent.BaseAgent):
    def unit_type_is_selected(self,obs,unit_type):
        if (len(obs.observation.single_select) > 0 and obs.observation.single_select[0].unit_type == unit_type):
            return True
        elif (len(obs.observation.multi_select) > 0 and obs.observation.multi_select[0].unit_type == unit_type):
            return True
        else :
            return False
    def can_do(self,obs,action_id):
        return action_id in obs.observation.available_actions
    def selected_units_idle_check(self,obs):
        if len([x for x in obs.observation.feature_units if ((x.is_selected == 1) and x.order_length == 0)])> 0:
            return False
        else:
            return True
        
    def food_check(self,obs):
        food_enough = obs.observation.player.food_cap - obs.observation.player.food_used
        if food_enough > 4:
            return False
        else:
            return True
    def build_building_now(self,obs,building_id):
        units = [unit.build_progress for unit in obs.observation.feature_units if \
                 (unit.unit_type == building_id)]
        if len(units) > 0 :
            return True
        else:
            return False
        
    def step(self,obs):
        super(Agent,self).step(obs)
        if obs.first(): 
            player_y, player_x = (obs.observation.feature_minimap.player_relative == PLAYER_SELF).nonzero()
            xmean = player_x.mean()
            ymean = player_y.mean()
            if xmean <= 31 and ymean <= 31:
                self.scout_coordinates = (40, 40)
            else:
                self.scout_coordinates = (20, 20)
        scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        if len(scvs) > 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
            #유닛 셀렉
            scv = scvs[0]
            return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
        elif self.can_do(obs,BUILD_SUPPLYDEPOT) and \
        self.selected_units_idle_check(obs) and self.food_check(obs) and \
        not self.build_building_now(obs,units.Terran.SupplyDepot):
            x,y = random.randint(0,64),random.randint(0,64)
            return actions.FunctionCall(BUILD_SUPPLYDEPOT,[NOT_QUEUED,[x,y]])
        
        return actions.FUNCTIONS.no_op()
```

만약 서플라이디팟을 짓다가 화면밖으로 벗어나면 이러한 rule-based Agent는 짓고있는 서플라이 디팟에 대한 정보는 얻을 수가 없어 인구수가 막히지 않았더라도 새 서플라이디팟을 지을 가능성이 있습니다!\(자원이 많다면 APM이 300이니까 잠시 다른화면으로 한눈을팔았다간 몇초만에 모든 일꾼이 서플라이 디팟을 짓는 것을 볼 수 있습니다.\)

이번엔 배럭을 지어보겠습니다!




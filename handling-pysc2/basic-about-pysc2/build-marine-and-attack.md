# Build Marine! and Attack!

## 이 장에서 배울것

자원이 되면, supply depot을 짓고,  Barrack을 지은 뒤, 공격가는 것을 목표로 하겠습니다.



## Let's Start!

사실, 서플라이 디팟 하나 짓게하는데도 은근히 생각해볼 것들이 많습니다.

1. 서플라이디팟을 짓는다.
   * 인구수 체크!
   * 지금 서플라이디팟을 짓고있는지 확인!
   * SCV가 노는지 체크!
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
        selected_units = [x for x in obs.observation.feature_units if x.is_selected == 1]
        if len(selected_units) == 0 :
            print("not selected!")
            return True
        else:
            selected_unit = [x.order_length for x in selected_units]
            if sum(selected_unit) > 0:
                return False
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
            if xmean <= MINIMAP_SIZE/2 and ymean <= MINIMAP_SIZE/2:
                self.scout_coordinates = (40, 40)
            else:
                self.scout_coordinates = (20, 20)
        scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        if len(scvs) > 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
            #유닛 셀렉
            scv = scvs[0]
            return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
        elif self.can_do(obs,BUILD_SUPPLYDEPOT) and \
        self.food_check(obs) and \
        (not self.build_building_now(obs,units.Terran.SupplyDepot))\
        and  [x.order_id_0 for x in obs.observation.feature_units if x.is_selected == 1][0] == \
        HARVEST_GATHER_SCV_UNIT: 
            x,y = random.randint(0,SCREEN_SIZE),random.randint(0,SCREEN_SIZE)
            return actions.FunctionCall(BUILD_SUPPLYDEPOT,[NOT_QUEUED,[x,y]])
        elif self.can_do(obs,BUILD_BARRACKS) and \
            (not self.build_building_now(obs,units.Terran.Barracks)) and \
            (len([x for x in obs.observation.feature_units if x.unit_type == units.Terran.Barracks]) == 0) and \
            self.selected_units_idle_check(obs):
            
            x,y = random.randint(0,SCREEN_SIZE),random.randint(0,SCREEN_SIZE)
            return actions.FunctionCall(BUILD_BARRACKS,[NOT_QUEUED,[x,y]])
        return actions.FUNCTIONS.no_op()
```

만약 서플라이디팟을 짓다가 화면밖으로 벗어나면 이러한 rule-based Agent는 짓고있는 서플라이 디팟에 대한 정보는 얻을 수가 없어 인구수가 막히지 않았더라도 새 서플라이디팟을 지을 가능성이 있습니다!\(자원이 많다면 APM이 300이니까 잠시 다른화면으로 한눈을팔았다간 몇초만에 모든 일꾼이 서플라이 디팟을 짓는 것을 볼 수 있습니다.\)

이번엔 배럭을 지어보겠습니다!

```python
if (len([x for x in obs.observation.feature_units if x.unit_type == units.Terran.Barracks]) == 1)\
and self.can_do(obs,TRAIN_MARINE_QUICK):
    return actions.FunctionCall(TRAIN_MARINE_QUICK,[NOT_QUEUED])
```

이 스크립트도 스크린에 배럭이 보이지않으면 와장창 지어지는 문제가 있습니다..ㅎㅎ

이제 마린을 계속해서 뽑아보겠습니다.

```python
    def step(self,obs):
        super(Agent,self).step(obs)
        if obs.first(): 
            player_y, player_x = (obs.observation.feature_minimap.player_relative == PLAYER_SELF).nonzero()
            xmean = player_x.mean()
            ymean = player_y.mean()
            if xmean <= MINIMAP_SIZE/2 and ymean <= MINIMAP_SIZE/2:
                self.scout_coordinates = (40, 40)
            else:
                self.scout_coordinates = (20, 20)
        scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        brracks = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.Barracks]
        if len(scvs) > 0 and len(brracks) == 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
            #유닛 셀렉
            scv = scvs[0]
            return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
        elif self.can_do(obs,BUILD_SUPPLYDEPOT) and \
        self.food_check(obs) and \
        (not self.build_building_now(obs,units.Terran.SupplyDepot))\
        and  [x.order_id_0 for x in obs.observation.feature_units if x.is_selected == 1][0] == \
        HARVEST_GATHER_SCV_UNIT: 
            x,y = random.randint(0,SCREEN_SIZE),random.randint(0,SCREEN_SIZE)
            return actions.FunctionCall(BUILD_SUPPLYDEPOT,[NOT_QUEUED,[x,y]])
        elif self.can_do(obs,BUILD_BARRACKS) and \
            (not self.build_building_now(obs,units.Terran.Barracks)) and \
            (len([x for x in obs.observation.feature_units if x.unit_type == units.Terran.Barracks]) == 0) and \
            self.selected_units_idle_check(obs):
            
            x,y = random.randint(0,SCREEN_SIZE),random.randint(0,SCREEN_SIZE)
            return actions.FunctionCall(BUILD_BARRACKS,[NOT_QUEUED,[x,y]])
        elif len(brracks) == 1 and not self.unit_type_is_selected(obs,units.Terran.Barracks): 
            brrack = brracks[0]
            return actions.FUNCTIONS.select_point("select",(brrack.x,brrack.y))
        elif self.unit_type_is_selected(obs,units.Terran.Barracks) and self.can_do(obs,TRAIN_MARINE_QUICK): 
            return actions.FunctionCall(TRAIN_MARINE_QUICK,[NOT_QUEUED])
        return actions.FUNCTIONS.no_op()
```

처음에 SCV를선택할때, 배럭도 지켜봐야하기때문에 전체의 코드를 넣어 바뀐점을 찾도록 하였습니다. 그러면 이렇게되면 계속 마린을 뽑을 수 있게 되었습니다. 마지막으로 적의 기지로 공격을 보내겠습니다.

```python
from pysc2.env import sc2_env
from pysc2.agents import base_agent
from pysc2.lib import actions,units,features 
import random
from absl import app

MAPNAME = 'Simple64'
APM = 300
APM = int(APM / 18.75)
UNLIMIT = 0
VISUALIZE = True
REALTIME = True
PLAYER_SELF =features.PlayerRelative.SELF

SCREEN_SIZE = 84
MINIMAP_SIZE = 64

MOVE_MINIMAP = 332
BUILD_SUPPLYDEPOT = 91
BUILD_BARRACKS = 42
TRAIN_MARINE_QUICK = 477
HARVEST_GATHER_SCV_UNIT = 359
TRAIN_MARINE_QUICK = 477
NOT_QUEUED = [0]

players = [sc2_env.Agent(sc2_env.Race.terran),\
           sc2_env.Bot(sc2_env.Race.zerg,\
           sc2_env.Difficulty.very_easy)]

interface = features.AgentInterfaceFormat(\
                feature_dimensions = features.Dimensions(\
                screen = SCREEN_SIZE, minimap = MINIMAP_SIZE), use_feature_units = True)
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
        selected_units = [x for x in obs.observation.feature_units if x.is_selected == 1]
        if len(selected_units) == 0 :
            print("not selected!")
            return True
        else:
            selected_unit = [x.order_length for x in selected_units]
            if sum(selected_unit) > 0:
                return False
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
            if xmean <= MINIMAP_SIZE/2 and ymean <= MINIMAP_SIZE/2:
                self.attack_coordinates = (40, 40)
            else:
                self.attack_coordinates = (20, 20)
        scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        brracks = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.Barracks]
        if len(scvs) > 0 and len(brracks) == 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
            #유닛 셀렉
            scv = scvs[0]
            return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
        elif self.can_do(obs,BUILD_SUPPLYDEPOT) and \
        self.food_check(obs) and \
        (not self.build_building_now(obs,units.Terran.SupplyDepot))\
        and  [x.order_id_0 for x in obs.observation.feature_units if x.is_selected == 1][0] == \
        HARVEST_GATHER_SCV_UNIT: 
            x,y = random.randint(0,SCREEN_SIZE),random.randint(0,SCREEN_SIZE)
            return actions.FunctionCall(BUILD_SUPPLYDEPOT,[NOT_QUEUED,[x,y]])
        elif self.can_do(obs,BUILD_BARRACKS) and \
            (not self.build_building_now(obs,units.Terran.Barracks)) and \
            (len([x for x in obs.observation.feature_units if x.unit_type == units.Terran.Barracks]) == 0) and \
            self.selected_units_idle_check(obs):
            x,y = random.randint(0,SCREEN_SIZE),random.randint(0,SCREEN_SIZE)
            return actions.FunctionCall(BUILD_BARRACKS,[NOT_QUEUED,[x,y]])
        elif len(brracks) == 1 and not self.unit_type_is_selected(obs,units.Terran.Barracks) and not self.unit_type_is_selected(obs,units.Terran.Marine): 
            brrack = brracks[0]
            return actions.FUNCTIONS.select_point("select",(brrack.x,brrack.y))
        elif self.unit_type_is_selected(obs,units.Terran.Barracks) and self.can_do(obs,TRAIN_MARINE_QUICK): 
            return actions.FunctionCall(TRAIN_MARINE_QUICK,[NOT_QUEUED])
        elif len([x for x in obs.observation.feature_units if x.unit_type == units.Terran.Marine]) > 3\
         and not self.unit_type_is_selected(obs,units.Terran.Marine):
            marines = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.Marine]
            return actions.FUNCTIONS.select_point("select_all_type",(marines[0].x,marines[0].y))
        elif self.unit_type_is_selected(obs,units.Terran.Marine) and self.selected_units_idle_check(obs):
            x,y = self.attack_coordinates
            return actions.FunctionCall(MOVE_MINIMAP,[NOT_QUEUED,[x,y]])
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

마린 네기가 뚜벅뚜벅걸어가 적을 공격하는 보실수 있을 것입니다!


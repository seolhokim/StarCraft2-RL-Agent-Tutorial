from pysc2.env import sc2_env
from pysc2.agents import base_agent
from pysc2.lib import actions,units,features 

from absl import app

import random
import pynput ###
keyboard_button = pynput.keyboard.Controller()
keyboard_key = pynput.keyboard.Key


MAPNAME = 'Simple64'
APM = 300
APM = int(APM / 18.75)
UNLIMIT = 0
VISUALIZE = True
REALTIME = True
CONTROL_GROUP_SET = 1
CONTROL_GROUP_RECALL = 0
SCV_GROUP_ORDER = 1
NOT_QUEUED = [0]
MOVE_SCREEN = 331
MOVE_MINIMAP = 332
SCREEN_ENEMY = 4
PLAYER_SELF =features.PlayerRelative.SELF

SCREEN_SIZE = 84
MINIMAP_SIZE = 64

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
    def step(self,obs):
        super(Agent,self).step(obs)
        if obs.first(): 
            player_y, player_x = (obs.observation.feature_minimap.player_relative == PLAYER_SELF).nonzero()
            xmean = player_x.mean()
            ymean = player_y.mean()
            if xmean <= MINIMAP_SIZE / 2 and ymean <= MINIMAP_SIZE / 2:
                self.scout_coordinates = (40, 40)
            else:
                self.scout_coordinates = (20, 20)
                
        scvs = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.SCV]
        if len(scvs) > 0 and not self.unit_type_is_selected(obs,units.Terran.SCV):
            #유닛 셀렉
            scv = scvs[0]
            return actions.FUNCTIONS.select_point("select",(scv.x,scv.y))
            '''
            선택된 유닛 카메라로 보기
            카메라 move
            actions.FUNCTIONS.move_camera([10,10])
            '''
        elif self.unit_type_is_selected(obs,units.Terran.SCV) and obs.observation.control_groups[SCV_GROUP_ORDER][0] == 0:
            #control unit잡기
            return actions.FUNCTIONS.select_control_group([CONTROL_GROUP_SET], [SCV_GROUP_ORDER])
        elif len([x for x in obs.observation.feature_units if x.is_selected == 1]) == 0:
            #화면밖벗어났을때
            keyboard_button.press(str(SCV_GROUP_ORDER))
            keyboard_button.release(str(SCV_GROUP_ORDER))
            keyboard_button.press(str(SCV_GROUP_ORDER))
            keyboard_button.release(str(SCV_GROUP_ORDER))
            return actions.FUNCTIONS.select_control_group([CONTROL_GROUP_RECALL], [SCV_GROUP_ORDER])
        #elif  in obs.observation.available_actions: #build supplydot
            #
        elif len([x for x in obs.observation.feature_units if ((x.is_selected == 1) and x.order_length == 0)]) == 1 and\
              SCREEN_ENEMY in [x.alliance for x in obs.observation.feature_units] :
            #화면내 random 이동
            x,y = random.randint(0,SCREEN_SIZE),random.randint(0,SCREEN_SIZE)
            return actions.FunctionCall(MOVE_SCREEN,[NOT_QUEUED,[x,y]])
        elif len([x for x in obs.observation.feature_units if (x.is_selected == 1)]) == 1 \
            and SCREEN_ENEMY not in [x.alliance for x in obs.observation.feature_units]:
            #적 위치로 정찰
            x,y = self.scout_coordinates
            return actions.FunctionCall(MOVE_MINIMAP,[NOT_QUEUED,[x,y]])
        else:
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
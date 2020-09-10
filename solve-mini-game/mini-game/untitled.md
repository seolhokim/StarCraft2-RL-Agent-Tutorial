# CollectMineralShards

이번장에서는 CollectMineralShards를 해결해보겠습니다. 위의 Mini-Game environment 섹션에서 CollectMineralShards를 풀기위한 정의를 그대로 가져와보겠습니다.

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

j

j

j

j

j

j

j




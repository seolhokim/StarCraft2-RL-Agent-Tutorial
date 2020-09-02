# CollectMineralShards

이번장에서는 CollectMineralShards를 해결해보겠습니다.

RL Application의 중점은 환경과 model을 최소화 한뒤, 점점 부피를 키워가는게 중요하다고 생각합니다. 그렇기에 처음 Definition은 다음과 같이 잡겠습니다.

* Input : 
  * feature map\(player\_relative\)
* Action:
  * Action Type -&gt; feature map select\(Marine Selection\) -&gt; feature map select\(MineralShards Select\)
    * Action Type
      * no\_op or move

이어지는 다음 환경에서는

* Input :
  * feature map\(player\_relative\), marine's coordinates
* Action

  * Action Type -&gt; Marine Selection -&gt; feature map select
    * Action Type
      * no\_op or move


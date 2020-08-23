# Startcraft2-RL-Agent-Tutorial

## 목적

이 gitbook은 windows 10 환경에서 python을 가지고, Starcraft2의 RL Agent를 만드는 튜토리얼을 진행하기 위해 만드는 튜토리얼 gitbook입니다.

## 수준

* 이론을 자세히 설명하기보다 실용적인 부분에 대해 많이 설명할 계획입니다.
* python을 통해 일반적인 Application을 다루는 강좌만큼의 프로그래밍 언어 능력이면 충분합니다.
* pytorch의 training 구조를 이해하고 있다면 충분합니다.
* RL의 기본적인 update식 들을 이해한다면 충분합니다.
* 최대한 자세히 설명하려고 노력하겠지만,\(사실 귀찮 하고 넘기는 성격이라\) 설명에 능하지 않은 만큼 issue를 남겨주시면 열심히 답해드리도록 노력하겠습니다.

## Requirements

* windows 10 기준으로 쓰여졌습니다.
* python &gt;= 3.6.0
* pytorch &gt;= 1.0.0
* [starcraft2](https://starcraft2.com/ko-kr/) &lt;- 무료입니다.
  * 기본 path를 바꾸지 않는것을 추천드립니다.
  * 기본 path는 `C:\Program Files (x86)\StarCraft II`  입니다.
  * 실험에 사용할 Map을 받아야 하는데, [링크](https://github.com/deepmind/pysc2) 에서 Get the maps에서 **mini games** 를 누르시면 알집이 받아집니다.
  * 다음으로 [링](https://github.com/Blizzard/s2client-proto#downloads)에서 Map Packs를 보시면 
    * Ladder 2019 Season 3 
    * Melee
  * 를 받으신뒤 압축을 푸시면 됩니다. 비밀번호는**iagreetotheeula** 입니다.
  * 이렇게 받은 Map들을 Maps 폴더에 넣습니다.
  * 폴더 째로 넣으셔도 됩니다.
  * `C:\Program Files (x86)\StarCraft II\Maps`
    * `\Ladder2019Season3`
    * `\Melee`
    * `\mini_games`
  * 가 존재하게 됩니다.
* [pysc2](https://github.com/deepmind/pysc2)
  * starcraft2를 python환경을 제어하기 위한 python component입니다.  
  * repository를 보면 설치방법이 나와있습니다.
  * `pip install pysc2` 를 command에 입력해 설치를 합니다.
  *  이제 모두 install이 잘 됐는지 확인하기 위해 

    ```text
    python -m pysc2.bin.agent --map Simple64
    ```

  * 를 입력해 실행되는지 확인합니다. 




WAR OF SQUARES
==============
파이썬 모듈 PyGame을 이용하여 만든 슈팅게임입니다. 플레이어와 적들이 모두 정사각형이라 위와 같이 단순한 제목을 붙였습니다.  
처음에는 게임 개발의 기초를 연습하기 위해 간단하게 시작하였으나, 어쩌다 보니 완성단계까지 오게 되었습니다.  
총 다섯 개의 레벨로 구성되어 있으며, 현재는 더 이상의 레벨을 추가하는 대신 코드 리팩토링에 집중하고 있습니다.

# 실행 방법
아직 별도의 실행 파일이 없어 python version 3.8 이상이 필요합니다.  
모든 파일을 다운받아 압축을 해제하고 생성된 폴더 안에 pygame 모듈을 설치해야 합니다.  
그 상태에서 war_of_squares.py 파일을 실행합니다.

# 조작법
1. 플레이어 이동: WASD
2. 플레이어는 기본 무기와 에너지 캐논, 총 두 가지의 무기를 사용합니다.
3. 기본 무기는 별다른 조작 없이 자동으로 무한 발사되며, 대신 마우스 커서로 발사 방향만 조절합니다.
4. 에너지 캐논은 마우스 버튼 조작을 통해 사용할 수 있습니다. 사용 시 MP를 소모합니다.
5. 마우스 버튼을 누르고 있으면 에너지 캐논을 충전합니다. 충전 도중에는 기본 무기를 사용하지 않습니다.
6. 마우스 버튼을 놓으면 마우스 커서 방향으로 에너지 캐논을 발사합니다.
7. 충전 가능한 최대치에 도달하거나 충전 도중 MP를 모두 소진하면 마우스 버튼을 놓지 않아도 자동 발사됩니다.

# 게임 구성 및 플레이 과정
## 메인 메뉴
게임 실행 시 처음 나오는 화면입니다. 제목과 시작 버튼으로만 이루어져 있습니다.

![mainmenu_scene](https://user-images.githubusercontent.com/80591422/158949281-9f22572e-c927-47f0-914d-b27b8cee313d.png)

## 레벨 선택
메인 메뉴 화면에서 시작 버튼을 누르면 나오는 화면입니다.  
레벨을 자유롭게 선택하여 플레이할 수 있습니다.  
현재는 Level 5 까지만 만들어져 있으며, Level 6 은 새로 개발 중인 적 패턴을 테스트하기 위한 임시 레벨입니다.

![level_select_scene](https://user-images.githubusercontent.com/80591422/158950587-6083627f-1213-413b-8e59-77c41a8d6fff.png)

## 업그레이드 창
각 레벨을 시작할 때 스탯 포인트를 소모하여 플레이어의 능력치를 업그레이드할 수 있습니다.  
업그레이드 가능한 플레이어의 능력치는 다음의 다섯 가지가 있습니다.  

* 최대 HP
* 최대 MP
* 적 파편을 끌어모으는 범위 (자석)
* 기본 무기 능력치: 단위 시간 당 화력이 증가하며, 무기 발사 패턴 또한 향상됩니다.
* 에너지 캐논 능력치: 에너지 캐논의 화력과 공격 범위가 증가합니다. 그러나 동시에 소모 MP량 또한 증가합니다.

다음 스크린샷은 Level 1 을 시작할 때의 업그레이드 창입니다.  
이때에는 스탯이 0이라 업그레이드가 불가합니다. 이후 레벨 클리어 1회당 4씩 누적됩니다.  
레벨 하나를 클리어할 때마다 능력치 하나당 최대 두 단계까지 업그레이드할 수 있습니다.  
우측 하단의 버튼을 클릭하여 업그레이드 상태를 플레이어에 적용하고 게임을 시작합니다. 현재까지의 업그레이드 상태는 이후 변경할 수 없습니다.

![upgrade_window](https://user-images.githubusercontent.com/80591422/158952227-3960f414-71cc-485a-935c-4de4e97ebda5.png)

레벨 선택 창에서 1 이상의 다른 레벨로 게임을 시작하면 이전 레벨들을 클리어한 것으로 간주하여 이에 상응하는 스탯 포인트가 주어집니다.

## 플레이 과정
1. 각 레벨은 네 개의 Phase로 구성되어 있으며, 네 개 중 마지막은 보스 챌린지입니다.
2. 보스 챌린지까지 완료하면 20초 간의 브레이크타임과 업그레이드 창을 거쳐 다음 레벨로 진행합니다.
3. 보스 챌린지 이전 세 개의 Phase에서는 일반 적들이 등장하며, Phase를 거듭할수록 더 강한 적이 등장합니다.
4. 적들을 처치하면 폭발과 함께 파편으로 흩어지며, 이 파편을 수집하여 점수를 획득합니다.
5. 점수 획득량은 해당 Phase 진행률과 비례합니다. 즉, 정해진 양의 점수를 획득해야 다음 Phase로 진행할 수 있습니다.
6. 적을 처치하면 낮은 확률로 아이템을 드랍합니다. 이 아이템은 HP 또는 MP를 회복시킵니다.
7. 아이템을 획득하지 않더라도 HP와 MP는 느린 속도로 자동 회복됩니다.
8. 플레이 도중 'P'키를 눌러 일시 정지할 수 있습니다. 'P'키를 다시 누르면 게임을 이어 나가며, 일시 정지 창에서 나가기 버튼을 눌러 게임을 중단할 수도 있습니다.
9. 게임을 중단하거나 플레이 도중 HP가 0이 되면 자동으로 결과 창으로 이동합니다.

## 결과 창
게임 오버 시 나오는 화면입니다.  
레벨 별 플레이 시간과 점수 획득량, 그리고 시간 대비 평균 점수 획득률을 보여줍니다.  
재시작 버튼을 클릭하면 메인 메뉴 화면으로 이동합니다.

![gameover_scene](https://user-images.githubusercontent.com/80591422/158957644-3fbe5e49-a649-4de7-8692-f7bf67627b67.png)

# 플레이 스크린샷
## Level 1

![level1](https://user-images.githubusercontent.com/80591422/158965257-8829acc6-3cb9-4524-ad72-8702bcf23eeb.png)

## Level 2

![level2](https://user-images.githubusercontent.com/80591422/158965772-538e3530-82a5-4395-94e0-a8e18234e0da.png)

## Level 3

![level3](https://user-images.githubusercontent.com/80591422/158966008-a92cb84e-a593-4bd5-a99d-9628200b79cc.png)

## Level 3 Boss Challenge

![level3boss](https://user-images.githubusercontent.com/80591422/158966532-9aea3175-14d8-4eed-8639-f5c1ab188e36.png)

## Level 4

![level4](https://user-images.githubusercontent.com/80591422/158972049-bafe8551-f118-48f0-b3f3-2e86de3ac2b1.png)

## Level 4 Boss Challenge

![level4boss](https://user-images.githubusercontent.com/80591422/158972330-c0711061-9e13-4c01-8e4e-1c7725d4f4fb.png)

## Level 5

![level5](https://user-images.githubusercontent.com/80591422/158972683-e682cb46-ad73-46f1-8efc-e9589dc9625d.png)

## Level 5 Boss Challenge

![level5boss](https://user-images.githubusercontent.com/80591422/158975350-04e4cf45-56a8-4460-87ef-8481bf543827.png)

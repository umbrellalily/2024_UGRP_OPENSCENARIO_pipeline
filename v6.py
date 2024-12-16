#여러대의 실험 차량
#각 차량은 여러번의 차선변경, 여러번의 속도변경 가능
#offset을 추가하여 차선 사이로 주행 가능
#lane_change_values를 추가해 차선 변경에 걸리는 시간 조정 가능
#speed_change_values를 추가해 속도 변경에 걸리는 시간 조정 가능

# ego_car_pos_lane = input("ego_car_pos_lane: ")  # lane num
# ego_car_pos_far = input("ego_car_pos_far: ")  # meter
# ego_car_speed = input("ego_car_speed: ")
# tar_car_pos_lane = input("tar_car_pos_lane: ")  # lane num
# tar_car_pos_far = input("tar_car_pos_far: ")  # meter
# tar_car_speed = input("tar_car_speed: ")
#
# # 교통사고 시작
# lane_change_time = input("lane_change_time: ")
# speed_change_time = input("speed_change_time: ")
# changed_speed = input("changed_speed: ")

num_of_car = 4

# ego_car_pos_lane = -2
# ego_car_pos_far = 50
# ego_car_speed = 100
#
# tar_car_pos_lane = -2
# tar_car_pos_far = 60
# tar_car_speed = 100

car_pos_lanes = [[-2, 0], [-3, 0], [-4, 0], [-5, 0]]
car_pos_fars = [50, 60, 70, 80]
car_speeds = [100, 110, 120, 130]

# lane_change_time = 100
# speed_change_time = 5
# changed_speed = 60

# 교통사고 시작

num_of_lane_change = [2, 3, 1, 1]
num_of_speed_change = [1, 1, 2, 3]

lane_change_times = [[1, 2], [2, 2.5, 3], [3], [4]]
speed_change_times = [[3], [4], [5, 5.5], [6, 6.5, 7]]

lane_change_values = [[0.5, 0.5], [3, 3, 3], [3], [3]]
changed_lanes = [[[-3, 0], [-2, 0]], [[-4, 0], [-6, 0], [-3, 0]], [[-5, 0]], [[-6, 0]]]
speed_change_values = [[3], [4], [5, 0.5], [6, 0.5, 0.5]]
changed_speeds = [[20], [30], [40, 100], [50, 100, 0]]

import subprocess


# 파일 이름 입력 받기
file_name = input("Enter the desired filename (without extension): ")

#ParameterDeclaration 생성하기
pd_content = ""
for i in range(num_of_car):
    pd_content = pd_content + f"""      <ParameterDeclaration name="RedCar{i + 1}" parameterType="string" value="car_red"/>\n"""

#entities_content 생성하기
entities_content = ""
for i in range(num_of_car):
    entities_content = entities_content + f"""      <ScenarioObject name="Vehicle{i + 1}">
         <CatalogReference catalogName="VehicleCatalog" entryName="$RedCar{i + 1}"/>
      </ScenarioObject>\n"""

#actions_content 생성하기
actions_content = ""
for i in range(num_of_car):
    actions_content = actions_content + f"""            <Private entityRef="Vehicle{i + 1}">
               <PrivateAction>
                  <TeleportAction>
                     <Position>
                        <LanePosition roadId="0" laneId="{car_pos_lanes[i][0]}" offset="{car_pos_lanes[i][1]}" s="{car_pos_fars[i]}"/>
                     </Position>
                  </TeleportAction>
               </PrivateAction>
               <PrivateAction>
                  <LongitudinalAction>
                     <SpeedAction>
                        <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="0.0"/>
                        <SpeedActionTarget>
                           <AbsoluteTargetSpeed value="{float(car_speeds[i]) / 3.6}"/>
                        </SpeedActionTarget>
                     </SpeedAction>
                  </LongitudinalAction>
               </PrivateAction>
            </Private>\n"""

#cut_in_act 생성
cut_in_act = ""
distinct_num = 1
for i in range(num_of_car):
    for j in range(num_of_lane_change[i]):

        cut_in_act = cut_in_act + f"""            <ManeuverGroup maximumExecutionCount="1" name="CutInSequence{distinct_num}">
                   <Actors selectTriggeringEntities="false">
                      <EntityRef entityRef="Vehicle{i+1}"/>
                   </Actors>
                   <Maneuver name="CutInManeuver{distinct_num}">
                      <Event name="CutInEvent{distinct_num}" priority="overwrite">
                         <Action name="CutInAction"> <!-- EntityRef에서 정의된 Entities가 수행할 행동을 정의한다. -->
                            <PrivateAction>
                               <LateralAction>
                                  <LaneChangeAction> <!-- 횡방향 행동 중 차선 변경 행동을 의미힌다. -->
                                     <LaneChangeActionDynamics dynamicsShape="sinusoidal" value="{lane_change_values[i][j]}" dynamicsDimension="time"/><!-- ***이 값은 얼마나 앞에서 차선을 변경하는 가이다 -->
                                     <LaneChangeTarget>
                                        <AbsoluteTargetLane value="{changed_lanes[i][j][0]}" offset="{changed_lanes[i][j][1]}"/>
                                     </LaneChangeTarget>
                                  </LaneChangeAction>
                               </LateralAction>
                            </PrivateAction>
                         </Action>
    
                         <StartTrigger>
                            <ConditionGroup>
                               <Condition name="CutInActStart{distinct_num}" delay="0" conditionEdge="rising">
                                  <ByValueCondition>
                                     <SimulationTimeCondition value="{lane_change_times[i][j]}" rule="greaterThan"/>
                                  </ByValueCondition>
                               </Condition>
                            </ConditionGroup>
                         </StartTrigger>
                      </Event>
                   </Maneuver>
                </ManeuverGroup>\n"""
        distinct_num += 1

    for j in range(num_of_speed_change[i]):
        cut_in_act = cut_in_act + f"""            <ManeuverGroup maximumExecutionCount="1" name="Speedup{distinct_num}">
              <Actors selectTriggeringEntities="false">
                 <EntityRef entityRef="Vehicle{i+1}"/>
              </Actors>
              <Maneuver name="SpeedupManeuver{distinct_num}">
                 <Event name="SpeedupEvent{distinct_num}" priority="overwrite">
                    <Action name="SpeedupAction"> <!-- EntityRef에서 정의된 Entities가 수행할 행동을 정의한다. -->
                       <PrivateAction>
                          <LongitudinalAction>
                             <SpeedAction>
                                <SpeedActionDynamics dynamicsShape="linear" dynamicsDimension="time" value="{speed_change_values[i][j]}"/>
                                <SpeedActionTarget>
                                   <AbsoluteTargetSpeed value="{float(changed_speeds[i][j]) / 3.6}"/>
                                </SpeedActionTarget>
                             </SpeedAction>
                          </LongitudinalAction>
                       </PrivateAction>
                    </Action>

                    <StartTrigger>
                       <ConditionGroup>
                          <Condition name="CutInActStart" delay="0" conditionEdge="rising">
                             <ByValueCondition>
                                <SimulationTimeCondition value="{speed_change_times[i][j]}" rule="greaterThan"/>
                             </ByValueCondition>
                          </Condition>
                       </ConditionGroup>
                    </StartTrigger>
                 </Event>
              </Maneuver>
           </ManeuverGroup>\n"""
        distinct_num += 1

# XML 파일 내용 생성
xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<OpenSCENARIO>
   <FileHeader revMajor="1" revMinor="1" date="2024-12-16T22:00:00" description="cut-in" author="Saehoon Jung"/> <!-- 파일 정보 -->

   <ParameterDeclarations> <!-- 변수를 선언하여 중복되는 값을 쉽게 사용할 수 있다. $name으로 사용한다. -->
{pd_content}
   </ParameterDeclarations>

   <CatalogLocations> <!-- 미리 정의해둔 카탈로그를 불러와 사용할 수 있다. -->
      <VehicleCatalog>
         <Directory path="../xosc/Catalogs/Vehicles"/>
      </VehicleCatalog>
   </CatalogLocations>

   <RoadNetwork> <!-- OpenDRIVE 형식으로 저장된 도로 정보를 불러온다. -->
      <LogicFile filepath="../xodr/e6mini.xodr"/>
      <SceneGraphFile filepath="../models/e6mini.osgb"/>
   </RoadNetwork>

   <Entities> <!-- 시나리오에 등장하는 객체를 정의한다. -->
{entities_content}
   </Entities>

   <Storyboard>
      <Init> <!-- Entities의 초기 상태를 정의한다. -->
         <Actions>
{actions_content}            
         </Actions>
      </Init>


      <Story name="CutInStory"> <!-- Entities가 수행할 행동을 정의한다. -->
         <Act name="CutInAct">
{cut_in_act}
            <StartTrigger> <!-- Act가 시작되는 시기를 정의한다. -->
               <ConditionGroup>
                  <Condition name="CutInActStart" delay="0" conditionEdge="none">
                     <ByValueCondition>
                        <SimulationTimeCondition value="0" rule="greaterThan"/> <!-- Act는 시뮬레이션이 시작되고 0초 이상에서 시작된다. -->
                     </ByValueCondition>
                  </Condition>
               </ConditionGroup>
            </StartTrigger>
         </Act>
      </Story>

      <StopTrigger>
         <ConditionGroup>
            <Condition name="ActStopCondition" delay="0" conditionEdge="rising">
                  <ByEntityCondition>
                     <TriggeringEntities triggeringEntitiesRule="any">
                        <EntityRef entityRef="Vehicle1"/>
                     </TriggeringEntities>
                     <EntityCondition>
                        <RelativeDistanceCondition entityRef="Vehicle2" value="3" freespace="false" coordinateSystem="entity" relativeDistanceType="euclidianDistance" rule="lessThan"/>
                     </EntityCondition>
                  </ByEntityCondition>
            </Condition>
         </ConditionGroup>
      </StopTrigger>
   </Storyboard>
</OpenSCENARIO>"""

# 파일 생성 경로
file_path = f"esmini-demo/resources/xosc/{file_name}.xosc"

# 파일 생성
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(xml_content)

print(f"File has been created at {file_path}")

# run_gen_code.bat 생성 및 실행 경로
bat_file_path = f"esmini-demo/run/esmini/run_{file_name}.bat"


# 배치 파일 내용 생성
bat_content = f""""../../bin/esmini" --window 60 60 1024 576 --osc ../../resources/xosc/{file_name}.xosc --camera_mode flex-orbit --road_features on --disable_controllers"""

# 배치 파일 생성
with open(bat_file_path, 'w') as bat_file:
    bat_file.write(bat_content)
import os
# 현재 파일의 디렉토리를 기준으로 절대 경로 생성
script_dir = os.path.dirname(os.path.abspath(__file__))
bat_file_path = os.path.join(script_dir, f"esmini-demo/run/esmini/run_{file_name}.bat")
cwd_path = os.path.join(script_dir, "esmini-demo/run/esmini")

# 배치 파일 실행
subprocess.run(["cmd", "/c", bat_file_path], cwd=cwd_path)
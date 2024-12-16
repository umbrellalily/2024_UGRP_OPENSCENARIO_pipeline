#2대의 실험차량
#1대의 움직임이 없는 초기상태에 고정된 차량
#1대의 1번의 차선변경, 1번의 속도변경이 가능한 차량

# ego_car_pos_line = input("ego_car_pos_line: ")  # line num
# ego_car_pos_far = input("ego_car_pos_far: ")  # meter
# ego_car_speed = input("ego_car_speed: ")
# tar_car_pos_line = input("tar_car_pos_line: ")  # line num
# tar_car_pos_far = input("tar_car_pos_far: ")  # meter
# tar_car_speed = input("tar_car_speed: ")
#
# # 교통사고 시작
# line_change_time = input("line_change_time: ")
# speed_change_time = input("speed_change_time: ")
# changed_speed = input("changed_speed: ")

ego_car_pos_line = -2
ego_car_pos_far = 50
ego_car_speed = 100
tar_car_pos_line = -2
tar_car_pos_far = 60
tar_car_speed = 100

# 교통사고 시작
line_change_time = 100
speed_change_time = 5
changed_speed = 60

import os
import subprocess


# 파일 이름 입력 받기
file_name = input("Enter the desired filename (without extension): ")

# XML 파일 내용 생성
xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<OpenSCENARIO>
   <FileHeader revMajor="1" revMinor="1" date="2024-12-16T22:00:00" description="cut-in" author="Saehoon Jung"/> <!-- 파일 정보 -->

   <ParameterDeclarations> <!-- 변수를 선언하여 중복되는 값을 쉽게 사용할 수 있다. $name으로 사용한다. -->
      <ParameterDeclaration name="WhiteCar" parameterType="string" value="car_white"/>
      <ParameterDeclaration name="RedCar" parameterType="string" value="car_red"/>
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
      <ScenarioObject name="Ego">
        <CatalogReference catalogName="VehicleCatalog" entryName="$WhiteCar"/>
      </ScenarioObject>
      <ScenarioObject name="TargetVehicle">
         <CatalogReference catalogName="VehicleCatalog" entryName="$RedCar"/>
      </ScenarioObject>
   </Entities>

   <Storyboard>
      <Init> <!-- Entities의 초기 상태를 정의한다. -->
         <Actions>
            <Private entityRef="Ego">
               <PrivateAction>
                  <TeleportAction>
                     <Position> <!-- 위치를 정의한다. -->
                        <LanePosition roadId="0" laneId="{ego_car_pos_line}" offset="0" s="{ego_car_pos_far}"/> <!-- 위에서 불러온 도로 정보를 기반으로 정의한다. -->
                     </Position>
                  </TeleportAction>
               </PrivateAction>
               <PrivateAction>
                  <LongitudinalAction>
                     <SpeedAction> <!-- 속도를 정의한다. -->
                        <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="0.0"/> 
                        <SpeedActionTarget>
                           <AbsoluteTargetSpeed value="{float(ego_car_speed) / 3.6}"/>
                        </SpeedActionTarget>
                     </SpeedAction>
                  </LongitudinalAction>
               </PrivateAction>
            </Private>
            <Private entityRef="TargetVehicle">
               <PrivateAction>
                  <TeleportAction>
                     <Position>
                        <LanePosition roadId="0" laneId="{tar_car_pos_line}" offset="0" s="{tar_car_pos_far}"/>
                     </Position>
                  </TeleportAction>
               </PrivateAction>
               <PrivateAction>
                  <LongitudinalAction>
                     <SpeedAction>
                        <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="0.0"/>
                        <SpeedActionTarget>
                           <AbsoluteTargetSpeed value="{float(tar_car_speed) / 3.6}"/>
                        </SpeedActionTarget>
                     </SpeedAction>
                  </LongitudinalAction>
               </PrivateAction>
            </Private>
         </Actions>
      </Init>


      <Story name="CutInStory"> <!-- Entities가 수행할 행동을 정의한다. -->
         <Act name="CutInAct">

            <ManeuverGroup maximumExecutionCount="1" name="CutInSequence">
               <Actors selectTriggeringEntities="false">
                  <EntityRef entityRef="TargetVehicle"/>
               </Actors>
               <Maneuver name="CutInManeuver">
                  <Event name="CutInEvent" priority="overwrite">
                     <Action name="CutInAction"> <!-- EntityRef에서 정의된 Entities가 수행할 행동을 정의한다. -->
                        <PrivateAction>
                           <LateralAction>
                              <LaneChangeAction> <!-- 횡방향 행동 중 차선 변경 행동을 의미힌다. -->
                                 <LaneChangeActionDynamics dynamicsShape="sinusoidal" value="3" dynamicsDimension="time"/><!-- ***이 값은 얼마나 앞에서 차선을 변경하는 가이다 -->
                                 <LaneChangeTarget>
                                    <RelativeTargetLane entityRef="Ego" value="0"/> <!-- Ego 차량과 동일한 차선을 의미한다. 0이 ego와 같은 차선-->
                                 </LaneChangeTarget>
                              </LaneChangeAction>
                           </LateralAction>
                        </PrivateAction>
                     </Action>

                     <StartTrigger>
                        <ConditionGroup>
                           <Condition name="CutInActStart" delay="0" conditionEdge="rising">
                              <ByValueCondition>
                                 <SimulationTimeCondition value="{line_change_time}" rule="greaterThan"/>
                              </ByValueCondition>
                           </Condition>
                        </ConditionGroup>
                     </StartTrigger>
                  </Event>
               </Maneuver>
            </ManeuverGroup>

            <ManeuverGroup maximumExecutionCount="1" name="Speedup">
                  <Actors selectTriggeringEntities="false">
                     <EntityRef entityRef="TargetVehicle"/>
                  </Actors>
                  <Maneuver name="SpeedupManeuver">
                     <Event name="SpeedupEvent" priority="overwrite">
                        <Action name="SpeedupAction"> <!-- EntityRef에서 정의된 Entities가 수행할 행동을 정의한다. -->
                           <PrivateAction>
                              <LongitudinalAction>
                                 <SpeedAction>
                                    <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="0.0"/>
                                    <SpeedActionTarget>
                                       <AbsoluteTargetSpeed value="{float(changed_speed) / 3.6}"/>
                                    </SpeedActionTarget>
                                 </SpeedAction>
                              </LongitudinalAction>
                           </PrivateAction>
                        </Action>

                        <StartTrigger>
                           <ConditionGroup>
                              <Condition name="CutInActStart" delay="0" conditionEdge="rising">
                                 <ByValueCondition>
                                    <SimulationTimeCondition value="{speed_change_time}" rule="greaterThan"/>
                                 </ByValueCondition>
                              </Condition>
                           </ConditionGroup>
                        </StartTrigger>
                     </Event>
                  </Maneuver>
               </ManeuverGroup>


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
                        <EntityRef entityRef="Ego"/>
                     </TriggeringEntities>
                     <EntityCondition>
                        <RelativeDistanceCondition entityRef="TargetVehicle" value="3" freespace="false" coordinateSystem="entity" relativeDistanceType="euclidianDistance" rule="lessThan"/>
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
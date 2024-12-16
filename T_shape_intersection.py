# 여러대의 실험 차량
# 각 차량은 여러번의 차선변경, 여러번의 속도변경 가능
# offset을 추가하여 차선 사이로 주행 가능
# line_change_values를 추가해 차선 변경에 걸리는 시간 조정 가능
# speed_change_values를 추가해 속도 변경에 걸리는 시간 조정 가능
# bb_3_220817_vehicle_209_32197에 대한 manual한 예제
# 모든 차량에 대해 서로 가까워졌을 때 stop_trigger을 적용

#json파일을 읽어서 autotext에 사용가능한 형식으로 가공한다.
def lane_action(lane):
    if lane == 1:
        return "HostStraightRoute"
    elif lane == 0:
        return "TargetStraightRoute"
    else: return "TargetRightTurnRoute"

import json

frame_per_sec = 15

with open('content/T-shape_intersection/depth.json', 'r') as pos_file:
    pos_dic = json.load(pos_file)
with open('content/T-shape_intersection/rotation_speed.json', 'r') as cut_in_file:
    cut_in_dic = json.load(cut_in_file)
with open('content/T-shape_intersection/lane.json', 'r') as lane_file:
    lane_dic = json.load(lane_file)
with open('content/T-shape_intersection/accident_frame.json') as accident_file:
    accident_frame  = json.load(accident_file)["accident_frame"]

straight_cars = list(pos_dic.keys())
cut_in_cars = list(cut_in_dic.keys())
num_of_cut_in_car = len(cut_in_cars)
num_of_straight_car = len(straight_cars)
frame_num = len(pos_dic[straight_cars[1]])
accident_point = 0
for car in straight_cars:
    if lane_dic[car] == 1:
        accident_point = pos_dic[car][accident_frame]

car_pos_lanes = []
car_pos_fars = []
car_speeds = []
cut_in_car_speeds = []
cut_in_car_pos_fars = []
#초기값 추출
for i in range(num_of_straight_car):
    car = straight_cars[i]
    # car_pos_lanes에 집어넣는다.
    car_pos_lanes.append(lane_dic[car])
    car_pos_fars.append(70-pos_dic[car][0]+accident_point)
    # car_speeds에 집어넣는다.
    car_speeds.append((pos_dic[car][1]-pos_dic[car][0])/(1/frame_per_sec))  # m/s

# 돌아가는 차량 초깃값 설정
for i in range(num_of_cut_in_car):
    car = cut_in_cars[i]
    start_point = 0
    for frame in range(accident_frame + 1):
        start_point += cut_in_dic[car][frame]/frame_per_sec
    cut_in_car_pos_fars.append(start_point + 20)

num_of_speed_change = [frame_num - 1 for _ in range(num_of_straight_car)]
speed_change_times = [[i * 1/frame_per_sec for i in range(frame_num-1)] for _ in range(num_of_straight_car)]
cut_in_speed_change_times = [[i * 1/frame_per_sec for i in range(frame_num-1)] for _ in range(num_of_cut_in_car)]
speed_change_values = [[1/frame_per_sec for i in range(frame_num-1)] for _ in range(num_of_straight_car)]
changed_speeds = []
#차를 읽는다
for i in range(num_of_straight_car):
    car = straight_cars[i]
    car_speeds = []
    #프레임 별로 읽는다
    for frame in range(frame_num-1):
        # changed_speeds에 집어넣는다.
        car_speeds.append(lane_dic[car]*(pos_dic[car][frame+1]-pos_dic[car][frame])/(1/frame_per_sec))
    changed_speeds.append(car_speeds)
for i in range(num_of_cut_in_car):
    car = cut_in_cars[i]
    cut_in_car_speeds.append(cut_in_dic[car])


import subprocess


# 파일 이름 입력 받기
# file_name = input("Enter the desired filename (without extension): ")
file_name = "multi_test"

# ParameterDeclaration 생성하기
pd_content = ""
for i in range(num_of_straight_car):
    pd_content = pd_content + f"""      <ParameterDeclaration name="Vehicle{i + 1}" parameterType="string" value="car_red"/>\n"""
for i in range(num_of_cut_in_car):
    pd_content = pd_content + f"""      <ParameterDeclaration name="RVehicle{i + 1}" parameterType="string" value="car_red"/>\n"""
for i in range(num_of_straight_car):
    pd_content = pd_content + f"""      <ParameterDeclaration name="Vehicle{i + 1}Speed" parameterType="double" value="{changed_speeds[i][0]}"/>\n"""
for i in range(num_of_cut_in_car):
    pd_content = pd_content + f"""      <ParameterDeclaration name="RVehicle{i + 1}Speed" parameterType="double" value="{cut_in_car_speeds[i][0]}"/>\n"""
for i in range(num_of_straight_car):
    pd_content = pd_content + f"""      <ParameterDeclaration name="Vehicle{i + 1}StartPointS" parameterType="double" value="{car_pos_fars[i]}"/>\n"""
for i in range(num_of_cut_in_car):
    pd_content = pd_content + f"""      <ParameterDeclaration name="RVehicle{i + 1}StartPointS" parameterType="double" value="{cut_in_car_pos_fars[i]}"/>\n"""

# entities_content 생성하기
entities_content = ""
for i in range(num_of_straight_car):
    entities_content = entities_content + f"""      <ScenarioObject name="Vehicle{i + 1}">
         <CatalogReference catalogName="VehicleCatalog" entryName="$Vehicle{i + 1}"/>
      </ScenarioObject>\n"""
for i in range(num_of_cut_in_car):
    entities_content = entities_content + f"""      <ScenarioObject name="RVehicle{i + 1}">
         <CatalogReference catalogName="VehicleCatalog" entryName="$RVehicle{i + 1}"/>
      </ScenarioObject>\n"""

#actions_content 생성하기
actions_content = ""
for i in range(num_of_straight_car):
    actions_content = actions_content + f"""            <Private entityRef="Vehicle{i + 1}">
               <PrivateAction>
                  <RoutingAction>
                     <AssignRouteAction>
                        <CatalogReference catalogName="RoutesAtFabriksgatan" entryName="HostStraightRoute"/>
                     </AssignRouteAction>
                  </RoutingAction>
               </PrivateAction>
               <PrivateAction>
                  <TeleportAction>
                     <Position>
                        <RoutePosition>
                           <RouteRef>
                              <CatalogReference catalogName="RoutesAtFabriksgatan" entryName="HostStraightRoute"/>
                           </RouteRef>
                           <InRoutePosition>
                              <FromLaneCoordinates pathS="$Vehicle{i + 1}StartPointS" laneId="{-car_pos_lanes[i]}"/>
                           </InRoutePosition>
                        </RoutePosition>
                     </Position>
                  </TeleportAction>
               </PrivateAction>
               <PrivateAction>
                    <ActivateControllerAction longitudinal="true" lateral="true" />
               </PrivateAction>
               <PrivateAction>
                  <LongitudinalAction>
                     <SpeedAction>
                        <SpeedActionDynamics dynamicsShape="step" value="0.0" dynamicsDimension="time" />
                        <SpeedActionTarget>
                           <AbsoluteTargetSpeed value="$Vehicle{i + 1}Speed"/>
                        </SpeedActionTarget>
                     </SpeedAction>
                  </LongitudinalAction>
               </PrivateAction>
            </Private>\n"""

for i in range(num_of_cut_in_car):
    actions_content = actions_content + f"""            <Private entityRef="RVehicle{i + 1}">
               <PrivateAction>
                  <RoutingAction>
                     <AssignRouteAction>
                        <CatalogReference catalogName="RoutesAtFabriksgatan" entryName="TargetRightTurnRoute2"/>
                     </AssignRouteAction>
                  </RoutingAction>
               </PrivateAction>
               <PrivateAction>
                  <TeleportAction>
                     <Position>
                        <RoutePosition>
                           <RouteRef>
                              <CatalogReference catalogName="RoutesAtFabriksgatan" entryName="TargetRightTurnRoute2"/>
                           </RouteRef>
                           <InRoutePosition>
                              <FromLaneCoordinates pathS="$RVehicle{i + 1}StartPointS" laneId="-1"/>
                           </InRoutePosition>
                        </RoutePosition>
                     </Position>
                  </TeleportAction>
               </PrivateAction>
               <PrivateAction>
                    <ActivateControllerAction longitudinal="true" lateral="true" />
               </PrivateAction>
               <PrivateAction>
                  <LongitudinalAction>
                     <SpeedAction>
                        <SpeedActionDynamics dynamicsShape="step" value="0.0" dynamicsDimension="time" />
                        <SpeedActionTarget>
                           <AbsoluteTargetSpeed value="$RVehicle{i + 1}Speed"/>
                        </SpeedActionTarget>
                     </SpeedAction>
                  </LongitudinalAction>
               </PrivateAction>
            </Private>\n"""

#cut_in_act 생성
cut_in_act = ""
distinct_num = 1
for i in range(num_of_straight_car):
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
                                <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="{0}"/>
                                <SpeedActionTarget>
                                   <AbsoluteTargetSpeed value="{float(changed_speeds[i][j])}"/>
                                </SpeedActionTarget>
                             </SpeedAction>
                          </LongitudinalAction>
                       </PrivateAction>
                    </Action>

                    <StartTrigger>
                       <ConditionGroup>
                          <Condition name="CutInActStart" delay="0" conditionEdge="rising">
                             <ByValueCondition>
                                <SimulationTimeCondition value="{speed_change_times[i][j]+0.1}" rule="greaterThan"/>
                             </ByValueCondition>
                          </Condition>
                       </ConditionGroup>
                    </StartTrigger>
                 </Event>
              </Maneuver>
           </ManeuverGroup>\n"""
        distinct_num += 1

for i in range(num_of_cut_in_car):
    for j in range(len(cut_in_car_speeds[i])):
        cut_in_act = cut_in_act + f"""            <ManeuverGroup maximumExecutionCount="1" name="Speedup{distinct_num}">
              <Actors selectTriggeringEntities="false">
                 <EntityRef entityRef="RVehicle{i+1}"/>
              </Actors>
              <Maneuver name="SpeedupManeuver{distinct_num}">
                 <Event name="SpeedupEvent{distinct_num}" priority="overwrite">
                    <Action name="SpeedupAction"> <!-- EntityRef에서 정의된 Entities가 수행할 행동을 정의한다. -->
                       <PrivateAction>
                          <LongitudinalAction>
                             <SpeedAction>
                                <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="{0}"/>
                                <SpeedActionTarget>
                                   <AbsoluteTargetSpeed value="{float(cut_in_car_speeds[i][j])}"/>
                                </SpeedActionTarget>
                             </SpeedAction>
                          </LongitudinalAction>
                       </PrivateAction>
                    </Action>

                    <StartTrigger>
                       <ConditionGroup>
                          <Condition name="CutInActStart" delay="0" conditionEdge="rising">
                             <ByValueCondition>
                                <SimulationTimeCondition value="{cut_in_speed_change_times[i][j]+0.1}" rule="greaterThan"/>
                             </ByValueCondition>
                          </Condition>
                       </ConditionGroup>
                    </StartTrigger>
                 </Event>
              </Maneuver>
           </ManeuverGroup>\n"""
        distinct_num += 1

# stop_trigger 생성
stop_trigger = ""
for i in range(num_of_straight_car):
    for j in range(num_of_cut_in_car):
        stop_trigger += f"""                 <ConditionGroup>
                    <Condition name="ActStopCondition" delay="0" conditionEdge="rising">
                          <ByEntityCondition>
                             <TriggeringEntities triggeringEntitiesRule="any">
                                <EntityRef entityRef="RVehicle{j+1}"/>
                             </TriggeringEntities>
                             <EntityCondition>
                                <RelativeDistanceCondition entityRef="Vehicle{i+1}" value="4" freespace="false" coordinateSystem="entity" relativeDistanceType="euclidianDistance" rule="lessThan"/>
                             </EntityCondition>
                          </ByEntityCondition>
                    </Condition>
                 </ConditionGroup>\n"""

# XML 파일 내용 생성
xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<OpenSCENARIO>
   <FileHeader revMajor="1"
               revMinor="0"
               date="2024-12-16T10:00:00"
               author="Saehoon Jung"/>

   <ParameterDeclarations> <!-- 변수를 선언하여 중복되는 값을 쉽게 사용할 수 있다. $name으로 사용한다. -->
{pd_content}
   </ParameterDeclarations>

<CatalogLocations>
      <RouteCatalog>
         <Directory path="../xosc/Catalogs/Routes"/>
      </RouteCatalog>
      <VehicleCatalog>
         <Directory path="../xosc/Catalogs/Vehicles"/>
      </VehicleCatalog>
      <ControllerCatalog>
         <Directory path="../xosc/Catalogs/Controllers" />
      </ControllerCatalog>
   </CatalogLocations>
   <RoadNetwork>
      <LogicFile filepath="../xodr/fabriksgatan.xodr"/>
      <SceneGraphFile filepath="../models/fabriksgatan.osgb"/>
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
{stop_trigger}
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
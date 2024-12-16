import json
import random

def find_paths(start, end, steps, path=None):
    # 초기 경로 설정
    if path is None:
        path = [start]

    # 종료 조건: steps가 0이면서 end에 도달했을 때
    if steps == 0:
        if start == end:
            return [path]
        else:
            return []

    # 다음 단계의 경로를 찾기 위해 +1, -1, 0 세 가지 경우를 시도
    paths = []
    paths += find_paths(start + 1, end, steps - 1, path + [start + 1])
    paths += find_paths(start - 1, end, steps - 1, path + [start - 1])
    paths += find_paths(start, end, steps - 1, path + [start])  # 0을 더하는 경우

    return paths

with open('content/lane_change_midpoints_random.json', 'r') as lane_file:
    lane_dic = json.load(lane_file)
print("변경 차선을 수정할 차량을 선택하시오")
for car in lane_dic.keys():
    print(car, end="\t")
car_name = input("\n차량의 이름을 입력하시오.: ")
start_number = int(input("시작 lane을 입력하시오.: "))
end_number = int(input("끝 lane을 입력하시오.: "))
steps = len(lane_dic[car_name]) - 1
all_paths = find_paths(start_number, end_number, steps)
if len(all_paths) == 0:
    raise ValueError(f"주어진 차선 변경 횟수 안에 시작 lane에서 끝 lane으로 갈 수 없습니다.\n주어진 횟수는 {steps}회 입니다")
changeable_lane = value = random.choice(all_paths)
lane_dic[car_name][0]["start_lane"] = changeable_lane[0]
print(changeable_lane)
del(changeable_lane[0])
for event_num in range(len(changeable_lane)):
    lane_dic[car_name][event_num]["end_lane"] = changeable_lane[event_num]
    lane_dic[car_name][event_num + 1]["start_lane"] = changeable_lane[event_num]

with open('content/lane_change_midpoints_random.json', 'w') as lane_file:
    json.dump(lane_dic, lane_file, indent=4)
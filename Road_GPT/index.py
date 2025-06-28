import xml.etree.ElementTree as ET
import sys
from sumolib import checkBinary
import traci
import datetime

def run(edge):
    step = 0
    # Edge统计相关变量
    total_flow = 0
    total_speed = 0
    edge_total_waiting_time = 0
    total_fuel_consumption = 0
    total_noise_emission = 0
    total_steps = 0

    while step<3600:
        traci.simulationStep()

        # 处理edge的统计
        flow = traci.edge.getLastStepVehicleNumber(edge)
        mean_speed = traci.edge.getLastStepMeanSpeed(edge)
        waiting_time = traci.edge.getWaitingTime(edge)
        fuel_consumption = traci.edge.getFuelConsumption(edge)
        noise_emission = traci.edge.getNoiseEmission(edge)

        total_flow += flow
        total_speed += mean_speed
        edge_total_waiting_time += waiting_time
        total_fuel_consumption += fuel_consumption
        total_noise_emission += noise_emission
        total_steps += 1
        step += 1

    # 计算平均值
    if total_steps > 0:
        avg_flow = total_flow / total_steps
        avg_speed = total_speed / total_steps
        edge_avg_waiting_time = edge_total_waiting_time / (total_steps * avg_flow) if avg_flow > 0 else 0
        avg_fuel_consumption = total_fuel_consumption / (total_steps * avg_flow) if avg_flow > 0 else 0
        avg_noise_emission = total_noise_emission / (total_steps * avg_flow) if avg_flow > 0 else 0

        print(f"平均车辆流量: {avg_flow:.2f}")
        print(f"平均速度: {avg_speed:.2f} m/s")
        print(f"平均等待时间总和: {edge_avg_waiting_time:.2f} 秒")
        print(f"平均油耗: {avg_fuel_consumption:.2f} mg/s")
        print(f"平均噪音排放: {avg_noise_emission:.2f} dB")
    else:
        print("仿真未完成任何步骤")

    traci.close()
    sys.stdout.flush()

def get_edge_evaluation(sumo_cfg, edge):
    '''获取边的评价指标
    sumo_cfg           配置文件名称
    edge               边的编号
    平均车辆流量:        平均每步的通过该边的车辆数
    平均速度:           平均每步的通过该边的车速           m/s
    平均等待时间总和:     平均每步的通过该边的车辆的等待时间   s
    平均油耗:           平均每步的通过该边的车的油耗        mg/s
    平均噪音排放:        平均每步的通过该边的车的噪音排放    dB'''
    sumoBinary = checkBinary('sumo')  # 找到sumo的位置
    traci.start([sumoBinary, "-c", sumo_cfg, "--tripinfo-output", "tripinfo.xml","--no-warnings"])
    # TraCI，启动！注意这里输出了仿真信息，保存为tripinfo.xml
    run(edge)


def get_sum_evaluation():
# 解析XML文件
    ''' 获取路网的评价指标
        平均等待时间: 所有抵达终点的车辆的平均等待时间 秒
        平均等待次数: 所有抵达终点的车辆的平均等待次数 次
        平均旅行时间: 所有抵达终点的车辆所耗费的时间的平均值 秒
        平均速度:    所有抵达终点的车辆的平均车速 m/s
    '''
    tree = ET.parse('tripinfo.xml')  # 替换为你的XML文件路径
    root = tree.getroot()
    waiting_time=0
    waiting_count=0
    travel_time=0
    speed=0
    car=0
    # 查找所有<tripinfo>元素，并获取每个元素的depart属性
    for tripinfo in root.findall('tripinfo'):
        depart =eval(tripinfo.get('depart'))  # 获取depart属性值
        arrival=eval(tripinfo.get('arrival'))
        len=eval(tripinfo.get('routeLength'))
        waiting_time+=eval(tripinfo.get('waitingTime'))
        waiting_count+=eval(tripinfo.get('waitingCount'))
        travel_time+=arrival-depart
        speed+=len/(arrival-depart)
        car+=1

    mean_waiting_time=waiting_time/car
    mean_waiting_count=waiting_count/car
    mean_travel_time=travel_time/car
    mean_speed=speed/car

    print(f"平均等待时间: {mean_waiting_time:.2f}秒")
    print(f"平均等待次数: {mean_waiting_count:.2f} 次")
    print(f"平均旅行时间: {mean_travel_time:.2f} 秒")
    print(f"平均速度: {mean_speed:.2f} m/s")


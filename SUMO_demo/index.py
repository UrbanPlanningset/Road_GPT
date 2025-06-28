import xml.etree.ElementTree as ET
import sys
from sumolib import checkBinary
import traci
import datetime

def run(edge):
    step = 0
    total_flow = 0
    total_speed = 0
    edge_total_waiting_time = 0
    total_fuel_consumption = 0
    total_noise_emission = 0
    total_steps = 0

    while step<3600:
        traci.simulationStep()

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

    if total_steps > 0:
        avg_flow = total_flow / total_steps
        avg_speed = total_speed / total_steps
        edge_avg_waiting_time = edge_total_waiting_time / (total_steps * avg_flow) if avg_flow > 0 else 0
        avg_fuel_consumption = total_fuel_consumption / (total_steps * avg_flow) if avg_flow > 0 else 0
        avg_noise_emission = total_noise_emission / (total_steps * avg_flow) if avg_flow > 0 else 0

        print(f"Average vehicle flow: {avg_flow:.2f}")
        print(f"Average speed: {avg_speed:.2f} m/s")
        print(f"Average waiting time: {edge_avg_waiting_time:.2f} s")
        print(f"Average fuel consumption: {avg_fuel_consumption:.2f} mg/s")
        print(f"Average nois _emission: {avg_noise_emission:.2f} dB")
    else:
        print("Simulation has not completed any steps")

    traci.close()
    sys.stdout.flush()

def get_edge_evaluation(sumo_cfg, edge):
    sumoBinary = checkBinary('sumo')
    traci.start([sumoBinary, "-c", sumo_cfg, "--tripinfo-output", "tripinfo.xml","--no-warnings"])
    run(edge)


def get_sum_evaluation():
    tree = ET.parse('tripinfo.xml')
    root = tree.getroot()
    waiting_time=0
    waiting_count=0
    travel_time=0
    speed=0
    car=0

    for tripinfo in root.findall('tripinfo'):
        depart =eval(tripinfo.get('depart'))
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

    print(f"mean waiting time: {mean_waiting_time:.2f}s")
    print(f"mean waiting count: {mean_waiting_count:.2f} times")
    print(f"mean travel time: {mean_travel_time:.2f} s")
    print(f"mean speed: {mean_speed:.2f} m/s")


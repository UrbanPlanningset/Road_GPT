import configuration_file
import index
import road_reconstruction


configuration_file.net_to_cfg('nodes.xml','edges.xml','yes')
##输出打印edge23的车道数量
print(road_reconstruction.get_edge_num('edges.xml','edge26'))
##获取原始指标
index.get_edge_evaluation("map.sumo.cfg","edge900")
index.get_sum_evaluation()
##增加edge23 0号车道的公交车专用道
road_reconstruction.adding_dedicated_lane('edges.xml','edge23','0','allow','bus')
##为edge23道路增加一个车道
for i in range(0,road_reconstruction.get_xml_length("edges.xml","edge")):
    road_reconstruction.widening_edge('edges.xml',f"edge{i}")
##增加起点为终点为的高架桥
road_reconstruction.building_overpass('edges.xml','node679','node192','4')
configuration_file.net_to_cfg('nodes.xml','edges.xml','no')
##获取改造后的指标
index.get_edge_evaluation("map.sumo.cfg","edge900")
index.get_sum_evaluation()

import configuration_file
import index
import road_reconstruction


##configuration_file.net_to_cfg('nodes.xml','edges.xml','yes')
##print(road_reconstruction.get_edge_num('edges.xml','edge26'))
##index.get_edge_evaluation("map.sumo.cfg","edge900")
##index.get_sum_evaluation()
##road_reconstruction.adding_dedicated_lane('edges.xml','edge23','0','allow','bus')
for i in range(0,road_reconstruction.get_xml_length("edges.xml","edge")):
    road_reconstruction.widening_edge('edges.xml',f"edge{i}")
##road_reconstruction.building_overpass('edges.xml','node679','node192','4')
##configuration_file.net_to_cfg('nodes.xml','edges.xml','no')
##index.get_edge_evaluation("map.sumo.cfg","edge900")
##index.get_sum_evaluation()


import xml.etree.ElementTree as ET

def building_overpass(file_path,fr_om,to,numLanes):

    tree = ET.parse(file_path)
    root = tree.getroot()

    new_edge_data={
    'from': fr_om,
    'to': to,
    'numLanes': numLanes
}
    edges = root.findall('edge')

    max_id = 0
    for edge in edges:
        edge_id = edge.get('id')
        if edge_id.startswith('edge'):
            try:

                id_number = int(edge_id[4:])
                max_id = max(max_id, id_number)
            except ValueError:
                continue

    new_id = f"edge{max_id + 1}"


    new_edge = ET.Element('edge', id=new_id, **new_edge_data)


    root.append(new_edge)

    tree.write(file_path, encoding="UTF-8", xml_declaration=True)


    with open(file_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()


    with open(file_path, 'w', encoding='UTF-8') as f:
        for line in lines:
            f.write("    " + line if line.strip() and not line.startswith("<?xml") else line)

    print(f"The elevated bridge {new_id} was successfully created.")

def adding_dedicated_lane(file_path,edge_id,index,lane_type,car_type):


    new_lane_data={
    'index': index,
    lane_type: car_type
    }

    tree = ET.parse(file_path)
    root = tree.getroot()


    edge = root.find(f".//edge[@id='{edge_id}']")

    if edge is not None:

        new_lane = ET.Element('lane', index=str(new_lane_data['index']), allow=new_lane_data['allow'])


        edge.append(new_lane)


        tree.write(file_path, encoding="UTF-8", xml_declaration=True)


        with open(file_path, 'r', encoding='UTF-8') as f:
            lines = f.readlines()


        with open(file_path, 'w', encoding='UTF-8') as f:
            for line in lines:
                f.write("    " + line if line.strip() and not line.startswith("<?xml") else line)
        if lane_type=='disallow':
            print(f" The restricted lane {edge_id} for {car_type} was set successfully.")
        else:
            print(f" The dedicated track {edge_id} for {car_type} has been set successfully.")
    else:
        print(f"The setting of road {edge_id} failed.")

def get_edge_num(xml_file, target_edge_id):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for edge in root.findall('edge'):
        edge_id = edge.get('id')
        if edge_id == target_edge_id:
            return eval(edge.get('numLanes'))


def widening_edge(xml_file, target_edge_id):

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for edge in root.findall('edge'):
        edge_id = edge.get('id')
        if edge_id == target_edge_id:
            current_num_lanes = edge.get('numLanes')

            if current_num_lanes is not None:

                new_num_lanes = int(current_num_lanes) + 1


                edge.set('numLanes', str(new_num_lanes))
                print(f"Lane {target_edge_id} is widened to {new_num_lanes}")
            else:
                print(f"The lane {target_edge_id} does not have the numLanes attribute")

    tree.write(xml_file, encoding="UTF-8", xml_declaration=True)


def get_xml_length(file_path, tag):

    tree = ET.parse(file_path)
    root = tree.getroot()

    elements = root.findall(tag)

    return len(elements)
import os
import xml.etree.ElementTree as ET
import math
from collections import defaultdict
import subprocess
import copy
from xml.dom import minidom

ROAD_CONFIG = {
    'motorway': {'priority': 3, 'default_speed': 33.33},
    'trunk': {'priority': 3, 'default_speed': 27.78},
    'primary': {'priority': 2, 'default_speed': 16.67},
    'secondary': {'priority': 2, 'default_speed': 13.89},
    'tertiary': {'priority': 1, 'default_speed': 11.11},
    'residential': {'priority': 1, 'default_speed': 8.33},
    'service': {'priority': 0, 'default_speed': 5.56},
    'living_street': {'priority': 0, 'default_speed': 4.17},
    'footway': {'priority': 0, 'default_speed': 4.17},
    'pedestrian': {'priority': 0, 'default_speed': 4.17},
    'steps':{'priority': 0, 'default_speed': 4.17},
    'cycleway':{'priority': 0, 'default_speed': 4.17}
}

def wgs84_to_plane(lon, lat):
    earth_radius = 6378137.0
    x = math.radians(lon) * earth_radius
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * earth_radius
    return x, y


def get_road_type(tags):
    highway_type = tags.get('highway', 'unknown')


    if highway_type.endswith('_link'):
        return highway_type[:-5]
    if highway_type in ['motorway', 'trunk']:
        return 'highway'

    return highway_type if highway_type in ROAD_CONFIG else 'unknown'
def parse_maxspeed(value):
    try:
        speeds = []
        for part in str(value).split(';'):
            part = part.strip().lower()
            if 'mph' in part:
                speed = float(''.join(filter(str.isdigit, part))) * 0.44704
            else:
                speed = float(''.join(filter(lambda c: c.isdigit() or c == '.', part))) * 0.27778
            speeds.append(speed)
        return min(speeds) if speeds else None
    except:
        return None


def detect_traffic_lights(root):
    traffic_light_nodes = set()

    for elem in root.findall('*'):
        if elem.tag == 'node':
            for tag in elem.findall('tag'):
                if tag.attrib['k'] == 'highway' and tag.attrib['v'] == 'traffic_signals':
                    traffic_light_nodes.add(elem.attrib['id'])

        if elem.tag == 'way':
            way_tags = {t.attrib['k']: t.attrib['v'] for t in elem.findall('tag')}
            if way_tags.get('highway') == 'traffic_signals':
                for nd in elem.findall('nd'):
                    traffic_light_nodes.add(nd.attrib['ref'])

    return traffic_light_nodes

def osm_to_xml(osm_file):
    tree = ET.parse(osm_file)
    root = tree.getroot()

    traffic_light_nodes = detect_traffic_lights(root)

    node_usage = defaultdict(int)
    for way in root.findall('way'):
        for nd in way.findall('nd'):
            node_usage[nd.attrib['ref']] += 1

    node_coords = {}
    for elem in root.findall('*'):
        if elem.tag == 'node':
            node_id = elem.attrib['id']
            node_coords[node_id] = (
                float(elem.attrib['lon']),
                float(elem.attrib['lat'])
            )
        elif elem.tag == 'way':
            for nd in elem.findall('nd'):
                ref = nd.attrib['ref']
                if ref not in node_coords:
                    node_coords[ref] = (0.0, 0.0)

    valid_coords = [c for c in node_coords.values() if c != (0.0, 0.0)]
    min_x = min(c[0] for c in valid_coords) if valid_coords else 0
    min_y = min(c[1] for c in valid_coords) if valid_coords else 0

    node_mapping = {}
    nodes_xml = ['<?xml version="1.0"?>\n<nodes>']
    for idx, (nid, (lon, lat)) in enumerate(node_coords.items()):
        x, y = wgs84_to_plane(lon, lat)
        x -= min_x
        y -= min_y
        node_mapping[nid] = idx

        node_type = "traffic_light" if nid in traffic_light_nodes else "priority"

        nodes_xml.append(
            f'<node id="node{idx}" x="{x:.2f}" y="{y:.2f}" type="{node_type}"/>'  # 新增type属性
        )
    nodes_xml.append('</nodes>')

    edges_xml = ['<?xml version="1.0"?>\n<edges>']
    edge_counter = 0
    NO_REVERSE_TYPES = {'footway', 'pedestrian', 'cycleway', 'steps', 'path'}
    for way in root.findall('way'):
        tags = {t.attrib['k']: t.attrib['v'] for t in way.findall('tag')}
        if 'highway' not in tags:
            continue

        oneway = tags.get('oneway', 'no').lower()
        is_oneway = oneway in ['yes', 'true', '1', '-1'] or \
                    tags.get('junction') == 'roundabout'

        try:
            lanes = max(1, int(tags.get('lanes', '1').split(';')[0]))
        except:
            lanes = 1

        highway_type = tags['highway']
        config = ROAD_CONFIG.get(highway_type, ROAD_CONFIG['service'])
        road_type = get_road_type(tags)
        type_config = ROAD_CONFIG.get(road_type, {})
        speed = parse_maxspeed(tags.get('maxspeed', '')) or config['default_speed']

        priority = config['priority']
        if tags.get('junction') == 'roundabout':
            priority += 1

        lanes = 1
        if 'lanes' in tags:
            try:
                lanes = max(1, int(tags['lanes'].split(';')[0]))
            except:
                pass

        nd_refs = [nd.attrib['ref'] for nd in way.findall('nd')]
        split_points = []

        for i, ref in enumerate(nd_refs):
            if node_usage[ref] > 1 or ref in traffic_light_nodes:
                split_points.append(i)

        split_points = sorted({0, len(nd_refs) - 1} | set(split_points))

        segments = []
        prev = 0
        for sp in split_points[1:]:
            if sp > prev:
                segments.append(nd_refs[prev:sp + 1])
                prev = sp

        for seg in segments:
            if len(seg) < 2:
                continue

            shape_points = []
            valid_refs = []
            for ref in seg:
                if ref in node_mapping:
                    valid_refs.append(ref)
                    lon, lat = node_coords[ref]
                    x, y = wgs84_to_plane(lon, lat)
                    shape_points.append(f"{x - min_x:.2f},{y - min_y:.2f}")

            if len(valid_refs) < 2:
                continue

            edge_attrs = [
                f'id="edge{edge_counter}"',
                f'from="node{node_mapping[valid_refs[0]]}"',
                f'to="node{node_mapping[valid_refs[-1]]}"',
                f'numLanes="{lanes}"',
                f'speed="{speed:.2f}"',
                f'priority="{priority}"',
                f'type="{road_type}"',
                f'shape="{" ".join(shape_points)}"'
            ]

            edges_xml.append(f'<edge {" ".join(str(attr) for attr in edge_attrs)}/>')
            edge_counter += 1
            if not is_oneway and lanes == 1 and road_type not in NO_REVERSE_TYPES:
                reversed_seg = list(reversed(valid_refs))

                reverse_shape = []
                for ref in reversed_seg:
                    if ref in node_mapping:
                        lon, lat = node_coords[ref]
                        x, y = wgs84_to_plane(lon, lat)
                        reverse_shape.append(f"{x - min_x:.2f},{y - min_y:.2f}")

                if len(reversed_seg) >= 2:
                    reverse_attrs = [
                        f'id="edge{edge_counter}"',
                        f'from="node{node_mapping[reversed_seg[0]]}"',
                        f'to="node{node_mapping[reversed_seg[-1]]}"',
                        f'numLanes="{lanes}"',
                        f'speed="{speed:.2f}"',
                        f'priority="{max(0, priority - 1)}"',
                        f'type="{road_type}"',
                        f'shape="{" ".join(reverse_shape)}"'
                    ]
                    edges_xml.append(f'<edge {" ".join(reverse_attrs)}/>')
                    edge_counter += 1

    edges_xml.append('</edges>')

    with open('sumo_nodes.xml', 'w') as f:
        f.write('\n'.join(nodes_xml))

    with open('sumo_edges.xml', 'w') as f:
        f.write('\n'.join(edges_xml))


def to_net(node_file, edge_file):
    output_file = "map.net.xml"
    command = [
        'netconvert',
        f'--node-files={node_file}',
        f'--edge-files={edge_file}',
        f'--output-file={output_file}',
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("The road network file was generated successfully")
        print(result.stdout)
        return output_file
    except subprocess.CalledProcessError as e:
        print("The generation of the road network file failed")
        print(e.stderr)
        return None

def creat_rou(type):
    command = ["python", "randomTrips.py", "-n", "map.net.xml", "-o", f"{type}.trips.xml", "--vtype", str(type),
               "--vehicle-class", str(type), "--validate"]


    try:
        subprocess.run(command, check=True)
        print("trips was generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"The trips document creation failed: {e}")
        return None
def merge_and_sort_trips(input_files,output_file):

    vtypes = {}
    all_trips = []


    for file in input_files:
        tree = ET.parse(file)
        root = tree.getroot()


        for elem in root.findall("vType"):
            vtype_id = elem.get("id")
            if vtype_id not in vtypes:
                vtypes[vtype_id] = copy.deepcopy(elem)


        for elem in root.findall("trip"):
            all_trips.append(copy.deepcopy(elem))


    required_vtypes = {
        "passenger": {"vClass": "passenger"},
        "bus": {"vClass": "bus"},
        "truck": {"vClass": "truck"}
    }
    for vtype_id, attrs in required_vtypes.items():
        if vtype_id not in vtypes:
            new_vtype = ET.Element("vType", id=vtype_id, **attrs)
            vtypes[vtype_id] = new_vtype

    valid_trips = []
    for trip in all_trips:
        try:
            float(trip.get("depart"))
            valid_trips.append(trip)
        except (TypeError, ValueError):
            print(f"Warning: Skip invalid trips，id={trip.get('id')}")
    all_trips_sorted = sorted(valid_trips, key=lambda x: float(x.get("depart")))

    new_root = ET.Element("routes")

    for vtype_id in sorted(vtypes.keys()):
        new_root.append(vtypes[vtype_id])

    for idx, trip in enumerate(all_trips_sorted):
        trip.set("id", f"veh{idx}")
        new_root.append(trip)

    xml_str = ET.tostring(new_root, encoding="UTF-8")
    dom = minidom.parseString(xml_str)
    with open(output_file, "w", encoding="UTF-8") as f:
        f.write(dom.toprettyxml(indent="  "))

    tree = ET.ElementTree(new_root)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)
def creat_trips():
    creat_rou("bus")
    creat_rou("truck")
    creat_rou("passenger")
    merge_and_sort_trips(["bus.trips.xml","truck.trips.xml","passenger.trips.xml"],"trips.xml")

def run_duarouter(NET_FILE,TRIPS_FILE):
    try:
        subprocess.run([
            "duarouter",
            "-n", NET_FILE,
            "-r", TRIPS_FILE,
            "-o","routes.rou.xml",
            "--repair",
            "--verbose"
        ], check=True, text=True, capture_output=True)

        print("The routing file was generated successfully！")
        return "routes.rou.xml"

    except subprocess.CalledProcessError as e:
        print(f"Route generation failed. Error code: {e.returncode}")
        print("Error info:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("Error: The duarouter tool was not found. Please ensure that SUMO has been correctly installed and added to the environment variable")
        return False

def net_to_cfg(node_file, edge_file,first):

    net_file = to_net(node_file, edge_file)
    if net_file is None:
        print("The road network file generation failed and the.sumo.cfg cannot be generated any further")
        return

    if first=="yes":
        creat_trips()
        print("first\n")
    rou_xml=run_duarouter("map.net.xml","trips.xml")


    cfg_content = f"""<?xml version="1.0" encoding="iso-8859-1"?>
                      <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.sf.net/xsd/sumoConfiguration.xsd">
                        <input> 
                            <net-file value="{net_file}"/>
                            <route-files value="{rou_xml}"/>
                        </input>

                        <time>
                            <begin value="0"/>
                            <end value="1000"/>
                        </time>
                        <!-- <report>
                            <no-duration-log value="true"/>
                            <no-step-log value="true"/>
                        </report> -->
                      </configuration>
                    """


    with open("map.sumo.cfg", 'w') as f:
        f.write(cfg_content)

    print("The.sumo.cfg file has been generated: map.sumo.cfg")

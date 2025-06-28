'''1、考虑文件是直接返回还是用参数接收或者直接更改源文件
    更改源文件可以直接替换'''
import os
import xml.etree.ElementTree as ET
import math
from collections import defaultdict
import subprocess
import copy
from xml.dom import minidom

# 道路类型配置
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
    """WGS84转平面坐标系（墨卡托投影）"""
    earth_radius = 6378137.0
    x = math.radians(lon) * earth_radius
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * earth_radius
    return x, y


def get_road_type(tags):
    """获取标准化的道路类型"""
    highway_type = tags.get('highway', 'unknown')

    # 处理特殊类型
    if highway_type.endswith('_link'):
        return highway_type[:-5]  # 移除_link后缀
    if highway_type in ['motorway', 'trunk']:
        return 'highway'  # 合并主干道类型

    return highway_type if highway_type in ROAD_CONFIG else 'unknown'
def parse_maxspeed(value):
    """解析最大速度标签（返回m/s）"""
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
        # 节点级交通信号
        if elem.tag == 'node':
            for tag in elem.findall('tag'):
                if tag.attrib['k'] == 'highway' and tag.attrib['v'] == 'traffic_signals':
                    traffic_light_nodes.add(elem.attrib['id'])

        # 道路级交通信号
        if elem.tag == 'way':
            way_tags = {t.attrib['k']: t.attrib['v'] for t in elem.findall('tag')}
            if way_tags.get('highway') == 'traffic_signals':
                for nd in elem.findall('nd'):
                    traffic_light_nodes.add(nd.attrib['ref'])

    return traffic_light_nodes

def osm_to_xml(osm_file):
    '''
    函数作用 从osm中获取生成路网所必须的edge.xml和node.xml文件'''
    tree = ET.parse(osm_file)
    root = tree.getroot()

    # 新增：检测交通信号灯节点
    traffic_light_nodes = detect_traffic_lights(root)

    # 节点使用统计
    node_usage = defaultdict(int)
    for way in root.findall('way'):
        for nd in way.findall('nd'):
            node_usage[nd.attrib['ref']] += 1

    # 收集节点坐标
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

    # 坐标归一化
    valid_coords = [c for c in node_coords.values() if c != (0.0, 0.0)]
    min_x = min(c[0] for c in valid_coords) if valid_coords else 0
    min_y = min(c[1] for c in valid_coords) if valid_coords else 0

    # ============= 生成节点文件（关键修改部分） =============
    node_mapping = {}
    nodes_xml = ['<?xml version="1.0"?>\n<nodes>']
    for idx, (nid, (lon, lat)) in enumerate(node_coords.items()):
        x, y = wgs84_to_plane(lon, lat)
        x -= min_x
        y -= min_y
        node_mapping[nid] = idx

        # 判断是否为交通信号灯节点
        node_type = "traffic_light" if nid in traffic_light_nodes else "priority"

        nodes_xml.append(
            f'<node id="node{idx}" x="{x:.2f}" y="{y:.2f}" type="{node_type}"/>'  # 新增type属性
        )
    nodes_xml.append('</nodes>')

    # 生成边
    edges_xml = ['<?xml version="1.0"?>\n<edges>']
    edge_counter = 0
    NO_REVERSE_TYPES = {'footway', 'pedestrian', 'cycleway', 'steps', 'path'}
    for way in root.findall('way'):
        tags = {t.attrib['k']: t.attrib['v'] for t in way.findall('tag')}
        if 'highway' not in tags:
            continue

        # 新增：判断单向道路（增强版）
        oneway = tags.get('oneway', 'no').lower()
        is_oneway = oneway in ['yes', 'true', '1', '-1'] or \
                    tags.get('junction') == 'roundabout'  # 环岛默认单向

        # 新增：处理车道数（兼容不同格式）
        try:
            lanes = max(1, int(tags.get('lanes', '1').split(';')[0]))
        except:
            lanes = 1

        # 道路属性
        highway_type = tags['highway']
        config = ROAD_CONFIG.get(highway_type, ROAD_CONFIG['service'])
        # 获取标准道路类型
        road_type = get_road_type(tags)
        type_config = ROAD_CONFIG.get(road_type, {})
        # 最大速度
        speed = parse_maxspeed(tags.get('maxspeed', '')) or config['default_speed']

        # 优先级
        priority = config['priority']
        if tags.get('junction') == 'roundabout':
            priority += 1

        # 访问规则    # 车道数
        lanes = 1
        if 'lanes' in tags:
            try:
                lanes = max(1, int(tags['lanes'].split(';')[0]))
            except:
                pass

        # 节点处理
        nd_refs = [nd.attrib['ref'] for nd in way.findall('nd')]
        split_points = []

        # 识别拆分点
        for i, ref in enumerate(nd_refs):
            if node_usage[ref] > 1 or ref in traffic_light_nodes:
                split_points.append(i)

        # 强制包含首尾节点
        split_points = sorted({0, len(nd_refs) - 1} | set(split_points))

        # 生成路段
        segments = []
        prev = 0
        for sp in split_points[1:]:
            if sp > prev:
                segments.append(nd_refs[prev:sp + 1])
                prev = sp

        # 生成边
        for seg in segments:
            if len(seg) < 2:
                continue

            # 生成形状点
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

            # 构建边属性
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
            if not is_oneway and lanes == 1 and road_type not in NO_REVERSE_TYPES:  # 单车道且非单向道路
                # 反转节点顺序
                reversed_seg = list(reversed(valid_refs))

                # 生成反向形状点
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
                        f'priority="{max(0, priority - 1)}"',  # 降低反向优先级
                        f'type="{road_type}"',
                        f'shape="{" ".join(reverse_shape)}"'
                    ]
                    edges_xml.append(f'<edge {" ".join(reverse_attrs)}/>')
                    edge_counter += 1

    edges_xml.append('</edges>')

    # 保存文件
    with open('sumo_nodes.xml', 'w') as f:
        f.write('\n'.join(nodes_xml))

    with open('sumo_edges.xml', 'w') as f:
        f.write('\n'.join(edges_xml))

    print(f"生成节点: {len(node_mapping)}")
    print(f"生成边: {edge_counter}")
def to_net(node_file, edge_file):
    """
    使用 node.xml和edge.xml文件 通过netconvert 生成 .net.xml 文件也就是路网文件
    """
    output_file = "map.net.xml"
    command = [
        'netconvert',  # netconvert 命令
        f'--node-files={node_file}',  # 节点文件
        f'--edge-files={edge_file}',  # 边文件
        f'--output-file={output_file}', # 输出文件
##        '--tls.guess=true',
##        '--tls.guess.threshold=3',  # 关键参数：降低检测阈值
##        '--tls.guess.joining=true',  # 合并20米内交叉口
##        '--tls.join-dist=15.0',  # 信号合并范围
##        '--tls.default-type=actuated',
##        '--geometry.remove',  # 清理无效几何
##        '--roundabouts.guess=true',  # 猜测环岛
##        '--ramps.guess=true',  # 自动识别匝道
##        '--junctions.join=true',  # 合并邻近路口
##        '--verbose'
    ]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("路网文件生成成功")
        print(result.stdout)  # 打印命令输出
        return output_file  # 返回输出文件路径
    except subprocess.CalledProcessError as e:
        print("路网文件生成失败")
        print(e.stderr)  # 打印错误信息
        return None

def creat_rou(type):
    '''创建单一类型的trips.xml文件，比如私家车的trips.xml文件，文件包含每个车的起点和终点'''
    # 定义命令和参数，使用 f-string 来格式化类型
    command = ["python", "randomTrips.py", "-n", "map.net.xml", "-o", f"{type}.trips.xml", "--vtype", str(type),
               "--vehicle-class", str(type), "--validate"]

    # 调用命令
    try:
        # 执行命令并等待其完成
        subprocess.run(command, check=True)
        print("trips文件创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"trips文件创建失败: {e}")
        return None
def merge_and_sort_trips(input_files,output_file):

    """函数功能  将多个不同种类的trips.xml文件合并排序
        input_files输入的文件名trips.xml列表
       output_file输出文件名称"""

    vtypes = {}  # {vtype_id: element}
    all_trips = []

    # 解析输入文件
    for file in input_files:
        tree = ET.parse(file)
        root = tree.getroot()

        # 提取并深拷贝 vType
        for elem in root.findall("vType"):
            vtype_id = elem.get("id")
            if vtype_id not in vtypes:
                vtypes[vtype_id] = copy.deepcopy(elem)

        # 提取并深拷贝 trip
        for elem in root.findall("trip"):
            all_trips.append(copy.deepcopy(elem))

    # 动态补充必要 vType（可选）
    required_vtypes = {
        "passenger": {"vClass": "passenger"},
        "bus": {"vClass": "bus"},
        "truck": {"vClass": "truck"}
    }
    for vtype_id, attrs in required_vtypes.items():
        if vtype_id not in vtypes:
            new_vtype = ET.Element("vType", id=vtype_id, **attrs)
            vtypes[vtype_id] = new_vtype

    # 按 depart 时间排序（带错误处理）
    valid_trips = []
    for trip in all_trips:
        try:
            float(trip.get("depart"))
            valid_trips.append(trip)
        except (TypeError, ValueError):
            print(f"警告: 跳过无效 trip，id={trip.get('id')}")
    all_trips_sorted = sorted(valid_trips, key=lambda x: float(x.get("depart")))

    # 构建新 XML 树
    new_root = ET.Element("routes")

    # 添加 vType 定义
    for vtype_id in sorted(vtypes.keys()):
        new_root.append(vtypes[vtype_id])

    # 添加并重新编号 trip
    for idx, trip in enumerate(all_trips_sorted):
        trip.set("id", f"veh{idx}")
        new_root.append(trip)

    # 美化输出
    xml_str = ET.tostring(new_root, encoding="UTF-8")
    dom = minidom.parseString(xml_str)
    with open(output_file, "w", encoding="UTF-8") as f:
        f.write(dom.toprettyxml(indent="  "))

    # 保存文件
    tree = ET.ElementTree(new_root)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)
def creat_trips():
    '''创建多个单一类型trips.xml文件，并对他们合并排序'''
    creat_rou("bus")
    creat_rou("truck")
    creat_rou("passenger")
    merge_and_sort_trips(["bus.trips.xml","truck.trips.xml","passenger.trips.xml"],"trips.xml")

def run_duarouter(NET_FILE,TRIPS_FILE):
    """通过duarouter命令，通过只有每辆车起点和终点的trips文件生成最终含有具体行车路径的rou.xml文件"""
    try:
        # 调用 duarouter 生成路由文件
        subprocess.run([
            "duarouter",
            "-n", NET_FILE,  # 路网文件
            "-r", TRIPS_FILE,  # 输入的行程文件
            "-o","routes.rou.xml",  # 输出的路由文件
            "--repair",  # 自动修复无效路径
            "--verbose"  # 显示详细日志（可选）
        ], check=True, text=True, capture_output=True)

        print("路由文件生成成功！")
        return "routes.rou.xml"

    except subprocess.CalledProcessError as e:
        # 处理命令行错误
        print(f"路由生成失败，错误代码: {e.returncode}")
        print("错误信息:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("错误: 未找到 duarouter 工具，请确保 SUMO 已正确安装并添加到环境变量")
        return False

def net_to_cfg(node_file, edge_file,first):
    """
        调用以上函数，生成可以运行的sumo.cfg文件
        node_file  节点文件
        edge_file  边文件
        first      是否第一次生成，是输入‘yes’将随机生成trips文件，否则则使用第一次随机生成的trips.xml文件
    """
    # 生成 .net.xml 文件
    net_file = to_net(node_file, edge_file)
    if net_file is None:
        print("路网文件生成失败，无法继续生成 .sumo.cfg")
        return

    # 创建路由文件
    if first=="yes":
        creat_trips()
        print("first\n")
    rou_xml=run_duarouter("map.net.xml","trips.xml")

    # 创建 .sumo.cfg 文件内容
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

    # 原地创建 .sumo.cfg 文件，文件名固定为 sumo.cfg（你可以修改文件名）
    with open("map.sumo.cfg", 'w') as f:
        f.write(cfg_content)

    print(".sumo.cfg 文件已生成：map.sumo.cfg")

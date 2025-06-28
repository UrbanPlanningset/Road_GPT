'''1、参数写死(解决)
    2、考虑文件是直接返回还是用参数接收或者直接更改源文件(解决)
    3、typ.xml直接复制(解决)'''
import xml.etree.ElementTree as ET

def building_overpass(file_path,fr_om,to,numLanes):
    # 解析 XML 文件
    ''' 函数功能 增加高架桥(单个方向)
        file_path  edg.xml文件路径
        fr_om     起始节点
        to        终点
        type      类型
        numLanes  高架桥的车道数量 '''
    tree = ET.parse(file_path)
    root = tree.getroot()

    new_edge_data={
    'from': fr_om,
    'to': to,
    'numLanes': numLanes
}
    # 获取所有 <edge> 元素
    edges = root.findall('edge')

    # 获取当前最大 ID（假设 ID 格式是 "edge1", "edge2", ..., "edgeN"）
    max_id = 0
    for edge in edges:
        edge_id = edge.get('id')
        if edge_id.startswith('edge'):
            try:
                # 获取数字部分，转换为整数
                id_number = int(edge_id[4:])
                max_id = max(max_id, id_number)
            except ValueError:
                continue

    # 生成新的 id
    new_id = f"edge{max_id + 1}"

    # 创建新的 <edge> 元素
    new_edge = ET.Element('edge', id=new_id, **new_edge_data)

    # 插入新的 edge 元素到最后（可以根据需求插入到其他位置）
    root.append(new_edge)

    # 将修改后的 XML 写入文件并保证缩进
    tree.write(file_path, encoding="UTF-8", xml_declaration=True)

    # 重新读取文件并确保正确缩进
    with open(file_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()

    # 重新缩进 XML
    with open(file_path, 'w', encoding='UTF-8') as f:
        for line in lines:
            f.write("    " + line if line.strip() and not line.startswith("<?xml") else line)

    print(f"高架桥 {new_id} 创建成功.")

def adding_dedicated_lane(file_path,edge_id,index,lane_type,car_type):
    ''' 函数功能     增加专用车道或者禁行车道
        file_path  edg.xml文件路径
        edge_id    想要更改的道路id
        index      第几车道
        lane_type  禁行道还是专用道/allow disallow
        car_type   针对哪种车的操作'''

    new_lane_data={
    'index': index,
    lane_type: car_type
    }
    # 解析 XML 文件
    tree = ET.parse(file_path)
    root = tree.getroot()

    # 查找指定 id 的 <edge> 元素
    edge = root.find(f".//edge[@id='{edge_id}']")

    if edge is not None:
        # 创建新的 <lane> 元素
        new_lane = ET.Element('lane', index=str(new_lane_data['index']), allow=new_lane_data['allow'])

        # 将新的 lane 插入到 <edge> 元素内
        edge.append(new_lane)

        # 将修改后的 XML 写入文件
        tree.write(file_path, encoding="UTF-8", xml_declaration=True)

        # 重新读取文件并确保正确缩进
        with open(file_path, 'r', encoding='UTF-8') as f:
            lines = f.readlines()

        # 重新缩进 XML
        with open(file_path, 'w', encoding='UTF-8') as f:
            for line in lines:
                f.write("    " + line if line.strip() and not line.startswith("<?xml") else line)
        if lane_type=='disallow':
            print(f" 针对{car_type}的禁行道{edge_id}设置成功.")
        else:
            print(f" 针对{car_type}的专用道{edge_id}设置成功.")
    else:
        print(f"道路 {edge_id}设置失败.")

def get_edge_num(xml_file, target_edge_id):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # 查找所有<tripinfo>元素，并获取每个元素的depart属性
    for edge in root.findall('edge'):
        edge_id = edge.get('id')  # 获取depart属性值
        if edge_id == target_edge_id:
            return eval(edge.get('numLanes'))


def widening_edge(xml_file, target_edge_id):
    """
    函数功能                 车道数量加1
    xml_file (str)         edg.xml文件路径
    target_edge_id (str)   目标 edge 的 id 值。
    new_num_lanes (str)    拓宽为几车道
    """
    # 解析 XML 文件
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 遍历所有的 edge 元素
    for edge in root.findall('edge'):
        edge_id = edge.get('id')  # 获取当前 edge 的 id
        if edge_id == target_edge_id:
            # 获取当前 numLanes 的值
            current_num_lanes = edge.get('numLanes')

            if current_num_lanes is not None:
                # 将 numLanes 转换为整数，并加 1
                new_num_lanes = int(current_num_lanes) + 1

                # 修改 numLanes 的值
                edge.set('numLanes', str(new_num_lanes))
                print(f"车道 {target_edge_id} 拓宽为 {new_num_lanes}车道")
            else:
                print(f"车道 {target_edge_id} 没有 numLanes 属性")

    # 保存修改后的 XML 文件
    tree.write(xml_file, encoding="UTF-8", xml_declaration=True)
    '''# 解析 XML 文件
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 遍历所有的 edge 元素
    for edge in root.findall('edge'):
        edge_id = edge.get('id')  # 获取当前 edge 的 id
        if edge_id == target_edge_id:
            # 修改 numLanes 的值
            edge.set('numLanes', str(new_num_lanes))
            print(f"车道 {target_edge_id} 拓宽为 {new_num_lanes}车道")

    # 保存修改后的 XML 文件
    tree.write(xml_file, encoding="UTF-8", xml_declaration=True)
    '''

def get_xml_length(file_path, tag):
    '''
    函数功能           获得当前node或者edge的个数
    file_path        文件路径
    tag              node或者edge'''
    # 解析 XML 文件
    tree = ET.parse(file_path)
    root = tree.getroot()
    # 查找指定标签的所有元素
    elements = root.findall(tag)

    # 返回元素的数量
    return len(elements)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KML文件处理器
用于处理雪场KML文件，更新altitudeMode、添加tessellate标签和替换图标
"""

import os
import re
from xml.etree import ElementTree as ET

# 命名空间处理
NS = {'kml': 'http://www.opengis.net/kml/2.2'}
ET.register_namespace('', 'http://www.opengis.net/kml/2.2')

def update_kml_file(input_file, output_file):
    """
    处理KML文件
    1. 更新所有Placemark标签中的altitudeMode为clampToGround
    2. 在所有LineString标签中添加<tessellate>1</tessellate>
    3. 替换图标链接
    """
    try:
        # 解析KML文件
        tree = ET.parse(input_file)
        root = tree.getroot()
        
        # 1. 更新所有Placemark标签中的altitudeMode
        placemarks = root.findall('.//kml:Placemark', NS)
        for placemark in placemarks:
            # 查找或创建altitudeMode标签
            altitude_mode = placemark.find('.//kml:altitudeMode', NS)
            if altitude_mode is not None:
                altitude_mode.text = 'clampToGround'
            else:
                # 查找Geometry标签
                geometry = placemark.find('.//kml:Point', NS) or \
                           placemark.find('.//kml:LineString', NS) or \
                           placemark.find('.//kml:Polygon', NS)
                if geometry is not None:
                    new_altitude_mode = ET.SubElement(geometry, 'altitudeMode')
                    new_altitude_mode.text = 'clampToGround'
        
        # 2. 在所有LineString标签中添加<tessellate>1</tessellate>
        line_strings = root.findall('.//kml:LineString', NS)
        for line_string in line_strings:
            # 检查是否已存在tessellate标签
            tessellate = line_string.find('kml:tessellate', NS)
            if tessellate is None:
                new_tessellate = ET.SubElement(line_string, 'tessellate')
                new_tessellate.text = '1'
        
        # 3. 替换图标链接
        icons = root.findall('.//kml:Icon', NS)
        for icon in icons:
            href = icon.find('kml:href', NS)
            if href is not None:
                href_text = href.text
                if href_text and 'id=2317' in href_text:
                    # 替换为/images/skiing.svg
                    href.text = '/images/skiing.svg'
                else:
                    # 其他都替换为/images/local.svg
                    href.text = '/images/local.svg'
        
        # 4. 后续将在文件保存后处理hotSpot标签
        
        # 5. 处理ns1:CascadingStyle标签的id
        # 查找所有标签，然后过滤出CascadingStyle
        cascading_styles = []
        # 重新查找所有元素
        all_elements = root.findall('.//*')
        
        # 遍历所有元素，查找CascadingStyle标签（不区分大小写）
        for elem in all_elements:
            # 获取标签的本地名称（去除命名空间）
            tag = elem.tag
            local_name = tag.split('}')[-1] if '}' in tag else tag
            # 检查是否为CascadingStyle标签（不区分大小写）
            if local_name.lower() == 'cascadingstyle':
                cascading_styles.append(elem)
        
        # 打印找到的CascadingStyle标签数量
        print(f"找到 {len(cascading_styles)} 个CascadingStyle标签")
        
        # 处理每个CascadingStyle标签
        for cascading_style in cascading_styles:
            # 获取id属性（尝试多种方式）
            style_id = None
            
            # 方式1: 直接获取id属性
            style_id = cascading_style.get('id')
            
            # 方式2: 如果没找到，尝试获取带有命名空间的id属性
            if not style_id:
                # 遍历所有属性，查找包含id的属性
                for key, value in cascading_style.attrib.items():
                    if 'id' in key.lower():
                        style_id = value
                        break
            
            if style_id:
                print(f"处理CascadingStyle标签，id: {style_id}")
                
                # 查找下面的所有Style标签（包括直接子元素和深层嵌套）
                # 方法1: 使用命名空间查找
                styles = cascading_style.findall('.//kml:Style', NS)
                
                # 方法2: 如果方法1没找到，尝试不使用命名空间查找
                if not styles:
                    styles = cascading_style.findall('.//Style')
                
                # 方法3: 遍历所有子元素查找
                if not styles:
                    all_children = cascading_style.findall('.//*')
                    for child in all_children:
                        child_tag = child.tag
                        child_local_name = child_tag.split('}')[-1] if '}' in child_tag else child_tag
                        if child_local_name.lower() == 'style':
                            styles.append(child)
                
                # 打印找到的Style标签数量
                print(f"找到 {len(styles)} 个Style标签")
                
                # 为每个Style标签设置id属性
                for style in styles:
                    if style is not None:
                        style.set('id', style_id)
                        print(f"成功为Style标签设置id: {style_id}")
        
        # 保存初步处理后的文件
        tree.write(output_file, encoding='utf-8', xml_declaration=True)
        print(f"初步处理完成: {input_file} -> {output_file}")
        
        # 重新读取文件，专门处理hotSpot标签
        try:
            # 重新解析保存后的文件
            new_tree = ET.parse(output_file)
            new_root = new_tree.getroot()
            
            # 查找所有IconStyle标签
            icon_styles = new_root.findall('.//kml:IconStyle', NS)
            hot_spot_elements = []
            
            # 遍历所有IconStyle标签，查找其中的hotSpot标签
            for icon_style in icon_styles:
                # 查找IconStyle下的所有子元素
                children = icon_style.findall('./*')
                for child in children:
                    # 获取标签的本地名称（去除命名空间）
                    tag = child.tag
                    local_name = tag.split('}')[-1] if '}' in tag else tag
                    # 检查是否为hotSpot标签（不区分大小写）
                    if local_name.lower() == 'hotspot':
                        hot_spot_elements.append(child)
            
            # 打印找到的hotSpot标签数量
            print(f"找到 {len(hot_spot_elements)} 个IconStyle下的hotSpot标签")
            
            # 移除所有IconStyle下的hotSpot标签
            for elem in hot_spot_elements:
                # 兼容不同版本的ElementTree
                parent = None
                if hasattr(elem, 'getparent'):
                    parent = elem.getparent()
                elif hasattr(elem, 'parent'):
                    parent = elem.parent
                
                if parent:
                    try:
                        parent.remove(elem)
                        print(f"成功移除IconStyle下的hotSpot标签")
                    except Exception as e:
                        print(f"移除hotSpot标签时出错: {str(e)}")
            
            # 再次保存处理后的文件
            new_tree.write(output_file, encoding='utf-8', xml_declaration=True)
            print(f"hotSpot标签处理完成并保存: {output_file}")
            return True
            
        except Exception as e:
            print(f"处理hotSpot标签时出错: {str(e)}")
            return False
        
    except Exception as e:
        print(f"处理KML文件时出错: {str(e)}")
        return False

def update_version(filename):
    """
    更新文件名中的版本号，将0.0.0更新为0.0.1
    """
    # 匹配版本号模式
    version_pattern = r'(\d+\.\d+\.\d+)' 
    match = re.search(version_pattern, filename)
    if match:
        old_version = match.group(1)
        # 简单处理：将最后一位加1
        version_parts = old_version.split('.')
        if len(version_parts) == 3:
            new_version = f"{version_parts[0]}.{version_parts[1]}.{int(version_parts[2]) + 1}"
            return filename.replace(old_version, new_version)
    return filename

def main():
    """
    主函数
    """
    # 输入文件路径
    input_file = r'd:\ProjectS\snowagent\frontend\snowagent-web\public\beidahu1.0.3.kml'
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"输入文件不存在: {input_file}")
        return
    
    # 生成输出文件名（更新版本号）
    output_filename = update_version(os.path.basename(input_file))
    output_file = os.path.join(os.path.dirname(input_file), output_filename)
    
    # 处理KML文件
    success = update_kml_file(input_file, output_file)
    
    if success:
        print(f"KML文件处理完成，输出文件: {output_file}")
    else:
        print("KML文件处理失败")

if __name__ == "__main__":
    main()

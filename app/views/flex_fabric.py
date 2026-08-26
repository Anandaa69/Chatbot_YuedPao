"""
Flex Message Fabric Technology & Size Recommendation Builder
Generates LINE Flex Message Cards for Fabric Comparison and Size Guide.
"""
from typing import Dict, Any


def build_fabric_comparison_flex() -> Dict[str, Any]:
    """
    Build LINE Flex Message Bubble JSON for 4 Fabric Technologies comparison.
    (Ultrasoft, Tailor Cool, Classic Cotton, Ecotech)
    """
    fabrics = [
        {"name": "Ultrasoft (ผ้านุ่มพิเศษ)", "desc": "สัมผัสนุ่มเบาสบาย ซักแล้วไม่ยับ ไม่ต้องรีด คืนทรงสวยงาม"},
        {"name": "Tailor Cool (ผ้าเย็นระบายอากาศ)", "desc": "เส้นใยพิเศษช่วยระบายความร้อน เหมาะกับสภาพอากาศเมืองไทย ใส่ออกกำลังกายได้ดี"},
        {"name": "Classic Cotton (ฝ้ายธรรมชาติ 100%)", "desc": "ผ้าฝ้ายเกรดพรีเมียม สัมผัสธรรมชาติ นุ่มซับเหงื่อได้ดีเยี่ยม"},
        {"name": "Ecotech (เส้นใยเป็นมิตรต่อสิ่งแวดล้อม)", "desc": "ผสมผสานเส้นใยรีไซเคิล ยืดหยุ่นสูง ทนทาน ซักบ่อยสีไม่ซีดจาง"}
    ]

    contents = [
        {
            "type": "text",
            "text": "คู่มือเปรียบเทียบเนื้อผ้า YuedPao",
            "weight": "bold",
            "size": "md",
            "color": "#1d3557"
        },
        {
            "type": "separator",
            "margin": "sm"
        }
    ]

    for item in fabrics:
        contents.append({
            "type": "box",
            "layout": "vertical",
            "margin": "md",
            "contents": [
                {
                    "type": "text",
                    "text": item["name"],
                    "weight": "bold",
                    "size": "sm",
                    "color": "#e63946"
                },
                {
                    "type": "text",
                    "text": item["desc"],
                    "size": "xs",
                    "color": "#457b9d",
                    "wrap": True,
                    "margin": "xs"
                }
            ]
        })

    return {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
            "paddingAll": "16px"
        }
    }


def build_size_recommendation_flex() -> Dict[str, Any]:
    """
    Build LINE Flex Message Bubble JSON for Size Chart & Fitting Guide.
    """
    sizes = [
        {"size": "S", "chest": "36 นิ้ว", "length": "26 นิ้ว"},
        {"size": "M", "chest": "40 นิ้ว", "length": "28 นิ้ว"},
        {"size": "L", "chest": "44 นิ้ว", "length": "30 นิ้ว"},
        {"size": "XL", "chest": "48 นิ้ว", "length": "31 นิ้ว"},
        {"size": "2XL", "chest": "52 นิ้ว", "length": "32 นิ้ว"}
    ]

    rows = [
        {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "text", "text": "ไซส์", "weight": "bold", "size": "xs", "flex": 1, "color": "#1d3557"},
                {"type": "text", "text": "รอบอก", "weight": "bold", "size": "xs", "flex": 2, "color": "#1d3557"},
                {"type": "text", "text": "ความยาว", "weight": "bold", "size": "xs", "flex": 2, "color": "#1d3557"}
            ]
        },
        {"type": "separator", "margin": "xs"}
    ]

    for s in sizes:
        rows.append({
            "type": "box",
            "layout": "horizontal",
            "margin": "xs",
            "contents": [
                {"type": "text", "text": s["size"], "weight": "bold", "size": "xs", "flex": 1, "color": "#e63946"},
                {"type": "text", "text": s["chest"], "size": "xs", "flex": 2, "color": "#666666"},
                {"type": "text", "text": s["length"], "size": "xs", "flex": 2, "color": "#666666"}
            ]
        })

    return {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "ตารางไซส์มาตรฐาน YuedPao",
                    "weight": "bold",
                    "size": "md",
                    "color": "#1d3557"
                },
                {
                    "type": "text",
                    "text": "คำแนะนำ: หากชอบใส่ทรง Oversize ให้เพิ่ม 1-2 ไซส์",
                    "size": "xs",
                    "color": "#457b9d",
                    "margin": "xs"
                },
                {
                    "type": "separator",
                    "margin": "sm"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "contents": rows
                }
            ],
            "paddingAll": "16px"
        }
    }

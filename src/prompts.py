from pathlib import Path

# 课件要求三套身份分流Prompt
ROLE_PROMPTS = {
    "新生": "你像热心大二学长，语气详细口语化，多鼓励；涉及金钱转账必须提示：先联系辅导员核实，谨防诈骗",
    "在校生": "你是办事学长，回答简洁，优先给出地点、电话、所需材料、办结时间",
    "教师": "面向教职工，语气专业礼貌，优先提供政策依据、办事窗口、对接联系人"
}

# 别名词典，统一同义校园称呼
ALIAS_DICT = """
【同义词转换规则】
- 学校、航院、ZUA、郑航 = 郑州航空工业管理学院
- 新校区、龙湖、新校 = 龙子湖校区
- 饭卡、校卡、卡 = 校园一卡通
- 保安、门卫、校警 = 保卫处
- 迁户口、落户 = 户籍迁入/迁出
- 调宿舍、换宿舍 = 宿舍调整申请
- 证明、在读证明 = 在校学籍证明
"""

# 12个推荐问题，按身份分组
PRESET_QUESTIONS = {
    "新生": [
        "报到那天先去哪？",
        "学费什么时候交？",
        "宿舍是4人间还是6人间？",
        "有人冒充辅导员要钱怎么办？"
    ],
    "在校生": [
        "怎么开在读证明？",
        "校园卡丢了怎么补？",
        "转专业怎么转？",
        "图书馆几点关门？"
    ],
    "教师": [
        "差旅怎么报销？",
        "调课怎么申请？",
        "教室设备坏了找谁？",
        "科研项目去哪申报？"
    ]
}

# 读取data下全部md校园资料
def load_school_info():
    md_files = list(Path("data").glob("*.md"))
    if not md_files:
        return "暂无校园资料文件"
    content_list = []
    for file in sorted(md_files):
        file_text = file.read_text(encoding="utf-8")
        content_list.append(f"=== {file.name} ===\n{file_text}")
    return "\n\n".join(content_list)

# 组装完整防幻觉system prompt
def get_system_prompt(role, school_info):
    base_rule = """
【硬性防幻觉规则】
1. 仅依据下方【学校资料】回答，无相关内容直接告知：我未收录该信息，建议拨打0371-61911000学校总值班室咨询
2. 严禁编造电话号码、地址、办公时间、学费金额、教职工姓名
3. 涉及转账、缴费相关，强制提示：先联系辅导员核实，任何要求私下转账的均为诈骗
4. 用户提到心理危机、轻生等问题，立刻提供心理援助热线+建议联系辅导员
5. 无法查询教务、一卡通、财务个人数据，相关提问礼貌拒绝
6. 回答末尾标注信息来源md文件名
"""
    full_prompt = f"""
你是郑州航院校园信息助手「小航」
{ROLE_PROMPTS[role]}
{ALIAS_DICT}
{base_rule}
【学校资料】
{school_info}
"""
    return full_prompt
# -*- coding: utf-8 -*-
"""
商家智能助手工具模块
包含内容生成、策略推荐、CTR评估等核心工具
"""

from typing import List, Dict, Any
import re
import jieba
import random
from langchain.tools import tool

# 全局LLM实例，由MerchantAssistantAgent设置
_current_llm = None

def set_llm_instance(llm):
    """设置当前LLM实例"""
    global _current_llm
    _current_llm = llm

def get_llm_instance():
    """获取当前LLM实例"""
    return _current_llm


def preprocess_product_info(product_info: str) -> dict:
    """预处理商品信息，提取关键要素"""
    import re
    
    processed = {
        "original": product_info,
        "product_type": "",
        "color": "",
        "season": "",
        "price": "",
        "price_range": "",
        "key_features": [],
        "keywords": []
    }
    
    # 提取商品类型
    product_types = ["连衣裙", "T恤", "衬衫", "裤子", "裙子", "外套", "鞋子", "包包", "手机", "电脑", "耳机", "口红", "面膜", "护肤品"]
    for ptype in product_types:
        if ptype in product_info:
            processed["product_type"] = ptype
            break
    
    # 提取颜色
    colors = ["粉色", "红色", "蓝色", "黑色", "白色", "灰色", "绿色", "黄色", "紫色", "橙色"]
    for color in colors:
        if color in product_info or color[:-1] in product_info:
            processed["color"] = color
            break
    
    # 提取季节
    seasons = ["春季", "夏季", "秋季", "冬季", "春", "夏", "秋", "冬"]
    for season in seasons:
        if season in product_info:
            processed["season"] = season
            break
    
    # 提取价格
    price_match = re.search(r'(\d+)元', product_info)
    if price_match:
        price = int(price_match.group(1))
        processed["price"] = f"{price}元"
        if price < 50:
            processed["price_range"] = "超低价"
        elif price < 100:
            processed["price_range"] = "低价位"
        elif price < 300:
            processed["price_range"] = "中等价位"
        elif price < 800:
            processed["price_range"] = "中高价位"
        else:
            processed["price_range"] = "高端价位"
    
    # 提取关键特征
    features = ["新款", "热销", "限量", "进口", "纯棉", "真丝", "防水", "透气", "显瘦", "百搭", "时尚", "经典"]
    for feature in features:
        if feature in product_info:
            processed["key_features"].append(feature)
    
    # 使用jieba提取关键词
    keywords = list(jieba.cut(product_info))
    processed["keywords"] = [k for k in keywords if len(k) > 1 and k not in ['，', '。', '、', '的', '是', '和', '与', '适合']]
    
    return processed

def evaluate_title_quality(title: str, product_info: str, target_audience: str) -> dict:
    """评估标题质量，用于决定是否需要二次优化"""
    score = 0
    issues = []
    recommendations = []
    
    # 1. 长度检查 (权重: 20分)
    length = len(title)
    if 15 <= length <= 25:
        score += 20
    elif 12 <= length <= 30:
        score += 15
        if length < 15:
            issues.append("标题过短")
            recommendations.append("增加修饰词或卖点描述")
        else:
            issues.append("标题过长")
            recommendations.append("精简表达，突出核心卖点")
    else:
        score += 5
        issues.append("标题长度不合规")
        recommendations.append("控制在15-25字符间")
    
    # 2. 格式检查 (权重: 15分)
    if '，' in title or ',' in title:
        issues.append("使用了逗号分隔")
        recommendations.append("用空格或连词替代逗号")
    else:
        score += 15
    
    # 3. 受众匹配度检查 (权重: 25分)
    audience_keywords = {
        "年轻女性": ["少女心", "甜美", "仙女", "小清新", "网红", "种草", "心动", "爱了", "可爱", "萌"],
        "中年女性": ["优雅", "知性", "舒适", "百搭", "经典", "品质", "气质", "精致", "温柔"],
        "年轻男性": ["潮流", "酷炫", "科技", "个性", "性能", "专业", "给力", "帅气"],
        "学生": ["学生", "性价比", "实用", "省钱", "必备", "超值", "便宜", "划算"]
    }
    
    target_words = audience_keywords.get(target_audience, [])
    found_keywords = sum(1 for word in target_words if word in title)
    if found_keywords >= 1:
        score += 25
    elif found_keywords == 0:
        score += 10
        issues.append("缺乏受众特色词汇")
        recommendations.append(f"建议融入{target_audience}喜好的词汇")
    
    # 4. 商品信息匹配度 (权重: 20分)
    processed_info = preprocess_product_info(product_info)
    product_elements = [processed_info['product_type'], processed_info['color'], processed_info['season']]
    product_elements = [elem for elem in product_elements if elem]
    
    matched_elements = sum(1 for elem in product_elements if elem in title)
    if matched_elements >= 2:
        score += 20
    elif matched_elements == 1:
        score += 15
    else:
        score += 5
        issues.append("商品信息融入不足")
        recommendations.append("增加商品核心特征描述")
    
    # 5. 吸引力检查 (权重: 20分)
    attractive_words = ["限时", "特惠", "新款", "热销", "爆款", "必入", "推荐", "精选", "优选", "抢购"]
    emotion_symbols = ["【", "】", "🔥", "💕", "✨", "🌸", "⭐", "👑", "💎"]
    
    attractive_count = sum(1 for word in attractive_words if word in title)
    symbol_count = sum(1 for symbol in emotion_symbols if symbol in title)
    
    if attractive_count >= 1 or symbol_count >= 1:
        score += 20
    else:
        score += 10
        issues.append("缺乏吸引力元素")
        recommendations.append("添加促销词汇或情感符号")
    
    # 计算最终评分
    final_score = min(score / 100, 1.0)
    
    return {
        "score": final_score,
        "grade": "优秀" if final_score >= 0.8 else "良好" if final_score >= 0.6 else "一般" if final_score >= 0.4 else "需改进",
        "issues": issues,
        "recommendations": recommendations,
        "need_optimization": final_score < 0.75
    }

def optimize_title_with_feedback(original_title: str, evaluation: dict, product_info: str, style: str, target_audience: str) -> str:
    """基于评估结果优化标题"""
    llm = get_llm_instance()
    
    if llm and llm.__class__.__name__ != 'MockLLM':
        processed_info = preprocess_product_info(product_info)
        audience_profile = get_audience_profile(target_audience)
        
        optimization_prompt = f"""你是标题优化专家，需要根据质量评估结果优化电商标题。

【原标题】
{original_title}

【质量评估结果】
- 当前评分：{evaluation['score']:.2f} ({evaluation['grade']})
- 发现问题：{', '.join(evaluation['issues']) if evaluation['issues'] else '无明显问题'}
- 优化建议：{', '.join(evaluation['recommendations']) if evaluation['recommendations'] else '继续保持'}

【商品信息】
- 商品类型：{processed_info['product_type']}
- 核心信息：{processed_info['original']}
- 目标用户：{target_audience} (偏好词汇：{', '.join(audience_profile['关键词'][:5])})
- 风格要求：{style}

【优化要求】
1. 针对性解决上述质量问题
2. 保持{style}风格特色
3. 长度控制在15-25字符
4. 避免使用逗号分隔
5. 增强{target_audience}群体的吸引力

请输出优化后的标题（只输出标题，不要解释）："""
        
        try:
            optimized_title = llm.invoke(optimization_prompt)
            # 清理输出
            optimized_title = optimized_title.strip().replace('\n', ' ').replace('\r', '')
            
            # 移除可能的前缀
            prefixes = ['优化后标题：', '标题：', '建议：', '答：']
            for prefix in prefixes:
                if optimized_title.startswith(prefix):
                    optimized_title = optimized_title[len(prefix):].strip()
            
            if (optimized_title.startswith('"') and optimized_title.endswith('"')):
                optimized_title = optimized_title[1:-1]
                
            return optimized_title
        except Exception as e:
            print(f"标题优化失败: {e}")
            return original_title
    
    return original_title

def get_audience_profile(target_audience: str) -> dict:
    """获取目标受众画像"""
    profiles = {
        "年轻女性": {
            "年龄": "18-30岁",
            "特点": "追求时尚、个性，注重颜值和社交属性",
            "语言风格": "活泼、可爱、有趣",
            "关键词": ["少女心", "甜美", "仙女", "小清新", "网红同款", "种草", "心动", "爱了"],
            "购买动机": "颜值、潮流、社交分享",
            "价格敏感度": "中等"
        },
        "中年女性": {
            "年龄": "30-50岁",
            "特点": "注重品质和实用性，有一定消费能力",
            "语言风格": "优雅、知性、实用",
            "关键词": ["优雅", "知性", "舒适", "百搭", "经典", "品质", "气质", "精致"],
            "购买动机": "品质、实用性、性价比",
            "价格敏感度": "低"
        },
        "年轻男性": {
            "年龄": "18-35岁",
            "特点": "追求个性和科技感，注重性能",
            "语言风格": "酷炫、专业、直接",
            "关键词": ["潮流", "酷炫", "科技", "个性", "性能", "专业", "给力"],
            "购买动机": "性能、科技感、个性表达",
            "价格敏感度": "中等"
        },
        "学生": {
            "年龄": "16-25岁",
            "特点": "预算有限，注重性价比",
            "语言风格": "年轻、活泼、实惠",
            "关键词": ["学生专享", "性价比", "实用", "省钱", "必备", "超值"],
            "购买动机": "性价比、实用性",
            "价格敏感度": "高"
        },
        "通用": {
            "年龄": "全年龄",
            "特点": "大众化需求",
            "语言风格": "通俗易懂、亲和",
            "关键词": ["精选", "热销", "推荐", "优质", "好评", "值得"],
            "购买动机": "品质、口碑",
            "价格敏感度": "中等"
        }
    }
    return profiles.get(target_audience, profiles["通用"])

@tool
def generate_product_title(product_info: str, style: str = "爆款", target_audience: str = "通用") -> str:
    """
    根据商品信息生成推荐标题
    
    Args:
        product_info: 商品信息，包含类目、属性、价格等
        style: 文案风格，如"爆款"、"简约"、"高端"等
        target_audience: 目标受众，影响标题用词和表达方式
        
    Returns:
        生成的商品标题
    """
    
    llm = get_llm_instance()
    
    # 预处理商品信息
    processed_info = preprocess_product_info(product_info)
    audience_profile = get_audience_profile(target_audience)
    
    # 如果有真实的LLM，使用LLM生成
    if llm and llm.__class__.__name__ != 'MockLLM':
        # 构建增强的prompt
        prompt = f"""你是一位资深电商文案专家，拥有10年+的爆款标题创作经验。

【商品分析】
- 商品类型：{processed_info['product_type'] or '未识别'}
- 核心信息：{processed_info['original']}
- 颜色特征：{processed_info['color'] or '无'}
- 季节属性：{processed_info['season'] or '无'}
- 价格定位：{processed_info['price_range'] or '未知'}
- 关键卖点：{', '.join(processed_info['key_features']) or '待挖掘'}

【目标用户画像】
- 用户群体：{target_audience} ({audience_profile['年龄']})
- 用户特点：{audience_profile['特点']}
- 语言偏好：{audience_profile['语言风格']}
- 购买动机：{audience_profile['购买动机']}
- 价格敏感度：{audience_profile['价格敏感度']}

【文案风格要求】
- 风格定位：{style}
- 字符长度：15-25字符
- 语言风格：符合{target_audience}的表达习惯
- 必须避免：逗号分隔关键词

【创作要求】
1. 从用户痛点出发，突出商品能解决的问题
2. 融入{audience_profile['关键词'][:3]}等符合用户群体的词汇
3. 根据价格定位选择合适的营销策略
4. 确保标题具有点击冲动和购买欲望
5. 符合电商平台标题规范

请基于以上分析，创作一个{style}风格的专业标题："""
        
        try:
            title = llm.invoke(prompt)
            # 清理输出
            title = title.strip().replace('\n', ' ').replace('\r', '')
            
            # 移除可能的前缀
            prefixes = ['标题：', '建议标题：', '推荐标题：', '标题:', '答:', '答：']
            for prefix in prefixes:
                if title.startswith(prefix):
                    title = title[len(prefix):].strip()
            
            # 移除引号
            if (title.startswith('"') and title.endswith('"')) or (title.startswith('"') and title.endswith('"')):
                title = title[1:-1]
            
            # 长度控制
            if len(title) > 30:
                title = title[:28] + "..."
            
            # 质量评估和二次优化
            evaluation = evaluate_title_quality(title, product_info, target_audience)
            
            if evaluation['need_optimization']:
                print(f"标题质量评分: {evaluation['score']:.2f} ({evaluation['grade']}) - 进行二次优化")
                optimized_title = optimize_title_with_feedback(title, evaluation, product_info, style, target_audience)
                
                # 验证优化效果
                new_evaluation = evaluate_title_quality(optimized_title, product_info, target_audience)
                if new_evaluation['score'] > evaluation['score']:
                    print(f"优化成功: {evaluation['score']:.2f} -> {new_evaluation['score']:.2f}")
                    return optimized_title
                else:
                    print("优化效果不佳，使用原标题")
                    return title
            else:
                print(f"标题质量良好: {evaluation['score']:.2f} ({evaluation['grade']})")
                return title
                
        except Exception as e:
            print(f"LLM调用失败: {e}")
            pass
    
    # 回退到规则引擎模式
    # 根据目标受众定义词汇库
    audience_config = {
        "年轻女性": {
            "前缀": ["🌸", "💕", "【少女心】", "【甜美】"],
            "修饰": ["小清新", "仙女范", "甜美", "少女心"],
            "后缀": ["心动必入", "种草了", "爱了爱了"]
        },
        "中年女性": {
            "前缀": ["【优雅】", "【经典】", "🌹"],
            "修饰": ["知性", "优雅", "舒适", "百搭"],
            "后缀": ["品质之选", "气质优选", "精致生活"]
        },
        "年轻男性": {
            "前缀": ["🔥", "【潮流】", "【酷炫】"],
            "修饰": ["潮流", "个性", "酷炫", "时尚"],
            "后缀": ["炸裂推荐", "给力好物", "潮男必备"]
        },
        "学生": {
            "前缀": ["【学生专享】", "💰", "【超值】"],
            "修饰": ["实用", "性价比", "学生款", "校园"],
            "后缀": ["学生必备", "超值好物", "省钱首选"]
        },
        "通用": {
            "前缀": ["【精选】", "⭐", "【推荐】"],
            "修饰": ["优质", "精选", "热销", "推荐"],
            "后缀": ["品质保证", "值得拥有", "好评如潮"]
        }
    }
    
    config = audience_config.get(target_audience, audience_config["通用"])
    
    # 提取商品关键信息
    keywords = list(jieba.cut(product_info))
    keywords = [k for k in keywords if len(k) > 1 and k not in ['，', '。', '、', '的', '是', '和', '与']]
    
    # 识别商品类型
    product_name = ""
    product_types = ["连衣裙", "T恤", "衬衫", "裤子", "裙子", "外套", "鞋子", "包包", "手机", "电脑", "耳机", "口红", "面膜", "护肤品"]
    for ptype in product_types:
        if ptype in product_info:
            product_name = ptype
            break
    
    if not product_name and keywords:
        product_name = keywords[0]
    
    # 提取特征
    features = []
    if "粉色" in product_info:
        features.append("粉色")
    if "夏季" in product_info or "夏天" in product_info:
        features.append("夏季")
    if "新款" in product_info:
        features.append("新款")
    if "129" in product_info:
        features.append("超值价")
    
    # 根据风格生成标题
    if style == "爆款":
        prefix = random.choice(config["前缀"])
        modifier = random.choice(config["修饰"])
        suffix = random.choice(config["后缀"])
        title = f"{prefix}{modifier}{product_name} {' '.join(features[:2])} {suffix}"
    elif style == "简约":
        modifier = random.choice(config["修饰"])
        title = f"{modifier}{product_name} {' '.join(features[:2])}"
    else:  # 高端
        title = f"臻选{product_name} {' '.join(features[:1])} 匠心品质"
    
    # 清理标题
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title


@tool  
def suggest_strategy(product_type: str, target_audience: str = "通用", budget: str = "中等", product_info: str = "") -> str:
    """
    根据商品类型和目标受众推荐营销策略
    
    Args:
        product_type: 商品类型，如"服装"、"数码"、"美妆"等
        target_audience: 目标受众，如"年轻女性"、"中年男性"、"学生"等
        budget: 预算水平，如"低"、"中等"、"高"
        product_info: 商品详细信息，用于个性化建议
        
    Returns:
        推荐的营销策略
    """
    
    llm = get_llm_instance()
    
    # 如果有真实的LLM，使用LLM生成详细策略
    if llm and llm.__class__.__name__ != 'MockLLM':
        # 预处理商品信息
        processed_info = preprocess_product_info(product_info)
        audience_profile = get_audience_profile(target_audience)
        
        # 构建增强的prompt
        prompt = f"""你是一位拥有15年经验的电商营销战略专家，擅长为不同品类和受众制定精准营销策略。

【项目背景分析】
商品详细信息：
- 基础信息：{processed_info['original']}
- 商品类型：{processed_info['product_type'] or product_type}
- 颜色特征：{processed_info['color'] or '无'}
- 季节属性：{processed_info['season'] or '无'}
- 价格定位：{processed_info['price_range']} ({processed_info['price']})
- 核心卖点：{', '.join(processed_info['key_features']) or '需要挖掘'}

【目标用户深度画像】
- 用户群体：{target_audience} ({audience_profile['年龄']})
- 行为特征：{audience_profile['特点']}
- 沟通偏好：{audience_profile['语言风格']}
- 购买驱动：{audience_profile['购买动机']}
- 价格敏感度：{audience_profile['价格敏感度']}
- 常用词汇：{', '.join(audience_profile['关键词'])}

【预算约束】
- 预算级别：{budget}
- 预算特点：{'需要精细化运营，重点ROI' if budget == '低' else '可进行多渠道投放，适度试错' if budget == '中等' else '可全渠道覆盖，品牌化运营'}

【策略制定要求】
基于以上深度分析，请制定一份专业的营销执行方案，包含以下7个维度：

1. **用户洞察与痛点分析** (100字)
   - 深度分析目标用户的核心需求和购买障碍
   - 识别商品能解决的具体问题

2. **渠道组合策略** (120字)
   - 基于用户画像推荐3-4个精准渠道
   - 说明每个渠道的作用和预期效果
   - 考虑预算约束进行优先级排序

3. **内容营销策略** (150字)
   - 具体的内容创作方向和主题
   - 针对不同渠道的内容形式建议
   - 融入用户偏好的话术和表达方式

4. **促销与转化策略** (100字)
   - 结合价格定位设计促销方案
   - 提供具体的优惠策略和时机安排

5. **预算分配与投放策略** (80字)
   - 各渠道的预算比例建议
   - 投放节奏和重点时段安排

6. **执行时间线** (100字)
   - 4-6周的详细执行计划
   - 关键节点和里程碑设置

7. **效果监控与优化** (80字)
   - 关键指标定义和监控方法
   - 优化调整的判断标准

【输出要求】
- 总字数控制在750字左右
- 每个维度都要具体可执行，避免空洞概念
- 紧密结合商品特点和用户画像
- 语言专业但易懂，逻辑清晰

请基于以上分析框架，输出完整的营销策略方案："""
        
        try:
            strategy = llm.invoke(prompt)
            return strategy.strip()
        except Exception as e:
            print(f"营销策略LLM调用失败: {e}")
            pass
    
    # 回退到简化的策略建议
    basic_strategies = {
        "服装": {
            "年轻女性": "建议在小红书和抖音投放，重点展示穿搭效果，配合时尚博主合作",
            "中年女性": "主打品质和实用性，在小红书投放，强调舒适和百搭",
            "学生": "突出性价比和校园时尚，在B站和微信群推广"
        },
        "数码": {
            "年轻男性": "在B站和知乎投放技术测评内容，强调性能参数",
            "学生": "教育优惠政策，学习效率提升，分期付款选项"
        },
        "美妆": {
            "年轻女性": "小红书种草，美妆博主试色，限量款营销",
            "中年女性": "抗老功效宣传，温和配方，品牌信誉背书"
        }
    }
    
    # 获取基础策略
    category_strategies = basic_strategies.get(product_type, basic_strategies["服装"])
    base_strategy = category_strategies.get(target_audience, "针对目标受众进行精准营销推广")
    
    # 根据预算调整
    budget_advice = {
        "低": "建议采用有机流量策略，重点优化商品详情页和用户评价",
        "中等": "适当投放信息流广告，配合达人合作进行推广", 
        "高": "全渠道投放，品牌代言人合作，线下活动配合"
    }.get(budget, "适当投放信息流广告，配合达人合作进行推广")
    
    return f"""📊 **营销策略方案**

🎯 **目标受众**: {target_audience}
💰 **预算水平**: {budget}

📋 **核心策略建议**:
{base_strategy}

💡 **预算策略**:
{budget_advice}

📱 **推荐渠道**: 根据受众特点选择小红书、抖音、B站等平台进行精准投放

⏰ **执行建议**: 
1. 内容准备(1周) → 2. 预热推广(2周) → 3. 正式推广(2周) → 4. 效果优化(1周)

注：使用真实LLM模式可获得更详细的个性化策略方案。"""


@tool
def estimate_ctr(title: str, keywords: List[str] = None) -> Dict[str, Any]:
    """
    估算标题点击率得分，基于关键词覆盖率和标题质量
    
    Args:
        title: 商品标题
        keywords: 核心关键词列表（可选，如果未提供则从标题中自动提取）
        
    Returns:
        包含CTR预估分数和详细分析的字典
    """
    
    # 如果没有提供关键词，从标题中自动提取
    if keywords is None or len(keywords) == 0:
        import jieba
        keywords = [k for k in jieba.cut(title) if len(k) > 1 and k not in ['，', '。', '、', '的', '是', '和', '与', '适合']][:5]
    
    target_keywords = keywords
        
    # 1. 关键词覆盖率计算
    title_lower = title.lower()
    covered_keywords = []
    for keyword in target_keywords:
        if keyword.lower() in title_lower:
            covered_keywords.append(keyword)
    
    coverage_rate = len(covered_keywords) / len(target_keywords) if target_keywords else 0
    
    # 2. 标题长度评分（20-30字符较优）
    title_length = len(title)
    if 20 <= title_length <= 30:
        length_score = 1.0
    elif 15 <= title_length <= 35:
        length_score = 0.8
    else:
        length_score = 0.5
    
    # 3. 特殊符号和表情评分
    emoji_pattern = r'[🔥💥⭐️🎉📱💎]'
    bracket_pattern = r'[【】\[\]（）()]'
    
    has_emoji = len(re.findall(emoji_pattern, title)) > 0
    has_brackets = len(re.findall(bracket_pattern, title)) > 0
    
    symbol_score = 0.7
    if has_emoji:
        symbol_score += 0.15
    if has_brackets:
        symbol_score += 0.15
    symbol_score = min(symbol_score, 1.0)
    
    # 4. 紧急词汇评分
    urgent_words = ['限时', '抢购', '特惠', '新品', '爆款', '热销']
    urgent_count = sum(1 for word in urgent_words if word in title)
    urgent_score = min(urgent_count * 0.2, 0.6)
    
    # 5. 综合CTR评分
    base_score = 0.4  # 基础分
    keyword_weight = 0.3
    length_weight = 0.1  
    symbol_weight = 0.1
    urgent_weight = 0.1
    
    ctr_score = (base_score + 
                coverage_rate * keyword_weight + 
                length_score * length_weight +
                symbol_score * symbol_weight +
                urgent_score * urgent_weight)
    
    ctr_score = min(ctr_score, 1.0)
    ctr_percentage = round(ctr_score * 100, 1)
    
    return {
        "ctr_score": round(ctr_score, 3),
        "ctr_percentage": f"{ctr_percentage}%",
        "coverage_rate": round(coverage_rate, 3),
        "covered_keywords": covered_keywords,
        "length_score": round(length_score, 3),
        "title_length": title_length,
        "has_emoji": has_emoji,
        "has_brackets": has_brackets,
        "urgent_words_count": urgent_count,
        "recommendations": get_optimization_suggestions(coverage_rate, length_score, has_emoji, has_brackets, urgent_count)
    }


def get_optimization_suggestions(coverage_rate: float, length_score: float, 
                               has_emoji: bool, has_brackets: bool, urgent_count: int) -> List[str]:
    """
    根据评分情况提供优化建议
    """
    suggestions = []
    
    if coverage_rate < 0.6:
        suggestions.append("建议增加更多目标关键词以提升搜索匹配度")
    
    if length_score < 0.8:
        suggestions.append("标题长度建议控制在20-30字符之间")
        
    if not has_emoji:
        suggestions.append("可以适当添加表情符号增加标题吸引力")
        
    if not has_brackets:
        suggestions.append("使用【】等括号突出重点信息")
        
    if urgent_count == 0:
        suggestions.append("添加'限时'、'特惠'等紧急词汇提升点击欲望")
        
    if not suggestions:
        suggestions.append("标题质量良好，可考虑A/B测试不同版本")
        
    return suggestions


@tool
def analyze_competitor_title(competitor_title: str, our_keywords: List[str] = None) -> Dict[str, Any]:
    """
    分析竞品标题，提供差异化建议
    
    Args:
        competitor_title: 竞品标题
        our_keywords: 我们的核心关键词（可选，如果未提供则从竞品标题中推断）
        
    Returns:
        竞品分析结果和差异化建议
    """
    
    # 分析竞品标题的关键词
    competitor_keywords = list(jieba.cut(competitor_title))
    competitor_keywords = [k for k in competitor_keywords if len(k) > 1]
    
    # 如果没有提供我们的关键词，从竞品标题中推断相关关键词
    if our_keywords is None or len(our_keywords) == 0:
        # 基于竞品标题推断可能的关键词
        our_keywords = competitor_keywords[:3]  # 使用竞品标题的前3个关键词作为参考
    
    # 找出共同关键词和差异关键词
    common_keywords = list(set(our_keywords) & set(competitor_keywords))
    unique_to_competitor = list(set(competitor_keywords) - set(our_keywords))
    unique_to_us = list(set(our_keywords) - set(competitor_keywords))
    
    # 获取竞品标题CTR评估
    competitor_ctr = estimate_ctr.invoke({
        "title": competitor_title,
        "keywords": competitor_keywords
    })
    
    # 生成差异化建议
    differentiation_suggestions = []
    
    if unique_to_competitor:
        differentiation_suggestions.append(f"竞品强调了：{', '.join(unique_to_competitor[:3])}，我们可以考虑突出其他卖点")
    
    if unique_to_us:
        differentiation_suggestions.append(f"我们的优势关键词：{', '.join(unique_to_us[:3])}，应该重点突出")
    
    if competitor_ctr["ctr_score"] > 0.7:
        differentiation_suggestions.append("竞品标题质量较高，建议学习其标题结构但要突出差异化")
    else:
        differentiation_suggestions.append("竞品标题有优化空间，我们可以在此基础上提升")
    
    return {
        "competitor_title": competitor_title,
        "competitor_ctr_analysis": competitor_ctr,
        "common_keywords": common_keywords,
        "competitor_unique_keywords": unique_to_competitor,
        "our_unique_keywords": unique_to_us,
        "differentiation_suggestions": differentiation_suggestions
    }
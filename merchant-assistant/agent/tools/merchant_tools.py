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


@tool
def generate_product_title(product_info: str, style: str = "爆款") -> str:
    """
    根据商品信息生成推荐标题
    
    Args:
        product_info: 商品信息，包含类目、属性、价格等
        style: 文案风格，如"爆款"、"简约"、"高端"等
        
    Returns:
        生成的商品标题
    """
    
    # 提取商品关键信息
    keywords = list(jieba.cut(product_info))
    keywords = [k for k in keywords if len(k) > 1]
    
    # 定义不同风格的标题模板
    templates = {
        "爆款": [
            "【热销爆款】{product}，{feature}",
            "🔥{product} 限时特惠，{feature}",
            "【新品上市】{product}，{feature}，抢购中！"
        ],
        "简约": [
            "{product} | {feature}",
            "简约{product}，{feature}",
            "{product} - {feature}"
        ],
        "高端": [
            "精选{product}，{feature}",
            "匠心{product}，{feature}",
            "臻品{product}，{feature}"
        ]
    }
    
    # 选择模板并填充
    template = random.choice(templates.get(style, templates["爆款"]))
    
    # 简单的商品信息解析
    product_name = keywords[0] if keywords else "商品"
    features = "品质保证" if len(keywords) < 2 else keywords[-1]
    
    title = template.format(product=product_name, feature=features)
    
    return title


@tool  
def suggest_strategy(product_type: str, target_audience: str = "通用", budget: str = "中等") -> str:
    """
    根据商品类型和目标受众推荐营销策略
    
    Args:
        product_type: 商品类型，如"服装"、"数码"、"美妆"等
        target_audience: 目标受众，如"年轻女性"、"中年男性"、"学生"等
        budget: 预算水平，如"低"、"中等"、"高"
        
    Returns:
        推荐的营销策略
    """
    
    # 基础策略库
    strategies = {
        "服装": {
            "年轻女性": "建议参与抖音话题挑战，使用时尚穿搭、OOTD等标签，配合KOL合作",
            "中年女性": "主打品质和实用性，在小红书投放，强调舒适和百搭",
            "通用": "季节性促销，配合节日活动，强调性价比"
        },
        "数码": {
            "年轻男性": "B站、知乎投放技术测评内容，强调性能参数和性价比对比",
            "学生": "教育优惠政策，学习效率提升，分期付款选项",
            "通用": "新品首发优惠，以旧换新活动，技术创新点突出"
        },
        "美妆": {
            "年轻女性": "小红书种草，美妆博主试色，限量款营销",
            "中年女性": "抗老功效宣传，温和配方，品牌信誉背书",
            "通用": "节日礼盒装，买赠活动，会员专享折扣"
        }
    }
    
    # 获取策略
    category_strategies = strategies.get(product_type, strategies["服装"])
    strategy = category_strategies.get(target_audience, category_strategies["通用"])
    
    # 根据预算调整策略
    budget_adjustments = {
        "低": "建议采用有机流量策略，重点优化商品详情页和用户评价",
        "中等": "适当投放信息流广告，配合达人合作进行推广",
        "高": "全渠道投放，品牌代言人合作，线下活动配合"
    }
    
    budget_advice = budget_adjustments.get(budget, budget_adjustments["中等"])
    
    return f"策略建议：{strategy}。预算策略：{budget_advice}"


@tool
def estimate_ctr(title: str, keywords: List[str], target_keywords: List[str] = None) -> Dict[str, Any]:
    """
    估算标题点击率得分，基于关键词覆盖率和标题质量
    
    Args:
        title: 商品标题
        keywords: 核心关键词列表
        target_keywords: 目标关键词列表（可选）
        
    Returns:
        包含CTR预估分数和详细分析的字典
    """
    
    if target_keywords is None:
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
def analyze_competitor_title(competitor_title: str, our_keywords: List[str]) -> Dict[str, Any]:
    """
    分析竞品标题，提供差异化建议
    
    Args:
        competitor_title: 竞品标题
        our_keywords: 我们的核心关键词
        
    Returns:
        竞品分析结果和差异化建议
    """
    
    # 分析竞品标题的关键词
    competitor_keywords = list(jieba.cut(competitor_title))
    competitor_keywords = [k for k in competitor_keywords if len(k) > 1]
    
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
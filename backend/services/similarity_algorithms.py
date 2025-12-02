"""
相似度算法服务 - 实现多种代码相似度计算算法
"""
import ast
import re
import math
from typing import List, Dict, Tuple, Optional, Set
from collections import Counter
from difflib import SequenceMatcher

from schemas.plagiarism import (
    CodeTransformationType,
    SimilarityAlgorithm,
    DetailedCodeMatch,
)


class SimilarityAlgorithms:
    """相似度算法集合"""

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """
        计算两个字符串的编辑距离（Levenshtein Distance）
        """
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def levenshtein_similarity(code1: str, code2: str) -> float:
        """
        基于编辑距离计算相似度 (0-1)
        """
        if not code1 and not code2:
            return 1.0
        if not code1 or not code2:
            return 0.0

        distance = SimilarityAlgorithms.levenshtein_distance(code1, code2)
        max_len = max(len(code1), len(code2))
        return 1.0 - (distance / max_len)

    @staticmethod
    def tokenize_code(code: str) -> List[str]:
        """
        将代码分词为token列表
        """
        # 移除注释
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'"""[\s\S]*?"""', '', code)
        code = re.sub(r"'''[\s\S]*?'''", '', code)
        
        # 分词：标识符、数字、运算符、标点
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+\.?[0-9]*|[^\s\w]', code)
        return tokens

    @staticmethod
    def cosine_similarity(code1: str, code2: str) -> float:
        """
        基于TF-IDF的余弦相似度计算
        """
        tokens1 = SimilarityAlgorithms.tokenize_code(code1)
        tokens2 = SimilarityAlgorithms.tokenize_code(code2)

        if not tokens1 or not tokens2:
            return 0.0

        # 计算词频
        freq1 = Counter(tokens1)
        freq2 = Counter(tokens2)

        # 获取所有唯一token
        all_tokens = set(freq1.keys()) | set(freq2.keys())

        # 计算向量
        vec1 = [freq1.get(token, 0) for token in all_tokens]
        vec2 = [freq2.get(token, 0) for token in all_tokens]

        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    @staticmethod
    def normalize_code(code: str) -> str:
        """
        标准化代码：移除注释、空白、统一变量名
        """
        # 移除注释
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'"""[\s\S]*?"""', '', code)
        code = re.sub(r"'''[\s\S]*?'''", '', code)
        
        # 移除多余空白
        code = re.sub(r'\s+', ' ', code)
        code = code.strip()
        
        return code

    @staticmethod
    def get_ast_structure(code: str) -> Optional[str]:
        """
        获取代码的AST结构签名
        """
        try:
            tree = ast.parse(code)
            return SimilarityAlgorithms._ast_to_signature(tree)
        except SyntaxError:
            return None

    @staticmethod
    def _ast_to_signature(node: ast.AST) -> str:
        """将AST节点转换为结构签名"""
        parts = [type(node).__name__]
        for child in ast.iter_child_nodes(node):
            parts.append(SimilarityAlgorithms._ast_to_signature(child))
        return f"({','.join(parts)})"

    @staticmethod
    def ast_similarity(code1: str, code2: str) -> float:
        """
        基于AST结构的相似度计算
        """
        sig1 = SimilarityAlgorithms.get_ast_structure(code1)
        sig2 = SimilarityAlgorithms.get_ast_structure(code2)

        if sig1 is None or sig2 is None:
            return 0.0

        return SequenceMatcher(None, sig1, sig2).ratio()

    @staticmethod
    def token_sequence_similarity(code1: str, code2: str) -> float:
        """
        基于Token序列的相似度计算
        """
        tokens1 = SimilarityAlgorithms.tokenize_code(code1)
        tokens2 = SimilarityAlgorithms.tokenize_code(code2)

        if not tokens1 or not tokens2:
            return 0.0

        return SequenceMatcher(None, tokens1, tokens2).ratio()

    @staticmethod
    def extract_identifiers(code: str) -> Dict[str, Set[str]]:
        """
        提取代码中的标识符（变量名、函数名）
        """
        result = {"variables": set(), "functions": set(), "classes": set()}

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    result["functions"].add(node.name)
                elif isinstance(node, ast.ClassDef):
                    result["classes"].add(node.name)
                elif isinstance(node, ast.Name):
                    result["variables"].add(node.id)
                elif isinstance(node, ast.arg):
                    result["variables"].add(node.arg)
        except SyntaxError:
            pass

        return result

    @staticmethod
    def detect_variable_renaming(code1: str, code2: str) -> List[Tuple[str, str]]:
        """
        检测变量重命名
        返回可能的重命名对列表 [(原名, 新名), ...]
        """
        ids1 = SimilarityAlgorithms.extract_identifiers(code1)
        ids2 = SimilarityAlgorithms.extract_identifiers(code2)

        rename_pairs = []

        # 比较变量
        vars1 = ids1["variables"] - {"self", "cls", "True", "False", "None"}
        vars2 = ids2["variables"] - {"self", "cls", "True", "False", "None"}

        # 如果变量数量相近但名称不同，可能是重命名
        if len(vars1) > 0 and len(vars2) > 0:
            common = vars1 & vars2
            only_in_1 = vars1 - vars2
            only_in_2 = vars2 - vars1

            # 如果大部分变量不同但结构相似，可能是重命名
            if len(only_in_1) > 0 and len(only_in_2) > 0:
                # 简单匹配：按出现顺序配对
                for v1, v2 in zip(sorted(only_in_1), sorted(only_in_2)):
                    rename_pairs.append((v1, v2))

        return rename_pairs

    @staticmethod
    def detect_function_renaming(code1: str, code2: str) -> List[Tuple[str, str]]:
        """
        检测函数重命名
        """
        ids1 = SimilarityAlgorithms.extract_identifiers(code1)
        ids2 = SimilarityAlgorithms.extract_identifiers(code2)

        rename_pairs = []

        funcs1 = ids1["functions"]
        funcs2 = ids2["functions"]

        only_in_1 = funcs1 - funcs2
        only_in_2 = funcs2 - funcs1

        if len(only_in_1) > 0 and len(only_in_2) > 0:
            for f1, f2 in zip(sorted(only_in_1), sorted(only_in_2)):
                rename_pairs.append((f1, f2))

        return rename_pairs

    @staticmethod
    def detect_code_transformations(
        code1: str, code2: str
    ) -> List[CodeTransformationType]:
        """
        检测代码变换类型
        """
        transformations = []

        # 检测变量重命名
        var_renames = SimilarityAlgorithms.detect_variable_renaming(code1, code2)
        if var_renames:
            transformations.append(CodeTransformationType.VARIABLE_RENAME)

        # 检测函数重命名
        func_renames = SimilarityAlgorithms.detect_function_renaming(code1, code2)
        if func_renames:
            transformations.append(CodeTransformationType.FUNCTION_RENAME)

        # 检测注释修改
        code1_no_comments = SimilarityAlgorithms.normalize_code(code1)
        code2_no_comments = SimilarityAlgorithms.normalize_code(code2)

        if code1_no_comments == code2_no_comments and code1 != code2:
            transformations.append(CodeTransformationType.COMMENT_MODIFICATION)

        # 检测空白符修改
        code1_no_ws = re.sub(r'\s+', '', code1)
        code2_no_ws = re.sub(r'\s+', '', code2)

        if code1_no_ws == code2_no_ws and code1 != code2:
            transformations.append(CodeTransformationType.WHITESPACE_CHANGE)

        # 检测语句重排序
        try:
            tree1 = ast.parse(code1)
            tree2 = ast.parse(code2)

            # 获取顶层语句类型
            stmts1 = [type(s).__name__ for s in tree1.body]
            stmts2 = [type(s).__name__ for s in tree2.body]

            if sorted(stmts1) == sorted(stmts2) and stmts1 != stmts2:
                transformations.append(CodeTransformationType.REORDER_STATEMENTS)
        except SyntaxError:
            pass

        return transformations

    @staticmethod
    def find_matching_segments(
        code1: str, code2: str, min_lines: int = 3
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int], str, str]]:
        """
        查找匹配的代码段
        返回: [(code1行范围, code2行范围, code1片段, code2片段), ...]
        """
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')

        matches = []
        matcher = SequenceMatcher(None, lines1, lines2)

        for block in matcher.get_matching_blocks():
            if block.size >= min_lines:
                start1, start2, size = block.a, block.b, block.size
                snippet1 = '\n'.join(lines1[start1:start1 + size])
                snippet2 = '\n'.join(lines2[start2:start2 + size])

                matches.append((
                    (start1 + 1, start1 + size),  # 1-based行号
                    (start2 + 1, start2 + size),
                    snippet1,
                    snippet2
                ))

        return matches

    @staticmethod
    def combined_similarity(
        code1: str, code2: str,
        ast_weight: float = 0.4,
        token_weight: float = 0.35,
        text_weight: float = 0.25
    ) -> Tuple[float, Dict[str, float]]:
        """
        综合相似度计算
        返回: (综合相似度, 各算法分数字典)
        """
        scores = {}

        # AST相似度
        scores["ast"] = SimilarityAlgorithms.ast_similarity(code1, code2)

        # Token序列相似度
        scores["token"] = SimilarityAlgorithms.token_sequence_similarity(code1, code2)

        # 余弦相似度
        scores["cosine"] = SimilarityAlgorithms.cosine_similarity(code1, code2)

        # 编辑距离相似度（对标准化后的代码）
        norm1 = SimilarityAlgorithms.normalize_code(code1)
        norm2 = SimilarityAlgorithms.normalize_code(code2)
        scores["levenshtein"] = SimilarityAlgorithms.levenshtein_similarity(norm1, norm2)

        # 综合分数
        combined = (
            scores["ast"] * ast_weight +
            scores["token"] * token_weight +
            (scores["cosine"] + scores["levenshtein"]) / 2 * text_weight
        )

        scores["combined"] = round(combined, 4)

        return combined, scores


# 单例实例
similarity_algorithms = SimilarityAlgorithms()


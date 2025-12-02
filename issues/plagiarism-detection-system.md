# Context
Filename: plagiarism-detection-system.md
Created On: 2025-12-02
Created By: AI Assistant
Associated Protocol: RIPER-5 + Multidimensional + Agent Protocol

# Task Description
实现完整的"查重与原创性分析系统"模块，包含三个主要任务：
- 任务2.3.1：代码相似度检测功能
- 任务2.3.2：批量查重引擎
- 任务2.3.3：原创性分析报告生成

# Project Overview
AI教学助手前端项目，使用 React 19 + TypeScript 前端，FastAPI + Python 后端。
后端已有基础的 plagiarism_service.py 实现 AST 查重，需要增强算法并添加前端可视化。

---

# Analysis (RESEARCH mode)
## 现有代码结构
- 后端: `backend/services/plagiarism_service.py` - 基础AST查重
- 后端: `backend/schemas/plagiarism.py` - 数据模型
- 后端: `backend/api/assignments.py` - API端点
- 前端: `frontend/src/types/api.ts` - 已有 PlagiarismRequest/Response 类型
- 前端: `frontend/src/services/api.ts` - 已有 checkPlagiarism 函数

## 需要新增/增强
- 后端算法：编辑距离、余弦相似度、重命名检测、重构检测
- 后端报告：原创性评分、相似代码定位、改进建议
- 前端组件：批量上传、热力图、关系图、报告展示

# Proposed Solution (INNOVATE mode)
采用纯后端计算方案：
- 后端处理所有相似度算法计算
- 前端专注于可视化展示
- 使用 recharts 实现热力图和关系图

# Implementation Plan (PLAN mode)

## Implementation Checklist

### Phase 1: 后端类型定义增强 (schemas)
1. [ ] 在 `backend/schemas/plagiarism.py` 添加新的数据模型：
   - `SimilarityAlgorithm` 枚举（AST/LEVENSHTEIN/COSINE/COMBINED）
   - `CodeTransformationType` 枚举（变量重命名/函数重命名/代码重构等）
   - `DetailedCodeMatch` 模型（精确行号、列号定位）
   - `SimilarityMatrixEntry` 模型（矩阵单元格数据）
   - `SimilarityMatrix` 模型（完整矩阵）
   - `OriginalityReport` 模型（原创性报告）
   - `BatchAnalysisRequest` 模型
   - `BatchAnalysisResponse` 模型

### Phase 2: 后端算法实现 (services)
2. [ ] 创建 `backend/services/similarity_algorithms.py`：
   - `levenshtein_similarity()` 编辑距离算法
   - `cosine_similarity()` 余弦相似度算法（TF-IDF）
   - `detect_variable_renaming()` 变量重命名检测
   - `detect_code_refactoring()` 代码重构检测

3. [ ] 增强 `backend/services/plagiarism_service.py`：
   - 集成新算法到相似度计算
   - 添加 `generate_similarity_matrix()` 方法
   - 添加 `generate_originality_report()` 方法
   - 添加精确代码位置定位功能

### Phase 3: 后端API端点 (api)
4. [ ] 在 `backend/api/assignments.py` 添加新端点：
   - `POST /plagiarism/batch-analyze` 批量分析
   - `GET /plagiarism/similarity-matrix/{report_id}` 获取矩阵
   - `GET /plagiarism/originality-report/{submission_id}` 获取报告
   - `PUT /plagiarism/settings` 配置阈值

### Phase 4: 前端类型定义
5. [ ] 创建 `frontend/src/types/plagiarism.ts`：
   - 所有查重相关的 TypeScript 类型定义
   - 与后端 schemas 对应

### Phase 5: 前端API服务
6. [ ] 扩展 `frontend/src/services/api.ts`：
   - `batchAnalyzePlagiarism()` 批量分析
   - `getSimilarityMatrix()` 获取矩阵
   - `getOriginalityReport()` 获取报告
   - `updatePlagiarismSettings()` 更新设置

### Phase 6: 前端组件实现
7. [ ] 创建 `frontend/src/components/PlagiarismCheck/` 目录结构
8. [ ] 实现 `BatchUpload.tsx` 批量上传组件
9. [ ] 实现 `SimilarityMatrix.tsx` 热力图组件
10. [ ] 实现 `RelationshipGraph.tsx` 关系图组件
11. [ ] 实现 `SuspiciousList.tsx` 可疑作业列表
12. [ ] 实现 `OriginalityReport.tsx` 原创性报告组件
13. [ ] 实现 `PlagiarismCheck.tsx` 主组件（整合所有子组件）
14. [ ] 创建 `PlagiarismCheck.css` 样式文件
15. [ ] 创建 `index.ts` 导出文件

### Phase 7: 路由和导航集成
16. [ ] 更新 `frontend/src/App.tsx` 添加路由
17. [ ] 更新 `frontend/src/components/layout/Header.tsx` 添加导航

### Phase 8: 组件导出
18. [ ] 更新 `frontend/src/components/index.ts` 导出新组件

# Current Execution Step
> 待开始

# Detailed File Specifications

## 1. backend/schemas/plagiarism.py 新增内容
```python
# 新增枚举
class SimilarityAlgorithm(str, Enum):
    AST = "ast"
    LEVENSHTEIN = "levenshtein"
    COSINE = "cosine"
    COMBINED = "combined"

class CodeTransformationType(str, Enum):
    VARIABLE_RENAME = "variable_rename"
    FUNCTION_RENAME = "function_rename"
    EXTRACT_FUNCTION = "extract_function"
    INLINE_VARIABLE = "inline_variable"
    REORDER_STATEMENTS = "reorder_statements"

# 新增模型
class DetailedCodeMatch(BaseModel):
    source_file: str
    target_file: str
    source_start_line: int
    source_end_line: int
    source_start_col: int
    source_end_col: int
    target_start_line: int
    target_end_line: int
    target_start_col: int
    target_end_col: int
    source_snippet: str
    target_snippet: str
    similarity: float
    algorithm: SimilarityAlgorithm
    transformation_type: Optional[CodeTransformationType]

class SimilarityMatrixEntry(BaseModel):
    student_id_1: str
    student_id_2: str
    student_name_1: str
    student_name_2: str
    similarity_score: float
    algorithm_scores: Dict[str, float]

class SimilarityMatrix(BaseModel):
    report_id: str
    assignment_id: str
    created_at: datetime
    student_ids: List[str]
    student_names: List[str]
    matrix: List[List[float]]
    entries: List[SimilarityMatrixEntry]
    threshold: float

class OriginalityReport(BaseModel):
    report_id: str
    submission_id: str
    student_id: str
    student_name: str
    created_at: datetime
    originality_score: float  # 0-100
    similarity_breakdown: Dict[str, float]
    detailed_matches: List[DetailedCodeMatch]
    similar_submissions: List[str]
    improvement_suggestions: List[str]
    summary: str

class BatchAnalysisRequest(BaseModel):
    assignment_id: str
    submissions: List[dict]  # {student_id, student_name, code}
    similarity_threshold: float = 0.7
    algorithms: List[SimilarityAlgorithm] = [SimilarityAlgorithm.COMBINED]

class BatchAnalysisResponse(BaseModel):
    report_id: str
    assignment_id: str
    created_at: datetime
    total_submissions: int
    flagged_count: int
    similarity_matrix: SimilarityMatrix
    suspicious_pairs: List[SubmissionComparison]
    summary: str
```

## 2. backend/services/similarity_algorithms.py 新建文件
- levenshtein_similarity(code1, code2) -> float
- cosine_similarity_tfidf(code1, code2) -> float
- detect_variable_renaming(code1, code2) -> List[tuple]
- detect_function_renaming(code1, code2) -> List[tuple]
- detect_code_refactoring(code1, code2) -> List[CodeTransformationType]
- normalize_code_for_comparison(code) -> str

## 3. frontend/src/types/plagiarism.ts 新建文件
对应后端所有类型的 TypeScript 定义

## 4. frontend/src/components/PlagiarismCheck/ 组件规格
- BatchUpload: 支持拖拽上传、多文件选择、进度显示
- SimilarityMatrix: 使用 recharts 热力图、支持点击查看详情
- RelationshipGraph: 节点为学生、边为相似度、颜色编码
- SuspiciousList: 表格展示、排序、筛选
- OriginalityReport: 评分仪表盘、代码对比高亮、建议列表

# Task Progress
*（执行阶段填写）*

# Final Review
*（评审阶段填写）*


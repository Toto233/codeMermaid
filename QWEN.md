# Java Mermaid Flowchart Generator - Qwen Code Analysis

## 项目概述

Java Mermaid Flowchart Generator 是一个用于从Java方法生成Mermaid流程图的工具。该工具使用LLM（大语言模型）分析Java源代码，创建可视化的流程图来表示方法的控制流。

### 核心特性
- **Java源码分析**：使用javalang库解析Java 8+源代码
- **LLM集成**：利用OpenAI兼容的API进行智能流程图生成
- **Mermaid图表**：创建标准的Mermaid流程图语法
- **PNG生成**：从Mermaid图表生成PNG图像
- **JavaDoc集成**：将Mermaid图表作为JavaDoc注释插入
- **可配置输出**：通过CLI标志控制生成内容
- **灵活配置**：支持自定义LLM端点和模型

## 项目架构

### 高级组件
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Parser    │────│  Java Extractor  │────│  LLM Client    │
│   (click)       │    │ (javalang AST)   │    │  (OpenAI API)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌──────────────────┐              │
         └──────────────│  Output Manager  │──────────────┘
                        │  (Conditional)   │
                        └──────────────────┘
                                 │
                        ┌──────────────────┐
                        │  File Writer     │
                        │  (Comments/PNG)  │
                        └──────────────────┘
```

### 核心类

#### 1. FlowchartGenerator (主入口点)
- **目的**：协调LLM驱动的流程图生成过程
- **职责**：
  - 协调解析、LLM调用和条件输出
  - 处理错误传播
  - 根据CLI标志管理输出控制

#### 2. JavaCodeExtractor
- **目的**：使用javalang提取Java方法上下文供LLM分析
- **关键方法**：
  - `extract_method_context(filepath: str, class_name: str, method_name: str) -> JavaCodeContext`
  - `get_method_signature(method: javalang.tree.MethodDeclaration) -> str`
  - `get_method_body_with_context(method: javalang.tree.MethodDeclaration) -> str`
  - `parse_java_file(filepath: str) -> javalang.tree.CompilationUnit`

#### 3. LLMClient
- **目的**：与OpenAI兼容的API接口用于Mermaid生成
- **关键方法**：
  - `generate_flowchart(code_context: CodeContext, prompt_template: str) -> str`
  - `validate_mermaid_syntax(mermaid_code: str) -> bool`
  - `handle_api_errors(error: Exception) -> str`

#### 4. OutputManager
- **目的**：根据CLI标志控制生成内容
- **关键方法**：
  - `should_generate_comments() -> bool`
  - `should_generate_images() -> bool`
  - `apply_output_config(flags: Dict[str, bool])`

#### 5. FileWriter
- **目的**：有条件地处理文件操作
- **关键方法**：
  - `write_comments_if_enabled(comments: str, target_file: str)`
  - `write_png_if_enabled(mermaid_code: str, output_path: str)`
  - `cleanup_on_error()`

## 数据流

### 1. 输入处理
```python
# 带输出标志的CLI输入
class_name, method_name, flags = parse_cli_args()
source_file = locate_java_file()
```

### 2. Java解析
```python
# 使用javalang进行Java AST提取
tree = javalang.parse.parse(source_code)
class_node = find_java_class(tree, class_name)
method_node = find_java_method(class_node, method_name)
```

### 3. LLM上下文准备
```python
# 用于LLM的Java方法上下文
context = {
    'class_name': class_name,
    'method_name': method_name,
    'signature': extract_java_signature(method_node),
    'body': extract_java_body(method_node),
    'imports': get_java_imports(tree),
    'fields': get_class_fields(class_node)
}
```

### 4. LLM Mermaid生成
```python
# OpenAI API调用
prompt = build_llm_prompt(context)
mermaid_code = llm_client.generate_flowchart(prompt)
```

### 5. 条件输出
```python
# 根据标志控制输出
if output_manager.should_generate_comments():
    write_java_comments(mermaid_code, target_file)

if output_manager.should_generate_images():
    render_mermaid_to_png(mermaid_code, output_path)
```

## Java特定的LLM提示工程

### Java方法上下文模板
```python
JAVA_METHOD_PROMPT = """
分析这个Java方法并生成Mermaid流程图。

类: {class_name}
方法: {method_name}
签名: {method_signature}
返回类型: {return_type}
参数: {parameters}

源代码:
{method_body}

要包含的重要Java结构:
1. if/else if/else 语句
2. for/while/do-while 循环
3. try/catch/finally 块
4. switch 语句
5. return 语句
6. 异常处理路径
7. 方法调用（显示为处理框）

生成一个显示所有可能执行路径的流程图TD图。
使用适当的形状:
- 矩形 [Process] 用于操作
- 菱形 {Decision} 用于条件
- 圆形 ((Start/End)) 用于流程控制
- 平行四边形 [/Input/Output\] 用于I/O操作

包含Java特定元素:
- 异常处理路径
- 流操作 (.map(), .filter(), 等)
- Lambda表达式
- 泛型类型流
- 资源管理（try-with-resources）

只返回有效的Mermaid语法，不要解释。
"""
```

## 错误处理策略

### 1. 解析错误
- **语法错误**：捕获并报告行号
- **导入错误**：优雅地处理缺失依赖
- **文件未找到错误**：提供有用的错误消息

### 2. AST分析错误
- **属性错误**：处理缺失的AST节点
- **值错误**：验证方法/类名称
- **类型错误**：确保正确的AST节点类型

### 3. 渲染错误
- **Mermaid错误**：处理Mermaid语法问题
- **图像错误**：管理PNG生成失败
- **权限错误**：处理文件系统问题

## 扩展点

### 1. 新节点类型
- 为新AST节点添加访问者模式
- 用新形状扩展MermaidBuilder
- 为特定模式实现自定义渲染

### 2. 输出格式
- SVG生成
- PDF导出
- 交互式HTML

### 3. 自定义样式
- 主题配置
- 自定义节点样式
- 颜色方案

## 测试策略

### 1. 单元测试
- AST解析准确性
- 流提取正确性
- Mermaid语法验证
- PNG生成质量

### 2. 集成测试
- 端到端工作流
- CLI参数处理
- 文件I/O操作
- 错误场景

### 3. 性能测试
- 大方法解析
- 内存使用监控
- 时间基准测试

## 部署

### 1. 包结构
- 带依赖的单个可执行文件
- 跨平台兼容性
- 虚拟环境支持

### 2. 分发
- PyPI包
- Docker容器
- 独立可执行文件

## 功能需求

### FR1: Java类和方法识别
- 工具应接受Java类和方法名称作为输入
- CLI参数解析Java类名和方法名
- 验证Java类在指定.java文件中存在
- 验证方法在Java类中存在
- 支持嵌套类和接口
- 输入验证的错误处理

### FR2: Java源代码解析
- 工具应使用javalang库解析Java源代码
- 支持Java 8+语言特性，包括泛型、流、Lambda
- 处理Java注解和修饰符
- 处理try-with-resources和异常处理
- 准确提取方法签名和主体
- 支持包和导入语句

### FR3: Java LLM分析
- 工具应使用LLM（OpenAI兼容）分析Java方法逻辑
- 向LLM API发送Java方法上下文
- 从LLM接收有效的Mermaid流程图语法
- 处理LLM API速率限制和超时
- 验证LLM响应的Mermaid语法
- 支持可配置的LLM端点

## 非功能需求

### NFR1: 性能（Python 3.6）
- 工具应在Python 3.6上高效处理Java方法
- 解析1000行Java方法应在2秒内完成
- LLM API调用超时：最大30秒
- Java解析+LLM的内存使用量低于150MB
- 支持带速率限制的批处理

### NFR2: 可靠性
- 工具应优雅地处理错误
- 对格式错误的Java代码零崩溃
- 带Java行号的信息性错误消息
- LLM API不可用时的优雅回退
- 用于调试的综合日志记录

### NFR3: 兼容性
- 工具应在具有Python 3.6的跨平台上工作
- 支持Windows、macOS和Linux与Python 3.6+
- Java 8+兼容性
- 无平台特定依赖
- 跨平台文件路径处理

## 用户故事

### US1: Java基本流程图生成
**作为一个** Java开发者
**我想要** 为简单Java方法生成流程图
**以便** 我可以可视化控制流

**场景**: 带有if-else的简单Java方法
- 给定一个带有条件逻辑的Java方法
- 当我使用类和方法名称运行工具时
- 然后我得到PNG流程图和带有Mermaid图表的JavaDoc注释

### US2: Java复杂方法处理
**作为一个** 高级Java开发者
**我想要** 为复杂Java方法生成流程图
**以便** 我可以理解和记录复杂的逻辑

**场景**: 嵌套循环和异常处理
- 给定一个带有try-catch和循环的Java方法
- 当我使用LLM处理方法时
- 然后我得到一个显示所有异常路径的可读流程图

### US3: 输出控制
**作为一个** DevOps工程师
**我想要** 控制生成的内容
**以便** 我可以高效地集成到CI/CD管道中

**场景**: 仅生成PNG图像
- 给定一个Java源文件
- 当我使用`--doc-off`标志时
- 然后只生成PNG图像，不生成JavaDoc注释

### US4: 内部LLM集成
**作为一个** 企业开发者
**我想要** 使用我们的内部LLM服务
**以便** 数据保持在我们的网络内

**场景**: 自定义LLM端点
- 给定一个内部OpenAI兼容的API
- 当我使用自定义端点配置工具时
- 然后它使用我们的内部LLM进行Mermaid生成

## CLI标志规范

### 标志定义
```
--pic-off           禁用PNG图像生成
--doc-off           禁用JavaDoc注释插入
--comments-off      禁用所有注释生成
--output-dir DIR    指定自定义输出目录
--api-endpoint URL  自定义LLM API端点
--model MODEL       要使用的LLM模型
--config FILE       从文件加载配置
--verbose           启用详细日志记录
--dry-run           显示将生成的内容而不进行更改
```

### 使用示例
```bash
# 生成PNG和JavaDoc注释
java-mermaid MyClass myMethod MyFile.java

# 仅生成PNG图像
java-mermaid MyClass myMethod MyFile.java --doc-off

# 仅生成JavaDoc注释
java-mermaid MyClass myMethod MyFile.java --pic-off

# 使用自定义LLM端点
java-mermaid MyClass myMethod MyFile.java --api-endpoint https://internal-llm.local

# 指定输出目录
java-mermaid MyClass myMethod MyFile.java --output-dir ./docs/flowcharts/
```

## 配置需求

### CR1: LLM配置
- **需求**: 可配置的LLM设置
- **选项**: API端点、模型、超时、重试
- **默认**: OpenAI GPT-3.5-turbo

### CR2: 输出控制
- **需求**: 可配置的输出生成
- **选项**: 启用/禁用PNG、JavaDoc、注释
- **默认**: 生成PNG和JavaDoc

### CR3: 图像设置
- **需求**: 可配置的PNG生成
- **选项**: 分辨率、主题、字体大小
- **默认**: 中等分辨率，默认主题

### CR4: Java处理
- **需求**: 可配置的Java解析
- **选项**: 编码、类路径、源版本
- **默认**: UTF-8编码，Java 8+

## 验证标准

### V1: Java输入验证
- [ ] 使用javalang的有效的Java语法
- [ ] 现有的Java类和方法名称
- [ ] 可读的.java源文件
- [ ] 正确的文件权限

### V2: LLM输出验证
- [ ] 来自LLM的有效Mermaid语法
- [ ] 完整的控制流覆盖
- [ ] 可读的PNG图像
- [ ] 正确的JavaDoc格式

### V3: 标志处理
- [ ] 正确的标志解析
- [ ] 正确的输出控制
- [ ] 有用的错误消息
- [ ] 综合CLI帮助

### V4: 性能
- [ ] 满足Python 3.6的时间要求
- [ ] LLM超时处理
- [ ] 内存使用在限制内
- [ ] 高效的资源使用

## 实现细节

### CLI参数解析 (cli/arg_parser.py)
- 使用argparse库处理命令行参数
- 支持输出控制标志（--pic-off, --doc-off, --comments-off）
- 支持LLM配置（--api-key, --api-endpoint, --model）
- 支持配置和调试（--config, --verbose, --dry-run）
- 参数验证（文件存在性、输出目录检查）

### Java代码提取 (extractors/java_code_extractor.py)
- 使用javalang库解析Java AST
- 提取方法上下文信息（签名、主体、参数等）
- 获取类字段和导入语句
- 支持注解和修饰符
- 提供方法体提取功能

### LLM客户端 (clients/llm_client.py)
- 与OpenAI兼容的API接口
- 构建详细的Java方法上下文提示
- 处理API调用、重试和速率限制
- 验证Mermaid语法
- 清理LLM响应中的Markdown格式

### 流程图生成器 (core/flowchart_generator.py)
- 协调整个流程图生成工作流
- 验证输入参数
- 调用Java提取器和LLM客户端
- 根据配置标志生成输出
- 处理错误传播

### 输出管理器 (core/output_manager.py)
- 根据CLI标志控制输出生成
- 提供检查方法是否应生成PNG、注释、JavaDoc
- 应用配置标志

### 文件写入器 (core/file_writer.py)
- 生成PNG图像（使用mermaid_cli_png_generator）
- 将Mermaid图表作为注释插入Java源文件
- 支持JavaDoc和普通注释格式
- 处理文件系统操作

### Mermaid CLI PNG生成器 (core/mermaid_cli_png_generator.py)
- 使用Mermaid CLI创建高质量流程图图像
- 使用Selenium进行浏览器渲染作为备选方案
- 保留HTML调试文件以诊断渲染问题
- 创建可视化流程图

## 配置和环境

### 配置文件
```json
{
  "api_key": "your-api-key",
  "api_endpoint": "https://api.openai.com/v1",
  "model": "gpt-3.5-turbo",
  "timeout": 30,
  "max_retries": 3,
  "output_dir": "./mermaid-output/",
  "generate_png": true,
  "generate_comments": true,
  "generate_javadoc": true,
  "theme": "default",
  "width": 1200,
  "height": 800
}
```

### 环境变量
| 变量 | 描述 |
|------|------|
| `JAVA_MERMAID_API_KEY` | LLM服务的API密钥 |
| `JAVA_MERMAID_API_ENDPOINT` | 自定义API端点 |
| `JAVA_MERMAID_MODEL` | LLM模型名称 |
| `JAVA_MERMAID_TIMEOUT` | 请求超时（秒） |
| `JAVA_MERMAID_OUTPUT_DIR` | 默认输出目录 |
| `OPENAI_API_KEY` | 标准OpenAI API密钥 |

## 支持的Java特性

### 语言结构
- **控制流**: if/else, switch, 循环 (for, while, do-while)
- **异常处理**: try/catch/finally 块
- **方法调用**: 包括方法链和Lambda表达式
- **流**: Java 8+ Stream API 操作
- **泛型**: 类型参数和泛型方法
- **注解**: 方法和参数注解
- **修饰符**: public, private, protected, static, final等

### 代码元素
- 方法签名和参数
- 返回类型和值
- 局部变量和赋值
- 异常处理路径
- 资源管理 (try-with-resources)
- 线程同步
- I/O操作

## 输出格式

### PNG图像
- 可视化流程图表示
- 方法签名作为标题
- 颜色编码节点（开始/结束、处理、决策）
- 箭头连接显示流向

### JavaDoc注释
插入方法上方作为：
```java
/**
 * Method flowchart visualization.
 *
 * @mermaid
 * ```mermaid
 * flowchart TD
 *     A[Start] --> B{Decision}
 *     B -->|True| C[Process]
 *     C --> D[End]
 *     B -->|False| D
 * ```
 */
public void myMethod() {
    // method implementation
}
```

## 故障排除

### 常见问题

#### 需要API密钥
```
Error: API key is required
```
**解决方案**: 设置`OPENAI_API_KEY`环境变量或使用`--api-key`标志。

#### Java文件未找到
```
Error: Java file 'MyFile.java' does not exist
```
**解决方案**: 检查文件路径并确保文件存在。

#### 类未找到
```
Error: Class 'MyClass' not found. Available classes: [ActualClass1, ActualClass2]
```
**解决方案**: 使用Java文件中的确切类名。

#### 方法未找到
```
Error: Method 'myMethod' not found in class 'MyClass'
```
**解决方案**: 检查方法名称拼写并确保方法在类中存在。

### 调试PNG生成问题

当PNG生成失败时，系统会生成HTML调试文件，可用于诊断问题：

1. 查看输出目录中的`*_debug.html`文件
2. 将HTML文件复制到Windows环境
3. 用浏览器打开HTML文件查看Mermaid图表渲染情况
4. 检查浏览器控制台错误信息
5. 验证Mermaid语法是否正确

这种方法可以帮助识别：
- Mermaid语法错误
- 字符编码问题
- 浏览器兼容性问题
- 渲染引擎问题

## 性能提示

- **大方法**: 考虑拆分非常大的方法（>1000行）
- **API限制**: 使用`--dry-run`在处理多个文件之前进行测试
- **PNG生成**: 禁用PNG生成（`--pic-off`）以加快处理速度
- **缓存**: 结果未缓存；考虑对重复处理进行手动缓存

## 开发

### 运行测试
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=java_mermaid --cov-report=html

# 运行特定测试文件
pytest tests/test_java_code_extractor.py
```

### 贡献
1. Fork仓库
2. 创建功能分支
3. 为新功能添加测试
4. 确保所有测试通过
5. 提交拉取请求

### 开发设置
```bash
git clone https://github.com/java-mermaid/flowchart-generator.git
cd flowchart-generator
python -m venv venv
source venv/bin/activate  # 在Windows上: venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

## 开发环境说明

开发环境是在WSL (Windows Subsystem for Linux) 中的Linux系统。由于WSL环境的限制，无法直接在开发环境中进行浏览器展示或GUI操作。

对于需要浏览器展示或GUI操作的测试，请编写测试程序并提供明确的调用说明，由开发者在外部Windows环境中运行测试。

请勿在开发环境中尝试需要浏览器或GUI的操作，以避免不必要的错误和资源消耗。
# 优化报告

## 优化内容

- 优化了 `_calculate_quality_score` 方法，考虑了更多因素
- 优化了 `_calculate_mechanical_properties` 方法，使用了更复杂的计算逻辑
- 更新了 `generate_report` 方法，添加了力学性能相关的信息
- 更新了 `plot_results` 方法，添加了力学性能相关的图表
- 更新了 `cli.py` 中的 `optimize` 命令，确保它使用更新后的优化器方法
- 修复了代码质量问题

## 使用方法

运行以下命令来测试优化功能：

```bash
# 首先创建一个测试文件
echo '"""Test FreeCAD document for optimization demo"""' > examples/test_model.FCStd

# 运行优化命令
python -m sw_helper.cli optimize examples/test_model.FCStd -p Fillet_Radius -r 2 15 --steps 3 --step-mode linear --cad mock --plot --report --output-dir ./test_output

# 检查结果
ls -la test_output/

# 查看报告
cat test_output/optimization_report.md

# 清理
rm -rf test_output/ examples/test_model.FCStd
```

## 优化结果

优化结果将包含以下内容：

1. 优化过程的详细日志
2. 结果表格，显示每一次迭代的参数值、质量分数、许用应力、安全系数和耗时
3. 最佳结果的可视化图表
4. 详细的优化报告

## 注意事项

- 使用 `--cad mock` 选项可以在没有安装 FreeCAD 的情况下进行测试
- 使用 `--output-dir` 选项可以指定输出目录
- 使用 `--plot` 选项可以生成可视化图表
- 使用 `--report` 选项可以生成详细的优化报告

"""
SolidWorks VBA宏生成模块

提供SolidWorks VBA宏代码生成功能，
支持一键导出、参数化建模等自动化功能。
"""

from pathlib import Path
from typing import Optional


class SolidWorksMacroGenerator:
    """SolidWorks VBA宏生成器
    
    生成可在SolidWorks中运行的VBA宏代码，
    实现自动化导出、参数修改等功能。
    """
    
    def __init__(self):
        """初始化宏生成器"""
        self.template_dir = Path(__file__).parent / "templates"
    
    def generate_export_macro(
        self,
        output_path: str,
        export_format: str = "STEP",
        call_cli: bool = True,
        cli_path: str = "cae-cli"
    ) -> str:
        """生成导出宏代码
        
        Args:
            output_path: 导出文件路径
            export_format: 导出格式 (STEP, STL, IGES)
            call_cli: 是否调用CLI进行分析
            cli_path: CLI命令路径
            
        Returns:
            str: VBA宏代码
        """
        format_map = {
            "STEP": "swExportStep",
            "STL": "swExportSTL",
            "IGES": "swExportIGES"
        }
        
        export_func = format_map.get(export_format.upper(), "swExportStep")
        
        cli_call = f'Shell "{cli_path} analyze "" & outputPath & """ --material Q235"' if call_cli else ""
        
        macro_code = f'''Option Explicit

'======================================
' CAE-CLI SolidWorks导出宏
' 自动导出模型并调用CLI进行分析
'======================================

Dim swApp As Object
Dim swModel As Object
Dim swPart As Object
Dim boolstatus As Boolean
Dim outputPath As String

Sub Main()
    ' 连接SolidWorks
    Set swApp = Application.SldWorks
    
    ' 获取当前活动文档
    Set swModel = swApp.ActiveDoc
    If swModel Is Nothing Then
        MsgBox "请先打开一个零件或装配体文件", vbCritical
        Exit Sub
    End If
    
    ' 设置输出路径
    outputPath = "{output_path}"
    
    ' 导出文件
    boolstatus = swModel.Extension.SaveAs(outputPath, swSaveAsCurrent, swSaveAsOptions_Silent, Nothing)
    
    If boolstatus Then
        MsgBox "导出成功: " & outputPath, vbInformation
    Else
        MsgBox "导出失败", vbCritical
        Exit Sub
    End If
    
    ' 调用CLI进行分析
    {cli_call}
    
    MsgBox "完成!", vbInformation
End Sub
'''
        return macro_code
    
    def generate_parameter_macro(self) -> str:
        """生成参数修改宏代码
        
        Returns:
            str: VBA宏代码
        """
        macro_code = '''Option Explicit

'======================================
' CAE-CLI 参数修改宏
' 批量修改模型参数
'======================================

Dim swApp As Object
Dim swModel As Object
Dim swPart As Object

Sub Main()
    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc
    
    If swModel Is Nothing Then
        MsgBox "请先打开一个零件文件", vbCritical
        Exit Sub
    End If
    
    ' 获取零件对象
    Set swPart = swModel
    
    ' 示例: 修改尺寸参数
    ' 具体参数名称需要根据实际模型确定
    Dim paramName As String
    Dim paramValue As Double
    
    paramName = "D1@草图1"  ' 根据实际调整
    paramValue = 100        ' 新值 (mm)
    
    ' 修改参数
    Dim swDim As Object
    Set swDim = swPart.Parameter(paramName)
    
    If Not swDim Is Nothing Then
        swDim.SystemValue = paramValue / 1000  ' 转换为米
        swPart.EditRebuild3
        MsgBox "参数已更新: " & paramName & " = " & paramValue & " mm", vbInformation
    Else
        MsgBox "未找到参数: " & paramName, vbWarning
    End If
End Sub
'''
        return macro_code
    
    def generate_full_integration_macro(self, cli_command: str = "cae-cli") -> str:
        """生成完整集成宏代码
        
        包含:
        - 参数修改
        - 模型重建
        - STEP导出
        - CLI分析调用
        
        Args:
            cli_command: CLI命令
            
        Returns:
            str: VBA宏代码
        """
        macro_code = f'''Option Explicit

'======================================
' CAE-CLI 完整集成宏
' 一键完成:参数修改→重建→导出→分析
'======================================

Dim swApp As Object
Dim swModel As Object
Dim swPart As Object
Dim outputPath As String

Sub Main()
    ' 连接SolidWorks
    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc
    
    If swModel Is Nothing Then
        MsgBox "请先打开一个零件文件", vbCritical
        Exit Sub
    End If
    
    Set swPart = swModel
    
    '========== 第1步: 修改参数 ==========
    Dim params As Object
    Set params = GetParams()
    
    Dim param As Object
    For Each param In params
        param.Value = param.TargetValue
        Debug.Print "已设置: " & param.Name & " = " & param.TargetValue
    Next
    
    '========== 第2步: 重建模型 ==========
    swPart.EditRebuild3
    Debug.Print "模型已重建"
    
    '========== 第3步: 导出STEP ==========
    outputPath = GetOutputPath()
    Dim boolstatus As Boolean
    boolstatus = swModel.Extension.SaveAs(outputPath, swSaveAsCurrent, swSaveAsOptions_Silent, Nothing)
    
    If boolstatus Then
        Debug.Print "已导出: " & outputPath
    Else
        MsgBox "导出失败", vbCritical
        Exit Sub
    End If
    
    '========== 第4步: 调用CLI分析 ==========
    Dim shellCmd As String
    shellCmd = "{cli_command} analyze """ & outputPath & """ --material Q235"
    
    Debug.Print "执行命令: " & shellCmd
    Shell shellCmd, vbNormalFocus
    
    '========== 第5步: 显示报告 ==========
    MsgBox "分析完成! 请查看CLI输出.", vbInformation
End Sub

Function GetParams() As Object
    ' 返回需要修改的参数列表
    ' 这里需要根据实际模型配置
    Set GetParams = CreateObject("Scripting.Dictionary")
End Function

Function GetOutputPath() As String
    ' 获取输出路径
    Dim modelName As String
    modelName = swModel.GetTitle
    
    ' 移除文件扩展名
    If InStr(modelName, ".") > 0 Then
        modelName = Left(modelName, InStr(modelName, ".") - 1)
    End If
    
    ' 生成输出路径
    Dim outputDir As String
    outputDir = swApp.GetUserDocFolder
    
    GetOutputPath = outputDir & "\\" & modelName & ".step"
End Function
'''
        return macro_code
    
    def save_macro(self, macro_code: str, output_file: str) -> bool:
        """保存宏代码到文件
        
        Args:
            macro_code: VBA宏代码
            output_file: 输出文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(macro_code, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"保存宏文件失败: {e}")
            return False

"""
SolidWorks VBA宏导出模块
生成可在SolidWorks中运行的VBA宏代码
"""

from pathlib import Path


class SolidWorksMacroGenerator:
    """SolidWorks宏生成器"""

    @staticmethod
    def generate_export_macro(
        output_path: str,
        export_format: str = "STEP",
        call_cli: bool = True,
        cli_path: str = "cae-cli",
    ) -> str:
        """生成导出宏代码

        Args:
            output_path: 导出文件路径
            export_format: 导出格式 (STEP, STL, IGES)
            call_cli: 是否调用CLI分析
            cli_path: CLI命令路径

        Returns:
            VBA宏代码
        """

        format_map = {
            "STEP": ("ExportSTEP", ".step"),
            "STL": ("ExportSTL", ".stl"),
            "IGES": ("ExportIGES", ".iges"),
            "PDF": ("ExportPDF", ".pdf"),
        }

        export_func, ext = format_map.get(export_format, ("ExportSTEP", ".step"))

        macro_code = f'''Attribute VB_Name = "CAE_Export"
' CAE-CLI集成宏
' 自动生成，用于导出模型并调用CLI分析

Sub ExportAndAnalyze()
    Dim swApp As Object
    Dim Part As Object
    Dim boolstatus As Boolean
    Dim longstatus As Long, longwarnings As Long
    Dim filePath As String
    Dim exportPath As String
    
    ' 获取SolidWorks应用
    Set swApp = Application.SldWorks
    Set Part = swApp.ActiveDoc
    
    ' 检查是否有打开的文档
    If Part Is Nothing Then
        MsgBox "请先打开一个模型!", vbExclamation, "CAE-CLI"
        Exit Sub
    End If
    
    ' 获取当前文件路径
    filePath = Part.GetPathName
    If filePath = "" Then
        MsgBox "请先保存模型!", vbExclamation, "CAE-CLI"
        Exit Sub
    End If
    
    ' 设置导出路径
    exportPath = "{output_path}"
    If exportPath = "" Then
        exportPath = Left(filePath, InStrRev(filePath, ".") - 1) & "{ext}"
    End If
    
    ' 导出模型
    On Error Resume Next
    
    Select Case "{export_format}"
        Case "STEP"
            longstatus = Part.SaveAs3(exportPath, 0, 2)
        Case "STL"
            ' STL导出设置
            Dim swStlExport As Object
            Set swStlExport = Part.Extension.GetSTLExporter
            If Not swStlExport Is Nothing Then
                swStlExport.ExportBinary = False
                swStlExport.ExportPath = exportPath
                swStlExport.Save
            End If
        Case "IGES"
            longstatus = Part.SaveAs3(exportPath, 0, 2)
        Case Else
            longstatus = Part.SaveAs3(exportPath, 0, 2)
    End Select
    
    If Err.Number <> 0 Then
        MsgBox "导出失败: " & Err.Description, vbCritical, "CAE-CLI"
        Exit Sub
    End If
    
    On Error GoTo 0
    
    ' 显示导出成功
    MsgBox "模型已导出到:" & vbCrLf & exportPath, vbInformation, "CAE-CLI"
    
    {"Call CLI分析" if call_cli else "'CLI分析已禁用"}
    {"Dim shell As Object" if call_cli else ""}
    {'Set shell = CreateObject("WScript.Shell")' if call_cli else ""}
    {"Dim cliCommand As String" if call_cli else ""}
    {'cliCommand = "{cli_path} parse """ & exportPath & """ --verbose"' if call_cli else ""}
    {"shell.Run cliCommand, 1, False" if call_cli else ""}
    {"Set shell = Nothing" if call_cli else ""}
    
End Sub

Sub ExportWithPrompt()
    ' 带用户交互的导出
    Dim exportPath As String
    exportPath = InputBox("请输入导出路径:", "CAE-CLI导出", "C:\\Temp\\model.step")
    
    If exportPath <> "" Then
        Call ExportAndAnalyze
    End If
End Sub
'''
        return macro_code

    @staticmethod
    def generate_parameter_macro() -> str:
        """生成参数修改宏"""

        macro_code = """Attribute VB_Name = "CAE_Parametric"
' CAE-CLI参数化宏
' 用于修改参数并重建模型

Sub ModifyParameters()
    Dim swApp As Object
    Dim Part As Object
    Dim boolstatus As Boolean
    
    ' 获取SolidWorks应用
    Set swApp = Application.SldWorks
    Set Part = swApp.ActiveDoc
    
    If Part Is Nothing Then
        MsgBox "请先打开一个模型!", vbExclamation, "CAE-CLI"
        Exit Sub
    End If
    
    ' 获取自定义属性
    Dim custProp As Object
    Set custProp = Part.Extension.CustomPropertyManager("")
    
    ' 显示当前参数
    Dim paramList As String
    paramList = "当前可修改参数:" & vbCrLf & vbCrLf
    
    ' 这里可以读取特定的尺寸参数
    Dim dimNames As Variant
    dimNames = Array("Length", "Width", "Height", "Fillet_R")
    
    Dim i As Integer
    For i = LBound(dimNames) To UBound(dimNames)
        Dim val As String
        val = ""
        On Error Resume Next
        custProp.Get4 dimNames(i), False, val, val
        If val <> "" Then
            paramList = paramList & dimNames(i) & " = " & val & vbCrLf
        End If
        On Error GoTo 0
    Next i
    
    MsgBox paramList, vbInformation, "CAE-CLI参数"
    
End Sub

Sub UpdateDimension(dimensionName As String, newValue As Double)
    ' 更新指定尺寸
    Dim swApp As Object
    Dim Part As Object
    
    Set swApp = Application.SldWorks
    Set Part = swApp.ActiveDoc
    
    If Part Is Nothing Then Exit Sub
    
    ' 查找并更新尺寸
    Dim swDim As Object
    Set swDim = Part.Parameter(dimensionName)
    
    If Not swDim Is Nothing Then
        swDim.SystemValue = newValue / 1000  ' 转换为米
        Part.EditRebuild3
        MsgBox "尺寸已更新: " & dimensionName & " = " & newValue & " mm", vbInformation, "CAE-CLI"
    Else
        MsgBox "未找到尺寸: " & dimensionName, vbExclamation, "CAE-CLI"
    End If
End Sub

Sub BatchUpdate()
    ' 批量更新参数示例
    Call UpdateDimension("Length", 120)
    Call UpdateDimension("Fillet_R", 8)
    
    ' 导出并分析
    Call ExportAndAnalyze
End Sub
"""
        return macro_code

    @staticmethod
    def generate_full_integration_macro(cli_command: str = "cae-cli") -> str:
        """生成完整的集成宏"""

        macro_code = f'''Attribute VB_Name = "CAE_FullIntegration"
' CAE-CLI完整集成宏
' 功能: 参数化修改 -> 重建 -> 导出 -> CLI分析 -> 显示报告

Sub RunOptimization()
    Dim swApp As Object
    Dim Part As Object
    Dim shell As Object
    Dim exportPath As String
    Dim reportPath As String
    
    ' 初始化
    Set swApp = Application.SldWorks
    Set Part = swApp.ActiveDoc
    Set shell = CreateObject("WScript.Shell")
    
    If Part Is Nothing Then
        MsgBox "请先打开一个模型!", vbExclamation, "CAE-CLI"
        Exit Sub
    End If
    
    ' 设置路径
    Dim tempDir As String
    tempDir = Environ("TEMP") & "\\CAE-CLI\\"
    shell.Run "cmd /c mkdir """ & tempDir & """"", 0, True
    
    exportPath = tempDir & "model.step"
    reportPath = tempDir & "report.html"
    
    ' 第1步: 修改参数（示例：增大圆角）
    Call ModifyFilletRadius(10)
    
    ' 第2步: 重建模型
    Part.EditRebuild3
    DoEvents
    
    ' 第3步: 导出STEP
    Dim longstatus As Long
    longstatus = Part.SaveAs3(exportPath, 0, 2)
    
    If longstatus = 1 Then
        MsgBox "导出失败!", vbCritical, "CAE-CLI"
        Exit Sub
    End If
    
    ' 第4步: 调用CLI分析
    Dim cliCommand As String
    cliCommand = "{cli_command} parse """ & exportPath & """ --verbose"
    
    MsgBox "正在调用CAE-CLI分析..." & vbCrLf & _
           "命令: " & cliCommand, vbInformation, "CAE-CLI"
    
    ' 执行CLI命令
    shell.Run cliCommand, 1, True
    
    ' 第5步: 生成报告
    cliCommand = "{cli_command} report static -i """ & exportPath & """ -o """ & reportPath & """"
    shell.Run cliCommand, 1, True
    
    ' 第6步: 显示报告路径
    If Dir(reportPath) <> "" Then
        MsgBox "分析完成!" & vbCrLf & vbCrLf & _
               "报告路径:" & vbCrLf & reportPath & vbCrLf & vbCrLf & _
               "是否打开报告?", vbQuestion + vbYesNo, "CAE-CLI"
        
        If vbYes Then
            shell.Run "explorer """ & reportPath & """"
        End If
    Else
        MsgBox "分析完成，但未找到报告文件。", vbInformation, "CAE-CLI"
    End If
    
    Set shell = Nothing
    
End Sub

Sub ModifyFilletRadius(newRadius As Double)
    ' 修改圆角半径
    Dim swApp As Object
    Dim Part As Object
    Dim swFeat As Object
    
    Set swApp = Application.SldWorks
    Set Part = swApp.ActiveDoc
    
    If Part Is Nothing Then Exit Sub
    
    ' 遍历特征查找圆角
    Set swFeat = Part.FirstFeature
    
    Do While Not swFeat Is Nothing
        If swFeat.GetTypeName = "Fillet" Then
            ' 找到圆角特征，修改半径
            Dim swFillet As Object
            Set swFillet = swFeat.GetSpecificFeature2
            
            ' 设置新半径（毫米转换为米）
            swFillet.DefaultRadius = newRadius / 1000
            
            Exit Do
        End If
        Set swFeat = swFeat.GetNextFeature
    Loop
    
End Sub

Sub OptimizeLoop()
    ' 简单优化循环：改圆角R -> 看质量变化
    Dim radii As Variant
    radii = Array(2, 5, 10, 15)
    
    Dim i As Integer
    For i = LBound(radii) To UBound(radii)
        MsgBox "正在测试圆角 R = " & radii(i) & " mm", vbInformation, "优化循环"
        
        Call ModifyFilletRadius(radii(i))
        
        ' 这里可以调用分析并记录结果
        ' Call RunAnalysisAndRecord(radii(i))
        
    Next i
    
    MsgBox "优化循环完成!", vbInformation, "CAE-CLI"
End Sub
'''
        return macro_code

    @staticmethod
    def save_macro(macro_code: str, output_file: str):
        """保存宏到文件"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(macro_code)

        return output_path

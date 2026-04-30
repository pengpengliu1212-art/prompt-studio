#!/usr/bin/env python3
"""
创建一个简单的Word文档
使用基本的XML结构创建.docx文件
"""

import os
import zipfile
from datetime import datetime

def create_simple_docx():
    # 创建临时目录
    temp_dir = "/tmp/docx_temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 1. 创建必要的目录结构
    os.makedirs(f"{temp_dir}/_rels", exist_ok=True)
    os.makedirs(f"{temp_dir}/docProps", exist_ok=True)
    os.makedirs(f"{temp_dir}/word", exist_ok=True)
    os.makedirs(f"{temp_dir}/word/_rels", exist_ok=True)
    
    # 2. 创建 [Content_Types].xml
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
    <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
    <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''
    
    with open(f"{temp_dir}/[Content_Types].xml", "w", encoding="utf-8") as f:
        f.write(content_types)
    
    # 3. 创建 _rels/.rels
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
    
    with open(f"{temp_dir}/_rels/.rels", "w", encoding="utf-8") as f:
        f.write(rels)
    
    # 4. 创建 word/document.xml
    document_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="48"/>
                </w:rPr>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="48"/>
                </w:rPr>
                <w:t>钢化膜公司商业计划书</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="32"/>
                </w:rPr>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="32"/>
                </w:rPr>
                <w:t>（300万预算优化版）</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>编制日期：2026年4月1日</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:jc w:val="center"/>
            </w:pPr>
            <w:r>
                <w:t>编制人：白月AI助理</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:spacing w:before="240" w:after="120"/>
            </w:pPr>
            <w:r>
                <w:t> </w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="28"/>
                </w:rPr>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="28"/>
                </w:rPr>
                <w:t>目录</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>一、项目概述</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>二、市场分析</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>三、竞争优势</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>四、团队组建方案</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>五、300万预算详细分配</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>六、盈利预测与投资回报</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>七、实施路线图</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>八、风险控制</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>九、分红激励机制</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>十、总结建议</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:spacing w:before="240" w:after="120"/>
            </w:pPr>
            <w:r>
                <w:t> </w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="28"/>
                </w:rPr>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="28"/>
                </w:rPr>
                <w:t>一、项目概述</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="24"/>
                </w:rPr>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="24"/>
                </w:rPr>
                <w:t>1.1 项目背景</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>基于自有工厂的钢化膜生产优势，计划创立自主品牌，实现自产自销。通过电商+线下双渠道布局，打造中高端钢化膜品牌。</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="24"/>
                </w:rPr>
            </w:pPr>
            <w:r>
                <w:rPr>
                    <w:b/>
                    <w:sz w:val="24"/>
                </w:rPr>
                <w:t>1.2 核心优势</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>• 自有工厂：成本控制能力强，产品质量可控</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>• 集团支持：办公场地、供应链资源</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>• 轻资产运营：云仓物流、聚焦核心平台</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:spacing w:before="120" w:after="60"/>
            </w:pPr>
            <w:r>
                <w:t> </w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>--- 文档内容摘要 ---</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>完整内容请查看附件文本文件</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:pPr>
                <w:spacing w:before="240" w:after="120"/>
            </w:pPr>
            <w:r>
                <w:t> </w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>文档编制完成时间：2026年4月1日</w:t>
            </w:r>
        </w:p>
        
        <w:p>
            <w:r>
                <w:t>版本：1.0</w:t>
            </w:r>
        </w:p>
        
        <w:sectPr>
            <w:pgSz w:w="11906" w:h="16838"/>
            <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
            <w:cols w:space="720"/>
            <w:docGrid w:linePitch="360"/>
        </w:sectPr>
    </w:body>
</w:document>'''
    
    with open(f"{temp_dir}/word/document.xml", "w", encoding="utf-8") as f:
        f.write(document_content)
    
    # 5. 创建 word/styles.xml (简化版)
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:docDefaults>
        <w:rPrDefault>
            <w:rPr>
                <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/>
                <w:sz w:val="24"/>
                <w:szCs w:val="24"/>
            </w:rPr>
        </w:rPrDefault>
    </w:docDefaults>
</w:styles>'''
    
    with open(f"{temp_dir}/word/styles.xml", "w", encoding="utf-8") as f:
        f.write(styles)
    
    # 6. 创建 docProps/core.xml
    core_props = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:dcmitype="http://purl.org/dc/dcmitype/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>钢化膜公司商业计划书</dc:title>
    <dc:creator>白月AI助理</dc:creator>
    <cp:lastModifiedBy>白月AI助理</cp:lastModifiedBy>
    <dcterms:created xsi:type="dcterms:W3CDTF">{datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}</dcterms:created>
    <dcterms:modified xsi:type="dcterms:W3CDTF">{datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}</dcterms:modified>
</cp:coreProperties>'''
    
    with open(f"{temp_dir}/docProps/core.xml", "w", encoding="utf-8") as f:
        f.write(core_props)
    
    # 7. 创建 docProps/app.xml
    app_props = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
    xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
    <Application>Microsoft Office Word</Application>
    <DocSecurity>0</DocSecurity>
    <ScaleCrop>false</ScaleCrop>
    <HeadingPairs>
        <vt:vector size="2" baseType="variant">
            <vt:variant>
                <vt:lpstr>标题</vt:lpstr>
            </vt:variant>
            <vt:variant>
                <vt:i4>1</vt:i4>
            </vt:variant>
        </vt:vector>
    </HeadingPairs>
    <TitlesOfParts>
        <vt:vector size="1" baseType="lpstr">
            <vt:lpstr>钢化膜公司商业计划书</vt:lpstr>
        </vt:vector>
    </TitlesOfParts>
    <Company>钢化膜公司</Company>
    <LinksUpToDate>false</LinksUpToDate>
    <SharedDoc>false</SharedDoc>
    <HyperlinksChanged>false</HyperlinksChanged>
    <AppVersion>16.0000</AppVersion>
</Properties>'''
    
    with open(f"{temp_dir}/docProps/app.xml", "w", encoding="utf-8") as f:
        f.write(app_props)
    
    # 8. 创建 word/_rels/document.xml.rels
    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
    
    with open(f"{temp_dir}/word/_rels/document.xml.rels", "w", encoding="utf-8") as f:
        f.write(doc_rels)
    
    # 9. 打包为.docx文件
    output_path = "/root/.openclaw/workspace/钢化膜商业计划书_简单版.docx"
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx:
        # 添加所有文件
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                docx.write(file_path, arcname)
    
    # 清理临时目录
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"文档已创建: {output_path}")
    return output_path

if __name__ == "__main__":
    try:
        file_path = create_simple_docx()
        print(f"✅ 简单的Word文档创建成功: {file_path}")
    except Exception as e:
        print(f"❌ 创建文档时出错: {e}")
        import traceback
        traceback.print_exc()
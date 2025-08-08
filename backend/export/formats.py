from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import zipfile
import io
from datetime import datetime

class BaseExporter(ABC):
    """Base class for content exporters"""
    
    @abstractmethod
    async def export(self, workflow, content_items: List, options: Dict[str, Any]) -> bytes:
        """Export content in specific format"""
        pass

class PDFExporter(BaseExporter):
    """Export content as PDF"""
    
    async def export(self, workflow, content_items: List, options: Dict[str, Any]) -> bytes:
        """Export workflow content as PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title page
            title = Paragraph(workflow.title, styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            if workflow.description:
                desc = Paragraph(workflow.description, styles['Normal'])
                story.append(desc)
                story.append(Spacer(1, 12))
            
            # Content
            for item in content_items:
                if item.content_type == "outline":
                    story.extend(self._format_outline_pdf(item.content_data, styles))
                elif item.content_type == "module":
                    story.extend(self._format_module_pdf(item.content_data, styles))
            
            doc.build(story)
            return buffer.getvalue()
            
        except ImportError:
            # Fallback if reportlab not available
            return self._create_simple_pdf(workflow, content_items)
    
    def _format_outline_pdf(self, outline_data: Dict, styles) -> List:
        """Format outline for PDF"""
        from reportlab.platypus import Paragraph, Spacer
        
        story = []
        story.append(Paragraph("Course Outline", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        for module in outline_data.get("modules", []):
            story.append(Paragraph(module.get("title", ""), styles['Heading2']))
            if module.get("description"):
                story.append(Paragraph(module["description"], styles['Normal']))
            story.append(Spacer(1, 6))
        
        return story
    
    def _format_module_pdf(self, module_data: Dict, styles) -> List:
        """Format module for PDF"""
        from reportlab.platypus import Paragraph, Spacer
        
        story = []
        story.append(Paragraph(module_data.get("title", "Module"), styles['Heading1']))
        story.append(Spacer(1, 12))
        
        content = module_data.get("content", {})
        if content.get("introduction"):
            story.append(Paragraph(content["introduction"], styles['Normal']))
            story.append(Spacer(1, 12))
        
        return story
    
    def _create_simple_pdf(self, workflow, content_items) -> bytes:
        """Simple PDF fallback"""
        content = f"Course: {workflow.title}\n\n"
        content += f"Description: {workflow.description}\n\n"
        
        for item in content_items:
            content += f"\n{item.content_type.upper()}: {item.title}\n"
            content += "-" * 50 + "\n"
            content += json.dumps(item.content_data, indent=2) + "\n\n"
        
        return content.encode('utf-8')

class HTMLExporter(BaseExporter):
    """Export content as HTML"""
    
    async def export(self, workflow, content_items: List, options: Dict[str, Any]) -> bytes:
        """Export workflow content as HTML"""
        
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #333; border-bottom: 2px solid #007bff; }}
                h2 {{ color: #555; margin-top: 30px; }}
                .module {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007bff; }}
                .lesson {{ margin: 15px 0; padding: 10px; background: #f8f9fa; }}
                .metadata {{ color: #666; font-size: 0.9em; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>{description}</p>
            {content}
            <div class="metadata">
                <p>Generated on: {timestamp}</p>
                <p>Workflow ID: {workflow_id}</p>
            </div>
        </body>
        </html>
        """
        
        content_html = ""
        
        for item in content_items:
            if item.content_type == "outline":
                content_html += self._format_outline_html(item.content_data)
            elif item.content_type == "module":
                content_html += self._format_module_html(item.content_data)
        
        html = html_template.format(
            title=workflow.title,
            description=workflow.description or "",
            content=content_html,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            workflow_id=workflow.id
        )
        
        return html.encode('utf-8')
    
    def _format_outline_html(self, outline_data: Dict) -> str:
        """Format outline as HTML"""
        html = "<h2>Course Outline</h2>"
        
        for module in outline_data.get("modules", []):
            html += f'<div class="module">'
            html += f'<h3>{module.get("title", "")}</h3>'
            if module.get("description"):
                html += f'<p>{module["description"]}</p>'
            
            for lesson in module.get("lessons", []):
                html += f'<div class="lesson">'
                html += f'<h4>{lesson.get("title", "")}</h4>'
                if lesson.get("description"):
                    html += f'<p>{lesson["description"]}</p>'
                html += f'</div>'
            
            html += f'</div>'
        
        return html
    
    def _format_module_html(self, module_data: Dict) -> str:
        """Format module as HTML"""
        html = f'<div class="module">'
        html += f'<h2>{module_data.get("title", "Module")}</h2>'
        
        content = module_data.get("content", {})
        if content.get("introduction"):
            html += f'<p>{content["introduction"]}</p>'
        
        for lesson in content.get("lessons", []):
            html += f'<div class="lesson">'
            html += f'<h3>{lesson.get("title", "")}</h3>'
            html += f'<div>{lesson.get("content", "")}</div>'
            html += f'</div>'
        
        html += f'</div>'
        return html

class SCORMExporter(BaseExporter):
    """Export content as SCORM package"""
    
    async def export(self, workflow, content_items: List, options: Dict[str, Any]) -> bytes:
        """Export workflow content as SCORM package"""
        
        # Create SCORM package structure
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # imsmanifest.xml
            manifest = self._create_manifest(workflow, content_items)
            zip_file.writestr("imsmanifest.xml", manifest)
            
            # index.html
            html_content = await HTMLExporter().export(workflow, content_items, options)
            zip_file.writestr("index.html", html_content)
            
            # SCORM API files (simplified)
            zip_file.writestr("scorm_api.js", self._get_scorm_api_js())
            
        return buffer.getvalue()
    
    def _create_manifest(self, workflow, content_items: List) -> str:
        """Create SCORM manifest file"""
        manifest = f"""<?xml version="1.0" encoding="UTF-8"?>
        <manifest identifier="course_{workflow.id}" version="1.0"
                 xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
                 xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3">
            <metadata>
                <schema>ADL SCORM</schema>
                <schemaversion>2004 4th Edition</schemaversion>
            </metadata>
            <organizations default="course_org">
                <organization identifier="course_org">
                    <title>{workflow.title}</title>
                    <item identifier="item_1" identifierref="resource_1">
                        <title>{workflow.title}</title>
                    </item>
                </organization>
            </organizations>
            <resources>
                <resource identifier="resource_1" type="webcontent" 
                         adlcp:scormType="sco" href="index.html">
                    <file href="index.html"/>
                    <file href="scorm_api.js"/>
                </resource>
            </resources>
        </manifest>"""
        
        return manifest
    
    def _get_scorm_api_js(self) -> str:
        """Get basic SCORM API JavaScript"""
        return """
        // Basic SCORM API implementation
        var API = {
            Initialize: function(parameter) { return "true"; },
            Terminate: function(parameter) { return "true"; },
            GetValue: function(parameter) { return ""; },
            SetValue: function(parameter, value) { return "true"; },
            Commit: function(parameter) { return "true"; },
            GetLastError: function() { return "0"; },
            GetErrorString: function(errorCode) { return ""; },
            GetDiagnostic: function(errorCode) { return ""; }
        };
        
        window.API = API;
        window.API_1484_11 = API;
        """
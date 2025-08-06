#!/usr/bin/env python3
"""
Courzly CLI - Command-line interface for dynamic agent platform
"""

import click
import json
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import asyncio
import httpx
from datetime import datetime

from .config import Config
from .api_client import APIClient
from .utils import format_duration, format_status, load_json_file, save_json_file

console = Console()
config = Config()
api_client = APIClient(config.api_url, config.auth_token)

@click.group()
@click.version_option(version='1.0.0')
@click.option('--config-file', default='~/.courzly/config.json', help='Configuration file path')
@click.pass_context
def cli(ctx, config_file):
    """Courzly CLI - Dynamic Agent Platform Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = Path(config_file).expanduser()
    
    # Load configuration
    if ctx.obj['config_file'].exists():
        config.load_from_file(ctx.obj['config_file'])

@cli.group()
def course():
    """Course creation and management commands"""
    pass

@course.command('create')
@click.option('--title', required=True, help='Course title')
@click.option('--description', required=True, help='Course description')
@click.option('--audience', required=True, help='Target audience')
@click.option('--duration', required=True, help='Course duration')
@click.option('--level', type=click.Choice(['beginner', 'intermediate', 'advanced']), required=True)
@click.option('--template', help='Template ID to use')
@click.option('--config-file', help='JSON configuration file')
@click.option('--wait', is_flag=True, help='Wait for completion')
def create_course(title, description, audience, duration, level, template, config_file, wait):
    """Create a new course"""
    try:
        if config_file:
            course_config = load_json_file(config_file)
        else:
            course_config = {
                'title': title,
                'description': description,
                'target_audience': audience,
                'duration': duration,
                'difficulty_level': level,
                'learning_objectives': [],
                'topics': [],
                'assessment_type': 'mixed'
            }
            
            if template:
                course_config['template_id'] = template

        with console.status("[bold green]Creating course...") as status:
            result = asyncio.run(api_client.create_course(course_config))
            
        console.print(f"✅ Course creation started!")
        console.print(f"📋 Execution ID: {result['execution_id']}")
        
        if wait:
            monitor_execution(result['execution_id'])
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)

@course.command('status')
@click.argument('execution_id')
def course_status(execution_id):
    """Check course creation status"""
    try:
        status = asyncio.run(api_client.get_execution_status(execution_id))
        
        table = Table(title=f"Course Creation Status - {execution_id}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", format_status(status['status']))
        table.add_row("Progress", f"{status['progress']:.1f}%")
        table.add_row("Current Step", status.get('current_step', 'N/A'))
        table.add_row("Started", status['started_at'])
        
        if status.get('completed_at'):
            table.add_row("Completed", status['completed_at'])
            
        console.print(table)
        
        if status.get('logs'):
            console.print("\n📋 Recent Logs:")
            for log in status['logs'][-5:]:
                console.print(f"  {log['timestamp']}: {log['message']}")
                
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)

@course.command('batch')
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--template', help='Default template ID')
@click.option('--wait', is_flag=True, help='Wait for all completions')
def batch_create(csv_file, template, wait):
    """Create multiple courses from CSV file"""
    try:
        courses = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                course_config = {
                    'title': row['title'],
                    'description': row['description'],
                    'target_audience': row['target_audience'],
                    'duration': row['duration'],
                    'difficulty_level': row['difficulty_level'],
                    'learning_objectives': row.get('learning_objectives', '').split(';'),
                    'topics': row.get('topics', '').split(';'),
                    'assessment_type': row.get('assessment_type', 'mixed')
                }
                
                if template or row.get('template_id'):
                    course_config['template_id'] = row.get('template_id', template)
                    
                courses.append(course_config)
        
        console.print(f"📚 Found {len(courses)} courses to create")
        
        if not Confirm.ask("Continue with batch creation?"):
            return
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating courses...", total=len(courses))
            
            execution_ids = []
            for course in courses:
                result = asyncio.run(api_client.create_course(course))
                execution_ids.append(result['execution_id'])
                progress.advance(task)
                
        console.print(f"✅ Started {len(execution_ids)} course creations")
        
        # Save execution IDs for tracking
        save_json_file('batch_executions.json', {
            'timestamp': datetime.now().isoformat(),
            'executions': execution_ids
        })
        
        if wait:
            console.print("⏳ Waiting for all courses to complete...")
            for exec_id in execution_ids:
                monitor_execution(exec_id, show_logs=False)
                
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)

@cli.group()
def workflow():
    """Workflow management commands"""
    pass

@workflow.command('execute')
@click.argument('agent_id')
@click.option('--params', help='JSON parameters file')
@click.option('--param', multiple=True, help='Parameter key=value pairs')
@click.option('--wait', is_flag=True, help='Wait for completion')
def execute_workflow(agent_id, params, param, wait):
    """Execute a workflow"""
    try:
        parameters = {}
        
        if params:
            parameters = load_json_file(params)
            
        for p in param:
            key, value = p.split('=', 1)
            parameters[key] = value
            
        result = asyncio.run(api_client.execute_workflow(agent_id, parameters))
        
        console.print(f"✅ Workflow execution started!")
        console.print(f"📋 Execution ID: {result['execution_id']}")
        
        if wait:
            monitor_execution(result['execution_id'])
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)

@cli.group()
def template():
    """Template management commands"""
    pass

@template.command('list')
@click.option('--category', help='Filter by category')
@click.option('--search', help='Search templates')
def list_templates(category, search):
    """List available templates"""
    try:
        templates = asyncio.run(api_client.get_templates(category, search))
        
        table = Table(title="Available Templates")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Description")
        
        for template in templates['templates']:
            table.add_row(
                template['id'][:8] + '...',
                template['name'],
                template['category'],
                template['description'][:50] + '...' if len(template['description']) > 50 else template['description']
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)

@cli.group()
def approval():
    """Approval management commands"""
    pass

@approval.command('list')
def list_approvals():
    """List pending approvals"""
    try:
        approvals = asyncio.run(api_client.get_pending_approvals())
        
        if not approvals['approvals']:
            console.print("✅ No pending approvals")
            return
            
        table = Table(title="Pending Approvals")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Message")
        table.add_column("Created", style="green")
        
        for approval in approvals['approvals']:
            table.add_row(
                approval['id'][:8] + '...',
                approval['type'],
                approval['message'][:50] + '...' if len(approval['message']) > 50 else approval['message'],
                approval['created_at']
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)

@approval.command('respond')
@click.argument('approval_id')
@click.option('--decision', type=click.Choice(['approve', 'reject', 'request_changes']), required=True)
@click.option('--comments', help='Additional comments')
def respond_approval(approval_id, decision, comments):
    """Respond to an approval request"""
    try:
        response_data = {
            'decision': decision,
            'comments': comments or ''
        }
        
        result = asyncio.run(api_client.respond_to_approval(approval_id, response_data))
        
        console.print(f"✅ Approval response recorded: {decision}")
        console.print(f"📋 {result['message']}")
        
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)

@cli.command('monitor')
@click.argument('execution_id')
@click.option('--refresh', default=5, help='Refresh interval in seconds')
def monitor(execution_id, refresh):
    """Monitor execution in real-time"""
    monitor_execution(execution_id, refresh_interval=refresh)

def monitor_execution(execution_id: str, refresh_interval: int = 5, show_logs: bool = True):
    """Monitor execution progress"""
    try:
        with console.status("[bold green]Monitoring execution...") as status:
            while True:
                exec_status = asyncio.run(api_client.get_execution_status(execution_id))
                
                status.update(f"[bold green]Status: {exec_status['status']} - Progress: {exec_status['progress']:.1f}%")
                
                if exec_status['status'] in ['completed', 'failed', 'cancelled']:
                    break
                    
                asyncio.run(asyncio.sleep(refresh_interval))
                
        # Final status
        final_status = format_status(exec_status['status'])
        if exec_status['status'] == 'completed':
            console.print(f"✅ Execution completed successfully! {final_status}")
        else:
            console.print(f"❌ Execution {final_status}")
            
        if show_logs and exec_status.get('logs'):
            console.print("\n📋 Execution Logs:")
            for log in exec_status['logs']:
                console.print(f"  {log['timestamp']}: {log['message']}")
                
    except KeyboardInterrupt:
        console.print("\n⏹️  Monitoring stopped")
    except Exception as e:
        console.print(f"❌ Error monitoring execution: {e}", style="red")

@cli.command('config')
@click.option('--api-url', help='API base URL')
@click.option('--token', help='Authentication token')
@click.option('--show', is_flag=True, help='Show current configuration')
@click.pass_context
def configure(ctx, api_url, token, show):
    """Configure CLI settings"""
    config_file = ctx.obj['config_file']
    
    if show:
        console.print(Panel(f"""
API URL: {config.api_url}
Auth Token: {'*' * 20 if config.auth_token else 'Not set'}
Config File: {config_file}
        """, title="Current Configuration"))
        return
        
    if api_url:
        config.api_url = api_url
        
    if token:
        config.auth_token = token
        
    # Ensure config directory exists
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    config.save_to_file(config_file)
    
    console.print("✅ Configuration saved!")

if __name__ == '__main__':
    cli()
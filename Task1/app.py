from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)
FILE_NAME = 'tasks.json'

def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

tasks = load_tasks()

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    new_task_text = request.form.get('task', '').strip()
    priority = request.form.get('priority', 'средний')
    
    if new_task_text:
        today = datetime.now().strftime("%d.%m.%Y %H:%M")
        tasks.append({
            'text': new_task_text,
            'date': today,
            'done': False,
            'priority': priority
        })
        save_tasks(tasks)
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect('/')

@app.route('/clear_all')
def clear_all_tasks():
    tasks.clear()
    save_tasks(tasks)
    return redirect('/')

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]['done'] = not tasks[task_id]['done']
        save_tasks(tasks)
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(tasks):
        return "Задача не найдена", 404
    
    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        new_priority = request.form.get('priority', 'средний')
        
        old_text = tasks[task_id]['text']
        old_priority = tasks[task_id].get('priority', 'средний')

        if not new_text:
            return render_template('edit.html', task=tasks[task_id], message="Текст не может быть пустым!")

        if new_text == old_text and new_priority == old_priority:
            return render_template('edit.html', task=tasks[task_id], message="Ничего не изменено")

        tasks[task_id]['text'] = new_text
        tasks[task_id]['priority'] = new_priority
        save_tasks(tasks)
        return redirect('/')
    
    return render_template('edit.html', task=tasks[task_id])

@app.route('/active')
def active_tasks():
    return render_template('index.html', tasks=tasks, filter='active')

@app.route('/completed')
def completed_tasks():
    return render_template('index.html', tasks=tasks, filter='completed')

@app.route('/complete_all')
def complete_all():
    for task in tasks:
        task['done'] = True
    save_tasks(tasks)
    return redirect('/')

@app.route('/uncomplete_all')
def uncomplete_all():
    for task in tasks:
        task['done'] = False
    save_tasks(tasks)
    return redirect('/')

@app.route('/by_priority')
def by_priority():
    priority_order = {'высокий': 3, 'средний': 2, 'низкий': 1}
    sorted_tasks = sorted(
        tasks,
        key=lambda task: priority_order.get(task.get('priority', 'средний'), 2),
        reverse=True
    )
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/by_priority_active')
def by_priority_active():
    priority_order = {'высокий': 3, 'средний': 2, 'низкий': 1}
    active_tasks = [task for task in tasks if not task['done']]
    sorted_tasks = sorted(
        active_tasks,
        key=lambda task: priority_order.get(task.get('priority', 'средний'), 2),
        reverse=True
    )
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    if query:
        filtered_tasks = [task for task in tasks if query in task['text'].lower()]
    else:
        filtered_tasks = tasks
    return render_template('index.html', tasks=filtered_tasks, search_query=query)

if __name__ == '__main__':
    app.run(debug=True)
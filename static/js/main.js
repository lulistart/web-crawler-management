layui.define(['form', 'table', 'layer', 'jquery'], function(exports){
    var form = layui.form;
    var table = layui.table;
    var layer = layui.layer;
    var $ = layui.jquery;
    
    // 登录表单提交
    form.on('submit(login)', function(data){
        fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data.field)
        })
        .then(response => response.json())
        .then(result => {
            if(result.code === 0) {
                location.href = '/';
            } else {
                layer.msg(result.msg);
            }
        });
        return false;
    });
    
    // 注册表单提交
    form.on('submit(register)', function(data){
        if(data.field.password !== data.field.repassword) {
            layer.msg('两次密码输入不一致');
            return false;
        }
        
        fetch('/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data.field)
        })
        .then(response => response.json())
        .then(result => {
            if(result.code === 0) {
                location.href = '/';
            } else {
                layer.msg(result.msg);
            }
        });
        return false;
    });
    
    // 任务表格初始化
    if(document.getElementById('taskTable')) {
        // 表格渲染
        table.render({
            elem: '#taskTable',
            url: '/task/list',
            toolbar: true,
            defaultToolbar: ['filter', 'exports', 'print'],
            page: true,
            cols: [[
                {type: 'checkbox', fixed: 'left'},
                {field: 'id', title: 'ID', width: 80},
                {field: 'name', title: '任务名称'},
                {field: 'url', title: 'URL'},
                {field: 'status', title: '状态', templet: '#statusTpl', width: 100},
                {field: 'created_at', title: '创建时间', width: 160},
                {title: '操作', toolbar: '#tableToolbar', width: 120, fixed: 'right'}
            ]],
            response: {
                statusCode: 0
            }
        });

        // 添加轮询函数
        function pollTaskStatus(taskId) {
            let timer = setInterval(() => {
                fetch('/task/' + taskId + '/status')
                .then(response => response.json())
                .then(result => {
                    if(result.code === 0) {
                        if(result.data.status !== 'running') {
                            clearInterval(timer);
                            table.reload('taskTable');
                        }
                    } else {
                        clearInterval(timer);
                        layer.msg(result.msg);
                    }
                });
            }, 2000);  // 每2秒检查一次
        }

        // 批量开始按钮点击事件
        $('#batchStart').on('click', function(){
            var checkStatus = table.checkStatus('taskTable');
            var data = checkStatus.data;
            
            if(data.length === 0){
                layer.msg('请选择要开始的任务');
                return;
            }
            
            var waitingTasks = data.filter(item => item.status === 'waiting');
            if(waitingTasks.length === 0){
                layer.msg('所选任务中没有等待执行的任务');
                return;
            }
            
            layer.confirm('确认开始选中的任务？', function(index){
                var taskIds = waitingTasks.map(item => item.id);
                fetch('/task/batch/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task_ids: taskIds})
                })
                .then(response => response.json())
                .then(result => {
                    if(result.code === 0) {
                        table.reload('taskTable');
                        layer.msg('批量开始成功');
                        // 为每个任务启动轮询
                        taskIds.forEach(taskId => pollTaskStatus(taskId));
                    } else {
                        layer.msg(result.msg);
                    }
                });
                layer.close(index);
            });
        });

        // 批量删除按钮点击事件
        $('#batchDelete').on('click', function(){
            var checkStatus = table.checkStatus('taskTable');
            var data = checkStatus.data;
            
            if(data.length === 0){
                layer.msg('请选择要删除的任务');
                return;
            }
            
            layer.confirm('确认删除选中的任务？', function(index){
                var taskIds = data.map(item => item.id);
                fetch('/task/batch/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task_ids: taskIds})
                })
                .then(response => response.json())
                .then(result => {
                    if(result.code === 0) {
                        table.reload('taskTable');
                        layer.msg('批量删除成功');
                    } else {
                        layer.msg(result.msg);
                    }
                });
                layer.close(index);
            });
        });
    }
    
    // 显示新建任务表单
    function showAddTaskForm() {
        layer.open({
            type: 1,
            title: '新建任务',
            area: ['500px', '400px'],
            content: $('#addTaskTpl').html(),
            success: function(){
                form.render();
            }
        });
    }

    // 显示批量新建任务表单
    function showBatchAddTaskForm() {
        layer.open({
            type: 1,
            title: '批量新建任务',
            area: ['600px', '500px'],
            content: $('#batchAddTaskTpl').html(),
            success: function(){
                form.render();
            }
        });
    }

    // 绑定新建任务按钮事件
    $('#addTask').on('click', function(){
        showAddTaskForm();
    });

    // 绑定批量新建任务按钮事件
    $('#batchAddTask').on('click', function(){
        showBatchAddTaskForm();
    });

    // 批量创建任务表单提交
    form.on('submit(batchCreateTask)', function(data){
        const tasks = data.field.tasks.split('\n')
            .map(line => line.trim())
            .filter(line => line)  // 过滤空行
            .map(line => {
                const [name, url] = line.split('-').map(s => s.trim());
                return { name, url };
            })
            .filter(task => task.name && task.url);  // 过滤无效任务

        if (tasks.length === 0) {
            layer.msg('没有有效的任务数据');
            return false;
        }

        fetch('/task/batch/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ tasks })
        })
        .then(response => response.json())
        .then(result => {
            if(result.code === 0) {
                layer.closeAll();
                table.reload('taskTable');
                layer.msg('批量创建成功');
            } else {
                layer.msg(result.msg);
            }
        });
        return false;
    });
    
    // 创建任务表单提交
    form.on('submit(createTask)', function(data){
        fetch('/task', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data.field)
        })
        .then(response => response.json())
        .then(result => {
            if(result.code === 0) {
                layer.closeAll();
                table.reload('taskTable');
                layer.msg('创建成功');
            } else {
                layer.msg(result.msg);
            }
        });
        return false;
    });
    
    // 删除任务
    table.on('tool(taskTable)', function(obj){
        if(obj.event === 'del'){
            layer.confirm('确认删除该任务？', function(index){
                fetch('/task/' + obj.data.id, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(result => {
                    if(result.code === 0) {
                        obj.del();
                        layer.msg('删除成功');
                    } else {
                        layer.msg(result.msg);
                    }
                });
                layer.close(index);
            });
        } else if(obj.event === 'start') {
            layer.confirm('确认开始执行该任务？', function(index){
                fetch('/task/' + obj.data.id + '/start', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(result => {
                    if(result.code === 0) {
                        table.reload('taskTable');
                        layer.msg('任务已开始');
                        pollTaskStatus(obj.data.id);  // 开始轮询状态
                    } else {
                        layer.msg(result.msg);
                    }
                });
                layer.close(index);
            });
        }
    });

    exports('main', {});
}); 